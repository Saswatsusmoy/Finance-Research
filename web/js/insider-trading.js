/* ==========================================
   INSIDER TRADING MODULE
   Enhanced insider trading analysis functionality
   ========================================== */

class InsiderTradingAnalyzer {
    constructor() {
        this.currentData = [];
        this.filteredData = [];
        this.currentPage = 1;
        this.pageSize = 25;
        this.currentSymbol = '';
        this.searchTerm = '';
        this.isLoading = false;
        this.init();
    }

    init() {
        console.log('Enhanced Insider Trading module initialized');
        this.setupEventListeners();
        this.initializeDefaultView();
    }

    initializeDefaultView() {
        console.log('Initializing insider trading default view...');
        
        // Hide main content initially
        const mainContent = document.querySelector('.insider-main-content');
        const overview = document.querySelector('.insider-overview');
        if (mainContent) {
            mainContent.style.display = 'none';
            console.log('Hidden main content');
        }
        if (overview) {
            overview.style.display = 'none';
            console.log('Hidden overview');
        }
        
        // Show empty state initially
        this.showEmptyState();
        
        // Set default symbol for demo
        setTimeout(() => {
            const symbolInput = document.getElementById('insider-symbol');
            if (symbolInput && !symbolInput.value) {
                symbolInput.value = 'AAPL';
                symbolInput.placeholder = 'Enter symbol (e.g., AAPL, MSFT, GOOGL)';
                console.log('Set default symbol to AAPL');
            }
        }, 100);
    }

    setupEventListeners() {
        // Search and analysis
        const searchInput = document.getElementById('insider-symbol');
        const analyzeBtn = document.getElementById('run-insider-analysis');
        const exportBtn = document.getElementById('export-insider-data');
        
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSymbolInput(e));
            searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') this.runAnalysis();
            });
        }

        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.runAnalysis());
        }

        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportData());
        }

        // Controls
        const lookbackSelect = document.getElementById('lookback-days');
        const transactionTypeSelect = document.getElementById('transaction-type');
        const sortSelect = document.getElementById('sort-transactions');
        const pageSizeSelect = document.getElementById('page-size');
        const transactionSearch = document.getElementById('transaction-search');

        if (lookbackSelect) {
            lookbackSelect.addEventListener('change', () => this.runAnalysis());
        }
        if (transactionTypeSelect) {
            transactionTypeSelect.addEventListener('change', () => this.applyFilters());
        }
        if (sortSelect) {
            sortSelect.addEventListener('change', (e) => this.changeSorting(e.target.value));
        }
        if (pageSizeSelect) {
            pageSizeSelect.addEventListener('change', (e) => this.changePageSize(e.target.value));
        }
        if (transactionSearch) {
            transactionSearch.addEventListener('input', (e) => this.searchTransactions(e.target.value));
        }

        // Pagination
        const prevBtn = document.getElementById('prev-page');
        const nextBtn = document.getElementById('next-page');
        if (prevBtn) prevBtn.addEventListener('click', () => this.previousPage());
        if (nextBtn) nextBtn.addEventListener('click', () => this.nextPage());

        // Chart controls
        document.querySelectorAll('.chart-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.changeChartView(e.target.dataset.view));
        });
    }

    handleSymbolInput(e) {
        const value = e.target.value.toUpperCase();
        if (value.length >= 1) {
            this.showSymbolSuggestions(value);
        } else {
            this.hideSymbolSuggestions();
        }
    }

    showSymbolSuggestions(query) {
        const suggestions = this.getSymbolSuggestions(query);
        const container = document.getElementById('insider-suggestions');
        
        if (container && suggestions.length > 0) {
            container.innerHTML = suggestions.map(symbol => 
                `<div class="suggestion-item" onclick="InsiderTrading.selectSymbol('${symbol}')">${symbol}</div>`
            ).join('');
            container.style.display = 'block';
        } else {
            this.hideSymbolSuggestions();
        }
    }

    hideSymbolSuggestions() {
        const container = document.getElementById('insider-suggestions');
        if (container) container.style.display = 'none';
    }

    selectSymbol(symbol) {
        const input = document.getElementById('insider-symbol');
        if (input) {
            input.value = symbol;
            this.hideSymbolSuggestions();
        }
    }

    getSymbolSuggestions(query) {
        const symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
            'AMD', 'INTC', 'CRM', 'ORCL', 'ADBE', 'SPY', 'QQQ', 'JPM'
        ];
        return symbols.filter(s => s.startsWith(query.toUpperCase())).slice(0, 8);
    }

    async runAnalysis() {
        console.log('=== Starting runAnalysis ===');
        
        const symbolInput = document.getElementById('insider-symbol');
        const lookbackDays = document.getElementById('lookback-days')?.value || 90;
        
        console.log('Symbol input:', symbolInput?.value);
        console.log('Lookback days:', lookbackDays);
        
        if (!symbolInput || !symbolInput.value.trim()) {
            console.warn('No symbol provided');
            this.showError('Please enter a stock symbol');
            return;
        }

        const symbol = symbolInput.value.trim().toUpperCase();
        this.currentSymbol = symbol;
        console.log('Processing symbol:', symbol);
        
        this.showLoading();
        this.hideSymbolSuggestions();

        try {
            console.log('Fetching insider data...');
            const data = await this.fetchInsiderData(symbol, lookbackDays);
            console.log('Data received:', data?.length, 'transactions');
            
            if (data && data.length > 0) {
                console.log('Processing data...');
                this.currentData = data;
                
                console.log('Processing data fields...');
                this.processData();
                
                console.log('Updating overview cards...');
                this.updateOverviewCards();
                
                console.log('Rendering charts...');
                this.renderCharts();
                
                console.log('Generating insights...');
                this.generateInsights();
                
                console.log('Applying filters...');
                this.applyFilters();
                
                console.log('Showing main content...');
                this.showMainContent();
                
                console.log('=== Analysis completed successfully ===');
            } else {
                console.warn('No data returned');
                this.showEmptyState('No insider trading data found for this symbol');
            }
        } catch (error) {
            console.error('=== Insider analysis failed ===');
            console.error('Error details:', error);
            console.error('Error stack:', error.stack);
            this.showError(`Analysis failed: ${error.message}`);
        }
    }

    async fetchInsiderData(symbol, lookbackDays) {
        console.log('fetchInsiderData called with:', symbol, lookbackDays);
        
        try {
            if (window.API && window.API.getInsiderTrading) {
                console.log('Trying real API...');
                const response = await window.API.getInsiderTrading(symbol, lookbackDays);
                if (response && response.transactions) {
                    console.log('Real API returned data:', response.transactions.length);
                    return response.transactions;
                }
            } else {
                console.log('No real API available, using mock data');
            }
        } catch (error) {
            console.warn('Real API failed, using mock data:', error);
        }
        
        console.log('Generating mock data...');
        const mockData = this.generateEnhancedMockData(symbol, lookbackDays);
        console.log('Mock data generated:', mockData.length, 'transactions');
        return mockData;
    }

    generateEnhancedMockData(symbol, lookbackDays) {
        console.log('Generating mock data for:', symbol, 'lookback days:', lookbackDays);
        
        try {
            const transactions = [];
            const numTransactions = Math.floor(Math.random() * 50) + 10;
            console.log('Will generate', numTransactions, 'transactions');
        
        const insiders = [
            { name: 'John Smith', role: 'CEO' },
            { name: 'Sarah Johnson', role: 'CFO' },
            { name: 'Michael Brown', role: 'COO' },
            { name: 'Emily Davis', role: 'CTO' },
            { name: 'Robert Wilson', role: 'Director' },
            { name: 'Lisa Anderson', role: 'VP Sales' }
        ];

        const basePrice = 100 + Math.random() * 300;

        for (let i = 0; i < numTransactions; i++) {
            const daysAgo = Math.floor(Math.random() * lookbackDays);
            const date = new Date();
            date.setDate(date.getDate() - daysAgo);

            const insider = insiders[Math.floor(Math.random() * insiders.length)];
            const isSignificant = Math.random() > 0.7;
            const isPurchase = Math.random() > 0.6;
            
            const shares = isPurchase 
                ? Math.floor(Math.random() * (isSignificant ? 50000 : 10000)) + 1000
                : Math.floor(Math.random() * (isSignificant ? 100000 : 20000)) + 2000;
            
            const priceVariation = (Math.random() - 0.5) * 20;
            const price = Math.max(basePrice + priceVariation, 10);
            const value = shares * price;

            const transaction = {
                id: `tx_${i}_${Date.now()}`,
                date: date.toISOString().split('T')[0],
                timestamp: date.getTime(),
                insider: insider.name,
                role: insider.role,
                transactionType: isPurchase ? 'Purchase' : 'Sale',
                shares: shares,
                price: price,
                value: value,
                isSignificant: isSignificant
            };
            
            // Debug first few transactions
            if (i < 3) {
                console.log(`Generated transaction ${i}:`, transaction);
            }
            
            transactions.push(transaction);
        }

            return transactions.sort((a, b) => b.timestamp - a.timestamp);
        } catch (error) {
            console.error('Error generating mock data:', error);
            return [];
        }
    }

    processData() {
        console.log('Processing', this.currentData.length, 'transactions');
        
        this.currentData.forEach((transaction, index) => {
            console.log(`Processing transaction ${index}:`, transaction);
            
            // Validate transaction data
            if (!transaction.value && transaction.value !== 0) {
                console.warn(`Transaction ${index} missing value:`, transaction);
                transaction.value = 0;
            }
            if (!transaction.price && transaction.price !== 0) {
                console.warn(`Transaction ${index} missing price:`, transaction);
                transaction.price = 0;
            }
            if (!transaction.transactionType) {
                console.warn(`Transaction ${index} missing transactionType:`, transaction);
                transaction.transactionType = 'Sale'; // Default to Sale
            }
            if (!transaction.insider) {
                console.warn(`Transaction ${index} missing insider:`, transaction);
                transaction.insider = 'Unknown';
            }
            if (!transaction.role) {
                console.warn(`Transaction ${index} missing role:`, transaction);
                transaction.role = 'Unknown';
            }
            if (!transaction.date) {
                console.warn(`Transaction ${index} missing date:`, transaction);
                transaction.date = new Date().toISOString().split('T')[0];
            }
            if (!transaction.shares && transaction.shares !== 0) {
                console.warn(`Transaction ${index} missing shares:`, transaction);
                transaction.shares = 0;
            }
            
            // Ensure values are correct types
            transaction.value = Number(transaction.value) || 0;
            transaction.price = Number(transaction.price) || 0;
            transaction.shares = Number(transaction.shares) || 0;
            
            // Validate transactionType
            if (!['Purchase', 'Sale'].includes(transaction.transactionType)) {
                console.warn(`Transaction ${index} invalid transactionType '${transaction.transactionType}', defaulting to Sale`);
                transaction.transactionType = 'Sale';
            }
            
            // Set size class
            if (transaction.value > 1000000) {
                transaction.sizeClass = 'large';
            } else if (transaction.value > 100000) {
                transaction.sizeClass = 'medium';
            } else {
                transaction.sizeClass = 'small';
            }

            transaction.formattedValue = this.formatCurrency(transaction.value);
            transaction.formattedPrice = this.formatCurrency(transaction.price);
        });
        
        console.log('Data processing completed');
    }

    updateOverviewCards() {
        const metrics = this.calculateMetrics();
        
        console.log('Updating overview cards with metrics:', metrics);
        
        // Update each metric card with error checking
        const elements = {
            'total-transactions': metrics.totalTransactions,
            'total-purchases': metrics.totalPurchases,
            'total-sales': metrics.totalSales,
            'total-value': metrics.totalValue,
            'buy-sell-ratio': metrics.buySellRatio
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
                console.log(`Updated ${id}: ${value}`);
            } else {
                console.warn(`Element with id '${id}' not found`);
            }
        });
    }

    calculateMetrics() {
        console.log('Calculating metrics for', this.currentData.length, 'transactions');
        
        // Debug: Check transaction types
        const transactionTypes = this.currentData.map(t => t.transactionType);
        console.log('Transaction types found:', [...new Set(transactionTypes)]);
        
        const totalTransactions = this.currentData.length;
        const purchases = this.currentData.filter(t => t.transactionType === 'Purchase');
        const sales = this.currentData.filter(t => t.transactionType === 'Sale');
        
        console.log('Purchases found:', purchases.length);
        console.log('Sales found:', sales.length);
        
        const totalPurchases = purchases.length;
        const totalSales = sales.length;
        
        const totalValue = this.currentData.reduce((sum, t) => {
            const value = Number(t.value) || 0;
            return sum + value;
        }, 0);
        
        const purchaseValue = purchases.reduce((sum, t) => {
            const value = Number(t.value) || 0;
            return sum + value;
        }, 0);
        
        const saleValue = sales.reduce((sum, t) => {
            const value = Number(t.value) || 0;
            return sum + value;
        }, 0);
        
        const buySellRatio = totalPurchases > 0 && totalSales > 0 
            ? (purchaseValue / saleValue).toFixed(2)
            : totalPurchases > 0 ? '∞' : '0';

        const metrics = {
            totalTransactions,
            totalPurchases,
            totalSales,
            totalValue: this.formatCurrency(totalValue),
            buySellRatio
        };
        
        console.log('Calculated metrics:', metrics);
        return metrics;
    }

    renderCharts() {
        console.log('Rendering charts...');
        
        if (typeof Plotly === 'undefined') {
            console.error('Plotly is not available');
            return;
        }
        
        try {
            this.renderTimelineChart();
            this.renderTransactionTypeChart();
            this.renderInsiderRoleChart();
            console.log('All charts rendered successfully');
        } catch (error) {
            console.error('Error rendering charts:', error);
        }
    }

    renderTimelineChart() {
        const chartContainer = document.getElementById('insider-timeline-chart');
        if (!chartContainer) return;

        const timelineData = this.aggregateTimelineData();
        
        const trace = {
            x: timelineData.dates,
            y: timelineData.values,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Transaction Value',
            line: { color: '#00d2ff', width: 3 },
            marker: { size: 8, color: '#00d2ff' }
        };

        const layout = {
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#ffffff' },
            xaxis: { gridcolor: 'rgba(255,255,255,0.1)', color: '#b3b8c8' },
            yaxis: { gridcolor: 'rgba(255,255,255,0.1)', color: '#b3b8c8' },
            margin: { t: 20, r: 20, b: 40, l: 60 }
        };

        Plotly.newPlot(chartContainer, [trace], layout, { displayModeBar: false, responsive: true });
    }

    aggregateTimelineData() {
        const dateMap = new Map();
        
        this.currentData.forEach(transaction => {
            const date = transaction.date;
            if (!dateMap.has(date)) {
                dateMap.set(date, { total: 0, count: 0 });
            }
            const entry = dateMap.get(date);
            entry.total += transaction.value;
            entry.count += 1;
        });

        const dates = Array.from(dateMap.keys()).sort();
        const values = dates.map(date => dateMap.get(date).total);
        return { dates, values };
    }

    renderTransactionTypeChart() {
        const chartContainer = document.getElementById('transaction-type-chart');
        if (!chartContainer) return;

        const purchases = this.currentData.filter(t => t.transactionType === 'Purchase').length;
        const sales = this.currentData.filter(t => t.transactionType === 'Sale').length;

        const trace = {
            values: [purchases, sales],
            labels: ['Purchases', 'Sales'],
            type: 'pie',
            marker: { colors: ['#10b981', '#ef4444'] },
            textinfo: 'label+percent',
            textfont: { color: '#ffffff' }
        };

        const layout = {
            paper_bgcolor: 'transparent',
            font: { color: '#ffffff' },
            margin: { t: 20, r: 20, b: 20, l: 20 },
            showlegend: false
        };

        Plotly.newPlot(chartContainer, [trace], layout, { displayModeBar: false, responsive: true });
    }

    renderInsiderRoleChart() {
        const chartContainer = document.getElementById('insider-role-chart');
        if (!chartContainer) return;

        const roleMap = new Map();
        this.currentData.forEach(transaction => {
            const role = transaction.role;
            roleMap.set(role, (roleMap.get(role) || 0) + 1);
        });

        const roles = Array.from(roleMap.keys());
        const counts = Array.from(roleMap.values());

        const trace = {
            x: roles,
            y: counts,
            type: 'bar',
            marker: { color: '#00d2ff', opacity: 0.8 }
        };

        const layout = {
            paper_bgcolor: 'transparent',
            font: { color: '#ffffff' },
            xaxis: { color: '#b3b8c8' },
            yaxis: { gridcolor: 'rgba(255,255,255,0.1)', color: '#b3b8c8' },
            margin: { t: 20, r: 20, b: 60, l: 60 }
        };

        Plotly.newPlot(chartContainer, [trace], layout, { displayModeBar: false, responsive: true });
    }

    generateInsights() {
        const insights = this.analyzeData();
        const container = document.getElementById('insider-insights');
        
        if (container && insights.length > 0) {
            container.innerHTML = insights.map(insight => `
                <div class="insight-item">
                    <div class="insight-icon">
                        <i class="${insight.icon}"></i>
                    </div>
                    <div class="insight-content">
                        <div class="insight-title">${insight.title}</div>
                        <div class="insight-description">${insight.description}</div>
                    </div>
                </div>
            `).join('');
        }
    }

    analyzeData() {
        const insights = [];
        
        if (this.currentData.length > 30) {
            insights.push({
                title: 'High Activity Period',
                description: `${this.currentData.length} transactions detected. Significant insider activity.`,
                icon: 'fas fa-chart-line'
            });
        }

        const purchaseValue = this.currentData.filter(t => t.transactionType === 'Purchase')
            .reduce((sum, t) => sum + t.value, 0);
        const saleValue = this.currentData.filter(t => t.transactionType === 'Sale')
            .reduce((sum, t) => sum + t.value, 0);

        if (purchaseValue > saleValue * 1.5) {
            insights.push({
                title: 'Bullish Signal',
                description: 'Insiders purchasing more than selling. Potential confidence indicator.',
                icon: 'fas fa-arrow-up'
            });
        }

        const largeTransactions = this.currentData.filter(t => t.value > 1000000);
        if (largeTransactions.length > 0) {
            insights.push({
                title: 'Significant Transactions',
                description: `${largeTransactions.length} large transactions (>$1M) detected.`,
                icon: 'fas fa-exclamation-triangle'
            });
        }

        return insights.slice(0, 4);
    }

    applyFilters() {
        const transactionType = document.getElementById('transaction-type')?.value || 'all';
        
        this.filteredData = this.currentData.filter(transaction => {
            if (transactionType !== 'all') {
                if (transactionType === 'purchase' && transaction.transactionType !== 'Purchase') return false;
                if (transactionType === 'sale' && transaction.transactionType !== 'Sale') return false;
                if (transactionType === 'significant' && !transaction.isSignificant) return false;
            }
            
            if (this.searchTerm) {
                const searchLower = this.searchTerm.toLowerCase();
                return transaction.insider.toLowerCase().includes(searchLower) ||
                       transaction.role.toLowerCase().includes(searchLower);
            }
            
            return true;
        });

        this.currentPage = 1;
        this.updateTransactionsList();
        this.updatePagination();
    }

    searchTransactions(term) {
        this.searchTerm = term;
        this.applyFilters();
    }

    changeSorting(sortValue) {
        const [field, direction] = sortValue.split('-');
        
        this.filteredData.sort((a, b) => {
            let aVal, bVal;
            
            switch (field) {
                case 'date':
                    aVal = new Date(a.date);
                    bVal = new Date(b.date);
                    break;
                case 'value':
                    aVal = a.value;
                    bVal = b.value;
                    break;
                default:
                    aVal = a[field];
                    bVal = b[field];
            }
            
            return direction === 'asc' ? (aVal > bVal ? 1 : -1) : (aVal < bVal ? 1 : -1);
        });
        
        this.updateTransactionsList();
    }

    changePageSize(size) {
        this.pageSize = parseInt(size);
        this.currentPage = 1;
        this.updateTransactionsList();
        this.updatePagination();
    }

    updateTransactionsList() {
        const container = document.getElementById('transactions-list');
        if (!container) return;

        const startIndex = (this.currentPage - 1) * this.pageSize;
        const endIndex = startIndex + this.pageSize;
        const pageData = this.filteredData.slice(startIndex, endIndex);

        container.innerHTML = pageData.map(transaction => {
            const rowClass = this.getTransactionRowClass(transaction);
            const valueClass = this.getValueClass(transaction.value);
            
            return `
                <div class="transaction-row ${rowClass}">
                    <div class="table-col col-date">${this.formatDate(transaction.date)}</div>
                    <div class="table-col col-insider" title="${transaction.insider}">${transaction.insider}</div>
                    <div class="table-col col-role">${transaction.role}</div>
                    <div class="table-col col-type ${transaction.transactionType.toLowerCase()}">${transaction.transactionType}</div>
                    <div class="table-col col-shares">${this.formatNumber(transaction.shares)}</div>
                    <div class="table-col col-price">${transaction.formattedPrice}</div>
                    <div class="table-col col-value ${valueClass}">${transaction.formattedValue}</div>
                </div>
            `;
        }).join('');
    }

    getTransactionRowClass(transaction) {
        if (transaction.isSignificant) return 'significant';
        if (transaction.transactionType === 'Purchase' && transaction.value > 500000) return 'large-purchase';
        if (transaction.transactionType === 'Sale' && transaction.value > 1000000) return 'large-sale';
        return '';
    }

    getValueClass(value) {
        if (value > 1000000) return 'value-large';
        if (value > 100000) return 'value-medium';
        return 'value-small';
    }

    updatePagination() {
        const totalPages = Math.ceil(this.filteredData.length / this.pageSize);
        const pageInfo = document.getElementById('page-info');
        const prevBtn = document.getElementById('prev-page');
        const nextBtn = document.getElementById('next-page');

        if (pageInfo) pageInfo.textContent = `Page ${this.currentPage} of ${totalPages}`;
        if (prevBtn) prevBtn.disabled = this.currentPage <= 1;
        if (nextBtn) nextBtn.disabled = this.currentPage >= totalPages;
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.updateTransactionsList();
            this.updatePagination();
        }
    }

    nextPage() {
        const totalPages = Math.ceil(this.filteredData.length / this.pageSize);
        if (this.currentPage < totalPages) {
            this.currentPage++;
            this.updateTransactionsList();
            this.updatePagination();
        }
    }

    changeChartView(view) {
        document.querySelectorAll('.chart-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-view="${view}"]`)?.classList.add('active');
        this.renderTimelineChart(view);
    }

    exportData() {
        if (this.currentData.length === 0) {
            this.showError('No data to export');
            return;
        }

        const csvContent = this.convertToCSV(this.currentData);
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `${this.currentSymbol}_insider_trading_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }

    convertToCSV(data) {
        const headers = ['Date', 'Insider', 'Role', 'Transaction Type', 'Shares', 'Price', 'Value'];
        const rows = data.map(t => [
            t.date, t.insider, t.role, t.transactionType, 
            t.shares, t.price.toFixed(2), t.value.toFixed(2)
        ]);

        return [headers, ...rows].map(row => 
            row.map(cell => `"${cell}"`).join(',')
        ).join('\n');
    }

    // State management
    showLoading() {
        this.isLoading = true;
        
        // Hide main content
        const mainContent = document.querySelector('.insider-main-content');
        const overview = document.querySelector('.insider-overview');
        if (mainContent) mainContent.style.display = 'none';
        if (overview) overview.style.display = 'none';
        
        // Show loading state
        const loadingState = document.getElementById('insider-loading');
        if (loadingState) {
            loadingState.classList.remove('hidden');
            loadingState.style.display = 'flex';
        }
        
        this.hideStates(['insider-loading']);
        console.log('Showing loading state');
    }

    showEmptyState(message = 'Enter a stock symbol above to analyze insider trading activity.') {
        // Hide main content
        const mainContent = document.querySelector('.insider-main-content');
        const overview = document.querySelector('.insider-overview');
        if (mainContent) mainContent.style.display = 'none';
        if (overview) overview.style.display = 'none';
        
        // Show empty state
        const emptyState = document.getElementById('insider-empty');
        if (emptyState) {
            emptyState.classList.remove('hidden');
            emptyState.style.display = 'flex';
        }
        
        const emptyElement = document.querySelector('#insider-empty p');
        if (emptyElement) emptyElement.textContent = message;
        
        // Hide other states
        this.hideStates(['insider-empty']);
        
        console.log('Showing empty state:', message);
    }

    showError(message) {
        // Hide main content
        const mainContent = document.querySelector('.insider-main-content');
        const overview = document.querySelector('.insider-overview');
        if (mainContent) mainContent.style.display = 'none';
        if (overview) overview.style.display = 'none';
        
        // Show error state
        const errorState = document.getElementById('insider-error');
        if (errorState) {
            errorState.classList.remove('hidden');
            errorState.style.display = 'flex';
        }
        
        const errorElement = document.getElementById('error-message');
        if (errorElement) errorElement.textContent = message;
        
        this.hideStates(['insider-error']);
        console.log('Showing error state:', message);
    }

    showMainContent() {
        // Hide all state screens
        this.hideStates();
        
        // Show main content areas
        const mainContent = document.querySelector('.insider-main-content');
        const overview = document.querySelector('.insider-overview');
        
        if (mainContent) mainContent.style.display = 'grid';
        if (overview) overview.style.display = 'grid';
        
        console.log('Showing main insider trading content');
    }

    hideStates(exclude = []) {
        const states = ['insider-loading', 'insider-empty', 'insider-error'];
        states.forEach(state => {
            if (!exclude.includes(state)) {
                const element = document.getElementById(state);
                if (element) {
                    element.classList.add('hidden');
                    element.style.display = 'none';
                }
            }
        });
    }

    // Utility functions
    formatCurrency(value) {
        if (value === undefined || value === null || isNaN(value)) {
            console.warn('formatCurrency called with invalid value:', value);
            return '$0';
        }
        
        const numValue = Number(value);
        if (numValue >= 1000000) return `$${(numValue / 1000000).toFixed(1)}M`;
        if (numValue >= 1000) return `$${(numValue / 1000).toFixed(0)}K`;
        return `$${numValue.toFixed(0)}`;
    }

    formatNumber(num) {
        return num.toLocaleString();
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { 
            month: 'short', day: 'numeric', year: '2-digit'
        });
    }

    retryAnalysis() {
        this.runAnalysis();
    }

    loadDemoData() {
        // Set AAPL as demo symbol and run analysis
        const symbolInput = document.getElementById('insider-symbol');
        if (symbolInput) {
            symbolInput.value = 'AAPL';
        }
        
        console.log('Loading demo data for AAPL...');
        this.runAnalysis();
    }

    debugInfo() {
        console.log('=== INSIDER TRADING DEBUG INFO ===');
        console.log('Module loaded:', !!window.InsiderTrading);
        console.log('Current data length:', this.currentData.length);
        console.log('Filtered data length:', this.filteredData.length);
        console.log('Current symbol:', this.currentSymbol);
        console.log('Is loading:', this.isLoading);
        
        // Check elements
        const elements = ['insider-empty', 'insider-loading', 'insider-error', 'insider-symbol'];
        elements.forEach(id => {
            const el = document.getElementById(id);
            console.log(`Element ${id}:`, el ? 'found' : 'NOT FOUND');
            if (el) {
                console.log(`  - Display: ${getComputedStyle(el).display}`);
                console.log(`  - Visibility: ${getComputedStyle(el).visibility}`);
                console.log(`  - Hidden class: ${el.classList.contains('hidden')}`);
            }
        });
        
        // Check main content areas
        const mainContent = document.querySelector('.insider-main-content');
        const overview = document.querySelector('.insider-overview');
        console.log('Main content:', mainContent ? 'found' : 'NOT FOUND');
        console.log('Overview:', overview ? 'found' : 'NOT FOUND');
        
        if (mainContent) console.log('Main content display:', getComputedStyle(mainContent).display);
        if (overview) console.log('Overview display:', getComputedStyle(overview).display);
        
        console.log('=== END DEBUG INFO ===');
        
        // Show alert with basic info
        alert(`Debug Info:\nModule: ${!!window.InsiderTrading ? 'Loaded' : 'Not Loaded'}\nData: ${this.currentData.length} items\nSymbol: ${this.currentSymbol || 'None'}\nCheck console for full details.`);
    }

    // Add a simple test method
    testMockDataGeneration() {
        console.log('=== Testing Mock Data Generation ===');
        try {
            const testData = this.generateEnhancedMockData('TEST', 30);
            console.log('Test data generated successfully:', testData.length, 'transactions');
            console.log('Sample transaction:', testData[0]);
            return testData;
        } catch (error) {
            console.error('Mock data generation failed:', error);
            return null;
        }
    }

    // Add a quick analysis test
    async testQuickAnalysis() {
        console.log('=== Testing Quick Analysis ===');
        try {
            this.currentSymbol = 'TEST';
            this.currentData = this.generateEnhancedMockData('TEST', 30);
            console.log('Generated data for test:', this.currentData.length);
            
            this.processData();
            console.log('Data processed');
            
            const metrics = this.calculateMetrics();
            console.log('Metrics calculated:', metrics);
            
            this.updateOverviewCards();
            console.log('Overview cards updated');
            
            this.showMainContent();
            console.log('Main content shown');
            
            return true;
        } catch (error) {
            console.error('Quick analysis test failed:', error);
            return false;
        }
    }
}

// Initialize and expose globally
const InsiderTrading = new InsiderTradingAnalyzer();
window.InsiderTrading = InsiderTrading;

document.addEventListener('DOMContentLoaded', () => {
    console.log('Insider Trading module ready');
});
