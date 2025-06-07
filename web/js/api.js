/* ==========================================
   FINANCESCOPE - API INTEGRATION
   Financial data API connections
   ========================================== */

class FinancialDataAPI {
    constructor() {
        this.baseURL = 'http://localhost:5000/api';  // Flask backend URL
        this.cache = new Map();
        this.cacheTimeout = 300000; // 5 minutes
        this.requestQueue = new Map();
    }
    
    // Generic API request handler with caching and error handling
    async makeRequest(endpoint, options = {}) {
        const cacheKey = `${endpoint}${JSON.stringify(options)}`;
        
        // Check cache first
        if (this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < this.cacheTimeout) {
                return cached.data;
            }
        }
        
        // Check if request is already in progress
        if (this.requestQueue.has(cacheKey)) {
            return this.requestQueue.get(cacheKey);
        }
        
        // Make new request
        const requestPromise = this._executeRequest(endpoint, options);
        this.requestQueue.set(cacheKey, requestPromise);
        
        try {
            const data = await requestPromise;
            
            // Cache the result
            this.cache.set(cacheKey, {
                data: data,
                timestamp: Date.now()
            });
            
            return data;
        } catch (error) {
            console.error(`API request failed for ${endpoint}:`, error);
            throw error;
        } finally {
            this.requestQueue.delete(cacheKey);
        }
    }
    
    async _executeRequest(endpoint, options) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        const response = await fetch(url, config);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    // Market Data Methods
    async getMarketData(symbol, market = 'US') {
        try {
            return await this.makeRequest(`/market/${symbol}?market=${market}`);
        } catch (error) {
            // Fallback to mock data if API fails
            console.warn(`API failed for ${symbol}, using mock data`);
            return this.generateMockMarketData(symbol);
        }
    }
    
    async getBatchMarketData(symbols, market = 'US') {
        try {
            const symbolsParam = symbols.join(',');
            return await this.makeRequest(`/market/batch?symbols=${symbolsParam}&market=${market}`);
        } catch (error) {
            // Fallback to individual requests
            const promises = symbols.map(symbol => this.getMarketData(symbol, market));
            return await Promise.all(promises);
        }
    }
    
    async getHistoricalData(symbol, market = 'US', period = '1M', interval = '1d') {
        try {
            return await this.makeRequest(`/historical/${symbol}?period=${period}&interval=${interval}&market=${market}`);
        } catch (error) {
            console.warn(`Historical data API failed for ${symbol}, using mock data`);
            return this.generateMockHistoricalData(symbol, period);
        }
    }
    
    async getIntradayData(symbol, interval = '5m') {
        try {
            return await this.makeRequest(`/intraday/${symbol}?interval=${interval}`);
        } catch (error) {
            console.warn(`Intraday data API failed for ${symbol}, using mock data`);
            return this.generateMockIntradayData(symbol);
        }
    }
    
    // Technical Indicators
    async getTechnicalIndicators(symbol, indicators = ['sma', 'rsi', 'macd']) {
        try {
            const indicatorsParam = indicators.join(',');
            return await this.makeRequest(`/technical/${symbol}?indicators=${indicatorsParam}`);
        } catch (error) {
            console.warn(`Technical indicators API failed for ${symbol}, using mock data`);
            return this.generateMockTechnicalData(symbol, indicators);
        }
    }
    
    async getRSI(symbol, period = 14) {
        try {
            return await this.makeRequest(`/technical/${symbol}/rsi?period=${period}`);
        } catch (error) {
            return this.generateMockRSI(symbol);
        }
    }
    
    async getMACD(symbol) {
        try {
            return await this.makeRequest(`/technical/${symbol}/macd`);
        } catch (error) {
            return this.generateMockMACD(symbol);
        }
    }
    
    async getBollingerBands(symbol, period = 20) {
        try {
            return await this.makeRequest(`/technical/${symbol}/bollinger?period=${period}`);
        } catch (error) {
            return this.generateMockBollingerBands(symbol);
        }
    }
    
    // Insider Trading Data
    async getInsiderTrading(symbol, lookbackDays = 90) {
        try {
            return await this.makeRequest(`/insider/${symbol}?lookback=${lookbackDays}`);
        } catch (error) {
            console.warn(`Insider trading API failed for ${symbol}, using mock data`);
            return this.generateMockInsiderData(symbol, lookbackDays);
        }
    }
    
    async getInsiderSummary(symbol) {
        try {
            return await this.makeRequest(`/insider/${symbol}/summary`);
        } catch (error) {
            return this.generateMockInsiderSummary(symbol);
        }
    }
    
    // News and Sentiment
    async getMarketNews(category = 'all', limit = 20) {
        try {
            return await this.makeRequest(`/news?category=${category}&limit=${limit}`);
        } catch (error) {
            console.warn('News API failed, using mock data');
            return this.generateMockNews(category, limit);
        }
    }
    
    async getSymbolNews(symbol, limit = 5) {
        try {
            return await this.makeRequest(`/news/${symbol}?limit=${limit}`);
        } catch (error) {
            return this.generateMockSymbolNews(symbol);
        }
    }
    
    async getSentimentAnalysis(symbol) {
        try {
            return await this.makeRequest(`/sentiment/${symbol}`);
        } catch (error) {
            return this.generateMockSentiment(symbol);
        }
    }
    
    // Portfolio and Analysis
    async getPortfolioAnalysis(holdings) {
        try {
            return await this.makeRequest('/portfolio/analyze', {
                method: 'POST',
                body: JSON.stringify({ holdings })
            });
        } catch (error) {
            return this.generateMockPortfolioAnalysis(holdings);
        }
    }
    
    async getRiskMetrics(symbol) {
        try {
            return await this.makeRequest(`/risk/${symbol}`);
        } catch (error) {
            return this.generateMockRiskMetrics(symbol);
        }
    }
    
    // Report Generation
    async generateReport(type, options = {}) {
        try {
            return await this.makeRequest('/reports/generate', {
                method: 'POST',
                body: JSON.stringify({ type, options })
            });
        } catch (error) {
            return this.generateMockReport(type, options);
        }
    }
    
    // Mock Data Generators (for fallback when API is unavailable)
    generateMockMarketData(symbol) {
        const basePrice = 100 + Math.random() * 400;
        const change = (Math.random() - 0.5) * 20;
        const changePercent = (change / basePrice) * 100;
        
        return {
            symbol: symbol,
            name: this.getCompanyName(symbol),
            price: basePrice.toFixed(2),
            change: change.toFixed(2),
            changePercent: changePercent.toFixed(2),
            volume: Math.floor(Math.random() * 10000000) + 1000000,
            marketCap: Math.floor(Math.random() * 1000000000000) + 10000000000,
            peRatio: (15 + Math.random() * 20).toFixed(2),
            high52Week: (basePrice * (1.2 + Math.random() * 0.3)).toFixed(2),
            low52Week: (basePrice * (0.7 + Math.random() * 0.2)).toFixed(2),
            avgVolume: Math.floor(Math.random() * 5000000) + 2000000,
            beta: (0.5 + Math.random() * 1.5).toFixed(2),
            eps: (Math.random() * 10).toFixed(2),
            dividendYield: (Math.random() * 5).toFixed(2),
            timestamp: Date.now()
        };
    }
    
    generateMockHistoricalData(symbol, period) {
        const days = this.getPeriodDays(period);
        const data = [];
        let basePrice = 100 + Math.random() * 400;
        
        for (let i = 0; i < days; i++) {
            const date = new Date();
            date.setDate(date.getDate() - (days - i));
            
            const volatility = 0.02; // 2% daily volatility
            const randomChange = (Math.random() - 0.5) * 2 * volatility;
            basePrice *= (1 + randomChange);
            
            const open = basePrice + (Math.random() - 0.5) * basePrice * 0.01;
            const close = basePrice;
            const high = Math.max(open, close) + Math.random() * basePrice * 0.02;
            const low = Math.min(open, close) - Math.random() * basePrice * 0.02;
            
            data.push({
                date: date.toISOString().split('T')[0],
                open: parseFloat(open.toFixed(2)),
                high: parseFloat(high.toFixed(2)),
                low: parseFloat(low.toFixed(2)),
                close: parseFloat(close.toFixed(2)),
                volume: Math.floor(Math.random() * 10000000) + 1000000,
                adjClose: parseFloat(close.toFixed(2))
            });
        }
        
        return {
            symbol: symbol,
            data: data,
            period: period
        };
    }
    
    generateMockIntradayData(symbol) {
        const data = [];
        const intervals = 78; // 6.5 hours * 12 (5-minute intervals)
        let basePrice = 100 + Math.random() * 400;
        
        for (let i = 0; i < intervals; i++) {
            const time = new Date();
            time.setHours(9, 30 + (i * 5), 0, 0);
            
            basePrice += (Math.random() - 0.5) * 2;
            
            data.push({
                time: time.toISOString(),
                price: basePrice.toFixed(2),
                volume: Math.floor(Math.random() * 100000) + 10000
            });
        }
        
        return {
            symbol: symbol,
            data: data,
            interval: '5m'
        };
    }
    
    generateMockTechnicalData(symbol, indicators) {
        const result = { symbol: symbol };
        
        if (indicators.includes('sma')) {
            result.sma = {
                sma20: (100 + Math.random() * 400).toFixed(2),
                sma50: (100 + Math.random() * 400).toFixed(2),
                sma200: (100 + Math.random() * 400).toFixed(2)
            };
        }
        
        if (indicators.includes('rsi')) {
            result.rsi = {
                current: (Math.random() * 100).toFixed(2),
                signal: Math.random() > 0.5 ? 'overbought' : Math.random() > 0.5 ? 'oversold' : 'neutral'
            };
        }
        
        if (indicators.includes('macd')) {
            result.macd = {
                macd: (Math.random() * 10 - 5).toFixed(4),
                signal: (Math.random() * 10 - 5).toFixed(4),
                histogram: (Math.random() * 10 - 5).toFixed(4)
            };
        }
        
        return result;
    }
    
    generateMockRSI(symbol) {
        const data = [];
        for (let i = 0; i < 30; i++) {
            const date = new Date();
            date.setDate(date.getDate() - (30 - i));
            
            data.push({
                date: date.toISOString().split('T')[0],
                rsi: Math.random() * 100
            });
        }
        
        return {
            symbol: symbol,
            data: data,
            current: data[data.length - 1].rsi,
            signal: data[data.length - 1].rsi > 70 ? 'overbought' : 
                   data[data.length - 1].rsi < 30 ? 'oversold' : 'neutral'
        };
    }
    
    generateMockMACD(symbol) {
        const data = [];
        for (let i = 0; i < 30; i++) {
            const date = new Date();
            date.setDate(date.getDate() - (30 - i));
            
            data.push({
                date: date.toISOString().split('T')[0],
                macd: (Math.random() - 0.5) * 10,
                signal: (Math.random() - 0.5) * 10,
                histogram: (Math.random() - 0.5) * 5
            });
        }
        
        return {
            symbol: symbol,
            data: data
        };
    }
    
    generateMockBollingerBands(symbol) {
        const data = [];
        let basePrice = 100 + Math.random() * 400;
        
        for (let i = 0; i < 30; i++) {
            const date = new Date();
            date.setDate(date.getDate() - (30 - i));
            
            basePrice += (Math.random() - 0.5) * 5;
            const std = basePrice * 0.02;
            
            data.push({
                date: date.toISOString().split('T')[0],
                close: basePrice,
                upperBand: basePrice + (2 * std),
                lowerBand: basePrice - (2 * std),
                middleBand: basePrice
            });
        }
        
        return {
            symbol: symbol,
            data: data
        };
    }
    
    generateMockInsiderData(symbol, lookbackDays) {
        const transactions = [];
        const insiders = [
            { name: 'John Smith', title: 'CEO' },
            { name: 'Jane Doe', title: 'CFO' },
            { name: 'Robert Johnson', title: 'Director' },
            { name: 'Mary Wilson', title: 'COO' },
            { name: 'David Brown', title: 'Director' }
        ];
        
        const numTransactions = Math.floor(Math.random() * 10) + 3;
        
        for (let i = 0; i < numTransactions; i++) {
            const insider = insiders[Math.floor(Math.random() * insiders.length)];
            const daysAgo = Math.floor(Math.random() * lookbackDays);
            const date = new Date();
            date.setDate(date.getDate() - daysAgo);
            
            transactions.push({
                insider: insider.name,
                title: insider.title,
                transactionType: Math.random() > 0.6 ? 'Purchase' : 'Sale',
                shares: Math.floor(Math.random() * 50000) + 1000,
                price: (Math.random() * 200 + 50).toFixed(2),
                value: Math.floor(Math.random() * 1000000) + 50000,
                date: date.toISOString().split('T')[0],
                filingDate: date.toISOString().split('T')[0]
            });
        }
        
        // Sort by date (most recent first)
        transactions.sort((a, b) => new Date(b.date) - new Date(a.date));
        
        return {
            symbol: symbol,
            transactions: transactions,
            summary: {
                totalTransactions: transactions.length,
                totalPurchases: transactions.filter(t => t.transactionType === 'Purchase').length,
                totalSales: transactions.filter(t => t.transactionType === 'Sale').length,
                netActivity: this.calculateNetInsiderActivity(transactions)
            }
        };
    }
    
    generateMockInsiderSummary(symbol) {
        return {
            symbol: symbol,
            lastUpdate: new Date().toISOString(),
            summary: {
                totalInsiders: Math.floor(Math.random() * 20) + 5,
                recentActivity: Math.floor(Math.random() * 10) + 1,
                sentimentScore: (Math.random() * 2 - 1).toFixed(2), // -1 to 1
                confidenceLevel: (Math.random() * 0.5 + 0.5).toFixed(2) // 0.5 to 1
            }
        };
    }
    
    generateMockNews(category = 'all', limit = 20) {
        const newsTemplates = {
            market: [
                {
                    title: 'S&P 500 Reaches New All-Time High Amid Economic Optimism',
                    summary: 'The benchmark index surged 1.2% as investors showed renewed confidence in the economic recovery, driven by strong earnings reports and positive employment data.',
                    source: 'Reuters',
                    category: 'market',
                    breaking: false,
                    icon: 'chart-line'
                },
                {
                    title: 'Volatility Index Drops to Lowest Level This Year',
                    summary: 'The VIX fell below 15 for the first time in 2024, signaling decreased market uncertainty and improved investor sentiment.',
                    source: 'Bloomberg',
                    category: 'market',
                    breaking: false,
                    icon: 'chart-area'
                },
                {
                    title: 'Dow Jones Industrial Average Closes Above 35,000',
                    summary: 'The blue-chip index marked its fifth consecutive day of gains, supported by strong corporate earnings and optimistic economic forecasts.',
                    source: 'MarketWatch',
                    category: 'market',
                    breaking: false,
                    icon: 'chart-line'
                }
            ],
            earnings: [
                {
                    title: 'Apple Reports Record Q4 Earnings, Beats Expectations',
                    summary: 'Apple Inc. announced quarterly earnings that exceeded analyst estimates, driven by strong iPhone sales and services revenue growth.',
                    source: 'CNBC',
                    category: 'earnings',
                    breaking: true,
                    icon: 'dollar-sign'
                },
                {
                    title: 'Microsoft Cloud Revenue Soars 25% Year-over-Year',
                    summary: 'The tech giant\'s Azure cloud platform continues to drive growth, with enterprise customers increasingly adopting cloud-first strategies.',
                    source: 'TechCrunch',
                    category: 'earnings',
                    breaking: false,
                    icon: 'cloud'
                },
                {
                    title: 'Tesla Q3 Deliveries Exceed Wall Street Estimates',
                    summary: 'Electric vehicle manufacturer reports 435,000 vehicle deliveries in the third quarter, surpassing analyst expectations of 420,000 units.',
                    source: 'Financial Times',
                    category: 'earnings',
                    breaking: false,
                    icon: 'car'
                }
            ],
            analysis: [
                {
                    title: 'Analysts Upgrade Tesla Price Target Following Delivery Numbers',
                    summary: 'Wall Street firms raise price targets for Tesla stock after the company reported better-than-expected vehicle deliveries for the quarter.',
                    source: 'MarketWatch',
                    category: 'analysis',
                    breaking: false,
                    icon: 'search-dollar'
                },
                {
                    title: 'Tech Sector Outlook: AI Revolution Drives Growth',
                    summary: 'Investment analysts predict continued growth in technology stocks as artificial intelligence adoption accelerates across industries.',
                    source: 'Barron\'s',
                    category: 'analysis',
                    breaking: false,
                    icon: 'robot'
                }
            ],
            crypto: [
                {
                    title: 'Bitcoin Surges Past $45,000 on Institutional Adoption',
                    summary: 'The world\'s largest cryptocurrency gained 8% today as major corporations announce Bitcoin treasury allocations.',
                    source: 'CoinDesk',
                    category: 'crypto',
                    breaking: true,
                    icon: 'bitcoin'
                },
                {
                    title: 'Ethereum 2.0 Staking Reaches New Milestone',
                    summary: 'Over 20 million ETH tokens are now staked in the Ethereum 2.0 network, representing approximately 16% of the total supply.',
                    source: 'Decrypt',
                    category: 'crypto',
                    breaking: false,
                    icon: 'coins'
                }
            ],
            economic: [
                {
                    title: 'Federal Reserve Signals Potential Rate Cuts in 2024',
                    summary: 'Fed officials hint at possible monetary policy easing if inflation continues to moderate toward the 2% target.',
                    source: 'Wall Street Journal',
                    category: 'economic',
                    breaking: false,
                    icon: 'university'
                },
                {
                    title: 'Unemployment Rate Drops to 3.5%, Lowest in Decades',
                    summary: 'The U.S. labor market shows remarkable strength with jobless claims falling and wage growth maintaining steady pace.',
                    source: 'Reuters',
                    category: 'economic',
                    breaking: false,
                    icon: 'users'
                }
            ]
        };

        // Select news based on category
        let allNews = [];
        if (category === 'all') {
            Object.values(newsTemplates).forEach(categoryNews => {
                allNews.push(...categoryNews);
            });
        } else if (newsTemplates[category]) {
            allNews = newsTemplates[category];
        } else {
            allNews = newsTemplates.market; // Default to market news
        }

                 // Add metadata and timestamps
         const enhancedNews = allNews.map((article, index) => {
             const timestamp = Date.now() - (index * 2 * 3600000) - (index * 15 * 60000); // Hours and minutes ago
             
             // Generate realistic URLs
             const urlTitle = article.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
             const sourceUrls = {
                 'Reuters': `https://www.reuters.com/business/${urlTitle}-${timestamp}`,
                 'Bloomberg': `https://www.bloomberg.com/news/articles/2024-12-14/${urlTitle}`,
                 'CNBC': `https://www.cnbc.com/2024/12/14/${urlTitle}.html`,
                 'MarketWatch': `https://www.marketwatch.com/story/${urlTitle}-${timestamp}`,
                 'Financial Times': `https://www.ft.com/content/${urlTitle}`,
                 'TechCrunch': `https://techcrunch.com/2024/12/14/${urlTitle}/`,
                 'CoinDesk': `https://www.coindesk.com/business/2024/12/14/${urlTitle}`,
                 'Decrypt': `https://decrypt.co/${urlTitle}`,
                 'Wall Street Journal': `https://www.wsj.com/articles/${urlTitle}-${timestamp}`,
                 'Barron\'s': `https://www.barrons.com/articles/${urlTitle}-${timestamp}`
             };
             
             return {
                 ...article,
                 id: `news_${timestamp}_${index}`,
                 timestamp: timestamp,
                 url: sourceUrls[article.source] || `https://example.com/news/${urlTitle}`,
                 tags: this.generateNewsTags(article.category, article.breaking)
             };
         });

        // Sort by timestamp (newest first) and limit
        return enhancedNews
            .sort((a, b) => b.timestamp - a.timestamp)
            .slice(0, limit);
    }

    generateNewsTags(category, breaking) {
        const tags = [];
        
        if (breaking) tags.push({ text: 'BREAKING', class: 'urgent' });
        
        const categoryTags = {
            market: ['Market Update', 'Trading'],
            earnings: ['Earnings', 'Financial Results'],
            analysis: ['Analysis', 'Expert Opinion'],
            crypto: ['Cryptocurrency', 'Digital Assets'],
            economic: ['Economic Policy', 'Federal Reserve']
        };

        if (categoryTags[category]) {
            tags.push({ text: categoryTags[category][0], class: 'normal' });
        }

        return tags;
    }
    
    generateMockSymbolNews(symbol) {
        const news = [
            {
                title: `${symbol} Reports Strong Quarterly Earnings`,
                summary: `${symbol} exceeded analyst expectations with strong revenue growth...`,
                source: "Reuters",
                timestamp: Date.now() - 3600000,
                url: "#"
            },
            {
                title: `Analyst Upgrades ${symbol} Price Target`,
                summary: `Wall Street firm raises price target citing strong fundamentals...`,
                source: "Bloomberg",
                timestamp: Date.now() - 7200000,
                url: "#"
            }
        ];
        
        return news;
    }
    
    generateMockSentiment(symbol) {
        return {
            symbol: symbol,
            overallSentiment: Math.random() > 0.5 ? 'positive' : Math.random() > 0.5 ? 'negative' : 'neutral',
            sentimentScore: (Math.random() * 2 - 1).toFixed(2), // -1 to 1
            socialMentions: Math.floor(Math.random() * 1000) + 100,
            newsArticles: Math.floor(Math.random() * 50) + 10,
            analystRatings: {
                buy: Math.floor(Math.random() * 10) + 5,
                hold: Math.floor(Math.random() * 8) + 3,
                sell: Math.floor(Math.random() * 3) + 1
            }
        };
    }
    
    generateMockPortfolioAnalysis(holdings) {
        const totalValue = holdings.reduce((sum, holding) => {
            return sum + (holding.shares * holding.price);
        }, 0);
        
        return {
            totalValue: totalValue,
            dayChange: (Math.random() * totalValue * 0.05 - totalValue * 0.025).toFixed(2),
            dayChangePercent: (Math.random() * 5 - 2.5).toFixed(2),
            diversificationScore: (Math.random() * 0.3 + 0.7).toFixed(2), // 0.7 to 1.0
            riskScore: (Math.random() * 10).toFixed(1), // 0 to 10
            holdings: holdings.map(holding => ({
                ...holding,
                weight: ((holding.shares * holding.price) / totalValue * 100).toFixed(2),
                dayChange: (Math.random() * 10 - 5).toFixed(2)
            }))
        };
    }
    
    generateMockRiskMetrics(symbol) {
        return {
            symbol: symbol,
            beta: (Math.random() * 1.5 + 0.5).toFixed(2),
            volatility: (Math.random() * 0.3 + 0.1).toFixed(3),
            sharpeRatio: (Math.random() * 2).toFixed(2),
            maxDrawdown: -(Math.random() * 30 + 5).toFixed(2),
            var95: -(Math.random() * 10 + 2).toFixed(2), // Value at Risk
            correlation_SPY: (Math.random() * 0.6 + 0.3).toFixed(2)
        };
    }
    
    generateMockReport(type, options) {
        return {
            type: type,
            generatedAt: new Date().toISOString(),
            options: options,
            status: 'completed',
            downloadUrl: '#',
            data: {
                summary: `Mock ${type} report generated successfully`,
                details: `This is a placeholder for the ${type} report content.`
            }
        };
    }
    
    // Utility methods
    getPeriodDays(period) {
        const periodMap = {
            '1D': 1,
            '1W': 7,
            '1M': 30,
            '3M': 90,
            '6M': 180,
            '1Y': 365,
            '2Y': 730,
            '5Y': 1825
        };
        return periodMap[period] || 30;
    }
    
    getCompanyName(symbol) {
        const companies = {
            'AAPL': 'Apple Inc.',
            'MSFT': 'Microsoft Corporation',
            'GOOGL': 'Alphabet Inc.',
            'AMZN': 'Amazon.com Inc.',
            'TSLA': 'Tesla Inc.',
            'META': 'Meta Platforms Inc.',
            'NVDA': 'NVIDIA Corporation',
            'SPY': 'SPDR S&P 500 ETF Trust',
            'QQQ': 'Invesco QQQ Trust',
            'VIX': 'CBOE Volatility Index',
            'DIA': 'SPDR Dow Jones Industrial Average ETF',
            'IWM': 'iShares Russell 2000 ETF'
        };
        return companies[symbol] || `${symbol} Corporation`;
    }
    
    calculateNetInsiderActivity(transactions) {
        const purchases = transactions.filter(t => t.transactionType === 'Purchase');
        const sales = transactions.filter(t => t.transactionType === 'Sale');
        
        const purchaseValue = purchases.reduce((sum, t) => sum + t.value, 0);
        const saleValue = sales.reduce((sum, t) => sum + t.value, 0);
        
        return purchaseValue - saleValue;
    }
    
    // Cache management
    clearCache() {
        this.cache.clear();
        console.log('API cache cleared');
    }
    
    getCacheStats() {
        return {
            size: this.cache.size,
            entries: Array.from(this.cache.keys())
        };
    }
}

// Export for use in other modules
window.FinancialDataAPI = FinancialDataAPI;

// Create global API instance
window.API = new FinancialDataAPI(); 