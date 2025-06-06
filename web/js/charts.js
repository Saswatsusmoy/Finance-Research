/* ==========================================
   CHART RENDERING MODULE
   Handle all chart creation and updates
   ========================================== */

class ChartManager {
    constructor() {
        this.charts = new Map();
        this.defaultColors = Utils.getChartColors('dark');
        this.chartConfig = {
            displayModeBar: false,
            responsive: true,
            displaylogo: false
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
            const traces = [];
            const historicalData = data.data;

            // Main price trace (candlestick or line)
            const priceTrace = {
                x: historicalData.map(d => d.date),
                open: historicalData.map(d => d.open),
                high: historicalData.map(d => d.high),
                low: historicalData.map(d => d.low),
                close: historicalData.map(d => d.close),
                type: 'candlestick',
                name: symbol,
                increasing: { line: { color: this.defaultColors.success } },
                decreasing: { line: { color: this.defaultColors.danger } },
                showlegend: false
            };
            traces.push(priceTrace);

            // Add technical indicators
            if (indicators.includes('ma')) {
                const closes = historicalData.map(d => d.close);
                const sma20 = Utils.calculateSMA(closes, 20);
                const sma50 = Utils.calculateSMA(closes, 50);

                // SMA 20
                traces.push({
                    x: historicalData.slice(19).map(d => d.date),
                    y: sma20,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'SMA 20',
                    line: { color: this.defaultColors.primary, width: 1 }
                });

                // SMA 50
                traces.push({
                    x: historicalData.slice(49).map(d => d.date),
                    y: sma50,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'SMA 50',
                    line: { color: this.defaultColors.warning, width: 1 }
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
                    name: 'Upper BB',
                    line: { color: this.defaultColors.secondary, width: 1, dash: 'dot' },
                    fill: 'tonexty',
                    fillcolor: 'rgba(58, 123, 213, 0.1)'
                });

                // Lower band
                traces.push({
                    x: historicalData.slice(19).map(d => d.date),
                    y: bollingerBands.lower,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Lower BB',
                    line: { color: this.defaultColors.secondary, width: 1, dash: 'dot' }
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
                    line: { color: this.defaultColors.warning, width: 2 }
                });
            }

            const layout = {
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                font: { color: this.defaultColors.text, family: 'Inter, sans-serif' },
                xaxis: {
                    gridcolor: this.defaultColors.grid,
                    showgrid: true,
                    color: this.defaultColors.text,
                    tickformat: '%Y-%m-%d'
                },
                yaxis: {
                    gridcolor: this.defaultColors.grid,
                    showgrid: true,
                    color: this.defaultColors.text,
                    title: 'Price ($)'
                },
                margin: { t: 30, r: 30, b: 50, l: 60 },
                height: 400,
                legend: {
                    x: 0,
                    y: 1,
                    bgcolor: 'rgba(0,0,0,0.5)',
                    bordercolor: this.defaultColors.grid,
                    borderwidth: 1
                }
            };

            await Plotly.newPlot('analysis-chart', traces, layout, this.chartConfig);
            this.charts.set('analysis-chart', { traces, layout });
            
            // Clear any residual loading indicators
            this.clearLoadingIndicators('analysis-chart');

        } catch (error) {
            console.error('Error rendering analysis chart:', error);
            this.showChartError('analysis-chart', 'Error rendering chart');
        }
    }

    // Render RSI indicator chart
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
                line: { color: this.defaultColors.primary, width: 2 }
            }];

            // Add overbought/oversold lines
            traces.push({
                x: historicalData.slice(14).map(d => d.date),
                y: new Array(rsi.length).fill(70),
                type: 'scatter',
                mode: 'lines',
                name: 'Overbought (70)',
                line: { color: this.defaultColors.danger, width: 1, dash: 'dash' }
            });

            traces.push({
                x: historicalData.slice(14).map(d => d.date),
                y: new Array(rsi.length).fill(30),
                type: 'scatter',
                mode: 'lines',
                name: 'Oversold (30)',
                line: { color: this.defaultColors.success, width: 1, dash: 'dash' }
            });

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
                    title: 'RSI',
                    range: [0, 100]
                },
                margin: { t: 30, r: 30, b: 50, l: 60 },
                height: 200,
                showlegend: false
            };

            await Plotly.newPlot('rsi-chart', traces, layout, this.chartConfig);
            this.charts.set('rsi-chart', { traces, layout });
            this.clearLoadingIndicators('rsi-chart');

        } catch (error) {
            console.error('Error rendering RSI chart:', error);
            this.showChartError('rsi-chart', 'Error rendering RSI');
        }
    }

    // Render volume chart
    async renderVolumeChart(symbol, data) {
        const chartContainer = document.getElementById('volume-chart');
        if (!chartContainer || !data || !data.data || data.data.length === 0) {
            this.showChartError('volume-chart', 'No volume data');
            return;
        }

        try {
            const historicalData = data.data;

            const trace = {
                x: historicalData.map(d => d.date),
                y: historicalData.map(d => d.volume),
                type: 'bar',
                name: 'Volume',
                marker: {
                    color: historicalData.map((d, i) => {
                        if (i === 0) return this.defaultColors.primary;
                        return d.close >= historicalData[i-1].close ? 
                            this.defaultColors.success : this.defaultColors.danger;
                    }),
                    opacity: 0.7
                }
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
                    title: 'Volume'
                },
                margin: { t: 30, r: 30, b: 50, l: 60 },
                height: 150,
                showlegend: false
            };

            await Plotly.newPlot('volume-chart', [trace], layout, this.chartConfig);
            this.charts.set('volume-chart', { traces: [trace], layout });
            this.clearLoadingIndicators('volume-chart');

        } catch (error) {
            console.error('Error rendering volume chart:', error);
            this.showChartError('volume-chart', 'Error rendering volume');
        }
    }

    // Render MACD chart
    async renderMACDChart(symbol, data) {
        const chartContainer = document.getElementById('macd-chart');
        if (!chartContainer || !data || !data.data || data.data.length === 0) {
            this.showChartError('macd-chart', 'No data for MACD');
            return;
        }

        try {
            const historicalData = data.data;
            const closes = historicalData.map(d => d.close);
            const macdData = Utils.calculateMACD(closes);

            const traces = [];

            // MACD Line
            traces.push({
                x: historicalData.slice(25).map(d => d.date),
                y: macdData.macdLine.slice(25),
                type: 'scatter',
                mode: 'lines',
                name: 'MACD',
                line: { color: this.defaultColors.primary, width: 2 }
            });

            // Signal Line
            if (macdData.signalLine && macdData.signalLine.length > 0) {
                traces.push({
                    x: historicalData.slice(33).map(d => d.date),
                    y: macdData.signalLine,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Signal',
                    line: { color: this.defaultColors.danger, width: 2 }
                });
            }

            // Histogram
            if (macdData.histogram && macdData.histogram.length > 0) {
                traces.push({
                    x: historicalData.slice(33).map(d => d.date),
                    y: macdData.histogram.slice(8),
                    type: 'bar',
                    name: 'Histogram',
                    marker: {
                        color: macdData.histogram.slice(8).map(val => 
                            val >= 0 ? this.defaultColors.success : this.defaultColors.danger
                        ),
                        opacity: 0.6
                    }
                });
            }

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
                    title: 'MACD'
                },
                margin: { t: 30, r: 30, b: 50, l: 60 },
                height: 200,
                showlegend: true
            };

            await Plotly.newPlot('macd-chart', traces, layout, this.chartConfig);
            this.charts.set('macd-chart', { traces, layout });
            this.clearLoadingIndicators('macd-chart');

        } catch (error) {
            console.error('Error rendering MACD chart:', error);
            this.showChartError('macd-chart', 'Error rendering MACD');
        }
    }

    // Render Stochastic Oscillator chart
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

            // %K Line
            traces.push({
                x: historicalData.slice(13).map(d => d.date),
                y: stochastic.k,
                type: 'scatter',
                mode: 'lines',
                name: '%K',
                line: { color: this.defaultColors.primary, width: 2 }
            });

            // %D Line
            traces.push({
                x: historicalData.slice(16).map(d => d.date),
                y: stochastic.d,
                type: 'scatter',
                mode: 'lines',
                name: '%D',
                line: { color: this.defaultColors.danger, width: 2 }
            });

            // Overbought/Oversold lines
            traces.push({
                x: historicalData.slice(13).map(d => d.date),
                y: new Array(stochastic.k.length).fill(80),
                type: 'scatter',
                mode: 'lines',
                name: 'Overbought (80)',
                line: { color: this.defaultColors.danger, width: 1, dash: 'dash' },
                showlegend: false
            });

            traces.push({
                x: historicalData.slice(13).map(d => d.date),
                y: new Array(stochastic.k.length).fill(20),
                type: 'scatter',
                mode: 'lines',
                name: 'Oversold (20)',
                line: { color: this.defaultColors.success, width: 1, dash: 'dash' },
                showlegend: false
            });

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
                    title: 'Stochastic %',
                    range: [0, 100]
                },
                margin: { t: 30, r: 30, b: 50, l: 60 },
                height: 200,
                showlegend: true
            };

            await Plotly.newPlot('stochastic-chart', traces, layout, this.chartConfig);
            this.charts.set('stochastic-chart', { traces, layout });
            this.clearLoadingIndicators('stochastic-chart');

        } catch (error) {
            console.error('Error rendering Stochastic chart:', error);
            this.showChartError('stochastic-chart', 'Error rendering Stochastic');
        }
    }

    // Update analysis metrics with comprehensive financial analysis
    updateAnalysisMetrics(symbol, data, technicalData) {
        const metricsContainer = document.getElementById('analysis-metrics');
        if (!metricsContainer) return;

        try {
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
                { label: 'Current Price', value: Utils.formatCurrency(currentData.close), category: 'price' },
                { label: 'Daily Change', value: `${change >= 0 ? '+' : ''}${Utils.formatCurrency(change)}`, class: Utils.getChangeClass(change), category: 'price' },
                { label: 'Daily Change %', value: `${change >= 0 ? '+' : ''}${changePercent.toFixed(2)}%`, class: Utils.getChangeClass(change), category: 'price' },
                { label: '52W High', value: Utils.formatCurrency(high52Week), category: 'price' },
                { label: '52W Low', value: Utils.formatCurrency(low52Week), category: 'price' },
                { label: 'Distance from High', value: `${priceFromHigh.toFixed(1)}%`, class: priceFromHigh > 20 ? 'negative' : 'neutral', category: 'price' },
                
                // Volume Analysis
                { label: 'Volume', value: Utils.formatVolume(volume), category: 'volume' },
                { label: 'Avg Volume', value: Utils.formatVolume(avgVolume), category: 'volume' },
                { label: 'Volume Ratio', value: `${volumeRatio.toFixed(2)}x`, class: volumeRatio > 1.5 ? 'positive' : volumeRatio < 0.5 ? 'negative' : 'neutral', category: 'volume' },
                { label: 'VWAP', value: Utils.formatCurrency(vwap), class: currentData.close > vwap ? 'positive' : 'negative', category: 'volume' },
                
                // Risk Metrics
                { label: 'Volatility (Ann.)', value: `${volatility.toFixed(2)}%`, class: volatility > 30 ? 'negative' : volatility < 15 ? 'positive' : 'neutral', category: 'risk' },
                { label: 'Max Drawdown', value: `${drawdown.maxDrawdown.toFixed(2)}%`, class: 'negative', category: 'risk' },
                { label: 'ATR', value: Utils.formatCurrency(currentATR), category: 'risk' },
                
                // Technical Indicators
                { label: 'RSI (14)', value: technicalData?.rsi?.current || 'N/A', class: technicalData?.rsi?.current > 70 ? 'negative' : technicalData?.rsi?.current < 30 ? 'positive' : 'neutral', category: 'technical' },
                { label: 'Williams %R', value: `${currentWilliamsR.toFixed(2)}%`, class: currentWilliamsR > -20 ? 'negative' : currentWilliamsR < -80 ? 'positive' : 'neutral', category: 'technical' },
                { label: 'CCI (20)', value: currentCCI.toFixed(2), class: currentCCI > 100 ? 'negative' : currentCCI < -100 ? 'positive' : 'neutral', category: 'technical' },
                
                // Support/Resistance
                { label: 'Pivot Point', value: Utils.formatCurrency(pivots.pivot), category: 'levels' },
                { label: 'Resistance 1', value: Utils.formatCurrency(pivots.r1), category: 'levels' },
                { label: 'Support 1', value: Utils.formatCurrency(pivots.s1), category: 'levels' },
                { label: 'Fib 61.8%', value: Utils.formatCurrency(fibonacci.level_618), category: 'levels' },
                { label: 'Fib 38.2%', value: Utils.formatCurrency(fibonacci.level_382), category: 'levels' }
            ];

            // Add moving averages if available
            if (technicalData?.sma) {
                metrics.push(
                    { label: 'SMA 20', value: Utils.formatCurrency(technicalData.sma.sma20), class: currentData.close > technicalData.sma.sma20 ? 'positive' : 'negative', category: 'technical' },
                    { label: 'SMA 50', value: Utils.formatCurrency(technicalData.sma.sma50), class: currentData.close > technicalData.sma.sma50 ? 'positive' : 'negative', category: 'technical' }
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
                    title: 'Price ($)'
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
                    <p>${message}</p>
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
}

// Export ChartManager globally
window.ChartManager = ChartManager; 