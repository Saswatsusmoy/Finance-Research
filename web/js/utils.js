/* ==========================================
   UTILITY FUNCTIONS
   Common helpers and utilities
   ========================================== */

const Utils = {
    // Formatting functions
    formatCurrency: function(value, decimals = 2) {
        if (isNaN(value)) return '$0.00';
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(value);
    },

    formatNumber: function(value, decimals = 2) {
        if (isNaN(value)) return '0';
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(value);
    },

    formatPercent: function(value, decimals = 2) {
        if (isNaN(value)) return '0%';
        return new Intl.NumberFormat('en-US', {
            style: 'percent',
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(value / 100);
    },

    formatLargeNumber: function(value) {
        if (isNaN(value)) return '0';
        
        const abs = Math.abs(value);
        if (abs >= 1e12) return (value / 1e12).toFixed(2) + 'T';
        if (abs >= 1e9) return (value / 1e9).toFixed(2) + 'B';
        if (abs >= 1e6) return (value / 1e6).toFixed(2) + 'M';
        if (abs >= 1e3) return (value / 1e3).toFixed(2) + 'K';
        return value.toFixed(2);
    },

    formatVolume: function(value) {
        if (isNaN(value)) return '0';
        return this.formatLargeNumber(value);
    },

    // Date and time functions
    formatDate: function(date, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        };
        
        const formatOptions = { ...defaultOptions, ...options };
        return new Date(date).toLocaleDateString('en-US', formatOptions);
    },

    formatDateTime: function(date) {
        return new Date(date).toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    getTimeAgo: function(timestamp) {
        const now = Date.now();
        const diff = now - new Date(timestamp).getTime();
        
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        const weeks = Math.floor(days / 7);
        const months = Math.floor(days / 30);
        const years = Math.floor(days / 365);

        if (years > 0) return `${years}y ago`;
        if (months > 0) return `${months}mo ago`;
        if (weeks > 0) return `${weeks}w ago`;
        if (days > 0) return `${days}d ago`;
        if (hours > 0) return `${hours}h ago`;
        if (minutes > 0) return `${minutes}m ago`;
        return 'Just now';
    },

    // Color and styling functions
    getChangeColor: function(change) {
        if (change > 0) return 'var(--accent-success)';
        if (change < 0) return 'var(--accent-danger)';
        return 'var(--text-secondary)';
    },

    getChangeClass: function(change) {
        if (change > 0) return 'positive';
        if (change < 0) return 'negative';
        return 'neutral';
    },

    // DOM manipulation helpers
    createElement: function(tag, className = '', innerHTML = '') {
        const element = document.createElement(tag);
        if (className) element.className = className;
        if (innerHTML) element.innerHTML = innerHTML;
        return element;
    },

    addEventListeners: function(element, events) {
        Object.keys(events).forEach(event => {
            element.addEventListener(event, events[event]);
        });
    },

    // Animation helpers
    animateNumber: function(element, start, end, duration = 1000) {
        const startTime = performance.now();
        const range = end - start;

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function (ease-out)
            const eased = 1 - Math.pow(1 - progress, 3);
            const current = start + (range * eased);
            
            element.textContent = Math.round(current);
            
            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }
        
        requestAnimationFrame(update);
    },

    // Data manipulation
    sortData: function(data, key, ascending = true) {
        return data.sort((a, b) => {
            const aVal = a[key];
            const bVal = b[key];
            
            if (aVal < bVal) return ascending ? -1 : 1;
            if (aVal > bVal) return ascending ? 1 : -1;
            return 0;
        });
    },

    filterData: function(data, filters) {
        return data.filter(item => {
            return Object.keys(filters).every(key => {
                const filterValue = filters[key];
                const itemValue = item[key];
                
                if (typeof filterValue === 'string') {
                    return itemValue.toLowerCase().includes(filterValue.toLowerCase());
                }
                
                return itemValue === filterValue;
            });
        });
    },

    groupBy: function(data, key) {
        return data.reduce((groups, item) => {
            const group = item[key];
            if (!groups[group]) {
                groups[group] = [];
            }
            groups[group].push(item);
            return groups;
        }, {});
    },

    // Validation functions
    isValidSymbol: function(symbol) {
        return /^[A-Z]{1,5}$/.test(symbol.toUpperCase());
    },

    isValidEmail: function(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    isValidDate: function(dateString) {
        const date = new Date(dateString);
        return date instanceof Date && !isNaN(date);
    },

    // Local storage helpers
    saveToStorage: function(key, data) {
        try {
            localStorage.setItem(key, JSON.stringify(data));
            return true;
        } catch (error) {
            console.error('Error saving to localStorage:', error);
            return false;
        }
    },

    loadFromStorage: function(key, defaultValue = null) {
        try {
            const data = localStorage.getItem(key);
            return data ? JSON.parse(data) : defaultValue;
        } catch (error) {
            console.error('Error loading from localStorage:', error);
            return defaultValue;
        }
    },

    removeFromStorage: function(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error('Error removing from localStorage:', error);
            return false;
        }
    },

    // Performance helpers
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    // Mathematical helpers
    calculatePercentChange: function(oldValue, newValue) {
        if (oldValue === 0) return 0;
        return ((newValue - oldValue) / oldValue) * 100;
    },

    calculateSMA: function(data, period) {
        const result = [];
        for (let i = period - 1; i < data.length; i++) {
            const sum = data.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
            result.push(sum / period);
        }
        return result;
    },

    calculateEMA: function(data, period) {
        const multiplier = 2 / (period + 1);
        const result = [data[0]];
        
        for (let i = 1; i < data.length; i++) {
            const ema = (data[i] * multiplier) + (result[i - 1] * (1 - multiplier));
            result.push(ema);
        }
        
        return result;
    },

    calculateRSI: function(prices, period = 14) {
        if (prices.length < period + 1) return [];
        
        const changes = [];
        for (let i = 1; i < prices.length; i++) {
            changes.push(prices[i] - prices[i - 1]);
        }
        
        const gains = changes.map(change => change > 0 ? change : 0);
        const losses = changes.map(change => change < 0 ? Math.abs(change) : 0);
        
        let avgGain = gains.slice(0, period).reduce((a, b) => a + b, 0) / period;
        let avgLoss = losses.slice(0, period).reduce((a, b) => a + b, 0) / period;
        
        const rsi = [100 - (100 / (1 + (avgGain / avgLoss)))];
        
        for (let i = period; i < changes.length; i++) {
            avgGain = ((avgGain * (period - 1)) + gains[i]) / period;
            avgLoss = ((avgLoss * (period - 1)) + losses[i]) / period;
            rsi.push(100 - (100 / (1 + (avgGain / avgLoss))));
        }
        
        return rsi;
    },

    // Chart helpers
    getChartColors: function(theme = 'dark') {
        if (theme === 'dark') {
            return {
                primary: '#00d2ff',
                secondary: '#3a7bd5',
                success: '#10b981',
                danger: '#ef4444',
                warning: '#f59e0b',
                background: 'transparent',
                text: '#ffffff',
                grid: 'rgba(255,255,255,0.1)'
            };
        } else {
            return {
                primary: '#3a7bd5',
                secondary: '#00d2ff',
                success: '#059669',
                danger: '#dc2626',
                warning: '#d97706',
                background: '#ffffff',
                text: '#1f2937',
                grid: 'rgba(0,0,0,0.1)'
            };
        }
    },

    // Error handling
    handleError: function(error, context = 'Unknown') {
        console.error(`Error in ${context}:`, error);
        
        // Show user-friendly notification
        if (window.financeApp && window.financeApp.showNotification) {
            window.financeApp.showNotification(
                'error',
                'Operation Failed',
                'An error occurred. Please try again later.'
            );
        }
    },

    // URL helpers
    updateURLParams: function(params) {
        const url = new URL(window.location);
        Object.keys(params).forEach(key => {
            if (params[key] !== null && params[key] !== undefined) {
                url.searchParams.set(key, params[key]);
            } else {
                url.searchParams.delete(key);
            }
        });
        window.history.replaceState({}, '', url);
    },

    getURLParams: function() {
        const params = {};
        const urlParams = new URLSearchParams(window.location.search);
        for (const [key, value] of urlParams) {
            params[key] = value;
        }
        return params;
    },

    // Device detection
    isMobile: function() {
        return window.innerWidth <= 768;
    },

    isTablet: function() {
        return window.innerWidth > 768 && window.innerWidth <= 1024;
    },

    isDesktop: function() {
        return window.innerWidth > 1024;
    },

    // Clipboard
    copyToClipboard: function(text) {
        if (navigator.clipboard) {
            return navigator.clipboard.writeText(text);
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            return Promise.resolve();
        }
    },

    // Random utilities
    generateId: function() {
        return '_' + Math.random().toString(36).substr(2, 9);
    },

    capitalizeFirst: function(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    },

    truncateText: function(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substr(0, maxLength) + '...';
    },

    isValidSymbol: function(symbol) {
        return symbol && symbol.length > 0 && /^[A-Z]{1,5}$/.test(symbol);
    },

    // Advanced Technical Analysis Calculations
    calculateMACD: function(prices, fastPeriod = 12, slowPeriod = 26, signalPeriod = 9) {
        if (!prices || prices.length < slowPeriod) {
            return { macdLine: [], signalLine: [], histogram: [] };
        }

        const fastEMA = this.calculateEMA(prices, fastPeriod);
        const slowEMA = this.calculateEMA(prices, slowPeriod);
        
        // Calculate MACD line
        const macdLine = [];
        for (let i = 0; i < prices.length; i++) {
            if (fastEMA[i] !== undefined && slowEMA[i] !== undefined) {
                macdLine[i] = fastEMA[i] - slowEMA[i];
            }
        }
        
        // Filter out undefined values for signal line calculation
        const validMacdValues = macdLine.filter(x => x !== undefined);
        if (validMacdValues.length < signalPeriod) {
            return { macdLine, signalLine: [], histogram: [] };
        }
        
        // Calculate signal line
        const signalEMA = this.calculateEMA(validMacdValues, signalPeriod);
        
        // Align signal line with MACD line indices
        const signalLine = [];
        let signalIndex = 0;
        for (let i = 0; i < macdLine.length; i++) {
            if (macdLine[i] !== undefined) {
                if (signalIndex < signalEMA.length) {
                    signalLine[i] = signalEMA[signalIndex];
                    signalIndex++;
                }
            }
        }
        
        // Calculate histogram
        const histogram = [];
        for (let i = 0; i < macdLine.length; i++) {
            if (macdLine[i] !== undefined && signalLine[i] !== undefined) {
                histogram[i] = macdLine[i] - signalLine[i];
            }
        }
        
        return { macdLine, signalLine, histogram };
    },

    calculateStochastic: function(highs, lows, closes, kPeriod = 14, dPeriod = 3) {
        const k = [];
        const d = [];
        
        for (let i = kPeriod - 1; i < closes.length; i++) {
            const highestHigh = Math.max(...highs.slice(i - kPeriod + 1, i + 1));
            const lowestLow = Math.min(...lows.slice(i - kPeriod + 1, i + 1));
            
            k[i] = ((closes[i] - lowestLow) / (highestHigh - lowestLow)) * 100;
        }
        
        for (let i = kPeriod + dPeriod - 2; i < k.length; i++) {
            const sum = k.slice(i - dPeriod + 1, i + 1).reduce((a, b) => a + b, 0);
            d[i] = sum / dPeriod;
        }
        
        return { k: k.filter(x => x !== undefined), d: d.filter(x => x !== undefined) };
    },

    calculateWilliamsR: function(highs, lows, closes, period = 14) {
        const williamsR = [];
        
        for (let i = period - 1; i < closes.length; i++) {
            const highestHigh = Math.max(...highs.slice(i - period + 1, i + 1));
            const lowestLow = Math.min(...lows.slice(i - period + 1, i + 1));
            
            williamsR[i] = ((highestHigh - closes[i]) / (highestHigh - lowestLow)) * -100;
        }
        
        return williamsR.filter(x => x !== undefined);
    },

    calculateATR: function(highs, lows, closes, period = 14) {
        const trueRanges = [];
        
        for (let i = 1; i < closes.length; i++) {
            const tr1 = highs[i] - lows[i];
            const tr2 = Math.abs(highs[i] - closes[i - 1]);
            const tr3 = Math.abs(lows[i] - closes[i - 1]);
            
            trueRanges[i] = Math.max(tr1, tr2, tr3);
        }
        
        return this.calculateSMA(trueRanges.filter(x => x !== undefined), period);
    },

    calculateCCI: function(highs, lows, closes, period = 20) {
        const typicalPrices = [];
        for (let i = 0; i < closes.length; i++) {
            typicalPrices[i] = (highs[i] + lows[i] + closes[i]) / 3;
        }
        
        const sma = this.calculateSMA(typicalPrices, period);
        const cci = [];
        
        for (let i = period - 1; i < typicalPrices.length; i++) {
            const slice = typicalPrices.slice(i - period + 1, i + 1);
            const mean = sma[i - period + 1];
            const meanDeviation = slice.reduce((sum, tp) => sum + Math.abs(tp - mean), 0) / period;
            
            cci[i] = (typicalPrices[i] - mean) / (0.015 * meanDeviation);
        }
        
        return cci.filter(x => x !== undefined);
    },

    calculateVolatility: function(prices, period = 20) {
        const returns = [];
        for (let i = 1; i < prices.length; i++) {
            returns.push((prices[i] - prices[i - 1]) / prices[i - 1]);
        }
        
        const volatilities = [];
        for (let i = period - 1; i < returns.length; i++) {
            const slice = returns.slice(i - period + 1, i + 1);
            const mean = slice.reduce((a, b) => a + b) / slice.length;
            const variance = slice.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / slice.length;
            volatilities.push(Math.sqrt(variance) * Math.sqrt(252) * 100);
        }
        
        return volatilities;
    },

    calculateVWAP: function(prices, volumes) {
        let totalVolume = 0;
        let totalValue = 0;
        
        for (let i = 0; i < prices.length; i++) {
            totalValue += prices[i] * volumes[i];
            totalVolume += volumes[i];
        }
        
        return totalVolume > 0 ? totalValue / totalVolume : 0;
    },

    calculateFibonacciRetracements: function(high, low) {
        const diff = high - low;
        return {
            level_0: high,
            level_236: high - (diff * 0.236),
            level_382: high - (diff * 0.382),
            level_500: high - (diff * 0.500),
            level_618: high - (diff * 0.618),
            level_786: high - (diff * 0.786),
            level_100: low
        };
    },

    calculatePivotPoints: function(high, low, close) {
        const pivot = (high + low + close) / 3;
        return {
            pivot: pivot,
            r1: (2 * pivot) - low,
            r2: pivot + (high - low),
            r3: high + 2 * (pivot - low),
            s1: (2 * pivot) - high,
            s2: pivot - (high - low),
            s3: low - 2 * (high - pivot)
        };
    },

    calculateDrawdown: function(prices) {
        let maxDrawdown = 0;
        let peak = prices[0];
        const drawdowns = [];
        
        for (let i = 0; i < prices.length; i++) {
            if (prices[i] > peak) {
                peak = prices[i];
            }
            
            const drawdown = (peak - prices[i]) / peak * 100;
            drawdowns.push(drawdown);
            
            if (drawdown > maxDrawdown) {
                maxDrawdown = drawdown;
            }
        }
        
        return { maxDrawdown, drawdowns };
    }
};

// Export Utils globally
window.Utils = Utils; 