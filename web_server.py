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

# Try to import AI analysis agent
try:
    from agents.ai_analysis_agent import AIAnalysisAgent, StockData, TechnicalIndicators
    ai_analysis_agent = AIAnalysisAgent()
    AI_ANALYSIS_AVAILABLE = True
except ImportError as e:
    print(f"AI analysis agent not available: {e}")
    ai_analysis_agent = None
    StockData = None
    TechnicalIndicators = None
    AI_ANALYSIS_AVAILABLE = False

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
        # Get market parameter from query string
        market = request.args.get('market', 'US').upper()
        
        cache_key = f"market_{symbol}_{market}"
        cached_data = get_from_cache(cache_key, 60)  # 1 minute cache
        
        if cached_data:
            return jsonify(cached_data)
        
        # Run async function in thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            data = loop.run_until_complete(market_agent.get_latest_price(symbol, market))
            
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
    market = request.args.get('market', 'US').upper()
    
    if not symbols:
        return jsonify({'error': 'No symbols provided'}), 400
    
    try:
        results = []
        
        # Process each symbol
        for symbol in symbols:
            cache_key = f"market_{symbol}_{market}"
            cached_data = get_from_cache(cache_key, 60)
            
            if cached_data:
                results.append(cached_data)
            else:
                # Fetch new data
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    data = loop.run_until_complete(market_agent.get_latest_price(symbol, market))
                    
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
    market = request.args.get('market', 'US').upper()
    
    try:
        cache_key = f"historical_{symbol}_{period}_{interval}_{market}"
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
                    end_date.strftime('%Y-%m-%d'),
                    interval,
                    market
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
    """Generate a comprehensive financial report"""
    try:
        data = request.get_json()
        report_type = data.get('type', 'portfolio')
        start_date = data.get('startDate')
        end_date = data.get('endDate')
        stock_symbol = data.get('stockSymbol', 'AAPL')
        options = data.get('options', {})
        format_type = data.get('format', 'interactive')
        
        # Generate report data based on type
        report_data = generate_report_data(report_type, start_date, end_date, stock_symbol, options)
        
        # Create comprehensive report response
        report = {
            'type': report_type,
            'generatedAt': datetime.now().isoformat(),
            'config': {
                'type': report_type,
                'startDate': start_date,
                'endDate': end_date,
                'stockSymbol': stock_symbol,
                'format': format_type,
                'options': options
            },
            'status': 'completed',
            'downloadUrl': f'/api/reports/download/{report_type}',
            'data': report_data,
            'metadata': {
                'generationTime': '2.3s',
                'dataPoints': len(report_data.get('holdings', [])) if 'holdings' in report_data else 100,
                'accuracy': '98.5%',
                'lastUpdated': datetime.now().isoformat()
            }
        }
        
        return jsonify(report)
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return jsonify({'error': str(e)}), 500

def generate_report_data(report_type, start_date, end_date, stock_symbol, options):
    """Generate mock data for different report types"""
    
    if report_type == 'portfolio':
        return generate_portfolio_data()
    elif report_type == 'market':
        return generate_market_data()
    elif report_type == 'stock':
        return generate_stock_data(stock_symbol)
    elif report_type == 'risk':
        return generate_risk_data()
    elif report_type == 'performance':
        return generate_performance_data()
    elif report_type == 'esg':
        return generate_esg_data()
    else:
        return {'error': f'Unknown report type: {report_type}'}

def generate_portfolio_data():
    """Generate comprehensive portfolio data"""
    import random
    
    # Mock portfolio holdings
    holdings = [
        {'symbol': 'AAPL', 'shares': 500, 'value': 87500, 'weight': 7.0, 'change': 2.1, 'sector': 'Technology'},
        {'symbol': 'MSFT', 'shares': 300, 'value': 105000, 'weight': 8.4, 'change': 1.8, 'sector': 'Technology'},
        {'symbol': 'GOOGL', 'shares': 200, 'value': 54000, 'weight': 4.3, 'change': -0.5, 'sector': 'Technology'},
        {'symbol': 'AMZN', 'shares': 150, 'value': 48750, 'weight': 3.9, 'change': 3.2, 'sector': 'Consumer'},
        {'symbol': 'TSLA', 'shares': 100, 'value': 25000, 'weight': 2.0, 'change': -1.2, 'sector': 'Technology'},
        {'symbol': 'JNJ', 'shares': 400, 'value': 68000, 'weight': 5.4, 'change': 0.8, 'sector': 'Healthcare'},
        {'symbol': 'JPM', 'shares': 350, 'value': 52500, 'weight': 4.2, 'change': 1.5, 'sector': 'Financials'},
        {'symbol': 'V', 'shares': 250, 'value': 62500, 'weight': 5.0, 'change': 2.3, 'sector': 'Financials'},
        {'symbol': 'PG', 'shares': 300, 'value': 45000, 'weight': 3.6, 'change': 0.5, 'sector': 'Consumer'},
        {'symbol': 'UNH', 'shares': 120, 'value': 60000, 'weight': 4.8, 'change': 1.9, 'sector': 'Healthcare'}
    ]
    
    total_value = sum(h['value'] for h in holdings)
    day_change = sum(h['value'] * h['change'] / 100 for h in holdings)
    day_change_percent = (day_change / total_value) * 100
    
    # Calculate sector allocation
    sector_allocation = {}
    for holding in holdings:
        sector = holding['sector']
        if sector not in sector_allocation:
            sector_allocation[sector] = 0
        sector_allocation[sector] += holding['weight']
    
    # Performance data
    performance = {
        '1D': round(day_change_percent, 2),
        '1W': round(random.uniform(-2, 5), 2),
        '1M': round(random.uniform(-5, 12), 2),
        '3M': round(random.uniform(-8, 20), 2),
        '6M': round(random.uniform(-10, 25), 2),
        '1Y': round(random.uniform(-15, 35), 2),
        '3Y': round(random.uniform(5, 25), 2),
        '5Y': round(random.uniform(8, 20), 2)
    }
    
    return {
        'totalValue': total_value,
        'dayChange': round(day_change, 2),
        'dayChangePercent': round(day_change_percent, 2),
        'holdings': holdings,
        'allocation': sector_allocation,
        'performance': performance,
        'diversificationScore': 0.78,
        'riskScore': 6.2,
        'beta': 1.12,
        'sharpeRatio': 1.45
    }

def generate_market_data():
    """Generate comprehensive market data"""
    import random
    
    indices = {
        'S&P 500': {'value': 4185.47, 'change': round(random.uniform(-2, 3), 2)},
        'NASDAQ': {'value': 12965.34, 'change': round(random.uniform(-3, 4), 2)},
        'Dow Jones': {'value': 33875.12, 'change': round(random.uniform(-2, 2), 2)},
        'Russell 2000': {'value': 1845.23, 'change': round(random.uniform(-3, 3), 2)},
        'VIX': {'value': 18.45, 'change': round(random.uniform(-10, 10), 2)}
    }
    
    sectors = {
        'Technology': round(random.uniform(-2, 4), 1),
        'Healthcare': round(random.uniform(-1, 3), 1),
        'Financials': round(random.uniform(-2, 3), 1),
        'Energy': round(random.uniform(-3, 5), 1),
        'Consumer Discretionary': round(random.uniform(-2, 3), 1),
        'Utilities': round(random.uniform(-1, 2), 1),
        'Real Estate': round(random.uniform(-2, 2), 1),
        'Materials': round(random.uniform(-2, 3), 1),
        'Industrials': round(random.uniform(-1, 3), 1),
        'Communication Services': round(random.uniform(-2, 4), 1),
        'Consumer Staples': round(random.uniform(-1, 2), 1)
    }
    
    breadth = {
        'advancing': random.randint(250, 350),
        'declining': random.randint(150, 250),
        'newHighs': random.randint(20, 80),
        'newLows': random.randint(5, 30),
        'volume': random.randint(3000000000, 6000000000)
    }
    
    economic_indicators = {
        'GDP Growth': '2.1%',
        'Inflation Rate': '3.2%',
        'Unemployment': '3.7%',
        'Fed Funds Rate': '5.25%',
        'Dollar Index': '103.45'
    }
    
    return {
        'indices': indices,
        'sectors': sectors,
        'breadth': breadth,
        'economicIndicators': economic_indicators,
        'marketSentiment': 'Cautiously Optimistic',
        'volatilityLevel': 'Moderate'
    }

def generate_stock_data(symbol):
    """Generate comprehensive stock analysis data"""
    import random
    
    # Mock stock data
    current_price = round(random.uniform(50, 300), 2)
    change = round(random.uniform(-5, 5), 2)
    change_percent = round((change / current_price) * 100, 2)
    
    return {
        'symbol': symbol.upper(),
        'companyName': f'{symbol.upper()} Inc.',
        'currentPrice': current_price,
        'change': change,
        'changePercent': change_percent,
        'volume': random.randint(1000000, 100000000),
        'marketCap': random.randint(10000000000, 3000000000000),
        'peRatio': round(random.uniform(15, 35), 1),
        'week52High': round(current_price * random.uniform(1.1, 1.5), 2),
        'week52Low': round(current_price * random.uniform(0.6, 0.9), 2),
        'technicals': {
            'rsi': round(random.uniform(20, 80), 1),
            'sma20': round(current_price * random.uniform(0.95, 1.05), 2),
            'sma50': round(current_price * random.uniform(0.9, 1.1), 2),
            'sma200': round(current_price * random.uniform(0.8, 1.2), 2),
            'support': round(current_price * random.uniform(0.9, 0.95), 2),
            'resistance': round(current_price * random.uniform(1.05, 1.15), 2),
            'macd': round(random.uniform(-2, 2), 3),
            'bollinger_upper': round(current_price * 1.1, 2),
            'bollinger_lower': round(current_price * 0.9, 2)
        },
        'fundamentals': {
            'eps': round(random.uniform(2, 15), 2),
            'dividendYield': round(random.uniform(0, 4), 2),
            'bookValue': round(random.uniform(10, 50), 2),
            'debtToEquity': round(random.uniform(0.2, 2.5), 2),
            'roe': round(random.uniform(5, 25), 1),
            'roa': round(random.uniform(2, 15), 1),
            'profitMargin': round(random.uniform(5, 30), 1)
        },
        'analyst': {
            'rating': random.choice(['Strong Buy', 'Buy', 'Hold', 'Sell']),
            'priceTarget': round(current_price * random.uniform(1.05, 1.25), 2),
            'consensus': 'Buy',
            'numAnalysts': random.randint(15, 35)
        }
    }

def generate_risk_data():
    """Generate comprehensive risk assessment data"""
    import random
    
    return {
        'portfolioBeta': round(random.uniform(0.8, 1.4), 2),
        'volatility': round(random.uniform(12, 25), 1),
        'sharpeRatio': round(random.uniform(0.8, 2.0), 2),
        'maxDrawdown': round(random.uniform(-25, -8), 1),
        'var95': round(random.uniform(-4, -1), 1),
        'cvar95': round(random.uniform(-5, -2), 1),
        'correlations': {
            'SPY': round(random.uniform(0.7, 0.95), 2),
            'QQQ': round(random.uniform(0.6, 0.9), 2),
            'VIX': round(random.uniform(-0.6, -0.2), 2),
            'DXY': round(random.uniform(-0.3, 0.3), 2)
        },
        'riskMetrics': {
            'Value at Risk (95%)': f'{round(random.uniform(-4, -1), 1)}%',
            'Expected Shortfall': f'{round(random.uniform(-5, -2), 1)}%',
            'Beta': f'{round(random.uniform(0.8, 1.4), 2)}',
            'Alpha': f'{round(random.uniform(-2, 6), 2)}%',
            'Tracking Error': f'{round(random.uniform(2, 8), 1)}%',
            'Information Ratio': f'{round(random.uniform(0.3, 1.2), 2)}',
            'Sortino Ratio': f'{round(random.uniform(1.0, 2.5), 2)}',
            'Calmar Ratio': f'{round(random.uniform(0.8, 2.0), 2)}'
        },
        'stressTesting': {
            '2008 Crisis': f'{round(random.uniform(-35, -20), 1)}%',
            '2020 Pandemic': f'{round(random.uniform(-25, -10), 1)}%',
            'Interest Rate +2%': f'{round(random.uniform(-15, -5), 1)}%',
            'Market Crash -20%': f'{round(random.uniform(-25, -15), 1)}%'
        }
    }

def generate_performance_data():
    """Generate comprehensive performance analytics data"""
    import random
    
    returns = {}
    periods = ['1D', '1W', '1M', '3M', '6M', '1Y', '2Y', '3Y', '5Y']
    for period in periods:
        returns[period] = round(random.uniform(-5, 25), 2)
    
    benchmark_comparison = {
        'portfolio': returns['1Y'],
        'sp500': round(random.uniform(15, 22), 2),
        'nasdaq': round(random.uniform(18, 28), 2),
        'russell2000': round(random.uniform(12, 20), 2),
        'outperformance': round(returns['1Y'] - random.uniform(15, 22), 2)
    }
    
    attribution = {
        'Asset Allocation': round(random.uniform(-1, 3), 1),
        'Security Selection': round(random.uniform(-2, 4), 1),
        'Currency Effect': round(random.uniform(-0.5, 0.5), 1),
        'Interaction': round(random.uniform(-0.5, 0.5), 1),
        'Total Active Return': round(random.uniform(-2, 5), 1)
    }
    
    return {
        'returns': returns,
        'benchmarkComparison': benchmark_comparison,
        'attribution': attribution,
        'riskAdjustedReturns': {
            'Sharpe Ratio': round(random.uniform(0.8, 2.0), 2),
            'Sortino Ratio': round(random.uniform(1.0, 2.5), 2),
            'Treynor Ratio': round(random.uniform(5, 15), 1),
            'Jensen Alpha': round(random.uniform(-2, 6), 2)
        },
        'consistency': {
            'Hit Rate': f'{random.randint(55, 75)}%',
            'Up Capture': f'{random.randint(85, 105)}%',
            'Down Capture': f'{random.randint(75, 95)}%',
            'Best Month': f'{round(random.uniform(8, 15), 1)}%',
            'Worst Month': f'{round(random.uniform(-12, -5), 1)}%'
        }
    }

def generate_esg_data():
    """Generate comprehensive ESG analysis data"""
    import random
    
    overall_score = random.randint(65, 95)
    environmental = random.randint(60, 95)
    social = random.randint(65, 90)
    governance = random.randint(70, 95)
    
    breakdown = {
        'Carbon Footprint': random.randint(70, 95),
        'Water Usage': random.randint(65, 90),
        'Waste Management': random.randint(70, 90),
        'Renewable Energy': random.randint(60, 95),
        'Employee Relations': random.randint(70, 90),
        'Community Impact': random.randint(65, 85),
        'Product Safety': random.randint(75, 95),
        'Board Diversity': random.randint(60, 90),
        'Executive Compensation': random.randint(65, 85),
        'Anti-Corruption': random.randint(80, 95)
    }
    
    trends = {}
    current_year = datetime.now().year
    for i in range(5):
        year = current_year - i
        trends[str(year)] = max(50, overall_score - random.randint(0, i*3))
    
    return {
        'overallScore': overall_score,
        'environmental': environmental,
        'social': social,
        'governance': governance,
        'breakdown': breakdown,
        'trends': trends,
        'industryComparison': {
            'Portfolio': overall_score,
            'Industry Average': random.randint(60, 80),
            'Best in Class': random.randint(85, 95),
            'Percentile Rank': random.randint(70, 95)
        },
        'controversies': {
            'Environmental': random.randint(0, 3),
            'Social': random.randint(0, 2),
            'Governance': random.randint(0, 1),
            'Total': random.randint(0, 5)
        },
        'certifications': [
            'UN Global Compact',
            'CDP Climate Change',
            'SASB Standards',
            'GRI Standards'
        ]
    }

@app.route('/api/reports/download/<report_type>')
def download_report(report_type):
    """Download report in specified format"""
    try:
        # Mock download functionality
        return jsonify({
            'downloadUrl': f'/downloads/{report_type}_report_{datetime.now().strftime("%Y%m%d")}.pdf',
            'filename': f'{report_type}_report_{datetime.now().strftime("%Y%m%d")}.pdf',
            'size': '2.3 MB',
            'status': 'ready'
        })
    except Exception as e:
        logger.error(f"Error preparing download: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/schedule', methods=['POST'])
def schedule_report():
    """Schedule automatic report generation"""
    try:
        data = request.get_json()
        report_type = data.get('type')
        frequency = data.get('frequency', 'weekly')
        email = data.get('email')
        
        # Mock scheduling functionality
        schedule_id = f"schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return jsonify({
            'scheduleId': schedule_id,
            'reportType': report_type,
            'frequency': frequency,
            'email': email,
            'nextRun': (datetime.now() + timedelta(days=7)).isoformat(),
            'status': 'scheduled'
        })
    except Exception as e:
        logger.error(f"Error scheduling report: {str(e)}")
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

@app.route('/api/ai-analysis', methods=['POST'])
def get_ai_analysis():
    """Get AI-powered analysis of stock data and technical indicators"""
    try:
        if not AI_ANALYSIS_AVAILABLE:
            return jsonify({
                'error': 'AI analysis service is not available',
                'fallback': True
            }), 503
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract data from request
        stock_data_dict = data.get('stock_data', {})
        technical_indicators_dict = data.get('technical_indicators', {})
        time_period = data.get('time_period', '3M')
        
        # Create data objects
        stock_data = StockData(
            symbol=stock_data_dict.get('symbol', ''),
            current_price=stock_data_dict.get('current_price', 0),
            price_change=stock_data_dict.get('price_change', 0),
            price_change_percent=stock_data_dict.get('price_change_percent', 0),
            volume=stock_data_dict.get('volume', 0),
            market_cap=stock_data_dict.get('market_cap'),
            day_range=stock_data_dict.get('day_range', {'low': 0, 'high': 0}),
            week_52_range=stock_data_dict.get('week_52_range', {'low': 0, 'high': 0}),
            market=stock_data_dict.get('market', 'US'),
            currency=stock_data_dict.get('currency', 'USD')
        )
        
        technical_indicators = TechnicalIndicators(
            rsi=technical_indicators_dict.get('rsi', 50),
            macd=technical_indicators_dict.get('macd', {'macd': 0, 'signal': 0, 'histogram': 0}),
            bollinger_bands=technical_indicators_dict.get('bollinger_bands', {'upper': 0, 'lower': 0, 'middle': 0}),
            moving_averages=technical_indicators_dict.get('moving_averages', {'sma20': 0, 'sma50': 0}),
            volume_analysis=technical_indicators_dict.get('volume_analysis', {}),
            support_resistance=technical_indicators_dict.get('support_resistance', {'support': 0, 'resistance': 0})
        )
        
        # Run AI analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            analysis_result = loop.run_until_complete(
                ai_analysis_agent.analyze_stock_comprehensive(
                    stock_data, 
                    technical_indicators, 
                    time_period
                )
            )
            
            return jsonify(analysis_result)
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error in AI analysis: {str(e)}")
        
        # Return fallback analysis
        try:
            data = request.get_json() or {}
            stock_data_dict = data.get('stock_data', {})
            technical_indicators_dict = data.get('technical_indicators', {})
            
            # Simple fallback analysis
            sentiment = 'neutral'
            rsi = technical_indicators_dict.get('rsi', 50)
            price_change_percent = stock_data_dict.get('price_change_percent', 0)
            
            if rsi > 70:
                sentiment = 'bearish'
            elif rsi < 30:
                sentiment = 'bullish'
            elif price_change_percent > 2:
                sentiment = 'bullish'
            elif price_change_percent < -2:
                sentiment = 'bearish'
            
            # Get currency symbol
            currency = stock_data_dict.get('currency', 'USD')
            currency_symbol = '₹' if currency == 'INR' else '$'
            market_name = 'Indian' if stock_data_dict.get('market') == 'IN' else 'US'
            
            fallback_analysis = {
                'overall_sentiment': sentiment,
                'price_analysis': f"Stock is trading at {currency_symbol}{stock_data_dict.get('current_price', 0):.2f} in the {market_name} market with a {abs(price_change_percent):.2f}% {'gain' if price_change_percent > 0 else 'loss'}.",
                'technical_summary': f"RSI at {rsi:.1f} indicates {'overbought' if rsi > 70 else 'oversold' if rsi < 30 else 'neutral'} conditions.",
                'volume_insights': f"Current volume suggests {'heightened' if technical_indicators_dict.get('volume_analysis', {}).get('volume_trend') == 'increasing' else 'normal'} market activity in the {market_name} market.",
                'support_resistance': f"Key levels identified from recent price action.",
                'risk_assessment': f"Monitor technical indicators for trend confirmation in the {market_name} market context.",
                'short_term_outlook': f"Watch for {sentiment} signals in the near term.",
                'key_levels': f"Important support and resistance levels to monitor.",
                'trading_suggestion': f"Educational analysis only - consult financial advisor for investment decisions."
            }
            
            return jsonify(fallback_analysis)
            
        except Exception as fallback_error:
            logger.error(f"Error in fallback analysis: {str(fallback_error)}")
            return jsonify({'error': 'Analysis service temporarily unavailable'}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'cache_size': len(data_cache),
        'ai_analysis_available': AI_ANALYSIS_AVAILABLE
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
    print("Dashboard will be available at: http://localhost:8080")
    print("API endpoints available at: http://localhost:8080/api/")
    
    # Run the Flask application
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=True,
        threaded=True
    ) 