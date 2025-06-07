/* ==========================================
   ENHANCED REPORTS MODULE
   Advanced report generation and management
   ========================================== */

const Reports = {
    currentReportType: 'portfolio',
    isGenerating: false,
    reportCache: new Map(),

    init() {
        console.log('Enhanced Reports module initialized');
        this.setupReportsEventListeners();
        this.initializeDateRange();
        this.setupAdvancedFilters();
    },

    setupReportsEventListeners() {
        // Report type selection
        document.querySelectorAll('.report-type-card').forEach(card => {
            card.addEventListener('click', (e) => this.selectReportType(e));
        });

        // Generate report button
        const generateBtn = document.getElementById('generate-report');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => this.generateReport());
        }

        // Advanced filters toggle
        const toggleBtn = document.getElementById('toggle-advanced-filters');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggleAdvancedFilters());
        }

        // Stock symbol input visibility
        document.querySelectorAll('.report-type-card').forEach(card => {
            card.addEventListener('click', () => this.updateStockSymbolVisibility());
        });

        console.log('Reports event listeners set up');
    },

    initializeDateRange() {
        const endDate = new Date();
        const startDate = new Date();
        startDate.setMonth(startDate.getMonth() - 3);

        const startInput = document.getElementById('start-date');
        const endInput = document.getElementById('end-date');

        if (startInput) startInput.value = startDate.toISOString().split('T')[0];
        if (endInput) endInput.value = endDate.toISOString().split('T')[0];
    },

    setupAdvancedFilters() {
        // Initialize advanced filter functionality
        const advancedFilters = document.getElementById('advanced-filters');
        if (advancedFilters) {
            advancedFilters.style.display = 'none';
        }
    },

    selectReportType(event) {
        // Remove active class from all cards
        document.querySelectorAll('.report-type-card').forEach(card => {
            card.classList.remove('active');
        });

        // Add active class to clicked card
        event.currentTarget.classList.add('active');
        this.currentReportType = event.currentTarget.dataset.type;

        // Update UI based on report type
        this.updateStockSymbolVisibility();
        
        console.log('Selected report type:', this.currentReportType);
    },

    updateStockSymbolVisibility() {
        const stockSymbolInput = document.getElementById('stock-symbol');
        if (stockSymbolInput) {
            if (this.currentReportType === 'stock') {
                stockSymbolInput.style.display = 'block';
                stockSymbolInput.parentElement.style.display = 'block';
            } else {
                stockSymbolInput.style.display = 'none';
                stockSymbolInput.parentElement.style.display = 'none';
            }
        }
    },

    toggleAdvancedFilters() {
        const filtersDiv = document.getElementById('advanced-filters');
        const toggleBtn = document.getElementById('toggle-advanced-filters');
        
        if (filtersDiv && toggleBtn) {
            const isVisible = filtersDiv.classList.contains('show');
            
            if (isVisible) {
                filtersDiv.classList.remove('show');
                toggleBtn.classList.remove('active');
            } else {
                filtersDiv.classList.add('show');
                toggleBtn.classList.add('active');
            }
        }
    },

    async generateReport() {
        if (this.isGenerating) return;

        this.isGenerating = true;
        const generateBtn = document.getElementById('generate-report');
        const reportContent = document.getElementById('report-content');

        // Update button state
        if (generateBtn) {
            generateBtn.classList.add('loading');
            generateBtn.innerHTML = '<i class="fas fa-spinner"></i> Generating...';
        }

        // Show loading state
        this.showLoadingState();

        try {
            const reportConfig = this.getReportConfiguration();
            const reportData = await this.fetchReportData(reportConfig);
            
            // Simulate processing time for better UX
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            this.displayReport(reportData);
            
        } catch (error) {
            console.error('Error generating report:', error);
            this.showErrorState(error.message);
        } finally {
            this.isGenerating = false;
            
            // Reset button state
            if (generateBtn) {
                generateBtn.classList.remove('loading');
                generateBtn.innerHTML = '<i class="fas fa-chart-bar"></i> Generate Report';
            }
        }
    },

    getReportConfiguration() {
        const startDate = document.getElementById('start-date')?.value;
        const endDate = document.getElementById('end-date')?.value;
        const format = document.getElementById('report-format')?.value;
        const stockSymbol = document.getElementById('stock-symbol')?.value;
        
        const options = {
            includeCharts: document.getElementById('include-charts')?.checked,
            includeRawData: document.getElementById('include-raw-data')?.checked,
            includeRecommendations: document.getElementById('include-recommendations')?.checked,
            includeBenchmarks: document.getElementById('include-benchmarks')?.checked
        };

        return {
            type: this.currentReportType,
            startDate,
            endDate,
            format,
            stockSymbol,
            options
        };
    },

    async fetchReportData(config) {
        // Check cache first
        const cacheKey = JSON.stringify(config);
        if (this.reportCache.has(cacheKey)) {
            return this.reportCache.get(cacheKey);
        }

        try {
            const response = await fetch('/api/reports/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Cache the result
            this.reportCache.set(cacheKey, data);
            
            return data;
        } catch (error) {
            console.error('Error fetching report data:', error);
            // Return mock data as fallback
            return this.generateMockReportData(config);
        }
    },

    generateMockReportData(config) {
        const mockData = {
            type: config.type,
            generatedAt: new Date().toISOString(),
            config: config,
            data: this.getMockDataForType(config.type, config)
        };

        return mockData;
    },

    getMockDataForType(type, config) {
        switch (type) {
            case 'portfolio':
                return this.generatePortfolioData(config);
            case 'market':
                return this.generateMarketData(config);
            case 'stock':
                return this.generateStockData(config);
            case 'risk':
                return this.generateRiskData(config);
            case 'performance':
                return this.generatePerformanceData(config);
            case 'esg':
                return this.generateESGData(config);
            default:
                return {};
        }
    },

    generatePortfolioData(config) {
        return {
            totalValue: 1250000,
            dayChange: 15750,
            dayChangePercent: 1.28,
            holdings: [
                { symbol: 'AAPL', shares: 500, value: 87500, weight: 7.0, change: 2.1 },
                { symbol: 'MSFT', shares: 300, value: 105000, weight: 8.4, change: 1.8 },
                { symbol: 'GOOGL', shares: 200, value: 54000, weight: 4.3, change: -0.5 },
                { symbol: 'AMZN', shares: 150, value: 48750, weight: 3.9, change: 3.2 },
                { symbol: 'TSLA', shares: 100, value: 25000, weight: 2.0, change: -1.2 }
            ],
            allocation: {
                'Technology': 45.2,
                'Healthcare': 18.7,
                'Financials': 15.3,
                'Consumer': 12.1,
                'Energy': 8.7
            },
            performance: {
                '1D': 1.28,
                '1W': 3.45,
                '1M': 8.92,
                '3M': 15.67,
                '1Y': 24.33
            }
        };
    },

    generateMarketData(config) {
        return {
            indices: {
                'S&P 500': { value: 4185.47, change: 1.2 },
                'NASDAQ': { value: 12965.34, change: 2.1 },
                'Dow Jones': { value: 33875.12, change: 0.8 },
                'VIX': { value: 18.45, change: -5.2 }
            },
            sectors: {
                'Technology': 2.3,
                'Healthcare': 1.8,
                'Financials': -0.5,
                'Energy': 3.1,
                'Consumer Discretionary': 1.2,
                'Utilities': -0.8,
                'Real Estate': 0.9,
                'Materials': 1.5,
                'Industrials': 0.7,
                'Communication Services': 1.9,
                'Consumer Staples': 0.3
            },
            breadth: {
                advancing: 285,
                declining: 215,
                newHighs: 45,
                newLows: 12
            }
        };
    },

    generateStockData(config) {
        const symbol = config.stockSymbol || 'AAPL';
        return {
            symbol: symbol,
            companyName: `${symbol} Inc.`,
            currentPrice: 175.43,
            change: 2.15,
            changePercent: 1.24,
            volume: 52847392,
            marketCap: 2750000000000,
            peRatio: 28.5,
            week52High: 182.94,
            week52Low: 124.17,
            technicals: {
                rsi: 65.4,
                sma20: 172.8,
                sma50: 168.2,
                sma200: 155.9,
                support: 170.0,
                resistance: 180.0
            },
            fundamentals: {
                eps: 6.15,
                dividendYield: 0.52,
                bookValue: 3.85,
                debtToEquity: 1.73
            }
        };
    },

    generateRiskData(config) {
        return {
            portfolioBeta: 1.12,
            volatility: 16.8,
            sharpeRatio: 1.45,
            maxDrawdown: -14.2,
            var95: -2.1,
            cvar95: -2.8,
            correlations: {
                'SPY': 0.85,
                'QQQ': 0.78,
                'VIX': -0.42
            },
            riskMetrics: {
                'Value at Risk (95%)': '-2.1%',
                'Expected Shortfall': '-2.8%',
                'Beta': '1.12',
                'Alpha': '4.32%',
                'Tracking Error': '3.2%'
            }
        };
    },

    generatePerformanceData(config) {
        return {
            returns: {
                '1D': 1.28,
                '1W': 3.45,
                '1M': 8.92,
                '3M': 15.67,
                '6M': 22.14,
                '1Y': 24.33,
                '3Y': 18.75,
                '5Y': 16.42
            },
            benchmarkComparison: {
                portfolio: 24.33,
                sp500: 19.85,
                nasdaq: 22.17,
                outperformance: 4.48
            },
            attribution: {
                'Asset Allocation': 2.1,
                'Security Selection': 1.8,
                'Interaction': 0.3,
                'Total': 4.2
            }
        };
    },

    generateESGData(config) {
        return {
            overallScore: 78,
            environmental: 82,
            social: 75,
            governance: 77,
            breakdown: {
                'Carbon Footprint': 85,
                'Water Usage': 78,
                'Waste Management': 80,
                'Employee Relations': 76,
                'Community Impact': 74,
                'Board Diversity': 79,
                'Executive Compensation': 75
            },
            trends: {
                '2023': 78,
                '2022': 74,
                '2021': 71,
                '2020': 68
            }
        };
    },

    showLoadingState() {
        const reportContent = document.getElementById('report-content');
        if (reportContent) {
            reportContent.innerHTML = `
                <div class="report-loading">
                    <div class="report-loading-animation">
                        <div class="report-loading-bars">
                            <div class="report-loading-bar"></div>
                            <div class="report-loading-bar"></div>
                            <div class="report-loading-bar"></div>
                            <div class="report-loading-bar"></div>
                            <div class="report-loading-bar"></div>
                        </div>
                    </div>
                    <h3>Generating Report</h3>
                    <p>Analyzing data and creating your comprehensive financial report...</p>
                </div>
            `;
        }
    },

    showErrorState(message) {
        const reportContent = document.getElementById('report-content');
        if (reportContent) {
            reportContent.innerHTML = `
                <div class="report-empty">
                    <i class="fas fa-exclamation-triangle" style="color: var(--accent-danger);"></i>
                    <h3>Report Generation Failed</h3>
                    <p>Unable to generate the report: ${message}</p>
                    <div class="demo-actions">
                        <button class="btn-report-action primary" onclick="Reports.generateReport()">
                            <i class="fas fa-redo"></i>
                            Try Again
                        </button>
                    </div>
                </div>
            `;
        }
    },

    displayReport(reportData) {
        const reportContent = document.getElementById('report-content');
        if (!reportContent) return;

        const reportHtml = this.generateReportHTML(reportData);
        reportContent.innerHTML = reportHtml;

        // Initialize any charts or interactive elements
        this.initializeReportCharts(reportData);
    },

    generateReportHTML(reportData) {
        const { type, data, config } = reportData;
        const reportTitle = this.getReportTitle(type);
        const reportIcon = this.getReportIcon(type);

        return `
            <div class="report-header">
                <h2><i class="${reportIcon}"></i> ${reportTitle}</h2>
                <div class="report-meta">
                    <div class="report-meta-item">
                        <i class="fas fa-calendar"></i>
                        <span>${config.startDate} to ${config.endDate}</span>
                    </div>
                    <div class="report-meta-item">
                        <i class="fas fa-clock"></i>
                        <span>Generated ${new Date().toLocaleString()}</span>
                    </div>
                    <div class="report-meta-item">
                        <i class="fas fa-file"></i>
                        <span>${config.format.toUpperCase()} Format</span>
                    </div>
                </div>
            </div>
            <div class="report-body">
                ${this.generateReportContent(type, data, config)}
                ${this.generateReportActions(reportData)}
            </div>
        `;
    },

    generateReportContent(type, data, config) {
        switch (type) {
            case 'portfolio':
                return this.generatePortfolioReportContent(data, config);
            case 'market':
                return this.generateMarketReportContent(data, config);
            case 'stock':
                return this.generateStockReportContent(data, config);
            case 'risk':
                return this.generateRiskReportContent(data, config);
            case 'performance':
                return this.generatePerformanceReportContent(data, config);
            case 'esg':
                return this.generateESGReportContent(data, config);
            default:
                return '<p>Report content not available.</p>';
        }
    },

    generatePortfolioReportContent(data, config) {
        return `
            <div class="report-section">
                <div class="report-section-header">
                    <h3 class="report-section-title">
                        <i class="fas fa-chart-pie"></i>
                        Portfolio Overview
                    </h3>
                </div>
                <div class="report-metrics">
                    <div class="report-metric-card">
                        <div class="metric-icon"><i class="fas fa-dollar-sign"></i></div>
                        <div class="metric-value">$${data.totalValue.toLocaleString()}</div>
                        <div class="metric-label">Total Portfolio Value</div>
                        <div class="metric-change positive">
                            <i class="fas fa-arrow-up"></i>
                            +${data.dayChangePercent}%
                        </div>
                    </div>
                    <div class="report-metric-card">
                        <div class="metric-icon"><i class="fas fa-chart-line"></i></div>
                        <div class="metric-value">+$${data.dayChange.toLocaleString()}</div>
                        <div class="metric-label">Daily Change</div>
                        <div class="metric-change positive">
                            <i class="fas fa-arrow-up"></i>
                            Today
                        </div>
                    </div>
                    <div class="report-metric-card">
                        <div class="metric-icon"><i class="fas fa-layer-group"></i></div>
                        <div class="metric-value">${data.holdings.length}</div>
                        <div class="metric-label">Holdings</div>
                        <div class="metric-change neutral">
                            <i class="fas fa-equals"></i>
                            Positions
                        </div>
                    </div>
                </div>
            </div>

            <div class="report-section">
                <div class="report-section-header">
                    <h3 class="report-section-title">
                        <i class="fas fa-list"></i>
                        Top Holdings
                    </h3>
                </div>
                <div class="report-table-container">
                    <table class="report-table">
                        <thead>
                            <tr>
                                <th>Symbol</th>
                                <th>Shares</th>
                                <th>Value</th>
                                <th>Weight</th>
                                <th>Change</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.holdings.map(holding => `
                                <tr>
                                    <td><strong>${holding.symbol}</strong></td>
                                    <td>${holding.shares.toLocaleString()}</td>
                                    <td>$${holding.value.toLocaleString()}</td>
                                    <td>${holding.weight}%</td>
                                    <td class="${holding.change >= 0 ? 'positive' : 'negative'}">
                                        ${holding.change >= 0 ? '+' : ''}${holding.change}%
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="report-section">
                <div class="report-section-header">
                    <h3 class="report-section-title">
                        <i class="fas fa-chart-pie"></i>
                        Sector Allocation
                    </h3>
                </div>
                <div class="report-chart-container">
                    <div class="report-chart" id="allocation-chart"></div>
                </div>
            </div>
        `;
    },

    generateMarketReportContent(data, config) {
        return `
            <div class="report-section">
                <div class="report-section-header">
                    <h3 class="report-section-title">
                        <i class="fas fa-globe"></i>
                        Market Indices
                    </h3>
                </div>
                <div class="report-metrics">
                    ${Object.entries(data.indices).map(([name, info]) => `
                        <div class="report-metric-card">
                            <div class="metric-icon"><i class="fas fa-chart-line"></i></div>
                            <div class="metric-value">${info.value.toLocaleString()}</div>
                            <div class="metric-label">${name}</div>
                            <div class="metric-change ${info.change >= 0 ? 'positive' : 'negative'}">
                                <i class="fas fa-arrow-${info.change >= 0 ? 'up' : 'down'}"></i>
                                ${info.change >= 0 ? '+' : ''}${info.change}%
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>

            <div class="report-section">
                <div class="report-section-header">
                    <h3 class="report-section-title">
                        <i class="fas fa-industry"></i>
                        Sector Performance
                    </h3>
                </div>
                <div class="report-chart-container">
                    <div class="report-chart" id="sector-chart"></div>
                </div>
            </div>
        `;
    },

    generateStockReportContent(data, config) {
        return `
            <div class="report-section">
                <div class="report-section-header">
                    <h3 class="report-section-title">
                        <i class="fas fa-chart-line"></i>
                        ${data.symbol} - ${data.companyName}
                    </h3>
                </div>
                <div class="report-metrics">
                    <div class="report-metric-card">
                        <div class="metric-icon"><i class="fas fa-dollar-sign"></i></div>
                        <div class="metric-value">$${data.currentPrice}</div>
                        <div class="metric-label">Current Price</div>
                        <div class="metric-change ${data.change >= 0 ? 'positive' : 'negative'}">
                            <i class="fas fa-arrow-${data.change >= 0 ? 'up' : 'down'}"></i>
                            ${data.change >= 0 ? '+' : ''}${data.changePercent}%
                        </div>
                    </div>
                    <div class="report-metric-card">
                        <div class="metric-icon"><i class="fas fa-building"></i></div>
                        <div class="metric-value">$${(data.marketCap / 1e12).toFixed(2)}T</div>
                        <div class="metric-label">Market Cap</div>
                        <div class="metric-change neutral">
                            <i class="fas fa-info"></i>
                            Large Cap
                        </div>
                    </div>
                    <div class="report-metric-card">
                        <div class="metric-icon"><i class="fas fa-chart-bar"></i></div>
                        <div class="metric-value">${data.peRatio}</div>
                        <div class="metric-label">P/E Ratio</div>
                        <div class="metric-change neutral">
                            <i class="fas fa-equals"></i>
                            Valuation
                        </div>
                    </div>
                </div>
            </div>

            <div class="report-section">
                <div class="report-section-header">
                    <h3 class="report-section-title">
                        <i class="fas fa-cogs"></i>
                        Technical Analysis
                    </h3>
                </div>
                <div class="report-table-container">
                    <table class="report-table">
                        <thead>
                            <tr>
                                <th>Indicator</th>
                                <th>Value</th>
                                <th>Signal</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>RSI (14)</td>
                                <td>${data.technicals.rsi}</td>
                                <td>${data.technicals.rsi > 70 ? 'Overbought' : data.technicals.rsi < 30 ? 'Oversold' : 'Neutral'}</td>
                            </tr>
                            <tr>
                                <td>SMA 20</td>
                                <td>$${data.technicals.sma20}</td>
                                <td>${data.currentPrice > data.technicals.sma20 ? 'Above' : 'Below'}</td>
                            </tr>
                            <tr>
                                <td>Support</td>
                                <td>$${data.technicals.support}</td>
                                <td>${data.currentPrice > data.technicals.support ? 'Above Support' : 'At Support'}</td>
                            </tr>
                            <tr>
                                <td>Resistance</td>
                                <td>$${data.technicals.resistance}</td>
                                <td>${data.currentPrice < data.technicals.resistance ? 'Below Resistance' : 'At Resistance'}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    },

    generateRiskReportContent(data, config) {
        return `
            <div class="report-section">
                <div class="report-section-header">
                    <h3 class="report-section-title">
                        <i class="fas fa-shield-alt"></i>
                        Risk Metrics
                    </h3>
                </div>
                <div class="report-metrics">
                    <div class="report-metric-card">
                        <div class="metric-icon"><i class="fas fa-chart-line"></i></div>
                        <div class="metric-value">${data.portfolioBeta}</div>
                        <div class="metric-label">Portfolio Beta</div>
                        <div class="metric-change ${data.portfolioBeta > 1 ? 'negative' : 'positive'}">
                            <i class="fas fa-info"></i>
                            ${data.portfolioBeta > 1 ? 'High Risk' : 'Low Risk'}
                        </div>
                    </div>
                    <div class="report-metric-card">
                        <div class="metric-icon"><i class="fas fa-wave-square"></i></div>
                        <div class="metric-value">${data.volatility}%</div>
                        <div class="metric-label">Volatility</div>
                        <div class="metric-change neutral">
                            <i class="fas fa-calendar"></i>
                            Annualized
                        </div>
                    </div>
                    <div class="report-metric-card">
                        <div class="metric-icon"><i class="fas fa-trophy"></i></div>
                        <div class="metric-value">${data.sharpeRatio}</div>
                        <div class="metric-label">Sharpe Ratio</div>
                        <div class="metric-change positive">
                            <i class="fas fa-arrow-up"></i>
                            Good
                        </div>
                    </div>
                    <div class="report-metric-card">
                        <div class="metric-icon"><i class="fas fa-arrow-down"></i></div>
                        <div class="metric-value">${data.maxDrawdown}%</div>
                        <div class="metric-label">Max Drawdown</div>
                        <div class="metric-change negative">
                            <i class="fas fa-exclamation"></i>
                            Risk
                        </div>
                    </div>
                </div>
            </div>

            <div class="report-section">
                <div class="report-section-header">
                    <h3 class="report-section-title">
                        <i class="fas fa-table"></i>
                        Detailed Risk Analysis
                    </h3>
                </div>
                <div class="report-table-container">
                    <table class="report-table">
                        <thead>
                            <tr>
                                <th>Risk Metric</th>
                                <th>Value</th>
                                <th>Interpretation</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${Object.entries(data.riskMetrics).map(([metric, value]) => `
                                <tr>
                                    <td>${metric}</td>
                                    <td>${value}</td>
                                    <td>${this.getRiskInterpretation(metric, value)}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    },

    generatePerformanceReportContent(data, config) {
        return `
            <div class="report-section">
                <div class="report-section-header">
                    <h3 class="report-section-title">
                        <i class="fas fa-trophy"></i>
                        Performance Returns
                    </h3>
                </div>
                <div class="report-metrics">
                    ${Object.entries(data.returns).slice(0, 4).map(([period, return_]) => `
                        <div class="report-metric-card">
                            <div class="metric-icon"><i class="fas fa-chart-line"></i></div>
                            <div class="metric-value">${return_}%</div>
                            <div class="metric-label">${period} Return</div>
                            <div class="metric-change ${return_ >= 0 ? 'positive' : 'negative'}">
                                <i class="fas fa-arrow-${return_ >= 0 ? 'up' : 'down'}"></i>
                                ${return_ >= 0 ? 'Gain' : 'Loss'}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>

            <div class="report-section">
                <div class="report-section-header">
                    <h3 class="report-section-title">
                        <i class="fas fa-balance-scale"></i>
                        Benchmark Comparison
                    </h3>
                </div>
                <div class="report-chart-container">
                    <div class="report-chart" id="performance-chart"></div>
                </div>
            </div>
        `;
    },

    generateESGReportContent(data, config) {
        return `
            <div class="report-section">
                <div class="report-section-header">
                    <h3 class="report-section-title">
                        <i class="fas fa-leaf"></i>
                        ESG Scores
                    </h3>
                </div>
                <div class="report-metrics">
                    <div class="report-metric-card">
                        <div class="metric-icon"><i class="fas fa-star"></i></div>
                        <div class="metric-value">${data.overallScore}</div>
                        <div class="metric-label">Overall ESG Score</div>
                        <div class="metric-change positive">
                            <i class="fas fa-arrow-up"></i>
                            Excellent
                        </div>
                    </div>
                    <div class="report-metric-card">
                        <div class="metric-icon"><i class="fas fa-tree"></i></div>
                        <div class="metric-value">${data.environmental}</div>
                        <div class="metric-label">Environmental</div>
                        <div class="metric-change positive">
                            <i class="fas fa-leaf"></i>
                            Green
                        </div>
                    </div>
                    <div class="report-metric-card">
                        <div class="metric-icon"><i class="fas fa-users"></i></div>
                        <div class="metric-value">${data.social}</div>
                        <div class="metric-label">Social</div>
                        <div class="metric-change positive">
                            <i class="fas fa-heart"></i>
                            Good
                        </div>
                    </div>
                    <div class="report-metric-card">
                        <div class="metric-icon"><i class="fas fa-gavel"></i></div>
                        <div class="metric-value">${data.governance}</div>
                        <div class="metric-label">Governance</div>
                        <div class="metric-change positive">
                            <i class="fas fa-check"></i>
                            Strong
                        </div>
                    </div>
                </div>
            </div>

            <div class="report-section">
                <div class="report-section-header">
                    <h3 class="report-section-title">
                        <i class="fas fa-chart-bar"></i>
                        ESG Breakdown
                    </h3>
                </div>
                <div class="report-chart-container">
                    <div class="report-chart" id="esg-chart"></div>
                </div>
            </div>
        `;
    },

    generateReportActions(reportData) {
        return `
            <div class="report-actions">
                <button class="btn-report-action primary" onclick="Reports.downloadReport('${reportData.config.format}')">
                    <i class="fas fa-download"></i>
                    Download ${reportData.config.format.toUpperCase()}
                </button>
                <button class="btn-report-action" onclick="Reports.shareReport()">
                    <i class="fas fa-share"></i>
                    Share Report
                </button>
                <button class="btn-report-action" onclick="Reports.scheduleReport()">
                    <i class="fas fa-clock"></i>
                    Schedule Report
                </button>
                <button class="btn-report-action" onclick="Reports.exportToEmail()">
                    <i class="fas fa-envelope"></i>
                    Email Report
                </button>
                <button class="btn-report-action" onclick="window.print()">
                    <i class="fas fa-print"></i>
                    Print Report
                </button>
            </div>
        `;
    },

    initializeReportCharts(reportData) {
        // Initialize charts based on report type
        const { type, data } = reportData;
        
        setTimeout(() => {
            switch (type) {
                case 'portfolio':
                    this.createAllocationChart(data.allocation);
                    break;
                case 'market':
                    this.createSectorChart(data.sectors);
                    break;
                case 'performance':
                    this.createPerformanceChart(data.benchmarkComparison);
                    break;
                case 'esg':
                    this.createESGChart(data.breakdown);
                    break;
            }
        }, 100);
    },

    createAllocationChart(allocation) {
        const chartElement = document.getElementById('allocation-chart');
        if (!chartElement) return;

        // Simple chart representation
        chartElement.innerHTML = `
            <div style="display: flex; flex-direction: column; gap: 10px;">
                ${Object.entries(allocation).map(([sector, percentage]) => `
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div style="width: 100px; font-size: 0.875rem;">${sector}</div>
                        <div style="flex: 1; background: var(--bg-tertiary); border-radius: 4px; height: 20px; position: relative;">
                            <div style="background: var(--accent-primary); height: 100%; width: ${percentage}%; border-radius: 4px;"></div>
                        </div>
                        <div style="width: 50px; text-align: right; font-size: 0.875rem;">${percentage}%</div>
                    </div>
                `).join('')}
            </div>
        `;
    },

    createSectorChart(sectors) {
        const chartElement = document.getElementById('sector-chart');
        if (!chartElement) return;

        chartElement.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                ${Object.entries(sectors).map(([sector, performance]) => `
                    <div style="text-align: center; padding: 15px; background: var(--bg-tertiary); border-radius: 8px;">
                        <div style="font-size: 0.875rem; margin-bottom: 5px;">${sector}</div>
                        <div style="font-size: 1.25rem; font-weight: 600; color: ${performance >= 0 ? 'var(--accent-success)' : 'var(--accent-danger)'};">
                            ${performance >= 0 ? '+' : ''}${performance}%
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    },

    createPerformanceChart(comparison) {
        const chartElement = document.getElementById('performance-chart');
        if (!chartElement) return;

        chartElement.innerHTML = `
            <div style="display: flex; justify-content: space-around; align-items: end; height: 200px; padding: 20px;">
                <div style="text-align: center;">
                    <div style="height: ${comparison.portfolio * 2}px; width: 60px; background: var(--accent-primary); margin-bottom: 10px; border-radius: 4px 4px 0 0;"></div>
                    <div style="font-size: 0.875rem;">Portfolio</div>
                    <div style="font-weight: 600;">${comparison.portfolio}%</div>
                </div>
                <div style="text-align: center;">
                    <div style="height: ${comparison.sp500 * 2}px; width: 60px; background: var(--accent-secondary); margin-bottom: 10px; border-radius: 4px 4px 0 0;"></div>
                    <div style="font-size: 0.875rem;">S&P 500</div>
                    <div style="font-weight: 600;">${comparison.sp500}%</div>
                </div>
                <div style="text-align: center;">
                    <div style="height: ${comparison.nasdaq * 2}px; width: 60px; background: var(--accent-tertiary); margin-bottom: 10px; border-radius: 4px 4px 0 0;"></div>
                    <div style="font-size: 0.875rem;">NASDAQ</div>
                    <div style="font-weight: 600;">${comparison.nasdaq}%</div>
                </div>
            </div>
        `;
    },

    createESGChart(breakdown) {
        const chartElement = document.getElementById('esg-chart');
        if (!chartElement) return;

        chartElement.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px;">
                ${Object.entries(breakdown).map(([category, score]) => `
                    <div style="text-align: center; padding: 10px;">
                        <div style="font-size: 0.75rem; margin-bottom: 5px;">${category}</div>
                        <div style="width: 60px; height: 60px; border-radius: 50%; background: conic-gradient(var(--accent-primary) ${score * 3.6}deg, var(--bg-tertiary) 0deg); display: flex; align-items: center; justify-content: center; margin: 0 auto;">
                            <div style="width: 40px; height: 40px; border-radius: 50%; background: var(--bg-card); display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 0.875rem;">
                                ${score}
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    },

    getReportTitle(type) {
        const titles = {
            portfolio: 'Portfolio Summary Report',
            market: 'Market Analysis Report',
            stock: 'Stock Research Report',
            risk: 'Risk Assessment Report',
            performance: 'Performance Analytics Report',
            esg: 'ESG Analysis Report'
        };
        return titles[type] || 'Financial Report';
    },

    getReportIcon(type) {
        const icons = {
            portfolio: 'fas fa-chart-pie',
            market: 'fas fa-globe',
            stock: 'fas fa-chart-line',
            risk: 'fas fa-shield-alt',
            performance: 'fas fa-trophy',
            esg: 'fas fa-leaf'
        };
        return icons[type] || 'fas fa-file-chart';
    },

    getRiskInterpretation(metric, value) {
        // Simple risk interpretation logic
        if (metric.includes('Beta')) {
            const beta = parseFloat(value);
            return beta > 1.2 ? 'High Risk' : beta < 0.8 ? 'Low Risk' : 'Moderate Risk';
        }
        if (metric.includes('VaR')) {
            return 'Maximum expected loss at 95% confidence';
        }
        if (metric.includes('Alpha')) {
            return parseFloat(value) > 0 ? 'Outperforming' : 'Underperforming';
        }
        return 'Within normal range';
    },

    // Action methods
    downloadReport(format) {
        console.log(`Downloading report in ${format} format`);
        // Implement download functionality
        alert(`Report download in ${format.toUpperCase()} format would start here.`);
    },

    shareReport() {
        console.log('Sharing report');
        // Implement share functionality
        if (navigator.share) {
            navigator.share({
                title: 'Financial Report',
                text: 'Check out this financial analysis report',
                url: window.location.href
            });
        } else {
            alert('Report sharing functionality would be implemented here.');
        }
    },

    scheduleReport() {
        console.log('Scheduling report');
        // Implement scheduling functionality
        alert('Report scheduling functionality would be implemented here.');
    },

    exportToEmail() {
        console.log('Exporting to email');
        // Implement email export functionality
        alert('Email export functionality would be implemented here.');
    },

    generateDemoReport() {
        console.log('Generating demo report');
        this.generateReport();
    }
};

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    Reports.init();
});

// Export for global access
window.Reports = Reports; 