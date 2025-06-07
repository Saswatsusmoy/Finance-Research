/* ==========================================
   CHART RENDERING MODULE
   Handle all chart creation and updates
   ========================================== */

class ChartManager {
    constructor() {
        this.charts = new Map();
        this.defaultColors = this.getEnhancedChartColors();
        this.chartConfig = {
            displayModeBar: false,
            responsive: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
            doubleClick: 'reset+autosize'
        };
    }

    // Enhanced color scheme for better visual appeal
    getEnhancedChartColors() {
        return {
            primary: '#00d2ff',
            secondary: '#3a7bd5',
            success: '#10b981',
            danger: '#ef4444',
            warning: '#f59e0b',
            purple: '#8b5cf6',
            pink: '#ec4899',
            teal: '#14b8a6',
            orange: '#f97316',
            background: 'rgba(15, 23, 42, 0.8)',
            grid: 'rgba(148, 163, 184, 0.1)',
            text: '#e2e8f0',
            cardBg: 'rgba(30, 41, 59, 0.8)',
            gradient: {
                primary: 'linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%)',
                success: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                danger: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'
            }
        };
    }

    // Enhanced layout configuration
    getEnhancedLayout(title, height = 400) {
        return {
            title: {
                text: title,
                font: { 
                    size: 18, 
                    color: this.defaultColors.text, 
                    family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif' 
                },
                x: 0.02,
                y: 0.98
            },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { 
                color: this.defaultColors.text, 
                family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
                size: 12
            },
            xaxis: {
                gridcolor: this.defaultColors.grid,
                showgrid: true,
                color: this.defaultColors.text,
                tickformat: '%Y-%m-%d',
                showline: true,
                linecolor: this.defaultColors.grid,
                mirror: true,
                tickfont: { size: 11 }
            },
            yaxis: {
                gridcolor: this.defaultColors.grid,
                showgrid: true,
                color: this.defaultColors.text,
                showline: true,
                linecolor: this.defaultColors.grid,
                mirror: true,
                tickfont: { size: 11 }
            },
            margin: { t: 50, r: 30, b: 50, l: 60 },
            height: height,
            legend: {
                orientation: 'h',
                yanchor: 'bottom',
                y: -0.2,
                xanchor: 'center',
                x: 0.5,
                bgcolor: 'rgba(0,0,0,0.3)',
                bordercolor: this.defaultColors.grid,
                borderwidth: 1,
                font: { size: 11 }
            },
            hovermode: 'x unified',
            hoverlabel: {
                bgcolor: 'rgba(0,0,0,0.9)',
                bordercolor: this.defaultColors.primary,
                font: { color: 'white', size: 12 },
                borderwidth: 2
            },
            transition: {
                duration: 500,
                easing: 'cubic-in-out'
            }
        };
    }

    // Main chart rendering for analysis page
    async renderAnalysisChart(symbol, data, indicators = []) {
        console.log('renderAnalysisChart called with:', { symbol, data, indicators });
        
        // Check if Plotly is available
        if (typeof Plotly === 'undefined') {
            console.error('Plotly is not loaded! Waiting for it to load...');
            // Wait for Plotly to load
            let attempts = 0;
            while (typeof Plotly === 'undefined' && attempts < 10) {
                await new Promise(resolve => setTimeout(resolve, 500));
                attempts++;
            }
            
            if (typeof Plotly === 'undefined') {
                console.error('Plotly failed to load after waiting');
                this.showChartError('analysis-chart', 'Chart library failed to load');
                return;
            }
        }
        
        const chartContainer = document.getElementById('analysis-chart');
        if (!chartContainer) {
            console.error('Chart container not found!');
            this.showChartError('analysis-chart', 'Chart container not found');
            return;
        }
        
        if (!data || !data.data || data.data.length === 0) {
            console.error('No data available for chart');
            this.showChartError('analysis-chart', 'No data available for chart');
            return;
        }

        try {
            // Get current currency from Analysis module
            let currentCurrency = 'USD';
            if (window.Analysis) {
                currentCurrency = window.Analysis.currentCurrency || 'USD';
            }
            const currencySymbol = currentCurrency === 'INR' ? '₹' : '$';
            
            const traces = [];
            const historicalData = data.data;

            // Enhanced candlestick chart
            const priceTrace = {
                x: historicalData.map(d => d.date),
                open: historicalData.map(d => d.open),
                high: historicalData.map(d => d.high),
                low: historicalData.map(d => d.low),
                close: historicalData.map(d => d.close),
                type: 'candlestick',
                name: symbol,
                increasing: { 
                    line: { color: this.defaultColors.success, width: 1.5 },
                    fillcolor: this.defaultColors.success
                },
                decreasing: { 
                    line: { color: this.defaultColors.danger, width: 1.5 },
                    fillcolor: this.defaultColors.danger
                },
                showlegend: false,
                hovertemplate: '<b>%{x}</b><br>' +
                              'Open: %{open:.2f}<br>' +
                              'High: %{high:.2f}<br>' +
                              'Low: %{low:.2f}<br>' +
                              'Close: %{close:.2f}<extra></extra>'
            };
            traces.push(priceTrace);

            // Add technical indicators with enhanced styling
            if (indicators.includes('ma')) {
                const closes = historicalData.map(d => d.close);
                const sma20 = Utils.calculateSMA(closes, 20);
                const sma50 = Utils.calculateSMA(closes, 50);

                // SMA 20 with gradient effect
                traces.push({
                    x: historicalData.slice(19).map(d => d.date),
                    y: sma20,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'SMA 20',
                    line: { 
                        color: this.defaultColors.warning, 
                        width: 2,
                        shape: 'spline',
                        smoothing: 0.3
                    },
                    hovertemplate: `<b>SMA 20</b><br>%{x}<br>${currencySymbol}%{y:.2f}<extra></extra>`
                });

                // SMA 50 with enhanced styling
                traces.push({
                    x: historicalData.slice(49).map(d => d.date),
                    y: sma50,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'SMA 50',
                    line: { 
                        color: this.defaultColors.purple, 
                        width: 2,
                        shape: 'spline',
                        smoothing: 0.3,
                        dash: 'dash'
                    },
                    hovertemplate: `<b>SMA 50</b><br>%{x}<br>${currencySymbol}%{y:.2f}<extra></extra>`
                });
            }

            if (indicators.includes('bollinger')) {
                const closes = historicalData.map(d => d.close);
                const bollingerBands = this.calculateBollingerBands(closes, 20, 2);
                
                // Upper band
                traces.push({
                    x: historicalData.slice(19).map(d => d.date),
                    y: bollingerBands.upper,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'BB Upper',
                    line: { 
                        color: this.defaultColors.secondary, 
                        width: 1.5, 
                        dash: 'dot' 
                    },
                    fill: 'tonexty',
                    fillcolor: 'rgba(58, 123, 213, 0.08)',
                    hovertemplate: `<b>BB Upper</b><br>%{x}<br>${currencySymbol}%{y:.2f}<extra></extra>`
                });

                // Lower band
                traces.push({
                    x: historicalData.slice(19).map(d => d.date),
                    y: bollingerBands.lower,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'BB Lower',
                    line: { 
                        color: this.defaultColors.secondary, 
                        width: 1.5, 
                        dash: 'dot' 
                    },
                    hovertemplate: `<b>BB Lower</b><br>%{x}<br>${currencySymbol}%{y:.2f}<extra></extra>`
                });
            }

            if (indicators.includes('vwap')) {
                const prices = historicalData.map(d => (d.high + d.low + d.close) / 3);
                const volumes = historicalData.map(d => d.volume);
                const vwap = [];
                
                for (let i = 0; i < prices.length; i++) {
                    vwap.push(Utils.calculateVWAP(prices.slice(0, i + 1), volumes.slice(0, i + 1)));
                }

                traces.push({
                    x: historicalData.map(d => d.date),
                    y: vwap,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'VWAP',
                    line: { 
                        color: this.defaultColors.teal, 
                        width: 2.5,
                        shape: 'spline',
                        smoothing: 0.2
                    },
                    hovertemplate: `<b>VWAP</b><br>%{x}<br>${currencySymbol}%{y:.2f}<extra></extra>`
                });
            }

            const layout = this.getEnhancedLayout(`${symbol} Price Analysis`, 450);
            layout.yaxis.title = `Price (${currencySymbol})`;

            await Plotly.newPlot('analysis-chart', traces, layout, this.chartConfig);
            this.charts.set('analysis-chart', { traces, layout });
            
            // Add chart animations
            this.addChartAnimations('analysis-chart');
            
            // Clear any residual loading indicators
            this.clearLoadingIndicators('analysis-chart');

        } catch (error) {
            console.error('Error rendering analysis chart:', error);
            this.showChartError('analysis-chart', 'Error rendering chart');
        }
    }

    // Enhanced RSI indicator chart
    async renderRSIChart(symbol, data) {
        const chartContainer = document.getElementById('rsi-chart');
        if (!chartContainer || !data || !data.data || data.data.length === 0) {
            this.showChartError('rsi-chart', 'No data for RSI');
            return;
        }

        try {
            const historicalData = data.data;
            const closes = historicalData.map(d => d.close);
            const rsi = Utils.calculateRSI(closes, 14);

            const traces = [{
                x: historicalData.slice(14).map(d => d.date),
                y: rsi,
                type: 'scatter',
                mode: 'lines',
                name: 'RSI',
                line: { 
                    color: this.defaultColors.purple, 
                    width: 2.5,
                    shape: 'spline',
                    smoothing: 0.3
                },
                fill: 'tonexty',
                fillcolor: 'rgba(139, 92, 246, 0.1)',
                hovertemplate: '<b>RSI</b><br>%{x}<br>%{y:.1f}<extra></extra>'
            }];

            const layout = this.getEnhancedLayout(`${symbol} RSI`, 250);
            layout.yaxis.title = 'RSI';
            layout.yaxis.range = [0, 100];
            
            // Add reference lines
            layout.shapes = [
                {
                    type: 'line',
                    x0: historicalData[14].date,
                    y0: 70,
                    x1: historicalData[historicalData.length - 1].date,
                    y1: 70,
                    line: { color: this.defaultColors.danger, width: 1.5, dash: 'dash' }
                },
                {
                    type: 'line',
                    x0: historicalData[14].date,
                    y0: 30,
                    x1: historicalData[historicalData.length - 1].date,
                    y1: 30,
                    line: { color: this.defaultColors.success, width: 1.5, dash: 'dash' }
                },
                {
                    type: 'line',
                    x0: historicalData[14].date,
                    y0: 50,
                    x1: historicalData[historicalData.length - 1].date,
                    y1: 50,
                    line: { color: this.defaultColors.text, width: 1, dash: 'dot' }
                }
            ];

            // Add annotations for overbought/oversold levels
            layout.annotations = [
                {
                    x: historicalData[Math.floor(historicalData.length * 0.8)].date,
                    y: 75,
                    text: 'Overbought',
                    showarrow: false,
                    font: { color: this.defaultColors.danger, size: 10 }
                },
                {
                    x: historicalData[Math.floor(historicalData.length * 0.8)].date,
                    y: 25,
                    text: 'Oversold',
                    showarrow: false,
                    font: { color: this.defaultColors.success, size: 10 }
                }
            ];

            await Plotly.newPlot('rsi-chart', traces, layout, this.chartConfig);
            this.charts.set('rsi-chart', { traces, layout });
            
            this.addChartAnimations('rsi-chart');

        } catch (error) {
            console.error('Error rendering RSI chart:', error);
            this.showChartError('rsi-chart', 'Error rendering RSI chart');
        }
    }

    // Enhanced Volume chart
    async renderVolumeChart(symbol, data) {
        const chartContainer = document.getElementById('volume-chart');
        if (!chartContainer || !data || !data.data || data.data.length === 0) {
            this.showChartError('volume-chart', 'No data for Volume');
            return;
        }

        try {
            const historicalData = data.data;

            // Color code volume bars based on price movement
            const volumeColors = historicalData.map(d => {
                return d.close >= d.open ? 
                    'rgba(16, 185, 129, 0.7)' : 
                    'rgba(239, 68, 68, 0.7)';
            });

            const traces = [{
                x: historicalData.map(d => d.date),
                y: historicalData.map(d => d.volume),
                type: 'bar',
                name: 'Volume',
                marker: {
                    color: volumeColors,
                    line: { width: 0 }
                },
                hovertemplate: '<b>Volume</b><br>%{x}<br>%{y:,.0f}<extra></extra>'
            }];

            const layout = this.getEnhancedLayout(`${symbol} Volume`, 250);
            layout.yaxis.title = 'Volume';
            layout.bargap = 0.1;

            await Plotly.newPlot('volume-chart', traces, layout, this.chartConfig);
            this.charts.set('volume-chart', { traces, layout });
            
            this.addChartAnimations('volume-chart');

        } catch (error) {
            console.error('Error rendering volume chart:', error);
            this.showChartError('volume-chart', 'Error rendering volume chart');
        }
    }

    // Enhanced MACD chart
    async renderMACDChart(symbol, data) {
        const chartContainer = document.getElementById('macd-chart');
        if (!chartContainer || !data || !data.data || data.data.length === 0) {
            this.showChartError('macd-chart', 'No data for MACD');
            return;
        }

        try {
            const historicalData = data.data;
            const closes = historicalData.map(d => d.close);
            
            console.log(`MACD Chart Debug - Symbol: ${symbol}, Data points: ${closes.length}`);
            
            // Validate data
            if (closes.length < 26) {
                console.warn(`Insufficient data for MACD: ${closes.length} points, need at least 26`);
                this.showChartError('macd-chart', `Insufficient data for MACD calculation (${closes.length} points, need 26+)`);
                return;
            }

            const macdData = Utils.calculateMACD(closes);
            console.log('MACD Data calculated:', {
                macdLineLength: macdData.macdLine.length,
                signalLineLength: macdData.signalLine.length,
                histogramLength: macdData.histogram.length
            });
            
            // Check if MACD calculation was successful
            if (!macdData || !macdData.macdLine || macdData.macdLine.length === 0) {
                console.error('MACD calculation failed:', macdData);
                this.showChartError('macd-chart', 'MACD calculation failed');
                return;
            }

            const traces = [];

            // Prepare data arrays with proper alignment
            const validIndices = [];
            const macdValues = [];
            const signalValues = [];
            const histogramValues = [];
            const dates = [];

            for (let i = 0; i < macdData.macdLine.length; i++) {
                if (macdData.macdLine[i] !== undefined) {
                    validIndices.push(i);
                    macdValues.push(macdData.macdLine[i]);
                    dates.push(historicalData[i].date);
                    
                    if (macdData.signalLine[i] !== undefined) {
                        signalValues.push(macdData.signalLine[i]);
                    }
                    
                    if (macdData.histogram[i] !== undefined) {
                        histogramValues.push(macdData.histogram[i]);
                    }
                }
            }

            console.log('MACD Chart Data prepared:', {
                macdValues: macdValues.length,
                signalValues: signalValues.length,
                histogramValues: histogramValues.length,
                dates: dates.length
            });

            // Enhanced Histogram with gradient colors
            if (histogramValues.length > 0) {
                const histogramColors = histogramValues.map(val => 
                    val >= 0 ? 'rgba(16, 185, 129, 0.8)' : 'rgba(239, 68, 68, 0.8)'
                );

                const histogramDates = [];
                let histIndex = 0;
                for (let i = 0; i < macdData.histogram.length; i++) {
                    if (macdData.histogram[i] !== undefined) {
                        histogramDates.push(historicalData[i].date);
                    }
                }

            traces.push({
                    x: histogramDates,
                    y: histogramValues,
                    type: 'bar',
                    name: 'MACD Histogram',
                    marker: {
                        color: histogramColors,
                        line: { width: 0 }
                    },
                    hovertemplate: '<b>Histogram</b><br>%{x}<br>%{y:.4f}<extra></extra>'
                });
            }

            // MACD Line with enhanced styling
            if (macdValues.length > 0) {
                traces.push({
                    x: dates,
                    y: macdValues,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'MACD Line',
                    line: { 
                        color: this.defaultColors.primary, 
                        width: 2.5,
                        shape: 'spline',
                        smoothing: 0.3
                    },
                    hovertemplate: '<b>MACD</b><br>%{x}<br>%{y:.4f}<extra></extra>'
                });
            }

            // Signal Line with enhanced styling
            if (signalValues.length > 0) {
                const signalDates = [];
                for (let i = 0; i < macdData.signalLine.length; i++) {
                    if (macdData.signalLine[i] !== undefined) {
                        signalDates.push(historicalData[i].date);
                    }
                }

                traces.push({
                    x: signalDates,
                    y: signalValues,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Signal Line',
                    line: { 
                        color: this.defaultColors.warning, 
                        width: 2,
                        dash: 'dash',
                        shape: 'spline',
                        smoothing: 0.3
                    },
                    hovertemplate: '<b>Signal</b><br>%{x}<br>%{y:.4f}<extra></extra>'
                });
            }

            if (traces.length === 0) {
                console.warn('No traces generated for MACD chart');
                this.showChartError('macd-chart', 'No valid MACD data to display');
                return;
            }

            console.log(`MACD Chart rendering with ${traces.length} traces`);

            const layout = this.getEnhancedLayout(`${symbol} MACD`, 280);
            layout.yaxis.title = 'MACD';
            layout.bargap = 0.1;
            
            // Add zero line if we have valid data
            if (dates.length > 0) {
                layout.shapes = [{
                    type: 'line',
                    x0: dates[0],
                    y0: 0,
                    x1: dates[dates.length - 1],
                    y1: 0,
                    line: { color: this.defaultColors.text, width: 1, dash: 'dot' }
                }];
            }

            await Plotly.newPlot('macd-chart', traces, layout, this.chartConfig);
            this.charts.set('macd-chart', { traces, layout });
            
            this.addChartAnimations('macd-chart');
            console.log('MACD Chart rendered successfully');

        } catch (error) {
            console.error('Error rendering MACD chart:', error);
            this.showChartError('macd-chart', `Error rendering MACD chart: ${error.message}`);
        }
    }

    // Enhanced Stochastic Oscillator chart
    async renderStochasticChart(symbol, data) {
        const chartContainer = document.getElementById('stochastic-chart');
        if (!chartContainer || !data || !data.data || data.data.length === 0) {
            this.showChartError('stochastic-chart', 'No data for Stochastic');
            return;
        }

        try {
            const historicalData = data.data;
            const highs = historicalData.map(d => d.high);
            const lows = historicalData.map(d => d.low);
            const closes = historicalData.map(d => d.close);
            const stochastic = Utils.calculateStochastic(highs, lows, closes);

            const traces = [];

            // Enhanced %K Line with gradient fill
            traces.push({
                x: historicalData.slice(13).map(d => d.date),
                y: stochastic.k,
                type: 'scatter',
                mode: 'lines',
                name: '%K (Fast)',
                line: { 
                    color: this.defaultColors.primary, 
                    width: 2.5,
                    shape: 'spline',
                    smoothing: 0.3
                },
                fill: 'tonexty',
                fillcolor: 'rgba(0, 210, 255, 0.1)',
                hovertemplate: '<b>%K</b><br>%{x}<br>%{y:.1f}%<extra></extra>'
            });

            // Enhanced %D Line
            traces.push({
                x: historicalData.slice(16).map(d => d.date),
                y: stochastic.d,
                type: 'scatter',
                mode: 'lines',
                name: '%D (Slow)',
                line: { 
                    color: this.defaultColors.warning, 
                    width: 2,
                    dash: 'dash',
                    shape: 'spline',
                    smoothing: 0.3
                },
                hovertemplate: '<b>%D</b><br>%{x}<br>%{y:.1f}%<extra></extra>'
            });

            const layout = this.getEnhancedLayout(`${symbol} Stochastic Oscillator`, 280);
            layout.yaxis.title = 'Stochastic %';
            layout.yaxis.range = [0, 100];
            
            // Add reference lines with enhanced styling
            layout.shapes = [
                {
                    type: 'line',
                    x0: historicalData[13].date,
                    y0: 80,
                    x1: historicalData[historicalData.length - 1].date,
                    y1: 80,
                    line: { color: this.defaultColors.danger, width: 1.5, dash: 'dash' }
                },
                {
                    type: 'line',
                    x0: historicalData[13].date,
                    y0: 20,
                    x1: historicalData[historicalData.length - 1].date,
                    y1: 20,
                    line: { color: this.defaultColors.success, width: 1.5, dash: 'dash' }
                },
                {
                    type: 'line',
                    x0: historicalData[13].date,
                    y0: 50,
                    x1: historicalData[historicalData.length - 1].date,
                    y1: 50,
                    line: { color: this.defaultColors.text, width: 1, dash: 'dot' }
                }
            ];

            // Add annotations for overbought/oversold levels
            layout.annotations = [
                {
                    x: historicalData[Math.floor(historicalData.length * 0.8)].date,
                    y: 85,
                    text: 'Overbought',
                    showarrow: false,
                    font: { color: this.defaultColors.danger, size: 10 }
                },
                {
                    x: historicalData[Math.floor(historicalData.length * 0.8)].date,
                    y: 15,
                    text: 'Oversold',
                    showarrow: false,
                    font: { color: this.defaultColors.success, size: 10 }
                }
            ];

            await Plotly.newPlot('stochastic-chart', traces, layout, this.chartConfig);
            this.charts.set('stochastic-chart', { traces, layout });
            
            this.addChartAnimations('stochastic-chart');

        } catch (error) {
            console.error('Error rendering Stochastic chart:', error);
            this.showChartError('stochastic-chart', 'Error rendering Stochastic chart');
        }
    }

    // Update stock overview section
    updateStockOverview(symbol, data) {
        try {
            const currentData = data.data[data.data.length - 1];
            const previousData = data.data[data.data.length - 2];
            const change = currentData.close - previousData.close;
            const changePercent = (change / previousData.close) * 100;

            // Get current market and currency from Analysis module
            let currentCurrency = 'USD';
            let selectedMarket = 'US';
            
            if (window.Analysis) {
                currentCurrency = window.Analysis.currentCurrency || 'USD';
                selectedMarket = window.Analysis.selectedMarket || 'US';
            }

            // Calculate ranges
            const dayHigh = currentData.high;
            const dayLow = currentData.low;
            const highs = data.data.map(d => d.high);
            const lows = data.data.map(d => d.low);
            const high52w = Math.max(...highs);
            const low52w = Math.min(...lows);
            const currentVolume = currentData.volume;

            // Update stock overview elements
            const symbolElement = document.getElementById('current-symbol');
            symbolElement.textContent = symbol.toUpperCase();
            
            // Add exchange badge for Indian stocks
            const existingBadge = symbolElement.querySelector('.exchange-badge');
            if (existingBadge) existingBadge.remove();
            
            if (selectedMarket === 'IN') {
                const exchangeBadge = document.createElement('span');
                exchangeBadge.className = 'exchange-badge nse';
                exchangeBadge.textContent = 'NSE';
                symbolElement.appendChild(exchangeBadge);
            }
            
            document.getElementById('current-stock-name').textContent = this.getCompanyName(symbol);
            
            document.getElementById('current-price').textContent = Utils.formatCurrency(currentData.close, 2, currentCurrency);
            
            const priceChangeEl = document.getElementById('price-change');
            priceChangeEl.textContent = `${change >= 0 ? '+' : ''}${Utils.formatCurrency(change, 2, currentCurrency)} (${changePercent >= 0 ? '+' : ''}${changePercent.toFixed(2)}%)`;
            priceChangeEl.className = `price-change ${change >= 0 ? 'positive' : 'negative'}`;

            document.getElementById('day-range').textContent = `${Utils.formatCurrency(dayLow, 2, currentCurrency)} - ${Utils.formatCurrency(dayHigh, 2, currentCurrency)}`;
            document.getElementById('week-range').textContent = `${Utils.formatCurrency(low52w, 2, currentCurrency)} - ${Utils.formatCurrency(high52w, 2, currentCurrency)}`;
            document.getElementById('current-volume').textContent = Utils.formatVolume(currentVolume);
            document.getElementById('market-cap').textContent = this.calculateMarketCap(currentData.close, currentCurrency);
        } catch (error) {
            console.error('Error updating stock overview:', error);
        }
    }

    // Get company name (simplified mapping)
    getCompanyName(symbol) {
        const companyNames = {
            // US Companies
            'AAPL': 'Apple Inc.',
            'GOOGL': 'Alphabet Inc.',
            'MSFT': 'Microsoft Corporation',
            'AMZN': 'Amazon.com Inc.',
            'TSLA': 'Tesla Inc.',
            'META': 'Meta Platforms Inc.',
            'NVDA': 'NVIDIA Corporation',
            'NFLX': 'Netflix Inc.',
            'SPY': 'SPDR S&P 500 ETF',
            'QQQ': 'Invesco QQQ Trust',
            'IWM': 'iShares Russell 2000 ETF',
            'JPM': 'JPMorgan Chase & Co',
            'JNJ': 'Johnson & Johnson',
            'V': 'Visa Inc',
            'PG': 'Procter & Gamble Co',
            'UNH': 'UnitedHealth Group Inc',
            'HD': 'Home Depot Inc',
            'MA': 'Mastercard Inc',
            
            // Indian Companies
            'RELIANCE': 'Reliance Industries Ltd',
            'TCS': 'Tata Consultancy Services',
            'HDFCBANK': 'HDFC Bank Ltd',
            'INFY': 'Infosys Ltd',
            'ICICIBANK': 'ICICI Bank Ltd',
            'HINDUNILVR': 'Hindustan Unilever Ltd',
            'ITC': 'ITC Ltd',
            'SBIN': 'State Bank of India',
            'BHARTIARTL': 'Bharti Airtel Ltd',
            'KOTAKBANK': 'Kotak Mahindra Bank',
            'LT': 'Larsen & Toubro Ltd',
            'ASIANPAINT': 'Asian Paints Ltd',
            'MARUTI': 'Maruti Suzuki India Ltd',
            'TITAN': 'Titan Company Ltd',
            'WIPRO': 'Wipro Ltd'
        };
        return companyNames[symbol.toUpperCase()] || `${symbol.toUpperCase()} Corporation`;
    }

    // Calculate market cap (simplified)
    calculateMarketCap(price, currency = 'USD') {
        // This is a simplified calculation - in reality you'd need shares outstanding
        const estimatedShares = 1000000000; // 1B shares as example
        const marketCap = price * estimatedShares;
        
        const currencySymbol = currency === 'INR' ? '₹' : '$';
        
        if (marketCap >= 1e12) {
            return `${currencySymbol}${(marketCap / 1e12).toFixed(2)}T`;
        } else if (marketCap >= 1e9) {
            return `${currencySymbol}${(marketCap / 1e9).toFixed(2)}B`;
        } else if (marketCap >= 1e6) {
            return `${currencySymbol}${(marketCap / 1e6).toFixed(2)}M`;
        }
        return `${currencySymbol}${marketCap.toFixed(0)}`;
    }

    // Update quick analysis
    updateQuickAnalysis(symbol, data, technicalData) {
        try {
            const closes = data.data.map(d => d.close);
            const volumes = data.data.map(d => d.volume);
            
            // Calculate trend
            const trend = this.calculateTrend(closes);
            
            // Calculate momentum using RSI
            const momentum = this.calculateMomentum(technicalData);
            
            // Calculate volatility
            const volatility = this.calculateVolatilityLevel(closes);
            
            // Update trend indicator
            const trendEl = document.getElementById('trend-indicator');
            if (trendEl) {
                trendEl.textContent = trend;
                trendEl.className = `summary-value trend ${trend}`;
            }
            
            // Update momentum indicator
            const momentumEl = document.getElementById('momentum-indicator');
            if (momentumEl) {
                momentumEl.textContent = momentum;
                momentumEl.className = `summary-value momentum ${momentum}`;
            }
            
            // Update volatility indicator
            const volatilityEl = document.getElementById('volatility-indicator');
            if (volatilityEl) {
                volatilityEl.textContent = volatility;
                volatilityEl.className = `summary-value volatility ${volatility}`;
            }
        } catch (error) {
            console.error('Error updating quick analysis:', error);
        }
    }

    // Calculate trend direction
    calculateTrend(prices) {
        if (prices.length < 10) return 'neutral';
        
        const recentPrices = prices.slice(-10);
        const firstHalf = recentPrices.slice(0, 5);
        const secondHalf = recentPrices.slice(5);
        
        const firstAvg = firstHalf.reduce((a, b) => a + b, 0) / firstHalf.length;
        const secondAvg = secondHalf.reduce((a, b) => a + b, 0) / secondHalf.length;
        
        const trendStrength = Math.abs(secondAvg - firstAvg) / firstAvg;
        
        if (trendStrength < 0.02) return 'neutral';
        return secondAvg > firstAvg ? 'bullish' : 'bearish';
    }

    // Calculate momentum from technical data
    calculateMomentum(technicalData) {
        if (!technicalData?.rsi?.current) return 'neutral';
        
        const rsi = technicalData.rsi.current;
        if (rsi > 70) return 'strong';
        if (rsi < 30) return 'weak';
        return 'neutral';
    }

    // Calculate volatility level
    calculateVolatilityLevel(prices) {
        if (prices.length < 20) return 'medium';
        
        const returns = [];
        for (let i = 1; i < prices.length; i++) {
            returns.push((prices[i] - prices[i-1]) / prices[i-1]);
        }
        
        const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length;
        const variance = returns.reduce((sum, ret) => sum + Math.pow(ret - avgReturn, 2), 0) / returns.length;
        const volatility = Math.sqrt(variance) * Math.sqrt(252); // Annualized
        
        if (volatility > 0.3) return 'high';
        if (volatility < 0.15) return 'low';
        return 'medium';
    }

    // Update analysis metrics with comprehensive financial analysis
    updateAnalysisMetrics(symbol, data, technicalData) {
        const metricsContainer = document.getElementById('analysis-metrics');
        if (!metricsContainer) return;

        try {
            // Get current market and currency from Analysis module
            let currentCurrency = 'USD';
            let selectedMarket = 'US';
            
            if (window.Analysis) {
                currentCurrency = window.Analysis.currentCurrency || 'USD';
                selectedMarket = window.Analysis.selectedMarket || 'US';
            }
            const currentData = data.data[data.data.length - 1];
            const previousData = data.data[data.data.length - 2];
            const closes = data.data.map(d => d.close);
            const highs = data.data.map(d => d.high);
            const lows = data.data.map(d => d.low);
            const volumes = data.data.map(d => d.volume);
            
            // Basic Price Metrics
            const change = currentData.close - previousData.close;
            const changePercent = (change / previousData.close) * 100;
            const volume = currentData.volume;
            const high52Week = Math.max(...highs);
            const low52Week = Math.min(...lows);
            
            // Advanced Technical Calculations
            const returns = [];
            for (let i = 1; i < closes.length; i++) {
                returns.push((closes[i] - closes[i-1]) / closes[i-1]);
            }
            
            const volatility = this.calculateStandardDeviation(returns) * Math.sqrt(252) * 100;
            const drawdown = Utils.calculateDrawdown(closes);
            const avgVolume = volumes.reduce((a, b) => a + b, 0) / volumes.length;
            const volumeRatio = volume / avgVolume;
            
            // VWAP Calculation
            const typicalPrices = data.data.map(d => (d.high + d.low + d.close) / 3);
            const vwap = Utils.calculateVWAP(typicalPrices, volumes);
            
            // Price Position Analysis
            const priceFromHigh = ((high52Week - currentData.close) / high52Week) * 100;
            const priceFromLow = ((currentData.close - low52Week) / low52Week) * 100;
            
            // Support and Resistance (Pivot Points)
            const pivots = Utils.calculatePivotPoints(currentData.high, currentData.low, currentData.close);
            
            // Fibonacci Retracements
            const fibonacci = Utils.calculateFibonacciRetracements(high52Week, low52Week);
            
            // Williams %R
            const williamsR = Utils.calculateWilliamsR(highs, lows, closes);
            const currentWilliamsR = williamsR[williamsR.length - 1];
            
            // ATR (Average True Range)
            const atr = Utils.calculateATR(highs, lows, closes);
            const currentATR = atr[atr.length - 1];
            
            // CCI (Commodity Channel Index)
            const cci = Utils.calculateCCI(highs, lows, closes);
            const currentCCI = cci[cci.length - 1];

            const metrics = [
                // Price Information
                { label: 'Current Price', value: Utils.formatCurrency(currentData.close, 2, currentCurrency), category: 'price' },
                { label: 'Daily Change', value: `${change >= 0 ? '+' : ''}${Utils.formatCurrency(change, 2, currentCurrency)}`, class: Utils.getChangeClass(change), category: 'price' },
                { label: 'Daily Change %', value: `${change >= 0 ? '+' : ''}${changePercent.toFixed(2)}%`, class: Utils.getChangeClass(change), category: 'price' },
                { label: '52W High', value: Utils.formatCurrency(high52Week, 2, currentCurrency), category: 'price' },
                { label: '52W Low', value: Utils.formatCurrency(low52Week, 2, currentCurrency), category: 'price' },
                { label: 'Distance from High', value: `${priceFromHigh.toFixed(1)}%`, class: priceFromHigh > 20 ? 'negative' : 'neutral', category: 'price' },
                
                // Volume Analysis
                { label: 'Volume', value: Utils.formatVolume(volume), category: 'volume' },
                { label: 'Avg Volume', value: Utils.formatVolume(avgVolume), category: 'volume' },
                { label: 'Volume Ratio', value: `${volumeRatio.toFixed(2)}x`, class: volumeRatio > 1.5 ? 'positive' : volumeRatio < 0.5 ? 'negative' : 'neutral', category: 'volume' },
                { label: 'VWAP', value: Utils.formatCurrency(vwap, 2, currentCurrency), class: currentData.close > vwap ? 'positive' : 'negative', category: 'volume' },
                
                // Risk Metrics
                { label: 'Volatility (Ann.)', value: `${volatility.toFixed(2)}%`, class: volatility > 30 ? 'negative' : volatility < 15 ? 'positive' : 'neutral', category: 'risk' },
                { label: 'Max Drawdown', value: `${drawdown.maxDrawdown.toFixed(2)}%`, class: 'negative', category: 'risk' },
                { label: 'ATR', value: Utils.formatCurrency(currentATR, 2, currentCurrency), category: 'risk' },
                
                // Technical Indicators
                { label: 'RSI (14)', value: technicalData?.rsi?.current || 'N/A', class: technicalData?.rsi?.current > 70 ? 'negative' : technicalData?.rsi?.current < 30 ? 'positive' : 'neutral', category: 'technical' },
                { label: 'Williams %R', value: `${currentWilliamsR.toFixed(2)}%`, class: currentWilliamsR > -20 ? 'negative' : currentWilliamsR < -80 ? 'positive' : 'neutral', category: 'technical' },
                { label: 'CCI (20)', value: currentCCI.toFixed(2), class: currentCCI > 100 ? 'negative' : currentCCI < -100 ? 'positive' : 'neutral', category: 'technical' },
                
                // Support/Resistance
                { label: 'Pivot Point', value: Utils.formatCurrency(pivots.pivot, 2, currentCurrency), category: 'levels' },
                { label: 'Resistance 1', value: Utils.formatCurrency(pivots.r1, 2, currentCurrency), category: 'levels' },
                { label: 'Support 1', value: Utils.formatCurrency(pivots.s1, 2, currentCurrency), category: 'levels' },
                { label: 'Fib 61.8%', value: Utils.formatCurrency(fibonacci.level_618, 2, currentCurrency), category: 'levels' },
                { label: 'Fib 38.2%', value: Utils.formatCurrency(fibonacci.level_382, 2, currentCurrency), category: 'levels' }
            ];

            // Add moving averages if available
            if (technicalData?.sma) {
                metrics.push(
                    { label: 'SMA 20', value: Utils.formatCurrency(technicalData.sma.sma20, 2, currentCurrency), class: currentData.close > technicalData.sma.sma20 ? 'positive' : 'negative', category: 'technical' },
                    { label: 'SMA 50', value: Utils.formatCurrency(technicalData.sma.sma50, 2, currentCurrency), class: currentData.close > technicalData.sma.sma50 ? 'positive' : 'negative', category: 'technical' }
                );
            }

            // Clear and rebuild metrics display
            metricsContainer.innerHTML = '';
            
            // Group metrics by category
            const categories = {
                'price': 'Price Analysis',
                'volume': 'Volume Analysis', 
                'risk': 'Risk Metrics',
                'technical': 'Technical Indicators',
                'levels': 'Support & Resistance'
            };
            
            Object.keys(categories).forEach(category => {
                const categoryMetrics = metrics.filter(m => m.category === category);
                if (categoryMetrics.length > 0) {
                    const categoryHeader = Utils.createElement('div', 'metrics-category-header');
                    categoryHeader.innerHTML = `<h4>${categories[category]}</h4>`;
                    metricsContainer.appendChild(categoryHeader);
                    
                    categoryMetrics.forEach(metric => {
                        const metricElement = Utils.createElement('div', 'metric-item');
                        metricElement.innerHTML = `
                            <span class="metric-label">${metric.label}</span>
                            <span class="metric-value ${metric.class || ''}">${metric.value}</span>
                        `;
                        metricsContainer.appendChild(metricElement);
                    });
                }
            });

        } catch (error) {
            console.error('Error updating analysis metrics:', error);
            metricsContainer.innerHTML = '<div class="error">Error loading metrics</div>';
        }
    }

    // Mini chart for dashboard cards
    renderMiniChart(elementId, data, changePercent) {
        const element = document.getElementById(elementId);
        if (!element) return;

        try {
            // Generate sample data points for sparkline
            const points = 20;
            const sparklineData = [];
            const baseValue = 100;
            
            for (let i = 0; i < points; i++) {
                const trend = (changePercent / 100) * (i / points);
                const noise = (Math.random() - 0.5) * 0.02;
                sparklineData.push(baseValue * (1 + trend + noise));
            }

            const trace = {
                x: Array.from({length: points}, (_, i) => i),
                y: sparklineData,
                type: 'scatter',
                mode: 'lines',
                line: { 
                    color: parseFloat(changePercent) >= 0 ? this.defaultColors.success : this.defaultColors.danger,
                    width: 2
                },
                showlegend: false,
                hoverinfo: 'none'
            };

            const layout = {
                margin: { t: 0, r: 0, b: 0, l: 0 },
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                xaxis: { visible: false },
                yaxis: { visible: false },
                height: 60
            };

            Plotly.newPlot(elementId, [trace], layout, this.chartConfig);

        } catch (error) {
            console.error(`Error rendering mini chart for ${elementId}:`, error);
        }
    }

    // Main dashboard chart
    async renderMainChart(data, symbol = 'SPY') {
        const chartContainer = document.getElementById('main-chart');
        if (!chartContainer) return;

        try {
            // Get current currency from Analysis module
            let currentCurrency = 'USD';
            if (window.Analysis) {
                currentCurrency = window.Analysis.currentCurrency || 'USD';
            }
            const currencySymbol = currentCurrency === 'INR' ? '₹' : '$';
            const trace = {
                x: data.map(d => d.date),
                y: data.map(d => d.close),
                type: 'scatter',
                mode: 'lines',
                name: symbol,
                line: { color: this.defaultColors.primary, width: 3 },
                fill: 'tonexty',
                fillcolor: 'rgba(0, 210, 255, 0.1)'
            };

            const layout = {
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                font: { color: this.defaultColors.text, family: 'Inter, sans-serif' },
                xaxis: { 
                    gridcolor: this.defaultColors.grid,
                    showgrid: true,
                    color: this.defaultColors.text
                },
                yaxis: { 
                    gridcolor: this.defaultColors.grid,
                    showgrid: true,
                    color: this.defaultColors.text,
                    title: `Price (${currencySymbol})`
                },
                margin: { t: 20, r: 20, b: 40, l: 60 },
                height: 400,
                showlegend: false
            };

            await Plotly.newPlot('main-chart', [trace], layout, this.chartConfig);

        } catch (error) {
            console.error('Error rendering main chart:', error);
            this.showChartError('main-chart', 'Error loading chart');
        }
    }

    // Helper methods
    calculateBollingerBands(prices, period, stdDev) {
        const sma = Utils.calculateSMA(prices, period);
        const bands = { upper: [], lower: [] };

        for (let i = period - 1; i < prices.length; i++) {
            const slice = prices.slice(i - period + 1, i + 1);
            const mean = slice.reduce((a, b) => a + b) / slice.length;
            const variance = slice.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / slice.length;
            const standardDeviation = Math.sqrt(variance);

            bands.upper.push(sma[i - period + 1] + (stdDev * standardDeviation));
            bands.lower.push(sma[i - period + 1] - (stdDev * standardDeviation));
        }

        return bands;
    }

    calculateStandardDeviation(values) {
        const mean = values.reduce((a, b) => a + b, 0) / values.length;
        const variance = values.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / values.length;
        return Math.sqrt(variance);
    }

    showChartError(containerId, message) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="chart-error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Chart Error</h3>
                    <p>${message}</p>
                    <small>Please try refreshing the data or selecting a different symbol.</small>
                </div>
            `;
        }
    }

    showChartLoading(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="chart-loading">
                    <div class="chart-loading-bars">
                        <div class="chart-loading-bar"></div>
                        <div class="chart-loading-bar"></div>
                        <div class="chart-loading-bar"></div>
                        <div class="chart-loading-bar"></div>
                        <div class="chart-loading-bar"></div>
                    </div>
                    <p>Loading chart data...</p>
                </div>
            `;
        }
    }

    // Clear loading indicators from specific chart
    clearLoadingIndicators(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            // Remove loading elements
            const loadingElements = container.querySelectorAll('.chart-loading, .loading-indicator');
            loadingElements.forEach(element => element.remove());
        }
    }

    // Resize all charts
    resizeCharts() {
        this.charts.forEach((chart, id) => {
            Plotly.Plots.resize(id);
        });
    }

    // Add chart animations and enhancements
    addChartAnimations(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            // Add fade-in animation
            container.style.opacity = '0';
            container.style.transform = 'translateY(20px)';
            container.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
            
            // Trigger animation
            setTimeout(() => {
                container.style.opacity = '1';
                container.style.transform = 'translateY(0)';
            }, 100);
            
            // Add hover effects for chart containers
            container.addEventListener('mouseenter', () => {
                container.style.transform = 'translateY(-2px)';
                container.style.boxShadow = '0 12px 35px rgba(0, 0, 0, 0.3)';
            });
            
            container.addEventListener('mouseleave', () => {
                container.style.transform = 'translateY(0)';
                container.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.2)';
            });
        }
    }
}

// Export ChartManager globally
window.ChartManager = ChartManager; 