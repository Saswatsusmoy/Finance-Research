/* ==========================================
   FINANCESCOPE - MAIN APPLICATION
   Core functionality and initialization
   ========================================== */

class FinanceScopeApp {
    constructor() {
        this.currentPage = 'dashboard';
        this.watchlist = JSON.parse(localStorage.getItem('watchlist')) || ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN'];
        this.settings = JSON.parse(localStorage.getItem('settings')) || this.getDefaultSettings();
        this.marketData = new Map();
        this.refreshInterval = null;
        this.apiConnected = false;
        this.newsData = [];
        this.currentNews = [];
        this.allNews = [];
        this.chartType = 'line';
        this.chartPeriod = '1M';
        
        // Create and expose ChartManager globally
        this.chartManager = new ChartManager();
        window.ChartManager = this.chartManager;
        
        this.init();
    }
    
    async init() {
        this.setupEventListeners();
        this.hideLoadingScreen();
        
        // Test API connection
        await this.testAPIConnection();
        
        this.loadInitialData();
        this.startAutoRefresh();
    }
    
    async testAPIConnection() {
        try {
            if (window.API) {
                console.log('Testing API connection...');
                
                // Try to fetch a simple health check or a test symbol
                const response = await fetch('http://localhost:5000/api/health');
                if (response.ok) {
                    console.log('✓ Backend API is connected');
                    this.apiConnected = true;
                    
                    // Test a simple market data call
                    try {
                        const testData = await window.API.getMarketData('SPY');
                        console.log('✓ Market data API is working:', testData);
                    } catch (error) {
                        console.warn('Market data API test failed:', error);
                    }
                } else {
                    console.warn('Backend API is not responding');
                    this.apiConnected = false;
                }
            } else {
                console.warn('API client not available');
                this.apiConnected = false;
            }
        } catch (error) {
            console.warn('API connection test failed:', error);
            this.apiConnected = false;
        }
    }
    
    getDefaultSettings() {
        return {
            theme: 'dark',
            defaultPeriod: '1M',
            autoRefresh: true,
            refreshInterval: 30000, // 30 seconds
            apiKeys: {
                alphaVantage: '',
                finnhub: '',
                sec: ''
            }
        };
    }
    
    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const page = e.currentTarget.dataset.page;
                this.navigateToPage(page);
            });
        });
        
        // Global refresh button
        const refreshBtn = document.getElementById('refresh-data');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshAllData());
        }
        
        // Modal handling
        this.setupModalListeners();
        
        // Watchlist management
        this.setupWatchlistListeners();
        
        // Chart controls
        this.setupChartControls();
        
        // Search functionality
        this.setupSearchListeners();
        
        // Settings
        this.setupSettingsListeners();
        
        // Keyboard shortcuts
        this.setupKeyboardShortcuts();
    }
    
    setupModalListeners() {
        const modalOverlay = document.getElementById('modal-overlay');
        const modalClose = document.querySelector('.modal-close');
        
        if (modalOverlay) {
            modalOverlay.addEventListener('click', (e) => {
                if (e.target === modalOverlay) {
                    this.closeModal();
                }
            });
        }
        
        if (modalClose) {
            modalClose.addEventListener('click', () => this.closeModal());
        }
        
        // ESC key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });
    }
    
    setupWatchlistListeners() {
        // Add symbol button
        const addSymbolBtn = document.getElementById('add-symbol');
        if (addSymbolBtn) {
            addSymbolBtn.addEventListener('click', () => this.showAddSymbolModal());
        }

        // Sort watchlist button
        const sortButton = document.getElementById('sort-watchlist');
        if (sortButton) {
            sortButton.addEventListener('click', () => this.sortWatchlist());
        }

        // Refresh watchlist button
        const refreshButton = document.getElementById('refresh-watchlist');
        if (refreshButton) {
            refreshButton.addEventListener('click', () => this.refreshWatchlist());
        }

        // Settings button
        const settingsButton = document.getElementById('watchlist-settings');
        if (settingsButton) {
            settingsButton.addEventListener('click', () => {
                this.showNotification('info', 'Settings', 'Watchlist settings coming soon!');
            });
        }

        // Expand watchlist button
        const expandButton = document.getElementById('expand-watchlist');
        if (expandButton) {
            expandButton.addEventListener('click', () => this.expandWatchlistView());
        }

        // Watchlist search
        const searchInput = document.getElementById('watchlist-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchWatchlist(e.target.value);
            });
        }

        // Modal event listeners
        const addSymbolConfirm = document.getElementById('add-symbol-confirm');
        const addSymbolCancel = document.getElementById('add-symbol-cancel');
        
        if (addSymbolConfirm) {
            addSymbolConfirm.addEventListener('click', () => this.addSymbolToWatchlist());
        }
        
        if (addSymbolCancel) {
            addSymbolCancel.addEventListener('click', () => this.closeModal());
        }
        
        // Enter key in symbol input
        const newSymbolInput = document.getElementById('new-symbol');
        if (newSymbolInput) {
            newSymbolInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    this.addSymbolToWatchlist();
                }
            });
        }
    }
    
    setupChartControls() {
        // Time period buttons
        document.querySelectorAll('.time-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const period = e.target.dataset.period;
                this.updateChartPeriod(period);
            });
        });
        
        // Chart type selector
        const chartTypeSelector = document.getElementById('chart-type');
        if (chartTypeSelector) {
            chartTypeSelector.addEventListener('change', (e) => {
                this.updateChartType(e.target.value);
            });
        }
    }
    
    setupSearchListeners() {
        // Analysis page is now handled by the Analysis module
        // Remove duplicate event listeners to avoid conflicts
        
        // Insider trading search
        const insiderSymbol = document.getElementById('insider-symbol');
        const runInsiderAnalysis = document.getElementById('run-insider-analysis');
        
        if (insiderSymbol && runInsiderAnalysis) {
            runInsiderAnalysis.addEventListener('click', () => {
                const symbol = insiderSymbol.value.trim().toUpperCase();
                const lookbackDays = document.getElementById('lookback-days').value;
                if (symbol) {
                    this.runInsiderAnalysis(symbol, lookbackDays);
                }
            });
        }
    }
    
    setupSettingsListeners() {
        const saveSettingsBtn = document.getElementById('save-settings');
        const resetSettingsBtn = document.getElementById('reset-settings');
        
        if (saveSettingsBtn) {
            saveSettingsBtn.addEventListener('click', () => this.saveSettings());
        }
        
        if (resetSettingsBtn) {
            resetSettingsBtn.addEventListener('click', () => this.resetSettings());
        }
        
        // Theme selector
        const themeSelector = document.getElementById('theme-selector');
        if (themeSelector) {
            themeSelector.addEventListener('change', (e) => {
                this.changeTheme(e.target.value);
            });
        }
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + number keys for navigation
            if ((e.ctrlKey || e.metaKey) && e.key >= '1' && e.key <= '5') {
                e.preventDefault();
                const pages = ['dashboard', 'analysis', 'insider-trading', 'reports', 'settings'];
                const pageIndex = parseInt(e.key) - 1;
                if (pages[pageIndex]) {
                    this.navigateToPage(pages[pageIndex]);
                }
            }
            
            // Ctrl/Cmd + R for refresh
            if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
                e.preventDefault();
                this.refreshAllData();
            }
        });
    }
    
    hideLoadingScreen() {
        setTimeout(() => {
            const loadingScreen = document.getElementById('loading-screen');
            if (loadingScreen) {
                loadingScreen.classList.add('hidden');
                setTimeout(() => {
                    loadingScreen.style.display = 'none';
                }, 500);
            }
        }, 2000);
    }

    showLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `
                <div class="loading-spinner">
                    <div class="spinner"></div>
                    <p>Loading...</p>
                </div>
            `;
        }
    }
    
    navigateToPage(pageName) {
        // Update navigation state
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        document.querySelector(`[data-page="${pageName}"]`).classList.add('active');
        
        // Update page visibility
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });
        
        const targetPage = document.getElementById(`${pageName}-page`);
        if (targetPage) {
            targetPage.classList.add('active');
            this.currentPage = pageName;
            
            // Load page-specific data
            this.loadPageData(pageName);
        }
    }
    
    async loadPageData(pageName) {
        switch (pageName) {
            case 'dashboard':
                await this.loadDashboardData();
                break;
            case 'analysis':
                // Analysis page loads data on symbol search
                break;
            case 'insider-trading':
                // Ensure insider trading module is properly initialized
                if (window.InsiderTrading) {
                    console.log('Insider trading page loaded, module ready');
                } else {
                    console.warn('Insider trading module not found');
                }
                break;
            case 'reports':
                this.loadReportsData();
                break;
            case 'settings':
                this.loadSettingsData();
                break;
        }
    }
    
    async loadInitialData() {
        console.log('=== Starting initial data load ===');
        
        // Check if API is available
        if (window.API) {
            console.log('✓ Financial API is available');
            console.log('API methods:', Object.getOwnPropertyNames(window.API));
            this.showNotification('info', 'Loading Market Data', 'Fetching real-time market information...');
        } else {
            console.warn('⚠️ Financial API is not available, will use fallback data');
            this.showNotification('warning', 'Using Demo Data', 'Real-time data unavailable, using demo data');
        }
        
        try {
            await Promise.all([
                this.loadMarketOverview(),
                this.loadWatchlistData(),
                this.loadNewsData()
            ]);
            
            const dataType = window.API ? 'Real-time data' : 'Demo data';
            this.showNotification('success', 'Data Loaded', `${dataType} loaded successfully`);
            console.log('=== Initial data load complete ===');
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showNotification('error', 'Loading Error', 'Failed to load some market data');
        }
    }
    
    async loadDashboardData() {
        console.log('Loading dashboard data...');
        
        // Show loading indicators
        this.showLoadingIndicators();
        
        try {
            await Promise.all([
                this.loadMarketOverview(),
                this.loadMainChart(),
                this.loadWatchlistData()
            ]);
            
            console.log('Dashboard data loaded successfully');
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showNotification('error', 'Data Load Failed', 'Some dashboard data could not be loaded');
        } finally {
            this.hideLoadingIndicators();
        }
    }
    
    showLoadingIndicators() {
        // Add loading states to market cards
        const symbols = ['spy', 'qqq', 'vix', 'dia'];
        symbols.forEach(symbol => {
            const valueElement = document.getElementById(`${symbol}-value`);
            const changeElement = document.getElementById(`${symbol}-change`);
            
            if (valueElement) valueElement.textContent = 'Loading...';
            if (changeElement) {
                changeElement.textContent = '...';
                changeElement.className = 'metric-change';
            }
        });
        
        // Add loading to watchlist
        const watchlistContent = document.querySelector('.watchlist-content');
        if (watchlistContent) {
            watchlistContent.innerHTML = '<div class="loading-indicator">Loading watchlist data...</div>';
        }
    }
    
    hideLoadingIndicators() {
        // Remove any remaining loading indicators
        const loadingElements = document.querySelectorAll('.loading-indicator');
        loadingElements.forEach(el => el.remove());
    }
    
    async loadMarketOverview() {
        const symbols = ['SPY', 'QQQ', 'VIX', 'DIA'];
        
        try {
            console.log('Loading market overview for:', symbols);
            
            // Fetch data for all symbols
            const promises = symbols.map(symbol => this.fetchMarketData(symbol));
            const results = await Promise.all(promises);
            
            console.log('Market data fetched:', results);
            
            // Update cards for all symbols
            const updatePromises = results.map((data, index) => 
                this.updateMarketCard(symbols[index], data)
            );
            await Promise.all(updatePromises);
            
            console.log('Market overview updated successfully');
        } catch (error) {
            console.error('Error loading market overview:', error);
        }
    }
    
    async loadMainChart() {
        try {
            const data = await this.fetchChartData('SPY', '1M');
            this.renderMainChart(data);
        } catch (error) {
            console.error('Error loading main chart:', error);
        }
    }
    
    async loadWatchlistData() {
        const promises = this.watchlist.map(symbol => this.fetchMarketData(symbol));
        
        try {
            const results = await Promise.all(promises);
            this.updateWatchlist(results);
        } catch (error) {
            console.error('Error loading watchlist data:', error);
        }
    }
    
    async loadNewsData() {
        try {
            // Show loading state
            this.showNewsLoading();
            
            const category = document.getElementById('news-category')?.value || 'all';
            const news = await this.fetchNewsData(category);
            
            // Store news for searching/filtering
            this.currentNews = news;
            this.allNews = news;
            
            this.updateNewsSection(news);
            this.setupNewsEventListeners();
        } catch (error) {
            console.error('Error loading news data:', error);
            this.showNewsError();
        }
    }

    showNewsLoading() {
        const newsContent = document.getElementById('news-feed');
        if (newsContent) {
            newsContent.innerHTML = `
                <div class="news-loading">
                    <div class="news-loading-animation">
                        <div class="news-pulse"></div>
                        <div class="news-pulse"></div>
                        <div class="news-pulse"></div>
                    </div>
                    <p>Loading latest news...</p>
                </div>
            `;
        }
    }

    showNewsError() {
        const newsContent = document.getElementById('news-feed');
        if (newsContent) {
            newsContent.innerHTML = `
                <div class="news-empty">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Failed to load news</p>
                    <button class="btn btn-sm btn-primary" onclick="app.refreshNews()">
                        <i class="fas fa-refresh"></i>
                        Try Again
                    </button>
                </div>
            `;
        }
    }

    setupNewsEventListeners() {
        // Category filter
        const categorySelect = document.getElementById('news-category');
        if (categorySelect) {
            categorySelect.addEventListener('change', () => {
                this.filterNews();
            });
        }

        // Search functionality
        const searchInput = document.getElementById('news-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchNews(e.target.value);
            });
        }

        // Refresh button
        const refreshBtn = document.getElementById('refresh-news');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshNews();
            });
        }

        // Expand button
        const expandBtn = document.getElementById('expand-news');
        if (expandBtn) {
            expandBtn.addEventListener('click', () => {
                this.expandNewsSection();
            });
        }

        // Load more button
        const loadMoreBtn = document.getElementById('load-more-news');
        if (loadMoreBtn) {
            loadMoreBtn.addEventListener('click', () => {
                this.loadMoreNews();
            });
        }
    }

    async filterNews() {
        const category = document.getElementById('news-category')?.value || 'all';
        this.showNewsLoading();
        
        try {
            const news = await this.fetchNewsData(category);
            this.currentNews = news;
            this.updateNewsSection(news);
            
            // Apply search if there's a search term
            const searchTerm = document.getElementById('news-search')?.value;
            if (searchTerm) {
                this.searchNews(searchTerm);
            }
        } catch (error) {
            console.error('Error filtering news:', error);
            this.showNewsError();
        }
    }

    searchNews(searchTerm) {
        if (!searchTerm.trim()) {
            this.updateNewsSection(this.currentNews);
            return;
        }

        const filteredNews = this.currentNews.filter(article => 
            article.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
            article.summary.toLowerCase().includes(searchTerm.toLowerCase()) ||
            article.source.toLowerCase().includes(searchTerm.toLowerCase())
        );

        this.updateNewsSection(filteredNews);
    }

    async refreshNews() {
        const refreshBtn = document.getElementById('refresh-news');
        if (refreshBtn) {
            refreshBtn.classList.add('loading');
        }

        try {
            await this.loadNewsData();
            this.showNotification('success', 'News Updated', 'Latest news articles loaded');
        } catch (error) {
            this.showNotification('error', 'Refresh Failed', 'Could not load latest news');
        } finally {
            if (refreshBtn) {
                refreshBtn.classList.remove('loading');
            }
        }
    }

    expandNewsSection() {
        // Create modal or expanded view for news
        const modal = document.createElement('div');
        modal.className = 'news-modal-overlay';
        modal.innerHTML = `
            <div class="news-modal">
                <div class="news-modal-header">
                    <h2>Market News</h2>
                    <button class="news-modal-close">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="news-modal-content" id="expanded-news-feed">
                    <!-- News will be populated here -->
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        
        // Populate with current news
        const expandedFeed = document.getElementById('expanded-news-feed');
        if (expandedFeed && this.currentNews) {
            this.populateExpandedNews(expandedFeed, this.currentNews);
        }

        // Close functionality
        const closeBtn = modal.querySelector('.news-modal-close');
        closeBtn.addEventListener('click', () => {
            document.body.removeChild(modal);
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });
    }

    populateExpandedNews(container, news) {
        container.innerHTML = '';
        news.forEach(article => {
            const item = document.createElement('div');
            item.className = 'expanded-news-item';
            item.innerHTML = `
                <h3>${article.title}</h3>
                <p>${article.summary}</p>
                <div class="expanded-news-meta">
                    <span class="source">${article.source}</span>
                    <span class="time">${this.getTimeAgo(article.timestamp)}</span>
                </div>
            `;
            container.appendChild(item);
        });
    }

    async loadMoreNews() {
        const loadMoreBtn = document.getElementById('load-more-news');
        if (loadMoreBtn) {
            loadMoreBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        }

        try {
            const category = document.getElementById('news-category')?.value || 'all';
            const moreNews = await this.fetchNewsData(category, 10);
            
            // Add to current news (avoid duplicates)
            const existingIds = new Set(this.currentNews.map(n => n.id));
            const newNews = moreNews.filter(n => !existingIds.has(n.id));
            
            this.currentNews.push(...newNews);
            this.updateNewsSection(this.currentNews);
            
            this.showNotification('success', 'More News Loaded', `${newNews.length} new articles added`);
        } catch (error) {
            this.showNotification('error', 'Load Failed', 'Could not load more news articles');
        } finally {
            if (loadMoreBtn) {
                loadMoreBtn.innerHTML = '<i class="fas fa-chevron-down"></i> Load More Articles';
            }
        }
    }

    showArticleModal(article) {
        // Create modal for article details
        const modal = document.createElement('div');
        modal.className = 'article-modal-overlay';
        modal.innerHTML = `
            <div class="article-modal">
                <div class="article-modal-header">
                    <div class="article-source-info">
                        <i class="fas fa-${article.icon || 'newspaper'}"></i>
                        <span class="article-source">${article.source}</span>
                        ${article.breaking ? '<span class="breaking-badge">BREAKING</span>' : ''}
                    </div>
                    <button class="article-modal-close">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="article-modal-content">
                    <h1 class="article-title">${article.title}</h1>
                    <div class="article-meta">
                        <span class="article-time">${this.getTimeAgo(article.timestamp)}</span>
                        <span class="article-category">${article.category.toUpperCase()}</span>
                    </div>
                    <div class="article-tags">
                        ${article.tags ? article.tags.map(tag => 
                            `<span class="article-tag ${tag.class}">${tag.text}</span>`
                        ).join('') : ''}
                    </div>
                    <div class="article-content">
                        <p class="article-summary">${article.summary}</p>
                        <div class="article-notice">
                            <i class="fas fa-info-circle"></i>
                            <p>This is a demo article. In a real application, this would show the full article content or redirect to the original source.</p>
                        </div>
                        <div class="article-actions">
                            <button class="btn btn-primary" onclick="window.open('${article.url.startsWith('#') ? `https://www.google.com/search?q=${encodeURIComponent(article.title)}` : article.url}', '_blank')">
                                <i class="fas fa-external-link-alt"></i>
                                Search Online
                            </button>
                            <button class="btn btn-secondary" onclick="this.closest('.article-modal-overlay').remove()">
                                <i class="fas fa-times"></i>
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        
        // Close functionality
        const closeBtn = modal.querySelector('.article-modal-close');
        closeBtn.addEventListener('click', () => {
            document.body.removeChild(modal);
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });

        // Add escape key handler
        const escapeHandler = (e) => {
            if (e.key === 'Escape') {
                document.body.removeChild(modal);
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);
    }
    
    async fetchMarketData(symbol) {
        try {
            // Try to use the real API first
            if (window.API && window.API.getMarketData) {
                console.log(`Fetching real market data for ${symbol}...`);
                const data = await window.API.getMarketData(symbol);
                
                // Format the data for the dashboard
                const formattedData = {
                    symbol: data.symbol || symbol,
                    price: data.price || data.current_price || 0,
                    change: data.change || 0,
                    changePercent: data.changePercent || data.change_percent || 0,
                    volume: data.volume || 0,
                    marketCap: data.marketCap || data.market_cap || 0,
                    timestamp: data.timestamp || Date.now()
                };
                
                this.marketData.set(symbol, formattedData);
                console.log(`Real data loaded for ${symbol}:`, formattedData);
                return formattedData;
            }
        } catch (error) {
            console.warn(`API failed for ${symbol}, using fallback data:`, error);
        }
        
        // Fallback to mock data if API is unavailable
        console.log(`Using fallback data for ${symbol}`);
        const mockData = {
            symbol: symbol,
            price: (Math.random() * 500 + 50).toFixed(2),
            change: (Math.random() * 10 - 5).toFixed(2),
            changePercent: (Math.random() * 5 - 2.5).toFixed(2),
            volume: Math.floor(Math.random() * 10000000),
            marketCap: Math.floor(Math.random() * 1000000000000),
            timestamp: Date.now()
        };
        this.marketData.set(symbol, mockData);
        return mockData;
    }
    
    async fetchChartData(symbol, period) {
        try {
            // Try to use the real API first
            if (window.API && window.API.getHistoricalData) {
                console.log(`Fetching real historical data for ${symbol}, period: ${period}...`);
                const response = await window.API.getHistoricalData(symbol, period);
                
                if (response && response.data && response.data.length > 0) {
                    console.log(`Real historical data loaded for ${symbol}:`, response.data.length, 'data points');
                    return response.data.map(item => ({
                        date: item.date,
                        open: parseFloat(item.open) || 0,
                        high: parseFloat(item.high) || 0,
                        low: parseFloat(item.low) || 0,
                        close: parseFloat(item.close) || 0,
                        volume: parseInt(item.volume) || 0
                    }));
                }
            }
        } catch (error) {
            console.warn(`Historical data API failed for ${symbol}, using fallback data:`, error);
        }
        
        // Fallback to mock data if API is unavailable
        console.log(`Using fallback historical data for ${symbol}`);
        const days = this.getPeriodDays(period);
        const data = [];
        let basePrice = 100 + Math.random() * 400;
        
        for (let i = 0; i < days; i++) {
            const date = new Date();
            date.setDate(date.getDate() - (days - i));
            
            basePrice += (Math.random() - 0.5) * 10;
            data.push({
                date: date.toISOString().split('T')[0],
                open: basePrice + Math.random() * 5 - 2.5,
                high: basePrice + Math.random() * 10,
                low: basePrice - Math.random() * 10,
                close: basePrice,
                volume: Math.floor(Math.random() * 10000000)
            });
        }
        
        return data;
    }
    
    async fetchNewsData(category = 'all', limit = 20) {
        try {
            // Try to fetch from API first
            if (window.API && window.API.getMarketNews) {
                return await window.API.getMarketNews(category, limit);
            }
            
            // Fallback to enhanced mock data
            return this.generateEnhancedMockNews(category, limit);
        } catch (error) {
            console.error('Error fetching news data:', error);
            return this.generateEnhancedMockNews(category, limit);
        }
    }

    generateEnhancedMockNews(category = 'all', limit = 20) {
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

        let allNews = [];
        
        if (category === 'all') {
            Object.values(newsTemplates).forEach(categoryNews => {
                allNews.push(...categoryNews);
            });
        } else if (newsTemplates[category]) {
            allNews = newsTemplates[category];
        }

        // Add random timestamps and URLs
        const enhancedNews = allNews.map((article, index) => ({
            ...article,
            id: `news_${Date.now()}_${index}`,
            url: `#news/${article.category}/${index}`,
            timestamp: Date.now() - (Math.random() * 86400000), // Random time within last 24 hours
            tags: this.generateNewsTags(article.category, article.breaking)
        }));

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
    
    getPeriodDays(period) {
        const periodMap = {
            '1D': 1,
            '1W': 7,
            '1M': 30,
            '3M': 90,
            '1Y': 365
        };
        return periodMap[period] || 30;
    }
    
    async updateMarketCard(symbol, data) {
        const valueElement = document.getElementById(`${symbol.toLowerCase()}-value`);
        const changeElement = document.getElementById(`${symbol.toLowerCase()}-change`);
        
        if (valueElement) {
            // Format price properly
            const price = parseFloat(data.price);
            valueElement.textContent = `$${price.toFixed(2)}`;
        }
        
        if (changeElement) {
            const changePercent = parseFloat(data.changePercent);
            const isPositive = changePercent >= 0;
            changeElement.textContent = `${isPositive ? '+' : ''}${changePercent.toFixed(2)}%`;
            changeElement.className = `metric-change ${isPositive ? 'positive' : 'negative'}`;
        }
        
        // Update mini chart
        await this.updateMiniChart(`${symbol.toLowerCase()}-chart`, data);
    }
    
    async updateMiniChart(elementId, data) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        try {
            // Try to get real mini chart data (7 days)
            let chartData = null;
            if (window.API && window.API.getHistoricalData) {
                const response = await window.API.getHistoricalData(data.symbol, '1W');
                if (response && response.data && response.data.length > 0) {
                    chartData = response.data.slice(-7); // Last 7 days
                }
            }
            
            let trace;
            if (chartData && chartData.length > 0) {
                // Use real historical data
                trace = {
                    x: chartData.map((_, i) => i),
                    y: chartData.map(d => parseFloat(d.close)),
                    type: 'scatter',
                    mode: 'lines',
                    line: { 
                        color: parseFloat(data.changePercent) >= 0 ? '#10b981' : '#ef4444',
                        width: 2
                    },
                    showlegend: false
                };
            } else {
                // Fallback to trend-based chart
                const basePrice = parseFloat(data.price) || 100;
                const change = parseFloat(data.changePercent) || 0;
                const trend = change / 100; // Convert percentage to decimal
                
                trace = {
                    x: Array.from({length: 7}, (_, i) => i),
                    y: Array.from({length: 7}, (_, i) => {
                        // Create a trend line based on the actual change
                        const variation = (Math.random() - 0.5) * 2; // Random variation
                        const trendEffect = trend * i * 0.5; // Gradual trend
                        return basePrice * (1 + trendEffect + variation * 0.01);
                    }),
                    type: 'scatter',
                    mode: 'lines',
                    line: { 
                        color: parseFloat(data.changePercent) >= 0 ? '#10b981' : '#ef4444',
                        width: 2
                    },
                    showlegend: false
                };
            }
            
            const layout = {
                margin: { t: 0, r: 0, b: 0, l: 0 },
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                xaxis: { visible: false },
                yaxis: { visible: false }
            };
            
            Plotly.newPlot(elementId, [trace], layout, { displayModeBar: false, responsive: true });
        } catch (error) {
            console.warn(`Mini chart update failed for ${elementId}:`, error);
            // Fallback to simple chart
            const trace = {
                x: Array.from({length: 7}, (_, i) => i),
                y: Array.from({length: 7}, () => Math.random() * 10 + 90),
                type: 'scatter',
                mode: 'lines',
                line: { 
                    color: parseFloat(data.changePercent) >= 0 ? '#10b981' : '#ef4444',
                    width: 2
                },
                showlegend: false
            };
            
            const layout = {
                margin: { t: 0, r: 0, b: 0, l: 0 },
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                xaxis: { visible: false },
                yaxis: { visible: false }
            };
            
            Plotly.newPlot(elementId, [trace], layout, { displayModeBar: false, responsive: true });
        }
    }
    
    renderMainChart(data) {
        const mainChart = document.getElementById('main-chart');
        if (!mainChart || !data || data.length === 0) return;
        
        const trace = {
            x: data.map(d => d.date),
            y: data.map(d => d.close),
            type: 'scatter',
            mode: 'lines',
            name: 'Price',
            line: { color: '#00d2ff', width: 3 }
        };
        
        const layout = {
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#ffffff' },
            xaxis: { 
                gridcolor: 'rgba(255,255,255,0.1)',
                showgrid: true,
                color: '#b3b8c8'
            },
            yaxis: { 
                gridcolor: 'rgba(255,255,255,0.1)',
                showgrid: true,
                color: '#b3b8c8'
            },
            margin: { t: 20, r: 20, b: 40, l: 60 }
        };
        
        const config = {
            displayModeBar: false,
            responsive: true
        };
        
        Plotly.newPlot('main-chart', [trace], layout, config);
    }
    
    updateWatchlist(dataArray) {
        const watchlistContainer = document.getElementById('watchlist-container');
        if (!watchlistContainer) return;
        
        // Clear container
        watchlistContainer.innerHTML = '';
        
        if (!dataArray || dataArray.length === 0) {
            watchlistContainer.innerHTML = `
                <div class="watchlist-empty">
                    <i class="fas fa-star"></i>
                    <p>Your watchlist is empty</p>
                    <button class="btn btn-sm btn-primary" onclick="app.showAddSymbolModal()">
                        <i class="fas fa-plus"></i>
                        Add Symbols
                    </button>
                </div>
            `;
            this.updateWatchlistStats([], 0, 0);
            return;
        }
        
        let gainers = 0;
        let losers = 0;
        let totalValue = 0;
        let totalChange = 0;
        
        dataArray.forEach((data, index) => {
            const symbol = this.watchlist[index];
            if (!symbol) return;
            
            const item = document.createElement('div');
            
            const price = parseFloat(data.price) || 0;
            const changePercent = parseFloat(data.changePercent) || 0;
            const changeValue = parseFloat(data.change) || 0;
            const volume = parseFloat(data.volume) || 0;
            const isPositive = changePercent >= 0;
            
            if (changePercent > 0) gainers++;
            else if (changePercent < 0) losers++;
            
            // Calculate portfolio metrics (assuming 100 shares for demo)
            const shares = 100;
            const positionValue = price * shares;
            const positionChange = changeValue * shares;
            totalValue += positionValue;
            totalChange += positionChange;
            
            // Determine trend class
            let trendClass = '';
            if (Math.abs(changePercent) > 2) {
                trendClass = changePercent > 0 ? 'trending-up' : 'trending-down';
            }
            
            item.className = `watchlist-item ${trendClass}`;
            
            item.innerHTML = `
                <div class="symbol-info">
                    <span class="symbol">${symbol}</span>
                    <span class="company">${data.name || this.getCompanyName(symbol)}</span>
                </div>
                <div class="price-info">
                    <span class="price">$${price.toFixed(2)}</span>
                    <span class="change ${isPositive ? 'positive' : 'negative'}">
                        ${isPositive ? '+' : ''}${changePercent.toFixed(2)}%
                    </span>
                    <div class="watchlist-volume-bar">
                        <div class="watchlist-volume-fill" style="width: ${Math.min(volume / 1000000 * 100, 100)}%"></div>
                    </div>
                </div>
                <div class="watchlist-actions-cell">
                    <button class="watchlist-btn" onclick="app.viewSymbolChart('${symbol}')" title="View Chart">
                        <i class="fas fa-chart-line"></i>
                    </button>
                    <button class="watchlist-btn remove" onclick="app.removeFromWatchlist('${symbol}')" title="Remove">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            
            // Add click handler for symbol navigation
            item.addEventListener('click', (e) => {
                // Don't navigate if clicking on action buttons
                if (e.target.closest('.watchlist-actions-cell')) return;
                
                this.navigateToPage('analysis');
                setTimeout(() => {
                    const analysisInput = document.getElementById('analysis-symbol');
                    if (analysisInput) {
                        analysisInput.value = symbol;
                        this.analyzeSymbol(symbol);
                    }
                }, 100);
            });
            
            watchlistContainer.appendChild(item);
        });
        
        // Update statistics
        this.updateWatchlistStats(dataArray, gainers, losers);
        this.updatePortfolioSummary(totalValue, totalChange, totalChange / (totalValue - totalChange) * 100);
    }
    
    updateWatchlistStats(dataArray, gainers, losers) {
        const countElement = document.getElementById('watchlist-count');
        const gainersElement = document.getElementById('gainers-count');
        const losersElement = document.getElementById('losers-count');
        
        if (countElement) countElement.textContent = dataArray.length;
        if (gainersElement) gainersElement.textContent = gainers;
        if (losersElement) losersElement.textContent = losers;
    }
    
    updatePortfolioSummary(totalValue, totalChange, changePercent) {
        const portfolioValueElement = document.getElementById('portfolio-value');
        const dailyChangeElement = document.getElementById('daily-change');
        
        if (portfolioValueElement) {
            portfolioValueElement.textContent = this.formatCurrency(totalValue);
        }
        
        if (dailyChangeElement) {
            const isPositive = totalChange >= 0;
            dailyChangeElement.textContent = `${isPositive ? '+' : ''}${this.formatCurrency(totalChange)} (${isPositive ? '+' : ''}${changePercent.toFixed(2)}%)`;
            dailyChangeElement.className = `value ${isPositive ? 'positive' : 'negative'}`;
        }
    }
    
    formatCurrency(value) {
        if (Math.abs(value) >= 1000000) {
            return `$${(value / 1000000).toFixed(1)}M`;
        } else if (Math.abs(value) >= 1000) {
            return `$${(value / 1000).toFixed(1)}K`;
        } else {
            return `$${value.toFixed(2)}`;
        }
    }
    
    viewSymbolChart(symbol) {
        this.navigateToPage('analysis');
        setTimeout(() => {
            const analysisInput = document.getElementById('analysis-symbol');
            if (analysisInput) {
                analysisInput.value = symbol;
                this.analyzeSymbol(symbol);
            }
        }, 100);
    }
    
    removeFromWatchlist(symbol) {
        const index = this.watchlist.indexOf(symbol);
        if (index > -1) {
            this.watchlist.splice(index, 1);
            localStorage.setItem('watchlist', JSON.stringify(this.watchlist));
            this.loadWatchlistData();
            this.showNotification('info', 'Symbol Removed', `${symbol} removed from watchlist`);
        }
    }
    
    sortWatchlist(sortBy = 'symbol') {
        // Will be implemented with sort functionality
        this.showNotification('info', 'Sort Feature', 'Sorting functionality coming soon!');
    }
    
    refreshWatchlist() {
        const refreshBtn = document.getElementById('refresh-watchlist');
        if (refreshBtn) {
            refreshBtn.classList.add('loading');
            setTimeout(() => refreshBtn.classList.remove('loading'), 1000);
        }
        this.loadWatchlistData();
    }
    
    searchWatchlist(query) {
        const items = document.querySelectorAll('.watchlist-item');
        items.forEach(item => {
            const symbol = item.querySelector('.symbol')?.textContent || '';
            const company = item.querySelector('.company')?.textContent || '';
            const matches = symbol.toLowerCase().includes(query.toLowerCase()) || 
                           company.toLowerCase().includes(query.toLowerCase());
            item.style.display = matches ? 'flex' : 'none';
        });
    }
    
    expandWatchlistView() {
        this.showNotification('info', 'Expanded View', 'Full watchlist view coming soon!');
    }
    
    updateNewsSection(news) {
        const newsContent = document.getElementById('news-feed');
        if (!newsContent) return;
        
        // Clear loading state
        newsContent.innerHTML = '';
        
        if (!news || news.length === 0) {
            newsContent.innerHTML = `
                <div class="news-empty">
                    <i class="fas fa-newspaper"></i>
                    <p>No news articles found</p>
                    <button class="btn btn-sm btn-primary" onclick="app.refreshNews()">
                        <i class="fas fa-refresh"></i>
                        Refresh News
                    </button>
                </div>
            `;
            return;
        }
        
        news.forEach(article => {
            const item = document.createElement('div');
            const hasExternalLink = article.url && article.url !== '#' && !article.url.startsWith('#news/');
            item.className = `news-item ${article.breaking ? 'breaking' : ''} ${hasExternalLink ? 'has-external-link' : ''}`;
            
            const timeAgo = this.getTimeAgo(article.timestamp);
            const iconClass = article.icon || 'newspaper';
            
            // Create tags HTML
            let tagsHtml = '';
            if (article.tags && article.tags.length > 0) {
                tagsHtml = `
                    <div class="news-tags">
                        ${article.tags.map(tag => 
                            `<span class="news-tag ${tag.class}">${tag.text}</span>`
                        ).join('')}
                    </div>
                `;
            }
            
            item.innerHTML = `
                <div class="news-thumbnail">
                    <i class="fas fa-${iconClass}"></i>
                </div>
                <div class="news-item-content">
                    <h4 class="news-title">${article.title}</h4>
                    <p class="news-summary">${article.summary}</p>
                    ${tagsHtml}
                    <div class="news-meta">
                        <span class="news-source">${article.source}</span>
                        <span class="news-time">${timeAgo}</span>
                    </div>
                </div>
            `;
            
            // Add click handler for article redirection
            item.addEventListener('click', (e) => {
                // Prevent event bubbling
                e.stopPropagation();
                
                if (article.url && article.url !== '#' && !article.url.startsWith('#news/')) {
                    // Show notification about redirection
                    this.showNotification('info', 'Opening Article', `Redirecting to ${article.source}...`);
                    
                    // Add a small delay to show the notification, then open the link
                    setTimeout(() => {
                        window.open(article.url, '_blank', 'noopener,noreferrer');
                    }, 500);
                } else {
                    // For demo articles or placeholder URLs
                    this.showArticleModal(article);
                }
            });

            // Add hover effect for better UX
            item.addEventListener('mouseenter', () => {
                if (article.url && article.url !== '#' && !article.url.startsWith('#news/')) {
                    item.style.cursor = 'pointer';
                    item.title = `Click to read full article on ${article.source}`;
                } else {
                    item.style.cursor = 'pointer';
                    item.title = 'Click to view article details';
                }
            });
            
            newsContent.appendChild(item);
        });
    }
    
    getCompanyName(symbol) {
        const companies = {
            'AAPL': 'Apple Inc.',
            'MSFT': 'Microsoft Corp.',
            'GOOGL': 'Alphabet Inc.',
            'TSLA': 'Tesla Inc.',
            'AMZN': 'Amazon.com Inc.',
            'SPY': 'SPDR S&P 500 ETF',
            'QQQ': 'Invesco QQQ Trust',
            'VIX': 'CBOE Volatility Index',
            'DIA': 'SPDR Dow Jones Industrial Average ETF'
        };
        return companies[symbol] || symbol;
    }
    
    getTimeAgo(timestamp) {
        const now = Date.now();
        const diff = now - timestamp;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        
        if (days > 0) return `${days}d ago`;
        if (hours > 0) return `${hours}h ago`;
        if (minutes > 0) return `${minutes}m ago`;
        return 'Just now';
    }
    
    showAddSymbolModal() {
        const modal = document.getElementById('modal-overlay');
        if (modal) {
            modal.classList.add('active');
            const input = document.getElementById('new-symbol');
            if (input) {
                input.focus();
                input.value = '';
            }
        }
    }
    
    closeModal() {
        const modal = document.getElementById('modal-overlay');
        if (modal) {
            modal.classList.remove('active');
        }
    }
    
    addSymbolToWatchlist() {
        const input = document.getElementById('new-symbol');
        if (input) {
            const symbol = input.value.trim().toUpperCase();
            if (symbol && !this.watchlist.includes(symbol)) {
                this.watchlist.push(symbol);
                localStorage.setItem('watchlist', JSON.stringify(this.watchlist));
                this.loadWatchlistData();
                this.showNotification('success', 'Symbol Added', `${symbol} added to watchlist`);
                this.closeModal();
            } else if (this.watchlist.includes(symbol)) {
                this.showNotification('warning', 'Symbol Exists', `${symbol} is already in your watchlist`);
            }
        }
    }
    
    updateChartPeriod(period) {
        // Update button states
        document.querySelectorAll('.time-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-period="${period}"]`).classList.add('active');
        
        // Reload chart data
        this.loadMainChart();
    }
    
    updateChartType(type) {
        // Implementation for different chart types
        console.log(`Chart type changed to: ${type}`);
    }
    
    // Analysis functionality moved to Analysis module
    
    async runInsiderAnalysis(symbol, lookbackDays) {
        this.showNotification('info', 'Insider Analysis', `Analyzing insider trading for ${symbol}...`);
        
        try {
            // Simulate insider trading analysis
            setTimeout(() => {
                const results = this.generateMockInsiderData(symbol, lookbackDays);
                this.displayInsiderResults(results);
                this.showNotification('success', 'Analysis Complete', `Insider analysis for ${symbol} completed`);
            }, 2000);
        } catch (error) {
            this.showNotification('error', 'Analysis Error', `Failed to analyze insider trading for ${symbol}`);
        }
    }
    
    generateMockInsiderData(symbol, lookbackDays) {
        // Generate mock insider trading data
        const transactions = [];
        const insiders = ['John Smith', 'Jane Doe', 'Robert Johnson', 'Mary Wilson'];
        const titles = ['CEO', 'CFO', 'Director', 'COO'];
        
        for (let i = 0; i < 5; i++) {
            transactions.push({
                insider: insiders[Math.floor(Math.random() * insiders.length)],
                title: titles[Math.floor(Math.random() * titles.length)],
                transactionType: Math.random() > 0.5 ? 'Purchase' : 'Sale',
                shares: Math.floor(Math.random() * 10000) + 1000,
                price: (Math.random() * 200 + 50).toFixed(2),
                date: new Date(Date.now() - Math.random() * lookbackDays * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
            });
        }
        
        return { symbol, transactions };
    }
    
    displayInsiderResults(results) {
        const resultsContainer = document.getElementById('insider-results');
        if (!resultsContainer) return;
        
        let html = `<h3>Insider Trading Activity for ${results.symbol}</h3>`;
        html += '<div class="insider-transactions">';
        
        results.transactions.forEach(transaction => {
            const typeClass = transaction.transactionType === 'Purchase' ? 'success' : 'danger';
            html += `
                <div class="transaction-item">
                    <div class="transaction-header">
                        <strong>${transaction.insider}</strong>
                        <span class="transaction-title">${transaction.title}</span>
                        <span class="badge badge-${typeClass}">${transaction.transactionType}</span>
                    </div>
                    <div class="transaction-details">
                        <span>${transaction.shares.toLocaleString()} shares at $${transaction.price}</span>
                        <span class="transaction-date">${transaction.date}</span>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        resultsContainer.innerHTML = html;
    }
    
    loadReportsData() {
        // Set default date range
        const endDate = new Date();
        const startDate = new Date();
        startDate.setMonth(startDate.getMonth() - 3);
        
        document.getElementById('start-date').value = startDate.toISOString().split('T')[0];
        document.getElementById('end-date').value = endDate.toISOString().split('T')[0];
        
        // Set up report generation
        const generateBtn = document.getElementById('generate-report');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => this.generateReport());
        }
        
        // Set up report type selection
        document.querySelectorAll('.report-type-card').forEach(card => {
            card.addEventListener('click', (e) => {
                document.querySelectorAll('.report-type-card').forEach(c => c.classList.remove('active'));
                e.currentTarget.classList.add('active');
            });
        });
    }
    
    generateReport() {
        const reportType = document.querySelector('.report-type-card.active').dataset.type;
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;
        const format = document.getElementById('report-format').value;
        
        this.showNotification('info', 'Generating Report', `Creating ${reportType} report...`);
        
        // Simulate report generation
        setTimeout(() => {
            this.displayReport(reportType, startDate, endDate, format);
            this.showNotification('success', 'Report Generated', `${reportType} report created successfully`);
        }, 3000);
    }
    
    displayReport(type, startDate, endDate, format) {
        const reportContent = document.getElementById('report-content');
        if (!reportContent) return;
        
        reportContent.innerHTML = `
            <div class="report-header">
                <h2>${type.charAt(0).toUpperCase() + type.slice(1)} Report</h2>
                <p>Period: ${startDate} to ${endDate}</p>
            </div>
            <div class="report-body">
                <p>Report content for ${type} would be displayed here...</p>
                <div class="report-placeholder">
                    <i class="fas fa-chart-bar" style="font-size: 4rem; color: var(--accent-primary); opacity: 0.3;"></i>
                    <p>Interactive ${type} report content</p>
                </div>
            </div>
        `;
    }
    
    loadSettingsData() {
        // Load current settings into form
        document.getElementById('theme-selector').value = this.settings.theme;
        document.getElementById('default-period').value = this.settings.defaultPeriod;
        
        // Load API keys (masked)
        Object.keys(this.settings.apiKeys).forEach(key => {
            const input = document.getElementById(`${key.replace(/([A-Z])/g, '-$1').toLowerCase()}-key`);
            if (input && this.settings.apiKeys[key]) {
                input.value = '••••••••••••••••';
            }
        });
    }
    
    saveSettings() {
        this.settings.theme = document.getElementById('theme-selector').value;
        this.settings.defaultPeriod = document.getElementById('default-period').value;
        
        localStorage.setItem('settings', JSON.stringify(this.settings));
        this.showNotification('success', 'Settings Saved', 'Your preferences have been saved');
    }
    
    resetSettings() {
        this.settings = this.getDefaultSettings();
        localStorage.setItem('settings', JSON.stringify(this.settings));
        this.loadSettingsData();
        this.showNotification('info', 'Settings Reset', 'Settings have been reset to defaults');
    }
    
    changeTheme(theme) {
        // Implementation for theme switching
        console.log(`Theme changed to: ${theme}`);
        this.settings.theme = theme;
    }
    
    async refreshAllData() {
        const refreshBtn = document.getElementById('refresh-data');
        if (refreshBtn) {
            const originalHTML = refreshBtn.innerHTML;
            refreshBtn.innerHTML = '<div class="spinner"></div> Refreshing...';
            refreshBtn.disabled = true;
        }
        
        try {
            await this.loadInitialData();
        } finally {
            if (refreshBtn) {
                refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh Data';
                refreshBtn.disabled = false;
            }
        }
    }
    
    startAutoRefresh() {
        if (this.settings.autoRefresh) {
            this.refreshInterval = setInterval(() => {
                this.loadMarketOverview();
                this.loadWatchlistData();
            }, this.settings.refreshInterval);
        }
    }
    
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
    
    showNotification(type, title, message, duration = 5000) {
        const container = document.getElementById('notification-container');
        if (!container) return;
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        notification.innerHTML = `
            <div class="notification-icon">
                <i class="${icons[type] || icons.info}"></i>
            </div>
            <div class="notification-content">
                <div class="notification-title">${title}</div>
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Add close functionality
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            this.removeNotification(notification);
        });
        
        container.appendChild(notification);
        
        // Trigger show animation
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Auto remove after duration
        if (duration > 0) {
            setTimeout(() => {
                this.removeNotification(notification);
            }, duration);
        }
    }
    
    removeNotification(notification) {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }

    // Support method for insider trading retry functionality
    retryInsiderAnalysis() {
        if (window.InsiderTrading) {
            window.InsiderTrading.retryAnalysis();
        }
    }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.financeApp = new FinanceScopeApp();
    // Expose app globally for insider trading callbacks
    window.app = window.financeApp;
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (window.financeApp) {
        if (document.hidden) {
            window.financeApp.stopAutoRefresh();
        } else {
            window.financeApp.startAutoRefresh();
        }
    }
}); 