# 🤝 Contributing to Financial Research Assistant

Thank you for your interest in contributing to the Financial Research Assistant! This document provides comprehensive guidelines for setting up the development environment, understanding the codebase, and contributing effectively.

## 📋 Table of Contents

- [Getting Started](#-getting-started)
- [Development Environment Setup](#-development-environment-setup)
- [Project Structure](#-project-structure)
- [Code Style Guidelines](#-code-style-guidelines)
- [Development Workflow](#-development-workflow)
- [Testing](#-testing)
- [Debugging Tools](#-debugging-tools)
- [API Development](#-api-development)
- [Frontend Development](#-frontend-development)
- [Deployment & Production](#-deployment--production)
- [Troubleshooting](#-troubleshooting)
- [Submitting Changes](#-submitting-changes)

---

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** with pip
- **Node.js 16+** with npm (for frontend tools)
- **Git** for version control
- **Code Editor** (VS Code recommended with Python extension)

### Quick Setup

1. **Fork & Clone the Repository**
   ```bash
   git clone https://github.com/your-username/financial-research-assistant.git
   cd financial-research-assistant
   ```

2. **Set Up Python Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env with your API keys (optional for development)
   ```

4. **Initialize Development Environment**
   ```bash
   python init_setup.py
   ```

---

## 🛠️ Development Environment Setup

### IDE Configuration

#### VS Code Settings (Recommended)

Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.linting.flake8Enabled": true,
    "editor.formatOnSave": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/venv": true,
        "**/.env": true
    }
}
```

#### Recommended VS Code Extensions

- Python
- Pylance
- Black Formatter
- GitLens
- REST Client
- JavaScript ES6 snippets
- HTML CSS Support

### Environment Variables

Create a comprehensive `.env` file for development:

```bash
# Development Settings
DEBUG_MODE=true
LOG_LEVEL=DEBUG
FLASK_ENV=development

# API Keys (Get from respective providers)
OPENAI_API_KEY=your_openai_api_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
FINNHUB_API_KEY=your_finnhub_key_here
NEWS_API_KEY=your_news_api_key_here

# Database (Optional - defaults to file storage)
DATABASE_URL=sqlite:///dev_database.db

# Cache Settings
CACHE_TIMEOUT=300
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your_dev_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here

# External Services
ENABLE_REAL_DATA=true
MOCK_DATA_FALLBACK=true
```

---

## 📁 Project Structure

### Directory Overview

```
financial-research-assistant/
├── src/                          # Core application code
│   ├── agents/                   # LangGraph AI agents
│   │   ├── insider_trading/      # Insider trading analysis
│   │   └── social_sentiment/     # Social media sentiment
│   ├── data/                     # Data processing modules
│   ├── ui/                       # Streamlit UI components
│   ├── utils/                    # Utility functions
│   └── api.py                    # FastAPI server
├── web/                          # Modern web interface
│   ├── css/                      # Stylesheets
│   ├── js/                       # JavaScript modules
│   └── index.html                # Main HTML file
├── tests/                        # Test suite
├── venv/                         # Virtual environment
├── web_server.py                 # Flask web server
├── app.py                        # Streamlit app entry point
├── requirements.txt              # Python dependencies
├── settings.json                 # Application settings
├── .env.example                  # Environment template
└── Dockerfile                    # Container configuration
```

### Key Components

#### Backend Architecture

1. **Flask Web Server** (`web_server.py`)
   - Main web application server
   - RESTful API endpoints
   - Static file serving
   - Session management

2. **FastAPI Server** (`src/api.py`)
   - High-performance API server
   - Automatic OpenAPI documentation
   - Async request handling
   - Data validation with Pydantic

3. **LangGraph Agents** (`src/agents/`)
   - AI-powered analysis modules
   - Multi-agent coordination
   - State management
   - Decision making logic

4. **Data Processing** (`src/data/`)
   - External API integrations
   - Data cleaning and validation
   - Caching mechanisms
   - Rate limiting

#### Frontend Architecture

1. **Modern Web Interface** (`web/`)
   - Vanilla JavaScript ES6+
   - Responsive CSS3 with glassmorphism
   - Plotly.js for interactive charts
   - Real-time data updates

2. **Streamlit Interface** (`src/ui/`)
   - Python-based UI components
   - Rapid prototyping interface
   - Interactive widgets
   - Data visualization

---

## 🎨 Code Style Guidelines

### Python Code Style

We follow **PEP 8** with these additions:

```python
# File header template
"""
Module: financial_analysis.py
Purpose: Comprehensive financial data analysis
Author: Your Name
Date: YYYY-MM-DD
"""

# Import organization
import os
import sys
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
from flask import Flask, request, jsonify

# Class naming: PascalCase
class MarketDataAnalyzer:
    """Analyzes market data with advanced technical indicators."""
    
    def __init__(self, config: Dict[str, str]) -> None:
        self.config = config
        self._cache: Dict[str, Any] = {}
    
    # Method naming: snake_case
    def fetch_market_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """
        Fetch market data for a given symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: Time period ('1d', '1w', '1m', '3m', '1y')
            
        Returns:
            DataFrame with OHLCV data
            
        Raises:
            ValueError: If symbol is invalid
            APIError: If data fetch fails
        """
        pass

# Constants: UPPER_SNAKE_CASE
DEFAULT_CACHE_TIMEOUT = 300
API_BASE_URL = "https://api.example.com/v1"
```

### JavaScript Code Style

We follow **ES6+ standards** with these guidelines:

```javascript
// File header
/**
 * Module: market-analysis.js
 * Purpose: Real-time market data analysis and visualization
 * Author: Your Name
 * Date: YYYY-MM-DD
 */

// Class naming: PascalCase
class MarketDataManager {
    constructor(config) {
        this.config = config;
        this.cache = new Map();
        this.subscribers = [];
    }
    
    // Method naming: camelCase
    async fetchMarketData(symbol, period = '1y') {
        try {
            const response = await fetch(`/api/market-data/${symbol}?period=${period}`);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(`API Error: ${data.message}`);
            }
            
            return this.processMarketData(data);
        } catch (error) {
            console.error('Failed to fetch market data:', error);
            throw error;
        }
    }
    
    // Private methods: underscore prefix
    _validateSymbol(symbol) {
        const symbolRegex = /^[A-Z]{1,5}$/;
        return symbolRegex.test(symbol);
    }
}

// Constants: UPPER_SNAKE_CASE
const DEFAULT_REFRESH_INTERVAL = 5000;
const API_ENDPOINTS = {
    MARKET_DATA: '/api/market-data',
    NEWS: '/api/news',
    INSIDER_TRADING: '/api/insider-trading'
};
```

### CSS Code Style

```css
/* Modern CSS with custom properties */
:root {
    /* Color palette */
    --primary-color: #00d2ff;
    --secondary-color: #3a7bd5;
    --accent-color: #f093fb;
    
    /* Spacing system */
    --space-xs: 0.25rem;
    --space-sm: 0.5rem;
    --space-md: 1rem;
    --space-lg: 1.5rem;
    --space-xl: 2rem;
    
    /* Typography */
    --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-mono: 'JetBrains Mono', 'Fira Code', Consolas, monospace;
}

/* BEM methodology for class naming */
.market-card {
    /* Block */
}

.market-card__header {
    /* Element */
}

.market-card__header--highlighted {
    /* Modifier */
}
```

---

## 🔄 Development Workflow

### 1. Start Development Environment

```bash
# Terminal 1: Start Flask web server
python web_server.py

# Terminal 2: Start FastAPI server (optional)
uvicorn src.api:app --reload --port 8000

# Terminal 3: Start Streamlit (optional)
streamlit run app.py
```

### 2. Development URLs

- **Main Web Interface**: http://localhost:5000
- **API Documentation**: http://localhost:8000/docs
- **Streamlit Interface**: http://localhost:8501

### 3. Hot Reloading

- **Python**: Flask and FastAPI support auto-reload in development
- **Frontend**: Browser refresh required for web interface
- **CSS/JS**: Changes reflected immediately on refresh

### 4. Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-analysis-tool

# Make your changes
git add .
git commit -m "feat: Add new technical analysis indicator"

# Push to your fork
git push origin feature/new-analysis-tool

# Create pull request on GitHub
```

---

## 🧪 Testing

### Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── test_api.py
│   ├── test_agents.py
│   └── test_utils.py
├── integration/             # Integration tests
│   ├── test_web_server.py
│   └── test_data_flow.py
├── e2e/                     # End-to-end tests
│   └── test_user_journey.py
├── fixtures/                # Test data
│   ├── market_data.json
│   └── news_samples.json
└── conftest.py              # Pytest configuration
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/unit/test_api.py

# Run with coverage
python -m pytest --cov=src tests/

# Run with verbose output
python -m pytest -v

# Run specific test function
python -m pytest tests/unit/test_api.py::test_market_data_endpoint
```

### Writing Tests

```python
# tests/unit/test_market_analyzer.py
import pytest
from unittest.mock import Mock, patch
from src.agents.market_analyzer import MarketAnalyzer

class TestMarketAnalyzer:
    
    @pytest.fixture
    def analyzer(self):
        config = {"api_key": "test_key"}
        return MarketAnalyzer(config)
    
    def test_fetch_market_data_success(self, analyzer):
        # Arrange
        symbol = "AAPL"
        expected_data = {"price": 150.0, "volume": 1000000}
        
        # Act
        with patch('src.utils.api_client.fetch_data') as mock_fetch:
            mock_fetch.return_value = expected_data
            result = analyzer.fetch_market_data(symbol)
        
        # Assert
        assert result["price"] == 150.0
        mock_fetch.assert_called_once_with(symbol)
    
    def test_fetch_market_data_invalid_symbol(self, analyzer):
        # Test error handling
        with pytest.raises(ValueError, match="Invalid symbol"):
            analyzer.fetch_market_data("INVALID_SYMBOL_123")
```

---

## 🐛 Debugging Tools

### 1. Python Debugging

#### Built-in Debug Mode

```python
# Enable debug mode in web_server.py
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

#### Using Python Debugger

```python
import pdb

def analyze_market_data(symbol):
    data = fetch_data(symbol)
    pdb.set_trace()  # Breakpoint
    processed_data = process_data(data)
    return processed_data
```

#### Logging Configuration

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def fetch_market_data(symbol):
    logger.debug(f"Fetching data for symbol: {symbol}")
    try:
        data = api_call(symbol)
        logger.info(f"Successfully fetched data for {symbol}")
        return data
    except Exception as e:
        logger.error(f"Failed to fetch data for {symbol}: {e}")
        raise
```

### 2. JavaScript Debugging

#### Browser Developer Tools

```javascript
// Console debugging
console.log('Market data:', marketData);
console.error('API call failed:', error);
console.warn('Using cached data');

// Debugger statement
function analyzeMarketTrends(data) {
    debugger; // Browser will pause here
    const trends = processData(data);
    return trends;
}

// Performance monitoring
console.time('Data Processing');
processMarketData(data);
console.timeEnd('Data Processing');
```

#### Debug Helper Functions

```javascript
// Debug utilities in web/js/debug.js
class DebugUtils {
    static logAPICall(endpoint, params, response) {
        if (window.DEBUG_MODE) {
            console.group(`API Call: ${endpoint}`);
            console.log('Parameters:', params);
            console.log('Response:', response);
            console.groupEnd();
        }
    }
    
    static validateData(data, schema) {
        // Data validation logic
        if (window.DEBUG_MODE) {
            console.log('Data validation:', { data, schema, valid: isValid });
        }
        return isValid;
    }
}

// Usage
DebugUtils.logAPICall('/api/market-data/AAPL', { period: '1y' }, response);
```

### 3. API Debugging

#### Flask Debug Endpoints

```python
# Add debug endpoints in web_server.py
@app.route('/debug/health')
def debug_health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'environment': os.getenv('FLASK_ENV', 'production')
    })

@app.route('/debug/api-status')
def debug_api_status():
    # Test all external API connections
    status = {}
    
    # Test Alpha Vantage
    try:
        # API test call
        status['alpha_vantage'] = 'connected'
    except:
        status['alpha_vantage'] = 'failed'
    
    return jsonify(status)

@app.route('/debug/cache-stats')
def debug_cache_stats():
    # Return cache performance metrics
    return jsonify({
        'cache_hits': cache_hits,
        'cache_misses': cache_misses,
        'cache_size': len(cache_store)
    })
```

#### API Testing with curl

```bash
# Test market data endpoint
curl -X GET "http://localhost:5000/api/market-data/AAPL" \
     -H "Accept: application/json"

# Test with parameters
curl -X GET "http://localhost:5000/api/chart-data/AAPL/1y" \
     -H "Accept: application/json"

# Test POST endpoint
curl -X POST "http://localhost:5000/api/insider-analysis" \
     -H "Content-Type: application/json" \
     -d '{"symbol": "AAPL", "lookback_days": 90}'
```

### 4. Frontend Debugging

#### Console Debug Commands

Available in browser console on the web interface:

```javascript
// Test insider trading module
window.InsiderTrading.debugInfo()
window.InsiderTrading.testMockDataGeneration()
window.InsiderTrading.testQuickAnalysis()

// Test API connections
window.API.testConnection()

// Test watchlist functionality
app.debugWatchlist()

// Manual data refresh
app.refreshAllData()

// Check application state
console.log('App state:', {
    currentPage: app.currentPage,
    watchlist: app.watchlist,
    settings: app.settings
});
```

---

## 🔌 API Development

### Adding New Endpoints

1. **Define the endpoint in Flask** (`web_server.py`):

```python
@app.route('/api/new-feature/<symbol>', methods=['GET'])
def get_new_feature(symbol):
    try:
        # Validate input
        if not symbol or len(symbol) > 5:
            return jsonify({'error': 'Invalid symbol'}), 400
        
        # Process request
        data = process_new_feature(symbol)
        
        # Return response
        return jsonify({
            'symbol': symbol,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error in new feature endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def process_new_feature(symbol):
    # Business logic here
    pass
```

2. **Add corresponding FastAPI endpoint** (`src/api.py`):

```python
from pydantic import BaseModel

class NewFeatureRequest(BaseModel):
    symbol: str
    parameters: Optional[Dict[str, Any]] = {}

class NewFeatureResponse(BaseModel):
    symbol: str
    data: Dict[str, Any]
    timestamp: str

@app.post("/api/new-feature", response_model=NewFeatureResponse)
async def new_feature_endpoint(request: NewFeatureRequest):
    try:
        data = await process_new_feature_async(request.symbol, request.parameters)
        return NewFeatureResponse(
            symbol=request.symbol,
            data=data,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

3. **Create frontend integration** (`web/js/api.js`):

```javascript
class API {
    static async getNewFeature(symbol, params = {}) {
        try {
            const response = await fetch(`/api/new-feature/${symbol}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    }
}
```

### Error Handling Best Practices

```python
# Standardized error responses
class APIError(Exception):
    def __init__(self, message, status_code=500, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload

@app.errorhandler(APIError)
def handle_api_error(error):
    response = {
        'error': error.message,
        'timestamp': datetime.now().isoformat()
    }
    if error.payload:
        response.update(error.payload)
    
    return jsonify(response), error.status_code

# Usage in endpoints
@app.route('/api/data/<symbol>')
def get_data(symbol):
    if not validate_symbol(symbol):
        raise APIError('Invalid symbol format', 400)
    
    try:
        data = fetch_external_data(symbol)
    except ExternalAPIError as e:
        raise APIError('External service unavailable', 503)
    
    return jsonify(data)
```

---

## 🎨 Frontend Development

### Adding New UI Components

1. **HTML Structure** (`web/index.html`):

```html
<!-- New Component Section -->
<div id="new-component-page" class="page">
    <div class="page-header">
        <h1 class="page-title">
            <i class="fas fa-chart-bar"></i>
            New Component
        </h1>
        <div class="component-controls">
            <input type="text" id="component-input" placeholder="Enter symbol...">
            <button class="btn btn-primary" id="component-analyze">
                <i class="fas fa-search"></i>
                Analyze
            </button>
        </div>
    </div>
    
    <div class="component-content">
        <div class="component-loading hidden" id="component-loading">
            <div class="loading-spinner"></div>
            <p>Loading data...</p>
        </div>
        
        <div class="component-results" id="component-results">
            <!-- Results will be populated here -->
        </div>
    </div>
</div>
```

2. **CSS Styling** (`web/css/styles.css`):

```css
/* New Component Styles */
.component-content {
    display: grid;
    grid-template-columns: 1fr;
    gap: var(--space-lg);
    padding: var(--space-lg);
}

.component-controls {
    display: flex;
    gap: var(--space-sm);
    align-items: center;
}

.component-results {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border-radius: var(--radius-lg);
    padding: var(--space-lg);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.component-chart {
    height: 400px;
    width: 100%;
    border-radius: var(--radius-md);
    overflow: hidden;
}

/* Responsive design */
@media (max-width: 768px) {
    .component-controls {
        flex-direction: column;
        width: 100%;
    }
    
    .component-chart {
        height: 300px;
    }
}
```

3. **JavaScript Functionality** (`web/js/new-component.js`):

```javascript
class NewComponentManager {
    constructor() {
        this.currentData = null;
        this.isLoading = false;
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        console.log('New Component Manager initialized');
    }
    
    setupEventListeners() {
        const analyzeBtn = document.getElementById('component-analyze');
        const input = document.getElementById('component-input');
        
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.runAnalysis());
        }
        
        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.runAnalysis();
                }
            });
        }
    }
    
    async runAnalysis() {
        const input = document.getElementById('component-input');
        const symbol = input?.value?.trim()?.toUpperCase();
        
        if (!symbol) {
            this.showError('Please enter a symbol');
            return;
        }
        
        try {
            this.showLoading();
            const data = await this.fetchComponentData(symbol);
            this.displayResults(data);
        } catch (error) {
            console.error('Analysis failed:', error);
            this.showError('Analysis failed. Please try again.');
        }
    }
    
    async fetchComponentData(symbol) {
        const response = await fetch(`/api/new-feature/${symbol}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return await response.json();
    }
    
    displayResults(data) {
        const resultsContainer = document.getElementById('component-results');
        if (!resultsContainer) return;
        
        resultsContainer.innerHTML = `
            <div class="component-summary">
                <h3>Analysis Results for ${data.symbol}</h3>
                <div class="metrics-grid">
                    ${this.renderMetrics(data)}
                </div>
            </div>
            <div class="component-chart" id="component-chart"></div>
        `;
        
        this.renderChart(data);
        this.hideLoading();
    }
    
    renderMetrics(data) {
        return Object.entries(data.metrics || {})
            .map(([key, value]) => `
                <div class="metric-item">
                    <span class="metric-label">${key}</span>
                    <span class="metric-value">${value}</span>
                </div>
            `).join('');
    }
    
    renderChart(data) {
        const chartContainer = document.getElementById('component-chart');
        if (!chartContainer || !data.chartData) return;
        
        const trace = {
            x: data.chartData.dates,
            y: data.chartData.values,
            type: 'scatter',
            mode: 'lines+markers',
            name: data.symbol,
            line: { color: '#00d2ff', width: 2 }
        };
        
        const layout = {
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#ffffff' },
            margin: { t: 20, r: 20, b: 40, l: 60 }
        };
        
        Plotly.newPlot(chartContainer, [trace], layout, {
            displayModeBar: false,
            responsive: true
        });
    }
    
    showLoading() {
        this.isLoading = true;
        const loading = document.getElementById('component-loading');
        const results = document.getElementById('component-results');
        
        if (loading) loading.classList.remove('hidden');
        if (results) results.style.display = 'none';
    }
    
    hideLoading() {
        this.isLoading = false;
        const loading = document.getElementById('component-loading');
        const results = document.getElementById('component-results');
        
        if (loading) loading.classList.add('hidden');
        if (results) results.style.display = 'block';
    }
    
    showError(message) {
        this.hideLoading();
        // Show error notification
        if (window.app) {
            window.app.showNotification('error', 'Error', message);
        }
    }
}

// Initialize component
const newComponentManager = new NewComponentManager();
window.NewComponent = newComponentManager;
```

### Chart Integration

Using Plotly.js for interactive charts:

```javascript
// Chart configuration template
const createChart = (containerId, data, options = {}) => {
    const defaultLayout = {
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { 
            color: '#ffffff',
            family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
        },
        xaxis: {
            gridcolor: 'rgba(255, 255, 255, 0.1)',
            color: '#b3b8c8'
        },
        yaxis: {
            gridcolor: 'rgba(255, 255, 255, 0.1)',
            color: '#b3b8c8'
        },
        margin: { t: 20, r: 20, b: 40, l: 60 },
        ...options.layout
    };
    
    const config = {
        displayModeBar: false,
        responsive: true,
        ...options.config
    };
    
    return Plotly.newPlot(containerId, data, defaultLayout, config);
};
```

---

## 🚀 Deployment & Production

### Production Checklist

Before deploying to production:

- [ ] All sensitive data removed from repository
- [ ] Environment variables properly configured
- [ ] Error handling implemented
- [ ] Logging configured appropriately
- [ ] Performance optimizations applied
- [ ] Security headers configured
- [ ] Rate limiting implemented
- [ ] Health checks added
- [ ] Monitoring setup
- [ ] Backup strategy in place

### Docker Production Build

```dockerfile
# Multi-stage production build
FROM python:3.9-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.9-slim as production

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/debug/health || exit 1

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "web_server:app"]
```

### Environment-Specific Configuration

```python
# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    LOG_LEVEL = 'INFO'
    # Production-specific settings

class TestingConfig(Config):
    TESTING = True
    LOG_LEVEL = 'ERROR'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. API Connection Failures

**Problem**: External APIs returning errors or timeouts

**Solutions**:
```python
# Implement retry logic with exponential backoff
import time
from functools import wraps

def retry_with_backoff(max_retries=3, backoff_factor=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    wait_time = backoff_factor ** attempt
                    time.sleep(wait_time)
            return None
        return wrapper
    return decorator

@retry_with_backoff()
def fetch_external_data(symbol):
    # API call logic
    pass
```

#### 2. Frontend JavaScript Errors

**Problem**: Console errors or broken functionality

**Debug Steps**:
1. Open browser Developer Tools (F12)
2. Check Console tab for errors
3. Verify network requests in Network tab
4. Use browser debugger with breakpoints

**Common Fixes**:
```javascript
// Null reference protection
const element = document.getElementById('some-element');
if (element) {
    element.addEventListener('click', handler);
}

// Async error handling
async function safeApiCall() {
    try {
        const response = await fetch('/api/data');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        return null; // or default data
    }
}
```

#### 3. Python Import Errors

**Problem**: Module not found or import errors

**Solutions**:
```bash
# Verify virtual environment is activated
which python
which pip

# Reinstall dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"

# Add project root to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### 4. Data Loading Issues

**Problem**: Charts not rendering or data not displaying

**Debug Steps**:
1. Check browser network tab for failed requests
2. Verify API responses contain expected data structure
3. Check console for JavaScript errors
4. Validate data format matches chart expectations

#### 5. Performance Issues

**Problem**: Slow loading or unresponsive interface

**Optimization Strategies**:
```python
# Implement caching
from functools import lru_cache
import redis

# Memory cache for small data
@lru_cache(maxsize=128)
def get_company_info(symbol):
    return fetch_company_data(symbol)

# Redis cache for larger data
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cached_market_data(symbol, period):
    cache_key = f"market_data:{symbol}:{period}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
    data = fetch_market_data(symbol, period)
    redis_client.setex(cache_key, 300, json.dumps(data))  # 5 min cache
    return data
```

---

## 📝 Submitting Changes

### Pull Request Process

1. **Ensure your fork is up to date**:
   ```bash
   git remote add upstream https://github.com/original/financial-research-assistant.git
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes and commit**:
   ```bash
   git add .
   git commit -m "feat: add new technical indicator analysis"
   ```

4. **Write comprehensive tests**:
   ```bash
   python -m pytest tests/ -v
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create pull request on GitHub**

### Commit Message Convention

We follow the **Conventional Commits** specification:

```
type(scope): description

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```bash
feat(api): add insider trading analysis endpoint
fix(ui): resolve watchlist refresh issue
docs(readme): update installation instructions
test(analyzer): add unit tests for market data processing
```

### Pull Request Template

When creating a pull request, please include:

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] All new and existing tests pass
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
```

---

## 📚 Additional Resources

### Documentation
- [Python Official Documentation](https://docs.python.org/3/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Plotly.js Documentation](https://plotly.com/javascript/)

### API Documentation
- [Alpha Vantage API](https://www.alphavantage.co/documentation/)
- [Finnhub API](https://finnhub.io/docs/api)
- [News API](https://newsapi.org/docs)

### Tools and Libraries
- [LangGraph Documentation](https://github.com/langchain-ai/langgraph)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [TA-Lib Documentation](https://ta-lib.org/)

---

## 🆘 Getting Help

If you encounter issues or have questions:

1. **Check existing issues** on GitHub
2. **Search the documentation** for relevant information
3. **Ask in GitHub Discussions** for general questions
4. **Create a new issue** for bugs or feature requests

### Issue Template

When reporting bugs, please include:

```markdown
**Bug Description**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
- OS: [e.g. Windows 10, macOS 12.0, Ubuntu 20.04]
- Python Version: [e.g. 3.9.7]
- Browser: [e.g. Chrome 96, Firefox 94]
- Version: [e.g. 1.0.0]

**Additional Context**
Add any other context about the problem here.
```

---

Thank you for contributing to the Financial Research Assistant! Your contributions help make this tool better for everyone in the financial analysis community. 🚀 