/* ==========================================
   ANALYSIS MODULE
   Advanced financial analysis functionality
   ========================================== */

const Analysis = {
    currentSymbol: null,
    currentData: null,
    indicators: new Set(['ma', 'rsi']), // Default indicators
    selectedMarket: 'US',
    currentCurrency: 'USD',

    init() {
        console.log('Analysis module initialized');
        this.setupAnalysisEventListeners();
        this.setupIndicatorToggles();
        this.setupAIAnalysisControls();
        this.setupMarketSelector();
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

        // Setup time range buttons
        this.setupTimeRangeButtons();
    },

    setupTimeRangeButtons() {
        const timeRangeButtons = document.querySelectorAll('.time-range-btn');
        timeRangeButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Remove active class from all buttons
                timeRangeButtons.forEach(b => b.classList.remove('active'));
                // Add active class to clicked button
                e.target.classList.add('active');
                
                // Get the selected range
                const range = e.target.dataset.range;
                this.selectedTimeRange = range;
                
                // Re-analyze with new time range if we have a current symbol
                if (this.currentSymbol) {
                    this.analyzeSymbol();
                }
            });
        });
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
            const errorMsg = this.selectedMarket === 'IN' 
                ? 'Please enter a valid Indian stock symbol (e.g., RELIANCE, TCS, HDFCBANK)'
                : 'Please enter a valid US stock symbol (1-5 letters, e.g., AAPL, MSFT)';
            this.showError(errorMsg);
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

            // Trigger AI analysis automatically
            setTimeout(() => {
                this.refreshAIAnalysis();
            }, 1000); // Small delay to let charts render first

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
                return await window.API.getMarketData(symbol, this.selectedMarket);
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
                console.log('Calling API.getHistoricalData for', symbol, 'market:', this.selectedMarket);
                const data = await window.API.getHistoricalData(symbol, this.selectedMarket);
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

            // Update all sidebar components
            window.ChartManager.updateStockOverview(symbol, historicalData);
            window.ChartManager.updateQuickAnalysis(symbol, historicalData, technicalData);
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
        if (!symbol || symbol.length === 0) {
            return false;
        }
        
        // Convert to uppercase for validation
        const upperSymbol = symbol.toUpperCase();
        
        // Market-aware validation
        if (this.selectedMarket === 'IN') {
            // Indian stocks: Allow 1-12 characters, letters and hyphens (for symbols like BAJAJ-AUTO)
            return /^[A-Z][A-Z0-9&-]{0,11}$/.test(upperSymbol);
        } else {
            // US stocks: Traditional 1-5 letter symbols
            return /^[A-Z]{1,5}$/.test(upperSymbol);
        }
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
    },

    // AI Analysis Methods
    setupAIAnalysisControls() {
        // Refresh AI Analysis button
        const refreshBtn = document.getElementById('refresh-ai-analysis');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshAIAnalysis());
        }

        // Toggle AI Details button
        const toggleBtn = document.getElementById('toggle-ai-details');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggleAIDetails());
        }

        // Retry AI Analysis button
        const retryBtn = document.getElementById('retry-ai-analysis');
        if (retryBtn) {
            retryBtn.addEventListener('click', () => this.refreshAIAnalysis());
        }
    },

    async refreshAIAnalysis() {
        if (!this.currentSymbol || !this.currentData) {
            console.warn('No symbol or data available for AI analysis');
            return;
        }

        console.log('Refreshing AI analysis for', this.currentSymbol);
        this.showAILoading();

        try {
            // Prepare data for AI analysis
            const analysisData = this.prepareAIAnalysisData();
            
            // Get AI analysis
            const aiAnalysis = await this.getAIAnalysis(analysisData);
            
            // Display results
            this.displayAIAnalysis(aiAnalysis);
            
        } catch (error) {
            console.error('AI Analysis error:', error);
            this.showAIError(error.message);
        }
    },

    prepareAIAnalysisData() {
        if (!this.currentData || !this.currentData.data) {
            throw new Error('No data available for analysis');
        }

        const data = this.currentData.data;
        const latest = data[data.length - 1];
        const previous = data[data.length - 2];

        // Calculate technical indicators
        const prices = data.map(d => d.close);
        const volumes = data.map(d => d.volume);
        
        // Calculate RSI
        const rsi = Utils.calculateRSI(prices);
        
        // Calculate MACD
        const macdResult = Utils.calculateMACD(prices);
        
        // Calculate Bollinger Bands
        const bb = Utils.calculateBollingerBands(prices);
        
        // Calculate Moving Averages
        const sma20 = Utils.calculateSMA(prices, 20);
        const sma50 = Utils.calculateSMA(prices, 50);
        
        // Calculate support and resistance
        const supportResistance = this.calculateSupportResistance(prices);

        // Prepare stock data
        const stockData = {
            symbol: this.currentSymbol,
            market: this.selectedMarket,
            currency: this.currentCurrency,
            current_price: latest.close,
            price_change: latest.close - previous.close,
            price_change_percent: ((latest.close - previous.close) / previous.close) * 100,
            volume: latest.volume,
            market_cap: this.estimateMarketCap(latest.close),
            day_range: {
                low: Math.min(...data.slice(-1).map(d => d.low)),
                high: Math.max(...data.slice(-1).map(d => d.high))
            },
            week_52_range: {
                low: Math.min(...prices.slice(-252)),
                high: Math.max(...prices.slice(-252))
            }
        };

        // Prepare technical indicators
        const technicalIndicators = {
            rsi: rsi[rsi.length - 1] || 50,
            macd: {
                macd: (macdResult.macdLine && macdResult.macdLine.length > 0) ? 
                      macdResult.macdLine.filter(x => x !== undefined).slice(-1)[0] || 0 : 0,
                signal: (macdResult.signalLine && macdResult.signalLine.length > 0) ? 
                        macdResult.signalLine.filter(x => x !== undefined).slice(-1)[0] || 0 : 0,
                histogram: (macdResult.histogram && macdResult.histogram.length > 0) ? 
                           macdResult.histogram.filter(x => x !== undefined).slice(-1)[0] || 0 : 0
            },
            bollinger_bands: {
                upper: (bb.upper && bb.upper.length > 0) ? bb.upper[bb.upper.length - 1] : latest.close * 1.02,
                lower: (bb.lower && bb.lower.length > 0) ? bb.lower[bb.lower.length - 1] : latest.close * 0.98,
                middle: (bb.middle && bb.middle.length > 0) ? bb.middle[bb.middle.length - 1] : latest.close
            },
            moving_averages: {
                sma20: (sma20 && sma20.length > 0) ? sma20[sma20.length - 1] : latest.close,
                sma50: (sma50 && sma50.length > 0) ? sma50[sma50.length - 1] : latest.close
            },
            volume_analysis: {
                current_volume: latest.volume,
                avg_volume: volumes.slice(-20).reduce((a, b) => a + b, 0) / 20,
                volume_trend: latest.volume > (volumes.slice(-5).reduce((a, b) => a + b, 0) / 5) ? 'increasing' : 'decreasing'
            },
            support_resistance: supportResistance
        };

        return {
            stock_data: stockData,
            technical_indicators: technicalIndicators,
            time_period: this.selectedTimeRange || '3M'
        };
    },

    async getAIAnalysis(analysisData) {
        try {
            // Try to call backend AI analysis endpoint
            const response = await fetch('/api/ai-analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(analysisData)
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error('AI service unavailable');
            }
        } catch (error) {
            console.warn('Backend AI analysis failed, using fallback:', error);
            return this.getFallbackAnalysis(analysisData);
        }
    },

    getFallbackAnalysis(data) {
        const { stock_data, technical_indicators } = data;
        const currencySymbol = stock_data.currency === 'INR' ? '₹' : '$';
        const marketContext = stock_data.market === 'IN' ? 'Indian market' : 'US market';
        
        // Determine sentiment
        let sentiment = 'neutral';
        if (technical_indicators.rsi > 70) {
            sentiment = 'bearish';
        } else if (technical_indicators.rsi < 30) {
            sentiment = 'bullish';
        } else if (stock_data.price_change_percent > 2) {
            sentiment = 'bullish';
        } else if (stock_data.price_change_percent < -2) {
            sentiment = 'bearish';
        }

        return {
            overall_sentiment: sentiment,
            price_analysis: `${stock_data.symbol} is trading at ${currencySymbol}${stock_data.current_price.toFixed(2)} in the ${marketContext}, showing a ${stock_data.price_change_percent > 0 ? 'gain' : 'loss'} of ${Math.abs(stock_data.price_change_percent).toFixed(2)}% from the previous session. The stock is currently ${stock_data.current_price > technical_indicators.moving_averages.sma20 ? 'above' : 'below'} its 20-day moving average.`,
            technical_summary: `RSI at ${technical_indicators.rsi.toFixed(1)} indicates ${technical_indicators.rsi > 70 ? 'overbought' : technical_indicators.rsi < 30 ? 'oversold' : 'neutral'} conditions. MACD shows ${technical_indicators.macd.macd > technical_indicators.macd.signal ? 'bullish' : 'bearish'} momentum with the MACD line ${technical_indicators.macd.macd > technical_indicators.macd.signal ? 'above' : 'below'} the signal line.`,
            volume_insights: `Current volume of ${stock_data.volume.toLocaleString()} shares is ${technical_indicators.volume_analysis.volume_trend} compared to recent averages, suggesting ${technical_indicators.volume_analysis.volume_trend === 'increasing' ? 'heightened' : 'normal'} market interest in the ${marketContext}.`,
            support_resistance: `Key support identified around ${currencySymbol}${technical_indicators.support_resistance.support.toFixed(2)} with resistance near ${currencySymbol}${technical_indicators.support_resistance.resistance.toFixed(2)}. These levels represent important psychological and technical barriers.`,
            risk_assessment: `Current ${marketContext} conditions present ${sentiment === 'bullish' ? 'moderate upside potential' : sentiment === 'bearish' ? 'downside risks' : 'mixed signals'}. Monitor key technical levels and volume for confirmation of trend direction.`,
            short_term_outlook: `Short-term outlook appears ${sentiment} based on current technical indicators. Watch for ${technical_indicators.rsi > 70 ? 'potential pullback from overbought levels' : technical_indicators.rsi < 30 ? 'potential bounce from oversold conditions' : 'breakout from current consolidation'}.`,
            key_levels: `Important levels to watch: Support at ${currencySymbol}${technical_indicators.support_resistance.support.toFixed(2)}, Resistance at ${currencySymbol}${technical_indicators.support_resistance.resistance.toFixed(2)}, 20-day MA at ${currencySymbol}${technical_indicators.moving_averages.sma20.toFixed(2)}`,
            trading_suggestion: `Based on current analysis, consider ${sentiment === 'bullish' ? 'potential long positions with stop-loss below support' : sentiment === 'bearish' ? 'caution and potential short positions with stop-loss above resistance' : 'waiting for clearer directional signals'}. Always use proper risk management and position sizing.`
        };
    },

    displayAIAnalysis(analysis) {
        // Hide loading and error states
        this.hideAILoading();
        this.hideAIError();

        // Show results
        const resultsDiv = document.getElementById('ai-analysis-results');
        if (resultsDiv) {
            resultsDiv.style.display = 'block';
        }

        // Update sentiment badge
        this.updateSentimentBadge(analysis.overall_sentiment);

        // Update insight cards
        this.updateInsightCard('ai-price-analysis', analysis.price_analysis);
        this.updateInsightCard('ai-technical-summary', analysis.technical_summary);
        this.updateInsightCard('ai-volume-insights', analysis.volume_insights);
        this.updateInsightCard('ai-risk-assessment', analysis.risk_assessment);

        // Update detailed sections
        this.updateInsightCard('ai-support-resistance', analysis.support_resistance);
        this.updateInsightCard('ai-short-term-outlook', analysis.short_term_outlook);
        this.updateInsightCard('ai-key-levels', analysis.key_levels);
        this.updateInsightCard('ai-trading-suggestion', analysis.trading_suggestion);

        console.log('AI Analysis displayed successfully');
    },

    updateSentimentBadge(sentiment) {
        const badge = document.getElementById('sentiment-badge');
        if (badge) {
            // Remove existing classes
            badge.classList.remove('bullish', 'bearish', 'neutral');
            
            // Add appropriate class and text
            if (sentiment.toLowerCase().includes('bullish')) {
                badge.classList.add('bullish');
                badge.textContent = 'Bullish';
            } else if (sentiment.toLowerCase().includes('bearish')) {
                badge.classList.add('bearish');
                badge.textContent = 'Bearish';
            } else {
                badge.classList.add('neutral');
                badge.textContent = 'Neutral';
            }
        }
    },

    updateInsightCard(elementId, content) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = content;
        }
    },

    toggleAIDetails() {
        const detailsDiv = document.getElementById('ai-detailed-analysis');
        const toggleBtn = document.getElementById('toggle-ai-details');
        
        if (detailsDiv && toggleBtn) {
            const isVisible = detailsDiv.style.display !== 'none';
            
            if (isVisible) {
                detailsDiv.style.display = 'none';
                toggleBtn.innerHTML = '<i class="fas fa-expand"></i> Show Details';
            } else {
                detailsDiv.style.display = 'block';
                toggleBtn.innerHTML = '<i class="fas fa-compress"></i> Hide Details';
            }
        }
    },

    showAILoading() {
        const loadingDiv = document.getElementById('ai-analysis-loading');
        const resultsDiv = document.getElementById('ai-analysis-results');
        const errorDiv = document.getElementById('ai-analysis-error');
        
        if (loadingDiv) loadingDiv.style.display = 'block';
        if (resultsDiv) resultsDiv.style.display = 'none';
        if (errorDiv) errorDiv.style.display = 'none';
    },

    hideAILoading() {
        const loadingDiv = document.getElementById('ai-analysis-loading');
        if (loadingDiv) loadingDiv.style.display = 'none';
    },

    showAIError(message) {
        const errorDiv = document.getElementById('ai-analysis-error');
        const loadingDiv = document.getElementById('ai-analysis-loading');
        const resultsDiv = document.getElementById('ai-analysis-results');
        
        if (errorDiv) {
            errorDiv.style.display = 'block';
            const errorText = errorDiv.querySelector('p');
            if (errorText) {
                errorText.textContent = message || 'AI analysis is currently unavailable. Please try again later.';
            }
        }
        if (loadingDiv) loadingDiv.style.display = 'none';
        if (resultsDiv) resultsDiv.style.display = 'none';
    },

    hideAIError() {
        const errorDiv = document.getElementById('ai-analysis-error');
        if (errorDiv) errorDiv.style.display = 'none';
    },

    // Technical Analysis Helper Methods
    calculateSupportResistance(prices) {
        if (prices.length < 20) {
            const current = prices[prices.length - 1];
            return {
                support: current * 0.95,
                resistance: current * 1.05
            };
        }
        
        // Simple support/resistance calculation
        const recentPrices = prices.slice(-50);
        const highs = [];
        const lows = [];
        
        // Find local highs and lows
        for (let i = 2; i < recentPrices.length - 2; i++) {
            if (recentPrices[i] > recentPrices[i-1] && recentPrices[i] > recentPrices[i+1] &&
                recentPrices[i] > recentPrices[i-2] && recentPrices[i] > recentPrices[i+2]) {
                highs.push(recentPrices[i]);
            }
            if (recentPrices[i] < recentPrices[i-1] && recentPrices[i] < recentPrices[i+1] &&
                recentPrices[i] < recentPrices[i-2] && recentPrices[i] < recentPrices[i+2]) {
                lows.push(recentPrices[i]);
            }
        }
        
        const resistance = highs.length ? Math.max(...highs) : Math.max(...recentPrices);
        const support = lows.length ? Math.min(...lows) : Math.min(...recentPrices);
        
        return { support, resistance };
    },

    estimateMarketCap(price) {
        // This is a rough estimation - in reality you'd need shares outstanding
        const estimatedShares = 1000000000; // 1B shares as rough estimate
        const marketCap = price * estimatedShares;
        
        if (this.currentCurrency === 'INR') {
            if (marketCap > 1e12) return `₹${(marketCap / 1e12).toFixed(1)}T`;
            if (marketCap > 1e9) return `₹${(marketCap / 1e9).toFixed(1)}B`;
            if (marketCap > 1e6) return `₹${(marketCap / 1e6).toFixed(1)}M`;
            return `₹${marketCap.toFixed(0)}`;
        } else {
            if (marketCap > 1e12) return `$${(marketCap / 1e12).toFixed(1)}T`;
            if (marketCap > 1e9) return `$${(marketCap / 1e9).toFixed(1)}B`;
            if (marketCap > 1e6) return `$${(marketCap / 1e6).toFixed(1)}M`;
            return `$${marketCap.toFixed(0)}`;
        }
    },

    setupMarketSelector() {
        const marketSelect = document.getElementById('market-select');
        const symbolInput = document.getElementById('analysis-symbol');
        
        if (marketSelect) {
            marketSelect.addEventListener('change', (e) => {
                this.selectedMarket = e.target.value;
                this.currentCurrency = e.target.value === 'IN' ? 'INR' : 'USD';
                
                // Update UI theme
                this.updateMarketTheme();
                
                // Update symbol input placeholder
                if (symbolInput) {
                    if (this.selectedMarket === 'IN') {
                        symbolInput.placeholder = 'Enter Indian stock (e.g., RELIANCE, TCS, HDFCBANK)';
                    } else {
                        symbolInput.placeholder = 'Enter US stock (e.g., AAPL, MSFT, GOOGL)';
                    }
                }
                
                // Update default currency displays
                this.updateDefaultCurrencyDisplays();
                
                // Clear current analysis when switching markets
                if (this.currentSymbol) {
                    this.clearAnalysis();
                }
                
                // Update market status
                this.updateMarketStatus();
                
                console.log(`Market changed to: ${this.selectedMarket}`);
            });
        }
        
        // Setup symbol suggestions
        this.setupSymbolSuggestions();
        
        // Setup market status
        this.updateMarketStatus();
        
        // Initialize default currency displays
        this.updateDefaultCurrencyDisplays();
    },

    updateMarketTheme() {
        const body = document.body;
        
        if (this.selectedMarket === 'IN') {
            body.classList.add('indian-market');
        } else {
            body.classList.remove('indian-market');
        }
    },

    updateDefaultCurrencyDisplays() {
        const currencySymbol = this.currentCurrency === 'INR' ? '₹' : '$';
        
        // Update default price display
        const currentPriceEl = document.getElementById('current-price');
        if (currentPriceEl && currentPriceEl.textContent.includes('--')) {
            currentPriceEl.textContent = `${currencySymbol}--`;
        }
        
        // Update default range displays
        const dayRangeEl = document.getElementById('day-range');
        if (dayRangeEl && dayRangeEl.textContent.includes('$')) {
            dayRangeEl.textContent = `${currencySymbol}-- - ${currencySymbol}--`;
        }
        
        const weekRangeEl = document.getElementById('week-range');
        if (weekRangeEl && weekRangeEl.textContent.includes('$')) {
            weekRangeEl.textContent = `${currencySymbol}-- - ${currencySymbol}--`;
        }
    },

    setupSymbolSuggestions() {
        const symbolInput = document.getElementById('analysis-symbol');
        const suggestionsDiv = document.getElementById('symbol-suggestions');
        
        if (!symbolInput || !suggestionsDiv) return;
        
        let suggestionTimeout;
        
        symbolInput.addEventListener('input', (e) => {
            const query = e.target.value.trim().toUpperCase();
            
            clearTimeout(suggestionTimeout);
            
            if (query.length < 2) {
                this.hideSuggestions();
                return;
            }
            
            suggestionTimeout = setTimeout(() => {
                this.showSymbolSuggestions(query);
            }, 300);
        });
        
        // Hide suggestions when clicking outside
        document.addEventListener('click', (e) => {
            if (!symbolInput.contains(e.target) && !suggestionsDiv.contains(e.target)) {
                this.hideSuggestions();
            }
        });
    },

    showSymbolSuggestions(query) {
        const suggestionsDiv = document.getElementById('symbol-suggestions');
        if (!suggestionsDiv) return;
        
        const suggestions = this.getSymbolSuggestions(query);
        
        if (suggestions.length === 0) {
            this.hideSuggestions();
            return;
        }
        
        suggestionsDiv.innerHTML = suggestions.map(suggestion => `
            <div class="suggestion-item" data-symbol="${suggestion.symbol}">
                <div class="suggestion-main">
                    <span class="suggestion-symbol">${suggestion.symbol}</span>
                    <span class="suggestion-name">${suggestion.name}</span>
                </div>
                <span class="suggestion-exchange ${suggestion.exchange.toLowerCase()}">${suggestion.exchange}</span>
            </div>
        `).join('');
        
        // Add click handlers
        suggestionsDiv.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                const symbol = item.dataset.symbol;
                document.getElementById('analysis-symbol').value = symbol;
                this.hideSuggestions();
                this.analyzeSymbol();
            });
        });
        
        suggestionsDiv.classList.add('show');
    },

    hideSuggestions() {
        const suggestionsDiv = document.getElementById('symbol-suggestions');
        if (suggestionsDiv) {
            suggestionsDiv.classList.remove('show');
        }
    },

    getSymbolSuggestions(query) {
        if (this.selectedMarket === 'IN') {
            return this.getIndianStockSuggestions(query);
        } else {
            return this.getUSStockSuggestions(query);
        }
    },

    getIndianStockSuggestions(query) {
        const indianStocks = [
            // Banking & Financial Services
            { symbol: 'HDFCBANK', name: 'HDFC Bank Ltd', exchange: 'NSE' },
            { symbol: 'ICICIBANK', name: 'ICICI Bank Ltd', exchange: 'NSE' },
            { symbol: 'SBIN', name: 'State Bank of India', exchange: 'NSE' },
            { symbol: 'KOTAKBANK', name: 'Kotak Mahindra Bank', exchange: 'NSE' },
            { symbol: 'AXISBANK', name: 'Axis Bank Ltd', exchange: 'NSE' },
            { symbol: 'BAJFINANCE', name: 'Bajaj Finance Ltd', exchange: 'NSE' },
            
            // Technology
            { symbol: 'TCS', name: 'Tata Consultancy Services', exchange: 'NSE' },
            { symbol: 'INFY', name: 'Infosys Ltd', exchange: 'NSE' },
            { symbol: 'WIPRO', name: 'Wipro Ltd', exchange: 'NSE' },
            { symbol: 'HCLTECH', name: 'HCL Technologies Ltd', exchange: 'NSE' },
            { symbol: 'TECHM', name: 'Tech Mahindra Ltd', exchange: 'NSE' },
            
            // Conglomerates & Energy
            { symbol: 'RELIANCE', name: 'Reliance Industries Ltd', exchange: 'NSE' },
            { symbol: 'ADANIPORTS', name: 'Adani Ports & SEZ Ltd', exchange: 'NSE' },
            { symbol: 'ONGC', name: 'Oil & Natural Gas Corp', exchange: 'NSE' },
            
            // Consumer Goods
            { symbol: 'HINDUNILVR', name: 'Hindustan Unilever Ltd', exchange: 'NSE' },
            { symbol: 'ITC', name: 'ITC Ltd', exchange: 'NSE' },
            { symbol: 'NESTLEIND', name: 'Nestle India Ltd', exchange: 'NSE' },
            { symbol: 'BRITANNIA', name: 'Britannia Industries Ltd', exchange: 'NSE' },
            
            // Automotive
            { symbol: 'MARUTI', name: 'Maruti Suzuki India Ltd', exchange: 'NSE' },
            { symbol: 'M&M', name: 'Mahindra & Mahindra Ltd', exchange: 'NSE' },
            { symbol: 'TATAMOTORS', name: 'Tata Motors Ltd', exchange: 'NSE' },
            { symbol: 'BAJAJ-AUTO', name: 'Bajaj Auto Ltd', exchange: 'NSE' },
            
            // Infrastructure & Construction
            { symbol: 'LT', name: 'Larsen & Toubro Ltd', exchange: 'NSE' },
            { symbol: 'ULTRACEMCO', name: 'UltraTech Cement Ltd', exchange: 'NSE' },
            
            // Telecom
            { symbol: 'BHARTIARTL', name: 'Bharti Airtel Ltd', exchange: 'NSE' },
            
            // Retail & Consumer
            { symbol: 'TITAN', name: 'Titan Company Ltd', exchange: 'NSE' },
            { symbol: 'ASIANPAINT', name: 'Asian Paints Ltd', exchange: 'NSE' },
            
            // Pharmaceuticals
            { symbol: 'SUNPHARMA', name: 'Sun Pharmaceutical Industries', exchange: 'NSE' },
            { symbol: 'DRREDDY', name: 'Dr Reddys Laboratories Ltd', exchange: 'NSE' },
            
            // Metals & Mining
            { symbol: 'TATASTEEL', name: 'Tata Steel Ltd', exchange: 'NSE' },
            { symbol: 'HINDALCO', name: 'Hindalco Industries Ltd', exchange: 'NSE' }
        ];
        
        return indianStocks.filter(stock => 
            stock.symbol.includes(query) || 
            stock.name.toUpperCase().includes(query)
        ).slice(0, 8);
    },

    getUSStockSuggestions(query) {
        const usStocks = [
            { symbol: 'AAPL', name: 'Apple Inc', exchange: 'NASDAQ' },
            { symbol: 'MSFT', name: 'Microsoft Corp', exchange: 'NASDAQ' },
            { symbol: 'GOOGL', name: 'Alphabet Inc', exchange: 'NASDAQ' },
            { symbol: 'AMZN', name: 'Amazon.com Inc', exchange: 'NASDAQ' },
            { symbol: 'TSLA', name: 'Tesla Inc', exchange: 'NASDAQ' },
            { symbol: 'META', name: 'Meta Platforms Inc', exchange: 'NASDAQ' },
            { symbol: 'NVDA', name: 'NVIDIA Corp', exchange: 'NASDAQ' },
            { symbol: 'NFLX', name: 'Netflix Inc', exchange: 'NASDAQ' },
            { symbol: 'JPM', name: 'JPMorgan Chase & Co', exchange: 'NYSE' },
            { symbol: 'JNJ', name: 'Johnson & Johnson', exchange: 'NYSE' },
            { symbol: 'V', name: 'Visa Inc', exchange: 'NYSE' },
            { symbol: 'PG', name: 'Procter & Gamble Co', exchange: 'NYSE' },
            { symbol: 'UNH', name: 'UnitedHealth Group Inc', exchange: 'NYSE' },
            { symbol: 'HD', name: 'Home Depot Inc', exchange: 'NYSE' },
            { symbol: 'MA', name: 'Mastercard Inc', exchange: 'NYSE' }
        ];
        
        return usStocks.filter(stock => 
            stock.symbol.includes(query) || 
            stock.name.toUpperCase().includes(query)
        ).slice(0, 8);
    },

    clearAnalysis() {
        this.currentSymbol = null;
        this.currentData = null;
        
        // Clear charts
        const chartIds = ['analysis-chart', 'rsi-chart', 'volume-chart', 'macd-chart', 'stochastic-chart'];
        chartIds.forEach(id => this.clearChart(id));
        
        // Reset stock overview
        document.getElementById('current-symbol').textContent = '--';
        document.getElementById('current-stock-name').textContent = 'Select a symbol';
        document.getElementById('current-price').textContent = this.currentCurrency === 'INR' ? '₹--' : '$--';
        document.getElementById('price-change').textContent = '--';
        
        // Update range displays with correct currency
        const currencySymbol = this.currentCurrency === 'INR' ? '₹' : '$';
        document.getElementById('day-range').textContent = `${currencySymbol}-- - ${currencySymbol}--`;
        document.getElementById('week-range').textContent = `${currencySymbol}-- - ${currencySymbol}--`;
        
        // Hide AI analysis
        this.hideAIError();
        this.hideAILoading();
        const resultsDiv = document.getElementById('ai-analysis-results');
        if (resultsDiv) {
            resultsDiv.style.display = 'none';
        }
    },

    updateMarketStatus() {
        const statusDot = document.getElementById('market-status-dot');
        const statusText = document.getElementById('market-status-text');
        
        if (!statusDot || !statusText) return;
        
        const now = new Date();
        const currentHour = now.getHours();
        const currentMinute = now.getMinutes();
        const currentTime = currentHour * 60 + currentMinute;
        
        let isOpen = false;
        let statusMessage = '';
        
        if (this.selectedMarket === 'IN') {
            // Indian market hours: 9:15 AM - 3:30 PM IST (Monday-Friday)
            const marketOpen = 9 * 60 + 15; // 9:15 AM
            const marketClose = 15 * 60 + 30; // 3:30 PM
            
            const isWeekday = now.getDay() >= 1 && now.getDay() <= 5;
            isOpen = isWeekday && currentTime >= marketOpen && currentTime <= marketClose;
            
            if (isOpen) {
                statusMessage = 'NSE/BSE Open';
            } else if (isWeekday && currentTime < marketOpen) {
                const minutesToOpen = marketOpen - currentTime;
                const hoursToOpen = Math.floor(minutesToOpen / 60);
                const minsToOpen = minutesToOpen % 60;
                statusMessage = `Opens in ${hoursToOpen}h ${minsToOpen}m`;
            } else if (isWeekday && currentTime > marketClose) {
                statusMessage = 'NSE/BSE Closed';
            } else {
                statusMessage = 'Weekend - Closed';
            }
        } else {
            // US market hours: 9:30 AM - 4:00 PM EST (Monday-Friday)
            const marketOpen = 9 * 60 + 30; // 9:30 AM
            const marketClose = 16 * 60; // 4:00 PM
            
            const isWeekday = now.getDay() >= 1 && now.getDay() <= 5;
            isOpen = isWeekday && currentTime >= marketOpen && currentTime <= marketClose;
            
            if (isOpen) {
                statusMessage = 'NYSE/NASDAQ Open';
            } else if (isWeekday && currentTime < marketOpen) {
                const minutesToOpen = marketOpen - currentTime;
                const hoursToOpen = Math.floor(minutesToOpen / 60);
                const minsToOpen = minutesToOpen % 60;
                statusMessage = `Opens in ${hoursToOpen}h ${minsToOpen}m`;
            } else if (isWeekday && currentTime > marketClose) {
                statusMessage = 'NYSE/NASDAQ Closed';
            } else {
                statusMessage = 'Weekend - Closed';
            }
        }
        
        statusDot.className = `market-status-dot ${isOpen ? '' : 'closed'}`;
        statusText.textContent = statusMessage;
        
        // Update every minute
        setTimeout(() => this.updateMarketStatus(), 60000);
    }
};

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    Analysis.init();
});

// Export for global access
window.Analysis = Analysis; 