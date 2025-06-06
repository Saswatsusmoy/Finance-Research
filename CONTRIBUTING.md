# Contributing Guide

## Table of Contents

1. [Overview](#overview)
2. [Development Environment](#development-environment)
3. [Project Architecture](#project-architecture)
4. [Development Standards](#development-standards)
5. [Testing Requirements](#testing-requirements)
6. [API Development Guidelines](#api-development-guidelines)
7. [Frontend Development Standards](#frontend-development-standards)
8. [Quality Assurance](#quality-assurance)
9. [Deployment Procedures](#deployment-procedures)
10. [Submission Requirements](#submission-requirements)

## Overview

The Financial Research Assistant is a sophisticated financial analysis platform that integrates artificial intelligence agents, real-time market data processing, and advanced analytics capabilities. This document provides comprehensive technical guidelines for contributing to the project.

### Technical Stack

- **Backend**: Python 3.9+, Flask, FastAPI
- **AI Framework**: LangGraph for multi-agent orchestration
- **Frontend**: Vanilla JavaScript ES6+, HTML5, CSS3
- **Data Processing**: Pandas, NumPy, TA-Lib
- **Visualization**: Plotly.js
- **Testing**: pytest, Jest
- **Containerization**: Docker

### Prerequisites

Contributors must have experience with:

- Python development and virtual environments
- RESTful API design and implementation
- Modern JavaScript (ES6+) and DOM manipulation
- Git version control and collaborative workflows
- Software testing methodologies

## Development Environment

### System Requirements

- Python 3.9 or higher
- Node.js 16+ (for frontend tooling)
- Git 2.30+
- Minimum 8GB RAM
- Docker (optional, for containerized development)

### Environment Setup

#### 1. Repository Configuration

```bash
git clone https://github.com/your-username/financial-research-assistant.git
cd financial-research-assistant
git remote add upstream https://github.com/original/financial-research-assistant.git
```

#### 2. Python Environment

```bash
python -m venv venv
source venv/bin/activate  # Unix/macOS
# or
venv\Scripts\activate  # Windows

pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

#### 3. Environment Variables

Create `.env` file with required configuration:

```bash
# Core Application
DEBUG_MODE=true
LOG_LEVEL=DEBUG
SECRET_KEY=development_secret_key

# External APIs
OPENAI_API_KEY=your_openai_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
FINNHUB_API_KEY=your_finnhub_key
NEWS_API_KEY=your_news_api_key

# Database Configuration
DATABASE_URL=sqlite:///development.db

# Cache Configuration
REDIS_URL=redis://localhost:6379/0
CACHE_TIMEOUT=300

# Security
JWT_SECRET_KEY=jwt_development_secret
CORS_ORIGINS=http://localhost:3000,http://localhost:5000
```

#### 4. IDE Configuration

Recommended VS Code settings (`.vscode/settings.json`):

```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.linting.flake8Enabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/venv": true,
        "**/.env": true,
        "**/*.pyc": true
    }
}
```

## Project Architecture

### Directory Structure

```
financial-research-assistant/
├── src/                          # Core application modules
│   ├── agents/                   # AI agent implementations
│   │   ├── __init__.py
│   │   ├── base_agent.py        # Base agent interface
│   │   ├── market_analyzer.py   # Market analysis agent
│   │   ├── risk_assessor.py     # Risk assessment agent
│   │   └── sentiment_analyzer.py # Sentiment analysis agent
│   ├── data/                     # Data processing modules
│   │   ├── __init__.py
│   │   ├── collectors.py        # Data collection interfaces
│   │   ├── processors.py        # Data transformation logic
│   │   └── validators.py        # Data validation utilities
│   ├── api/                      # API layer
│   │   ├── __init__.py
│   │   ├── routes.py            # API route definitions
│   │   ├── models.py            # Pydantic models
│   │   └── middleware.py        # Request/response middleware
│   ├── utils/                    # Utility modules
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration management
│   │   ├── logging_config.py    # Logging configuration
│   │   └── exceptions.py        # Custom exception classes
│   └── tests/                    # Test modules
├── web/                          # Frontend assets
│   ├── js/                       # JavaScript modules
│   ├── css/                      # Stylesheets
│   └── index.html               # Main HTML template
├── docs/                         # Documentation
├── scripts/                      # Development scripts
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
├── pytest.ini                   # Test configuration
├── .flake8                      # Linting configuration
├── .gitignore                   # Git ignore patterns
└── docker-compose.yml           # Container orchestration
```

### Core Components

#### Agent System Architecture

The AI agent system follows a modular, event-driven architecture:

```python
# src/agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class AgentContext:
    """Context object passed between agents."""
    request_id: str
    user_id: Optional[str]
    session_data: Dict[str, Any]
    metadata: Dict[str, Any]

class BaseAgent(ABC):
    """Abstract base class for all AI agents."""
  
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__
      
    @abstractmethod
    async def process(self, context: AgentContext, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results."""
        pass
      
    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data format and requirements."""
        pass
```

## Development Standards

### Code Style Guidelines

#### Python Standards

Follow PEP 8 with the following additions:

- **Line Length**: Maximum 88 characters (Black formatter default)
- **Import Organization**: Use isort with the following configuration
- **Type Hints**: Required for all public functions and class methods
- **Docstrings**: Google-style docstrings for all modules, classes, and functions

Example:

```python
"""
Market data analysis module.

This module provides functionality for analyzing real-time and historical
market data using various technical indicators and statistical methods.
"""

from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
import logging

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class MarketAnalyzer:
    """Analyzes market data with technical indicators.
  
    This class provides methods for processing market data and generating
    technical analysis indicators including moving averages, RSI, MACD, etc.
  
    Attributes:
        config: Configuration dictionary containing API keys and settings.
        cache_timeout: Cache timeout in seconds for data storage.
    """
  
    def __init__(self, config: Dict[str, str], cache_timeout: int = 300) -> None:
        """Initialize MarketAnalyzer with configuration.
      
        Args:
            config: Dictionary containing API configurations.
            cache_timeout: Cache timeout in seconds.
          
        Raises:
            ValueError: If required configuration keys are missing.
        """
        self.config = config
        self.cache_timeout = cache_timeout
        self._validate_config()
      
    def analyze_symbol(
        self, 
        symbol: str, 
        period: str = "1y",
        indicators: Optional[List[str]] = None
    ) -> Dict[str, Union[float, Dict[str, float]]]:
        """Analyze market data for a given symbol.
      
        Args:
            symbol: Stock symbol (e.g., 'AAPL').
            period: Analysis period ('1d', '1w', '1m', '3m', '1y').
            indicators: List of technical indicators to calculate.
          
        Returns:
            Dictionary containing analysis results with calculated indicators.
          
        Raises:
            ValueError: If symbol format is invalid.
            APIError: If market data retrieval fails.
        """
        if not self._validate_symbol(symbol):
            raise ValueError(f"Invalid symbol format: {symbol}")
          
        logger.info(f"Starting analysis for symbol: {symbol}")
      
        try:
            market_data = self._fetch_market_data(symbol, period)
            analysis_results = self._calculate_indicators(market_data, indicators)
          
            logger.info(f"Analysis completed for {symbol}")
            return analysis_results
          
        except Exception as e:
            logger.error(f"Analysis failed for {symbol}: {str(e)}")
            raise
```

#### JavaScript Standards

Follow modern ES6+ standards with the following guidelines:

- **Module System**: Use ES6 modules with import/export
- **Async/Await**: Prefer async/await over Promise chains
- **Error Handling**: Implement comprehensive error handling
- **Documentation**: JSDoc comments for all public methods

Example:

```javascript
/**
 * Market data management and visualization module.
 * @module MarketManager
 */

/**
 * Manages real-time market data and chart visualization.
 */
class MarketManager {
    /**
     * Create a MarketManager instance.
     * @param {Object} config - Configuration object
     * @param {string} config.apiBaseUrl - Base URL for API calls
     * @param {number} config.refreshInterval - Data refresh interval in ms
     */
    constructor(config) {
        this.config = config;
        this.cache = new Map();
        this.subscribers = new Set();
        this.isInitialized = false;
    }
  
    /**
     * Fetch market data for a specific symbol.
     * @param {string} symbol - Stock symbol
     * @param {string} period - Time period for data
     * @returns {Promise<Object>} Market data object
     * @throws {Error} When API call fails or data is invalid
     */
    async fetchMarketData(symbol, period = '1y') {
        try {
            this._validateSymbol(symbol);
          
            const cacheKey = `${symbol}-${period}`;
            if (this.cache.has(cacheKey)) {
                return this.cache.get(cacheKey);
            }
          
            const url = `${this.config.apiBaseUrl}/market-data/${symbol}`;
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });
          
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
          
            const data = await response.json();
            this._validateMarketData(data);
          
            this.cache.set(cacheKey, data);
            return data;
          
        } catch (error) {
            console.error(`Failed to fetch market data for ${symbol}:`, error);
            throw new Error(`Market data fetch failed: ${error.message}`);
        }
    }
  
    /**
     * Validate stock symbol format.
     * @private
     * @param {string} symbol - Symbol to validate
     * @throws {Error} When symbol format is invalid
     */
    _validateSymbol(symbol) {
        if (!symbol || typeof symbol !== 'string') {
            throw new Error('Symbol must be a non-empty string');
        }
      
        const symbolRegex = /^[A-Z]{1,5}$/;
        if (!symbolRegex.test(symbol)) {
            throw new Error('Symbol must be 1-5 uppercase letters');
        }
    }
}

export default MarketManager;
```

### Git Workflow Standards

#### Branch Naming Convention

- **Feature branches**: `feature/description-of-feature`
- **Bug fixes**: `fix/description-of-bug`
- **Documentation**: `docs/description-of-changes`
- **Refactoring**: `refactor/description-of-refactor`

#### Commit Message Standards

Follow Conventional Commits specification:

```
type(scope): description

[optional body]

[optional footer]
```

**Types**:

- `feat`: New feature implementation
- `fix`: Bug fix
- `docs`: Documentation updates
- `style`: Code formatting changes
- `refactor`: Code refactoring without feature changes
- `test`: Test additions or modifications
- `chore`: Maintenance tasks

**Examples**:

```
feat(agents): implement portfolio risk assessment agent
fix(api): resolve market data caching issue
docs(contributing): update development setup instructions
test(utils): add comprehensive validation tests
```

## Testing Requirements

### Test Architecture

Tests are organized into three categories:

#### Unit Tests

- **Location**: `src/tests/unit/`
- **Purpose**: Test individual functions and classes in isolation
- **Coverage**: Minimum 90% code coverage required

#### Integration Tests

- **Location**: `src/tests/integration/`
- **Purpose**: Test component interactions and API endpoints
- **Requirements**: Test with mock external services

#### End-to-End Tests

- **Location**: `src/tests/e2e/`
- **Purpose**: Test complete user workflows
- **Tools**: Selenium WebDriver for browser automation

### Testing Standards

#### Pytest Configuration (`pytest.ini`)

```ini
[tool:pytest]
testpaths = src/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --verbose
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=90
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
```

#### Test Implementation Example

```python
"""
Unit tests for market data analyzer.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from src.agents.market_analyzer import MarketAnalyzer
from src.utils.exceptions import ValidationError, APIError


class TestMarketAnalyzer:
    """Test suite for MarketAnalyzer class."""
  
    @pytest.fixture
    def analyzer_config(self):
        """Provide test configuration for MarketAnalyzer."""
        return {
            'api_key': 'test_api_key',
            'base_url': 'https://test-api.example.com',
            'timeout': 30
        }
  
    @pytest.fixture
    def market_analyzer(self, analyzer_config):
        """Provide MarketAnalyzer instance for testing."""
        return MarketAnalyzer(analyzer_config)
  
    @pytest.fixture
    def sample_market_data(self):
        """Provide sample market data for testing."""
        return {
            'symbol': 'AAPL',
            'price': 150.25,
            'volume': 1000000,
            'timestamp': datetime.now().isoformat()
        }
  
    def test_analyzer_initialization_success(self, analyzer_config):
        """Test successful analyzer initialization."""
        analyzer = MarketAnalyzer(analyzer_config)
        assert analyzer.config == analyzer_config
        assert analyzer.cache_timeout == 300  # default value
  
    def test_analyzer_initialization_missing_config(self):
        """Test analyzer initialization with missing configuration."""
        with pytest.raises(ValueError, match="Missing required configuration"):
            MarketAnalyzer({})
  
    @patch('src.agents.market_analyzer.external_api_call')
    def test_analyze_symbol_success(self, mock_api_call, market_analyzer, sample_market_data):
        """Test successful symbol analysis."""
        # Arrange
        mock_api_call.return_value = sample_market_data
        symbol = 'AAPL'
      
        # Act
        result = market_analyzer.analyze_symbol(symbol)
      
        # Assert
        assert result['symbol'] == symbol
        assert 'technical_indicators' in result
        mock_api_call.assert_called_once_with(symbol, '1y')
  
    def test_analyze_symbol_invalid_format(self, market_analyzer):
        """Test symbol analysis with invalid symbol format."""
        invalid_symbols = ['', 'TOOLONG', '123', 'aa', None]
      
        for symbol in invalid_symbols:
            with pytest.raises(ValueError, match="Invalid symbol format"):
                market_analyzer.analyze_symbol(symbol)
  
    @patch('src.agents.market_analyzer.external_api_call')
    def test_analyze_symbol_api_failure(self, mock_api_call, market_analyzer):
        """Test symbol analysis when external API fails."""
        # Arrange
        mock_api_call.side_effect = APIError("External service unavailable")
      
        # Act & Assert
        with pytest.raises(APIError):
            market_analyzer.analyze_symbol('AAPL')
  
    @pytest.mark.integration
    def test_full_analysis_workflow(self, market_analyzer):
        """Integration test for complete analysis workflow."""
        # This test would use actual API calls in integration environment
        pass
  
    @pytest.mark.slow
    def test_performance_large_dataset(self, market_analyzer):
        """Test analyzer performance with large datasets."""
        # Performance testing code
        pass
```

### Test Execution

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m "not slow"

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest src/tests/unit/test_market_analyzer.py

# Run with verbose output and debugging
pytest -v -s --pdb
```

## API Development Guidelines

### API Design Principles

1. **RESTful Design**: Follow REST conventions for resource-based URLs
2. **Stateless**: Each request must contain all necessary information
3. **Idempotent**: GET, PUT, DELETE operations should be idempotent
4. **Versioning**: Use URL versioning (e.g., `/api/v1/`)
5. **Error Handling**: Consistent error response format

### Endpoint Implementation

#### Flask Route Example

```python
"""
API routes for market data endpoints.
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any
import logging

from src.agents.market_analyzer import MarketAnalyzer
from src.utils.validation import validate_symbol, validate_period
from src.utils.exceptions import ValidationError, APIError
from src.utils.auth import require_auth, get_current_user

logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


@api_bp.route('/market-data/<symbol>', methods=['GET'])
@require_auth
def get_market_data(symbol: str) -> Dict[str, Any]:
    """
    Retrieve market data for a specific symbol.
  
    Args:
        symbol: Stock symbol (path parameter)
      
    Query Parameters:
        period: Time period (1d, 1w, 1m, 3m, 1y)
        indicators: Comma-separated list of technical indicators
      
    Returns:
        JSON response with market data and analysis
      
    Raises:
        400: Invalid symbol or parameters
        401: Authentication required
        404: Symbol not found
        500: Internal server error
    """
    try:
        # Validate input parameters
        if not validate_symbol(symbol):
            return jsonify({
                'error': 'Invalid symbol format',
                'message': 'Symbol must be 1-5 uppercase letters',
                'timestamp': datetime.now().isoformat()
            }), 400
      
        period = request.args.get('period', '1y')
        if not validate_period(period):
            return jsonify({
                'error': 'Invalid period',
                'message': 'Period must be one of: 1d, 1w, 1m, 3m, 1y',
                'timestamp': datetime.now().isoformat()
            }), 400
      
        indicators = request.args.get('indicators', '').split(',') if request.args.get('indicators') else None
      
        # Get current user context
        user = get_current_user()
      
        # Process request
        analyzer = MarketAnalyzer(current_app.config['MARKET_CONFIG'])
        result = analyzer.analyze_symbol(
            symbol=symbol,
            period=period,
            indicators=indicators
        )
      
        # Add metadata
        response_data = {
            'symbol': symbol,
            'period': period,
            'data': result,
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'user_id': user.id if user else None,
                'request_id': request.headers.get('X-Request-ID')
            }
        }
      
        logger.info(f"Market data request completed for {symbol}", extra={
            'symbol': symbol,
            'period': period,
            'user_id': user.id if user else None
        })
      
        return jsonify(response_data), 200
      
    except ValidationError as e:
        logger.warning(f"Validation error for symbol {symbol}: {str(e)}")
        return jsonify({
            'error': 'Validation failed',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 400
      
    except APIError as e:
        logger.error(f"API error for symbol {symbol}: {str(e)}")
        return jsonify({
            'error': 'External service error',
            'message': 'Unable to retrieve market data',
            'timestamp': datetime.now().isoformat()
        }), 503
      
    except Exception as e:
        logger.error(f"Unexpected error for symbol {symbol}: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred',
            'timestamp': datetime.now().isoformat()
        }), 500


@api_bp.errorhandler(404)
def handle_not_found(e):
    """Handle 404 errors with consistent format."""
    return jsonify({
        'error': 'Resource not found',
        'message': 'The requested resource was not found',
        'timestamp': datetime.now().isoformat()
    }), 404


@api_bp.errorhandler(500)
def handle_internal_error(e):
    """Handle 500 errors with consistent format."""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An internal error occurred',
        'timestamp': datetime.now().isoformat()
    }), 500
```

### API Documentation

All endpoints must include comprehensive OpenAPI documentation:

```python
@api_bp.route('/market-data/<symbol>', methods=['GET'])
def get_market_data(symbol: str):
    """
    Get Market Data
    ---
    tags:
      - Market Data
    parameters:
      - name: symbol
        in: path
        type: string
        required: true
        description: Stock symbol (1-5 uppercase letters)
        example: AAPL
      - name: period
        in: query
        type: string
        required: false
        description: Time period for data
        enum: [1d, 1w, 1m, 3m, 1y]
        default: 1y
      - name: indicators
        in: query
        type: string
        required: false
        description: Comma-separated technical indicators
        example: sma,rsi,macd
    responses:
      200:
        description: Market data retrieved successfully
        schema:
          type: object
          properties:
            symbol:
              type: string
              example: AAPL
            data:
              type: object
              properties:
                price:
                  type: number
                  example: 150.25
                volume:
                  type: integer
                  example: 1000000
      400:
        description: Invalid input parameters
      401:
        description: Authentication required
      500:
        description: Internal server error
    """
```

## Frontend Development Standards

### Component Architecture

Frontend components follow a modular, event-driven architecture:

```javascript
/**
 * Base component class for all UI components.
 * @abstract
 */
class BaseComponent {
    /**
     * Create a component instance.
     * @param {HTMLElement} container - Container element
     * @param {Object} options - Component options
     */
    constructor(container, options = {}) {
        this.container = container;
        this.options = { ...this.getDefaultOptions(), ...options };
        this.state = {};
        this.eventListeners = new Map();
        this.isInitialized = false;
    }
  
    /**
     * Get default component options.
     * @abstract
     * @returns {Object} Default options
     */
    getDefaultOptions() {
        return {};
    }
  
    /**
     * Initialize the component.
     * @async
     * @returns {Promise<void>}
     */
    async init() {
        if (this.isInitialized) {
            return;
        }
      
        try {
            await this.render();
            this.attachEventListeners();
            this.isInitialized = true;
            this.emit('initialized');
        } catch (error) {
            console.error(`Failed to initialize component:`, error);
            throw error;
        }
    }
  
    /**
     * Render component HTML.
     * @abstract
     * @async
     * @returns {Promise<void>}
     */
    async render() {
        throw new Error('render() method must be implemented');
    }
  
    /**
     * Attach event listeners.
     * @abstract
     */
    attachEventListeners() {
        // Override in subclasses
    }
  
    /**
     * Update component state.
     * @param {Object} newState - New state properties
     */
    setState(newState) {
        const oldState = { ...this.state };
        this.state = { ...this.state, ...newState };
        this.onStateChange(this.state, oldState);
    }
  
    /**
     * Handle state changes.
     * @param {Object} newState - New state
     * @param {Object} oldState - Previous state
     */
    onStateChange(newState, oldState) {
        // Override in subclasses
    }
  
    /**
     * Emit custom event.
     * @param {string} eventName - Event name
     * @param {*} data - Event data
     */
    emit(eventName, data = null) {
        const event = new CustomEvent(eventName, { detail: data });
        this.container.dispatchEvent(event);
    }
  
    /**
     * Destroy component and clean up resources.
     */
    destroy() {
        this.eventListeners.forEach((listener, element) => {
            element.removeEventListener(listener.event, listener.handler);
        });
        this.eventListeners.clear();
        this.isInitialized = false;
    }
}
```

### Chart Implementation Standards

```javascript
/**
 * Market chart component for data visualization.
 * @extends BaseComponent
 */
class MarketChart extends BaseComponent {
    getDefaultOptions() {
        return {
            theme: 'dark',
            responsive: true,
            height: 400,
            showToolbar: false,
            indicators: ['sma', 'volume']
        };
    }
  
    async render() {
        this.container.innerHTML = `
            <div class="chart-container">
                <div class="chart-header">
                    <h3 class="chart-title" id="chart-title">Loading...</h3>
                    <div class="chart-controls">
                        <select id="period-select" class="chart-select">
                            <option value="1d">1 Day</option>
                            <option value="1w">1 Week</option>
                            <option value="1m">1 Month</option>
                            <option value="3m">3 Months</option>
                            <option value="1y" selected>1 Year</option>
                        </select>
                    </div>
                </div>
                <div class="chart-content" id="chart-content"></div>
                <div class="chart-loading hidden" id="chart-loading">
                    <div class="loading-spinner"></div>
                    <p>Loading chart data...</p>
                </div>
            </div>
        `;
    }
  
    attachEventListeners() {
        const periodSelect = this.container.querySelector('#period-select');
        if (periodSelect) {
            periodSelect.addEventListener('change', (e) => {
                this.updatePeriod(e.target.value);
            });
        }
    }
  
    /**
     * Update chart with new data.
     * @param {string} symbol - Stock symbol
     * @param {Object} data - Chart data
     */
    async updateChart(symbol, data) {
        try {
            this.showLoading();
          
            const chartData = this.prepareChartData(data);
            const layout = this.getChartLayout();
            const config = this.getChartConfig();
          
            await Plotly.newPlot(
                this.container.querySelector('#chart-content'),
                chartData,
                layout,
                config
            );
          
            this.updateTitle(symbol);
            this.hideLoading();
          
            this.emit('chartUpdated', { symbol, data });
          
        } catch (error) {
            console.error('Failed to update chart:', error);
            this.showError('Failed to load chart data');
        }
    }
  
    prepareChartData(data) {
        return [{
            x: data.dates,
            y: data.prices,
            type: 'scatter',
            mode: 'lines',
            name: 'Price',
            line: {
                color: '#00d2ff',
                width: 2
            }
        }];
    }
  
    getChartLayout() {
        return {
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { 
                color: '#ffffff',
                family: 'Inter, sans-serif'
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
            height: this.options.height
        };
    }
  
    getChartConfig() {
        return {
            displayModeBar: this.options.showToolbar,
            responsive: this.options.responsive,
            displaylogo: false
        };
    }
  
    showLoading() {
        const loading = this.container.querySelector('#chart-loading');
        const content = this.container.querySelector('#chart-content');
      
        if (loading) loading.classList.remove('hidden');
        if (content) content.style.opacity = '0.3';
    }
  
    hideLoading() {
        const loading = this.container.querySelector('#chart-loading');
        const content = this.container.querySelector('#chart-content');
      
        if (loading) loading.classList.add('hidden');
        if (content) content.style.opacity = '1';
    }
  
    showError(message) {
        this.container.querySelector('#chart-content').innerHTML = `
            <div class="chart-error">
                <i class="fas fa-exclamation-triangle"></i>
                <p>${message}</p>
                <button class="btn btn-secondary" onclick="location.reload()">
                    Retry
                </button>
            </div>
        `;
        this.hideLoading();
    }
}
```

## Quality Assurance

### Code Quality Tools

#### Linting Configuration (`.flake8`)

```ini
[flake8]
max-line-length = 88
select = E,W,F
ignore = 
    E203,  # whitespace before ':'
    E501,  # line too long (handled by black)
    W503,  # line break before binary operator
exclude = 
    .git,
    __pycache__,
    venv,
    .venv,
    build,
    dist,
    *.egg-info
```

#### Pre-commit Configuration (`.pre-commit-config.yaml`)

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
    
  - repo: https://github.com/psf/black
    rev: 22.12.0
    hooks:
      - id: black
        language_version: python3
      
  - repo: https://github.com/pycqa/isort
    rev: 5.11.4
    hooks:
      - id: isort
        args: ["--profile", "black"]
      
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
      
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.991
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

### Performance Standards

#### Performance Monitoring

```python
"""
Performance monitoring utilities.
"""

import time
import functools
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)


def monitor_performance(threshold_seconds: float = 1.0):
    """
    Decorator to monitor function execution time.
  
    Args:
        threshold_seconds: Log warning if execution exceeds this threshold
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                execution_time = time.time() - start_time
              
                if execution_time > threshold_seconds:
                    logger.warning(
                        f"Function {func.__name__} took {execution_time:.2f}s "
                        f"(threshold: {threshold_seconds}s)"
                    )
                else:
                    logger.debug(f"Function {func.__name__} took {execution_time:.2f}s")
                  
        return wrapper
    return decorator


class PerformanceTracker:
    """Track and report application performance metrics."""
  
    def __init__(self):
        self.metrics = {}
      
    def record_metric(self, name: str, value: float, unit: str = 'ms'):
        """Record a performance metric."""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append({'value': value, 'unit': unit, 'timestamp': time.time()})
      
    def get_average(self, name: str) -> float:
        """Get average value for a metric."""
        if name not in self.metrics:
            return 0.0
        values = [m['value'] for m in self.metrics[name]]
        return sum(values) / len(values)
      
    def report(self) -> dict:
        """Generate performance report."""
        report = {}
        for name, metrics in self.metrics.items():
            values = [m['value'] for m in metrics]
            report[name] = {
                'count': len(values),
                'average': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'unit': metrics[0]['unit'] if metrics else 'unknown'
            }
        return report
```

## Deployment Procedures

### Production Configuration

#### Environment Configuration

```python
"""
Production configuration settings.
"""

import os
from typing import Dict, Any


class ProductionConfig:
    """Production environment configuration."""
  
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
  
    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL')
    DATABASE_POOL_SIZE = int(os.environ.get('DATABASE_POOL_SIZE', '10'))
  
    # External APIs
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')
  
    # Cache
    REDIS_URL = os.environ.get('REDIS_URL')
    CACHE_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', '300'))
  
    # Application
    DEBUG = False
    TESTING = False
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
  
    # Performance
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', '30'))
  
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        required_vars = [
            'SECRET_KEY',
            'JWT_SECRET_KEY',
            'DATABASE_URL',
            'OPENAI_API_KEY'
        ]
      
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        if missing_vars:
            raise EnvironmentError(f"Missing required environment variables: {missing_vars}")
```

#### Docker Configuration

```dockerfile
# Production Dockerfile
FROM python:3.9-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN useradd --create-home --shell /bin/bash appuser

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt requirements-prod.txt ./
RUN pip install --no-cache-dir -r requirements-prod.txt

# Production stage
FROM python:3.9-slim as production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN useradd --create-home --shell /bin/bash appuser

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to application user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5000/api/v1/health || exit 1

# Expose port
EXPOSE 5000

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=web_server.py
ENV FLASK_ENV=production

# Start application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "30", "web_server:app"]
```

## Submission Requirements

### Pull Request Process

1. **Pre-submission Checklist**:

   - [ ] Code follows style guidelines
   - [ ] Documentation updated
   - [ ] No security vulnerabilities introduced
2. **Branch Preparation**:

   ```bash
   # Ensure branch is up to date
   git fetch upstream
   git rebase upstream/main

   # Run quality checks
   python -m pytest
   python -m flake8 src/
   python -m black src/ --check
   python -m mypy src/
   ```
3. **Pull Request Template**:

```markdown
## Summary

Brief description of changes made and problem solved.

## Type of Change

- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Changes Made

- Detailed list of changes
- Include any new dependencies
- Note any configuration changes required

## Testing

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed
- [ ] Performance impact assessed

### Test Coverage

Current coverage: ___%
New/modified files coverage: ___%

## Documentation

- [ ] Code comments added/updated
- [ ] API documentation updated
- [ ] User documentation updated
- [ ] README updated if necessary

## Security Considerations

- [ ] No sensitive data exposed
- [ ] Input validation implemented
- [ ] Authentication/authorization maintained
- [ ] No new security vulnerabilities

## Performance Impact

- [ ] No significant performance degradation
- [ ] Database queries optimized
- [ ] Caching strategy considered
- [ ] Memory usage acceptable

## Deployment Notes

Any special deployment considerations or migration steps required.

## Screenshots

Include screenshots for UI changes.

## Related Issues

Fixes #(issue number)
Related to #(issue number)
```

### Code Review Guidelines

#### For Authors

1. **Self-Review**: Review your own code before submitting
2. **Clear Description**: Provide comprehensive PR description
3. **Small Changes**: Keep PRs focused and reasonably sized
4. **Documentation**: Update relevant documentation
5. **Tests**: Include appropriate test coverage

#### For Reviewers

1. **Functionality**: Verify code solves the stated problem
2. **Code Quality**: Check adherence to style guidelines
3. **Architecture**: Ensure changes align with project architecture
4. **Security**: Review for potential security issues
5. **Performance**: Consider performance implications
6. **Testing**: Verify adequate test coverage

### Release Process

#### Version Management

Follow Semantic Versioning (SemVer):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

#### Release Checklist

1. **Pre-release**:

   - [ ] All tests pass
   - [ ] Documentation updated
   - [ ] Security scan completed
   - [ ] Performance benchmarks acceptable
2. **Release**:

   - [ ] Version number updated
   - [ ] Changelog updated
   - [ ] Git tag created
   - [ ] Docker images built and pushed
3. **Post-release**:

   - [ ] Deployment verified
   - [ ] Monitoring alerts configured
   - [ ] Documentation published

This contributing guide ensures consistent, high-quality contributions to the Financial Research Assistant project. All contributors must adhere to these standards to maintain code quality, security, and performance standards.
