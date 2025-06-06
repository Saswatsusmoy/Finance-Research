#!/usr/bin/env python3
"""
FinanceScope Web Server
Flask application to serve the HTML financial research dashboard
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import threading
import logging

# Import existing agents
import sys
sys.path.append('src')
from agents.market_data_agent import MarketDataAgent
from agents.insider_trading_agent import InsiderTradingAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
            static_folder='web',
            template_folder='web')
CORS(app)

# Initialize agents
market_agent = MarketDataAgent()
insider_agent = InsiderTradingAgent()

# Global cache for data
data_cache = {}
cache_timeout = 300  # 5 minutes

def get_from_cache(key, max_age=300):
    """Get data from cache if it's not expired"""
    if key in data_cache:
        timestamp, data = data_cache[key]
        if datetime.now().timestamp() - timestamp < max_age:
            return data
    return None

def set_cache(key, data):
    """Store data in cache with timestamp"""
    data_cache[key] = (datetime.now().timestamp(), data)

@app.route('/')
def index():
    """Serve the main dashboard HTML page"""
    return send_from_directory('web', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (CSS, JS, images)"""
    return send_from_directory('web', filename)

@app.route('/api/market/<symbol>')
def get_market_data(symbol):
    """Get current market data for a symbol"""
    try:
        cache_key = f"market_{symbol}"
        cached_data = get_from_cache(cache_key, 60)  # 1 minute cache
        
        if cached_data:
            return jsonify(cached_data)
        
        # Run async function in thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            data = loop.run_until_complete(market_agent.get_latest_price(symbol))
            
            # Format data for frontend
            formatted_data = {
                'symbol': symbol,
                'name': data.get('company_name', symbol),
                'price': data.get('current_price', 0),
                'change': data.get('change', 0),
                'changePercent': data.get('change_percent', 0),
                'volume': data.get('volume', 0),
                'marketCap': 0,  # Not available in get_latest_price
                'peRatio': 0,   # Not available in get_latest_price
                'high52Week': 0,  # Not available in get_latest_price
                'low52Week': 0,   # Not available in get_latest_price
                'avgVolume': 0,   # Not available in get_latest_price
                'beta': 0,        # Not available in get_latest_price
                'eps': 0,         # Not available in get_latest_price
                'dividendYield': 0,  # Not available in get_latest_price
                'timestamp': data.get('timestamp', datetime.now().isoformat())
            }
            
            set_cache(cache_key, formatted_data)
            return jsonify(formatted_data)
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error fetching market data for {symbol}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/market/batch')
def get_batch_market_data():
    """Get market data for multiple symbols"""
    symbols = request.args.get('symbols', '').split(',')
    symbols = [s.strip().upper() for s in symbols if s.strip()]
    
    if not symbols:
        return jsonify({'error': 'No symbols provided'}), 400
    
    try:
        results = []
        
        # Process each symbol
        for symbol in symbols:
            cache_key = f"market_{symbol}"
            cached_data = get_from_cache(cache_key, 60)
            
            if cached_data:
                results.append(cached_data)
            else:
                # Fetch new data
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    data = loop.run_until_complete(market_agent.get_latest_price(symbol))
                    
                    formatted_data = {
                        'symbol': symbol,
                        'name': data.get('company_name', symbol),
                        'price': data.get('current_price', 0),
                        'change': data.get('change', 0),
                        'changePercent': data.get('change_percent', 0),
                        'volume': data.get('volume', 0),
                        'marketCap': 0,
                        'timestamp': data.get('timestamp', datetime.now().isoformat())
                    }
                    
                    set_cache(cache_key, formatted_data)
                    results.append(formatted_data)
                    
                finally:
                    loop.close()
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error fetching batch market data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/historical/<symbol>')
def get_historical_data(symbol):
    """Get historical price data for a symbol"""
    period = request.args.get('period', '1M')
    interval = request.args.get('interval', '1d')
    
    try:
        cache_key = f"historical_{symbol}_{period}_{interval}"
        cached_data = get_from_cache(cache_key, 300)  # 5 minute cache
        
        if cached_data:
            return jsonify(cached_data)
        
        # Convert period to start/end dates
        end_date = datetime.now()
        period_days = {
            '1D': 1, '1W': 7, '1M': 30, '3M': 90, 
            '6M': 180, '1Y': 365, '2Y': 730, '5Y': 1825
        }
        days = period_days.get(period, 30)
        start_date = end_date - timedelta(days=days)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            data = loop.run_until_complete(
                market_agent.fetch_market_data(
                    symbol, 
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                )
            )
            
            # Format data
            formatted_data = {
                'symbol': symbol,
                'period': period,
                'interval': interval,
                'data': []
            }
            
            if isinstance(data, dict) and 'historical_data' in data:
                for item in data['historical_data']:
                    # Convert pandas timestamp to string if needed
                    date_str = item.get('Date', item.get('date', ''))
                    if hasattr(date_str, 'strftime'):
                        date_str = date_str.strftime('%Y-%m-%d')
                    elif isinstance(date_str, str) and 'T' in date_str:
                        date_str = date_str.split('T')[0]
                    
                    formatted_data['data'].append({
                        'date': str(date_str),
                        'open': float(item.get('Open', item.get('open', 0))),
                        'high': float(item.get('High', item.get('high', 0))),
                        'low': float(item.get('Low', item.get('low', 0))),
                        'close': float(item.get('Close', item.get('close', 0))),
                        'volume': int(item.get('Volume', item.get('volume', 0))),
                        'adjClose': float(item.get('Close', item.get('close', 0)))
                    })
            
            set_cache(cache_key, formatted_data)
            return jsonify(formatted_data)
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/insider/<symbol>')
def get_insider_trading(symbol):
    """Get insider trading data for a symbol"""
    lookback_days = int(request.args.get('lookback', 90))
    
    try:
        cache_key = f"insider_{symbol}_{lookback_days}"
        cached_data = get_from_cache(cache_key, 3600)  # 1 hour cache
        
        if cached_data:
            return jsonify(cached_data)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)
            
            # Run the insider trading agent with input data
            input_data = {
                'symbol': symbol,
                'lookback_days': lookback_days
            }
            result = loop.run_until_complete(insider_agent.run(input_data))
            
            # Extract data from result
            if result.get('status') == 'success':
                data = result.get('data', {})
            else:
                data = {'error': result.get('message', 'Unknown error')}
            
            # Format data for frontend
            formatted_data = {
                'symbol': symbol,
                'lookbackDays': lookback_days,
                'transactions': [],
                'summary': {
                    'totalTransactions': 0,
                    'totalPurchases': 0,
                    'totalSales': 0,
                    'netActivity': 0
                }
            }
            
            if isinstance(data, dict) and 'insider_data' in data:
                insider_data = data['insider_data']
                if 'transactions' in insider_data:
                    transactions = insider_data['transactions']
                    formatted_data['transactions'] = transactions
                    formatted_data['summary']['totalTransactions'] = len(transactions)
                    
                    # Calculate summary stats
                    purchases = [t for t in transactions if t.get('transactionType') == 'Purchase']
                    sales = [t for t in transactions if t.get('transactionType') == 'Sale']
                    
                    formatted_data['summary']['totalPurchases'] = len(purchases)
                    formatted_data['summary']['totalSales'] = len(sales)
                    
                    purchase_value = sum(t.get('value', 0) for t in purchases)
                    sale_value = sum(t.get('value', 0) for t in sales)
                    formatted_data['summary']['netActivity'] = purchase_value - sale_value
            
            set_cache(cache_key, formatted_data)
            return jsonify(formatted_data)
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error fetching insider trading data for {symbol}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/news')
def get_market_news():
    """Get general market news with enhanced features"""
    category = request.args.get('category', 'all')
    limit = int(request.args.get('limit', 20))
    
    try:
        cache_key = f"news_{category}_{limit}"
        cached_data = get_from_cache(cache_key, 600)  # 10 minute cache
        
        if cached_data:
            return jsonify(cached_data)
        
        # Enhanced mock news data with more realistic content
        news_templates = {
            'market': [
                {
                    'title': 'S&P 500 Reaches New All-Time High Amid Economic Optimism',
                    'summary': 'The benchmark index surged 1.2% as investors showed renewed confidence in the economic recovery, driven by strong earnings reports and positive employment data.',
                    'source': 'Reuters',
                    'category': 'market',
                    'breaking': False,
                    'icon': 'chart-line'
                },
                {
                    'title': 'Volatility Index Drops to Lowest Level This Year',
                    'summary': 'The VIX fell below 15 for the first time in 2024, signaling decreased market uncertainty and improved investor sentiment.',
                    'source': 'Bloomberg',
                    'category': 'market',
                    'breaking': False,
                    'icon': 'chart-area'
                },
                {
                    'title': 'Dow Jones Industrial Average Closes Above 35,000',
                    'summary': 'The blue-chip index marked its fifth consecutive day of gains, supported by strong corporate earnings and optimistic economic forecasts.',
                    'source': 'MarketWatch',
                    'category': 'market',
                    'breaking': False,
                    'icon': 'chart-line'
                }
            ],
            'earnings': [
                {
                    'title': 'Apple Reports Record Q4 Earnings, Beats Expectations',
                    'summary': 'Apple Inc. announced quarterly earnings that exceeded analyst estimates, driven by strong iPhone sales and services revenue growth.',
                    'source': 'CNBC',
                    'category': 'earnings',
                    'breaking': True,
                    'icon': 'dollar-sign'
                },
                {
                    'title': 'Microsoft Cloud Revenue Soars 25% Year-over-Year',
                    'summary': 'The tech giant\'s Azure cloud platform continues to drive growth, with enterprise customers increasingly adopting cloud-first strategies.',
                    'source': 'TechCrunch',
                    'category': 'earnings',
                    'breaking': False,
                    'icon': 'cloud'
                },
                {
                    'title': 'Tesla Q3 Deliveries Exceed Wall Street Estimates',
                    'summary': 'Electric vehicle manufacturer reports 435,000 vehicle deliveries in the third quarter, surpassing analyst expectations of 420,000 units.',
                    'source': 'Financial Times',
                    'category': 'earnings',
                    'breaking': False,
                    'icon': 'car'
                }
            ],
            'analysis': [
                {
                    'title': 'Analysts Upgrade Tesla Price Target Following Delivery Numbers',
                    'summary': 'Wall Street firms raise price targets for Tesla stock after the company reported better-than-expected vehicle deliveries for the quarter.',
                    'source': 'MarketWatch',
                    'category': 'analysis',
                    'breaking': False,
                    'icon': 'search-dollar'
                },
                {
                    'title': 'Tech Sector Outlook: AI Revolution Drives Growth',
                    'summary': 'Investment analysts predict continued growth in technology stocks as artificial intelligence adoption accelerates across industries.',
                    'source': 'Barron\'s',
                    'category': 'analysis',
                    'breaking': False,
                    'icon': 'robot'
                }
            ],
            'crypto': [
                {
                    'title': 'Bitcoin Surges Past $45,000 on Institutional Adoption',
                    'summary': 'The world\'s largest cryptocurrency gained 8% today as major corporations announce Bitcoin treasury allocations.',
                    'source': 'CoinDesk',
                    'category': 'crypto',
                    'breaking': True,
                    'icon': 'bitcoin'
                },
                {
                    'title': 'Ethereum 2.0 Staking Reaches New Milestone',
                    'summary': 'Over 20 million ETH tokens are now staked in the Ethereum 2.0 network, representing approximately 16% of the total supply.',
                    'source': 'Decrypt',
                    'category': 'crypto',
                    'breaking': False,
                    'icon': 'coins'
                }
            ],
            'economic': [
                {
                    'title': 'Federal Reserve Signals Potential Rate Cuts in 2024',
                    'summary': 'Fed officials hint at possible monetary policy easing if inflation continues to moderate toward the 2% target.',
                    'source': 'Wall Street Journal',
                    'category': 'economic',
                    'breaking': False,
                    'icon': 'university'
                },
                {
                    'title': 'Unemployment Rate Drops to 3.5%, Lowest in Decades',
                    'summary': 'The U.S. labor market shows remarkable strength with jobless claims falling and wage growth maintaining steady pace.',
                    'source': 'Reuters',
                    'category': 'economic',
                    'breaking': False,
                    'icon': 'users'
                }
            ]
        }
        
        # Select news based on category
        all_news = []
        if category == 'all':
            for cat_news in news_templates.values():
                all_news.extend(cat_news)
        elif category in news_templates:
            all_news = news_templates[category]
        else:
            all_news = news_templates['market']  # Default to market news
        
        # Add metadata and timestamps
        enhanced_news = []
        for i, article in enumerate(all_news):
            # Generate unique ID and timestamp
            timestamp = datetime.now() - timedelta(hours=i*2, minutes=i*15)
            
            # Generate realistic URLs based on source and article
            article_url = generate_article_url(article['source'], article['title'], i)
            
            enhanced_article = {
                **article,
                'id': f"news_{int(timestamp.timestamp())}_{i}",
                'timestamp': timestamp.isoformat(),
                'url': article_url,
                'tags': generate_news_tags(article['category'], article['breaking'])
            }
            enhanced_news.append(enhanced_article)
        
        # Sort by timestamp (newest first) and limit
        enhanced_news.sort(key=lambda x: x['timestamp'], reverse=True)
        filtered_news = enhanced_news[:limit]
        
        set_cache(cache_key, filtered_news)
        return jsonify(filtered_news)
        
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        return jsonify({'error': str(e)}), 500

def generate_article_url(source, title, index):
    """Generate realistic article URLs based on source and title"""
    # Convert title to URL-friendly format
    url_title = title.lower().replace(' ', '-').replace(',', '').replace(':', '').replace('%', 'percent')
    url_title = ''.join(c for c in url_title if c.isalnum() or c in '-')
    
    # Generate URLs based on actual news source patterns
    source_urls = {
        'Reuters': f"https://www.reuters.com/business/{url_title}-{index}",
        'Bloomberg': f"https://www.bloomberg.com/news/articles/{url_title}",
        'CNBC': f"https://www.cnbc.com/2024/12/14/{url_title}.html",
        'MarketWatch': f"https://www.marketwatch.com/story/{url_title}-{index}",
        'Financial Times': f"https://www.ft.com/content/{url_title}",
        'TechCrunch': f"https://techcrunch.com/2024/12/14/{url_title}/",
        'CoinDesk': f"https://www.coindesk.com/business/2024/12/14/{url_title}",
        'Decrypt': f"https://decrypt.co/{url_title}",
        'Wall Street Journal': f"https://www.wsj.com/articles/{url_title}-{index}",
        'Barron\'s': f"https://www.barrons.com/articles/{url_title}-{index}"
    }
    
    return source_urls.get(source, f"https://example.com/news/{url_title}")

def generate_news_tags(category, breaking):
    """Generate tags for news articles"""
    tags = []
    
    if breaking:
        tags.append({'text': 'BREAKING', 'class': 'urgent'})
    
    category_tags = {
        'market': ['Market Update', 'Trading'],
        'earnings': ['Earnings', 'Financial Results'],
        'analysis': ['Analysis', 'Expert Opinion'],
        'crypto': ['Cryptocurrency', 'Digital Assets'],
        'economic': ['Economic Policy', 'Federal Reserve']
    }
    
    if category in category_tags:
        tags.append({'text': category_tags[category][0], 'class': 'normal'})
    
    return tags

@app.route('/api/news/<symbol>')
def get_symbol_news(symbol):
    """Get news specific to a symbol"""
    limit = int(request.args.get('limit', 5))
    
    try:
        cache_key = f"news_{symbol}_{limit}"
        cached_data = get_from_cache(cache_key, 600)
        
        if cached_data:
            return jsonify(cached_data)
        
        # Mock symbol-specific news
        mock_news = [
            {
                'title': f'{symbol} Reports Strong Quarterly Earnings',
                'summary': f'{symbol} exceeded analyst expectations with strong revenue growth...',
                'source': 'Reuters',
                'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
                'url': '#'
            },
            {
                'title': f'Analyst Upgrades {symbol} Price Target',
                'summary': f'Wall Street firm raises price target citing strong fundamentals...',
                'source': 'Bloomberg',
                'timestamp': (datetime.now() - timedelta(hours=4)).isoformat(),
                'url': '#'
            }
        ]
        
        filtered_news = mock_news[:limit]
        set_cache(cache_key, filtered_news)
        return jsonify(filtered_news)
        
    except Exception as e:
        logger.error(f"Error fetching news for {symbol}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/analyze', methods=['POST'])
def analyze_portfolio():
    """Analyze a portfolio of holdings"""
    try:
        data = request.get_json()
        holdings = data.get('holdings', [])
        
        if not holdings:
            return jsonify({'error': 'No holdings provided'}), 400
        
        # Calculate portfolio metrics
        total_value = sum(holding['shares'] * holding['price'] for holding in holdings)
        
        analysis = {
            'totalValue': total_value,
            'dayChange': 0,  # Would calculate from real data
            'dayChangePercent': 0,
            'diversificationScore': 0.75,  # Mock score
            'riskScore': 6.2,  # Mock risk score
            'holdings': []
        }
        
        for holding in holdings:
            holding_value = holding['shares'] * holding['price']
            weight = (holding_value / total_value) * 100 if total_value > 0 else 0
            
            analysis['holdings'].append({
                **holding,
                'value': holding_value,
                'weight': round(weight, 2),
                'dayChange': 0  # Would calculate from real data
            })
        
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"Error analyzing portfolio: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    """Generate a financial report"""
    try:
        data = request.get_json()
        report_type = data.get('type')
        options = data.get('options', {})
        
        # Mock report generation
        report = {
            'type': report_type,
            'generatedAt': datetime.now().isoformat(),
            'options': options,
            'status': 'completed',
            'downloadUrl': '#',
            'data': {
                'summary': f'Mock {report_type} report generated successfully',
                'details': f'This is a placeholder for the {report_type} report content.'
            }
        }
        
        return jsonify(report)
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/technical/<symbol>')
def get_technical_indicators(symbol):
    """Get technical indicators for a symbol"""
    indicators = request.args.get('indicators', 'sma,rsi,macd').split(',')
    
    try:
        cache_key = f"technical_{symbol}_{','.join(indicators)}"
        cached_data = get_from_cache(cache_key, 300)
        
        if cached_data:
            return jsonify(cached_data)
        
        # Mock technical data - replace with actual calculations
        result = {'symbol': symbol}
        
        if 'sma' in indicators:
            result['sma'] = {
                'sma20': round(100 + (hash(symbol) % 100), 2),
                'sma50': round(100 + (hash(symbol + 'sma50') % 100), 2),
                'sma200': round(100 + (hash(symbol + 'sma200') % 100), 2)
            }
        
        if 'rsi' in indicators:
            rsi_value = (hash(symbol + 'rsi') % 100)
            result['rsi'] = {
                'current': round(rsi_value, 2),
                'signal': 'overbought' if rsi_value > 70 else 'oversold' if rsi_value < 30 else 'neutral'
            }
        
        if 'macd' in indicators:
            result['macd'] = {
                'macd': round((hash(symbol + 'macd') % 1000 - 500) / 100, 4),
                'signal': round((hash(symbol + 'signal') % 1000 - 500) / 100, 4),
                'histogram': round((hash(symbol + 'hist') % 1000 - 500) / 100, 4)
            }
        
        set_cache(cache_key, result)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error fetching technical indicators for {symbol}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'cache_size': len(data_cache)
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Ensure web directory exists
    if not os.path.exists('web'):
        os.makedirs('web')
        print("Created web directory. Please ensure your HTML, CSS, and JS files are placed there.")
    
    print("Starting FinanceScope Web Server...")
    print("Dashboard will be available at: http://localhost:5000")
    print("API endpoints available at: http://localhost:5000/api/")
    
    # Run the Flask application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    ) 