/* ==========================================
   ANALYSIS MODULE
   Advanced financial analysis functionality
   ========================================== */

const Analysis = {
    currentSymbol: null,
    currentData: null,
    indicators: new Set(['ma', 'rsi']), // Default indicators

    init() {
        console.log('Analysis module initialized');
        this.setupAnalysisEventListeners();
        this.setupIndicatorToggles();
    },

    setupAnalysisEventListeners() {
        // Symbol analysis button
        const analyzeBtn = document.getElementById('analyze-symbol');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.analyzeSymbol());
        }

        // Enter key for symbol input
        const symbolInput = document.getElementById('analysis-symbol');
        if (symbolInput) {
            symbolInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.analyzeSymbol();
                }
            });
        }
    },

    setupIndicatorToggles() {
        // Setup indicator checkboxes
        const indicators = document.querySelectorAll('input[data-indicator]');
        indicators.forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const indicator = e.target.dataset.indicator;
                if (e.target.checked) {
                    this.indicators.add(indicator);
                } else {
                    this.indicators.delete(indicator);
                }
                
                // Re-render charts if we have current data
                if (this.currentSymbol && this.currentData) {
                    this.renderIndicatorCharts();
                }
            });

            // Initialize indicator set based on checked state
            if (checkbox.checked) {
                this.indicators.add(checkbox.dataset.indicator);
            }
        });
    },

    async analyzeSymbol() {
        const symbolInput = document.getElementById('analysis-symbol');
        if (!symbolInput) {
            console.error('Symbol input not found');
            return;
        }

        const symbol = symbolInput.value.trim().toUpperCase();
        if (!this.validateSymbol(symbol)) {
            this.showError('Please enter a valid stock symbol (1-5 letters)');
            return;
        }

        console.log(`Starting comprehensive analysis for ${symbol}`);
        this.showLoading();

        try {
            // Set current symbol
            this.currentSymbol = symbol;

            console.log('Fetching data...');
            // Fetch comprehensive data
            const [marketData, historicalData] = await Promise.all([
                this.fetchMarketData(symbol),
                this.fetchHistoricalData(symbol)
            ]);

            console.log('Data received:', { marketData, historicalData });

            if (!historicalData || !historicalData.data || historicalData.data.length === 0) {
                throw new Error('No historical data available');
            }

            this.currentData = historicalData;

            console.log('Rendering charts...');
            
            // Check if ChartManager is available
            if (!window.ChartManager) {
                console.error('ChartManager not available, creating new instance');
                window.ChartManager = new ChartManager();
            }

            // Render main price chart
            await this.renderMainChart(symbol, historicalData);
            
            // Render all indicator charts
            await this.renderIndicatorCharts();

            // Update comprehensive metrics
            this.updateAdvancedMetrics(symbol, historicalData, marketData);

            // Hide loading indicators after all rendering is complete
            this.hideLoading();

            console.log(`Analysis complete for ${symbol}`);

        } catch (error) {
            console.error('Analysis error:', error);
            this.showError(`Failed to analyze ${symbol}: ${error.message}`);
            this.showChartErrors();
        }
    },

    async fetchMarketData(symbol) {
        try {
            if (window.API && window.API.getMarketData) {
                return await window.API.getMarketData(symbol);
            }
            return null;
        } catch (error) {
            console.warn('Failed to fetch market data:', error);
            return null;
        }
    },

    async fetchHistoricalData(symbol) {
        try {
            console.log('API check:', !!window.API);
            if (window.API && window.API.getHistoricalData) {
                console.log('Calling API.getHistoricalData for', symbol);
                const data = await window.API.getHistoricalData(symbol);
                console.log('API returned data:', data);
                return data;
            }
            throw new Error('API not available');
        } catch (error) {
            console.error('Failed to fetch historical data:', error);
            throw error;
        }
    },

    async renderMainChart(symbol, data) {
        console.log('renderMainChart called with:', { symbol, data });
        
        if (!window.ChartManager) {
            console.error('ChartManager not available');
            return;
        }

        try {
            const selectedIndicators = Array.from(this.indicators);
            console.log('Selected indicators:', selectedIndicators);
            console.log('Calling ChartManager.renderAnalysisChart...');
            await window.ChartManager.renderAnalysisChart(symbol, data, selectedIndicators);
            console.log('Main chart rendered successfully');
        } catch (error) {
            console.error('Error rendering main chart:', error);
        }
    },

    async renderIndicatorCharts() {
        console.log('renderIndicatorCharts called');
        
        if (!this.currentData || !window.ChartManager) {
            console.error('Missing data or ChartManager:', { data: !!this.currentData, chartManager: !!window.ChartManager });
            return;
        }

        const symbol = this.currentSymbol;
        const data = this.currentData;

        try {
            console.log('Rendering RSI and Volume charts...');
            // Always render RSI and Volume
            await Promise.all([
                window.ChartManager.renderRSIChart(symbol, data),
                window.ChartManager.renderVolumeChart(symbol, data)
            ]);
            console.log('RSI and Volume charts rendered');

            // Render MACD if selected
            if (this.indicators.has('macd')) {
                console.log('Rendering MACD chart...');
                await window.ChartManager.renderMACDChart(symbol, data);
            } else {
                this.clearChart('macd-chart');
            }

            // Render Stochastic if selected
            if (this.indicators.has('stochastic')) {
                console.log('Rendering Stochastic chart...');
                await window.ChartManager.renderStochasticChart(symbol, data);
            } else {
                this.clearChart('stochastic-chart');
            }

            console.log('All indicator charts rendered successfully');

        } catch (error) {
            console.error('Error rendering indicator charts:', error);
        }
    },

    clearChart(chartId) {
        const chartElement = document.getElementById(chartId);
        if (chartElement) {
            chartElement.innerHTML = '';
        }
    },

    updateAdvancedMetrics(symbol, historicalData, marketData) {
        if (!window.ChartManager || !window.ChartManager.updateAnalysisMetrics) {
            console.warn('ChartManager metrics updater not available');
            return;
        }

        try {
            // Calculate comprehensive technical data
            const closes = historicalData.data.map(d => d.close);
            const rsi = Utils.calculateRSI(closes);
            const sma20 = Utils.calculateSMA(closes, 20);
            const sma50 = Utils.calculateSMA(closes, 50);

            const technicalData = {
                rsi: {
                    current: rsi[rsi.length - 1]?.toFixed(2) || 'N/A',
                    values: rsi
                },
                sma: {
                    sma20: sma20[sma20.length - 1] || 0,
                    sma50: sma50[sma50.length - 1] || 0
                }
            };

            // Update metrics display
            window.ChartManager.updateAnalysisMetrics(symbol, historicalData, technicalData);

        } catch (error) {
            console.error('Error updating metrics:', error);
        }
    },

    showLoading() {
        const charts = ['analysis-chart', 'rsi-chart', 'volume-chart', 'macd-chart', 'stochastic-chart'];
        charts.forEach(chartId => {
            const chart = document.getElementById(chartId);
            if (chart) {
                chart.innerHTML = '<div class="loading-indicator">Loading...</div>';
            }
        });
    },

    hideLoading() {
        // Use a slight delay to ensure Plotly has finished rendering
        setTimeout(() => {
            const charts = ['analysis-chart', 'rsi-chart', 'volume-chart', 'macd-chart', 'stochastic-chart'];
            charts.forEach(chartId => {
                const chart = document.getElementById(chartId);
                if (chart) {
                    // Remove any loading elements that might still be hanging around
                    const loadingElements = chart.querySelectorAll('.chart-loading, .loading-indicator');
                    loadingElements.forEach(element => {
                        element.remove();
                    });
                    
                    // Also check for text-based loading indicators
                    if (chart.innerHTML.includes('Loading') && !chart.querySelector('.js-plotly-plot')) {
                        chart.innerHTML = '';
                    }
                }
            });
        }, 100); // Small delay to let Plotly finish
    },

    showError(message) {
        if (window.financeApp && window.financeApp.showNotification) {
            window.financeApp.showNotification('error', 'Analysis Error', message);
        } else {
            console.error('Analysis Error:', message);
            alert(message);
        }
    },

    showChartErrors() {
        const charts = ['analysis-chart', 'rsi-chart', 'volume-chart', 'macd-chart', 'stochastic-chart'];
        charts.forEach(chartId => {
            const chart = document.getElementById(chartId);
            if (chart && chart.innerHTML.includes('Loading')) {
                chart.innerHTML = `
                    <div class="chart-error">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>Error loading chart</p>
                    </div>
                `;
            }
        });
    },

    validateSymbol(symbol) {
        return symbol && symbol.length > 0 && /^[A-Z]{1,5}$/.test(symbol);
    },

    // Get analysis summary for current symbol
    getAnalysisSummary() {
        if (!this.currentData || !this.currentSymbol) return null;

        const data = this.currentData.data;
        const current = data[data.length - 1];
        const previous = data[data.length - 2];
        
        const change = current.close - previous.close;
        const changePercent = (change / previous.close) * 100;

        // Calculate RSI for trend analysis
        const closes = data.map(d => d.close);
        const rsi = Utils.calculateRSI(closes);
        const currentRSI = rsi[rsi.length - 1];

        // Determine trend
        let trend = 'Neutral';
        if (changePercent > 2) trend = 'Strong Bullish';
        else if (changePercent > 0.5) trend = 'Bullish';
        else if (changePercent < -2) trend = 'Strong Bearish';
        else if (changePercent < -0.5) trend = 'Bearish';

        // RSI analysis
        let rsiSignal = 'Neutral';
        if (currentRSI > 70) rsiSignal = 'Overbought';
        else if (currentRSI < 30) rsiSignal = 'Oversold';

        return {
            symbol: this.currentSymbol,
            price: current.close,
            change: change,
            changePercent: changePercent,
            trend: trend,
            rsi: currentRSI,
            rsiSignal: rsiSignal,
            volume: current.volume
        };
    }
};

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    Analysis.init();
});

// Export for global access
window.Analysis = Analysis; 