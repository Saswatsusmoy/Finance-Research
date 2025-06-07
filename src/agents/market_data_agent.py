from typing import Dict, Any, List, Optional
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import asyncio
import logging
from pydantic import BaseModel, Field

from src.agents.base_agent import BaseAgent, AgentState

class MarketDataState(AgentState):
    """State for the market data agent"""
    cached_data: Dict[str, Any] = Field(default_factory=dict)
    data_sources: List[str] = Field(default_factory=lambda: ["yahoo_finance"])
    last_cache_update: Optional[datetime] = None
    cache_duration: int = 3600  # Cache duration in seconds (default: 1 hour)

class MarketDataAgent(BaseAgent):
    """Agent responsible for fetching and processing market data"""
    
    def __init__(self, agent_id: str = "market_data_agent"):
        """Initialize the market data agent"""
        super().__init__(agent_id, "market_data")
        self.state = MarketDataState(agent_id=agent_id, agent_type="market_data")
        self.logger = logging.getLogger(__name__)
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the market data agent's main functionality"""
        self.update_status("running")
        
        try:
            # Extract parameters from input data
            symbols = input_data.get("symbols", [])
            start_date = input_data.get("start_date")
            end_date = input_data.get("end_date")
            interval = input_data.get("interval", "1d")
            
            # Fetch data for each symbol
            results = {}
            for symbol in symbols:
                self.state.add_message("system", f"Fetching data for {symbol}")
                data = await self.fetch_market_data(symbol, start_date, end_date, interval)
                results[symbol] = data
            
            self.update_status("idle")
            return {"status": "success", "data": results}
        
        except Exception as e:
            self.logger.error(f"Error in market data agent: {str(e)}")
            self.update_status("error")
            self.state.add_message("system", f"Error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def process(self, query: str) -> Dict[str, Any]:
        """Process a specific query related to market data"""
        self.update_status("processing")
        self.state.add_message("user", query)
        
        # Simple query processing logic
        if "price" in query.lower():
            # Extract symbol from query
            # This is a simple implementation - in a real system you'd use NLP
            words = query.split()
            symbols = [word.upper() for word in words if word.isupper() and len(word) <= 5]
            
            if not symbols:
                response = {"status": "error", "message": "No stock symbol found in query"}
            else:
                results = {}
                for symbol in symbols:
                    data = await self.get_latest_price(symbol)
                    results[symbol] = data
                
                response = {"status": "success", "data": results}
        
        elif "historical" in query.lower():
            # Extract symbol and date range from query
            # Again, this is simplified - use NLP in real implementation
            words = query.split()
            symbols = [word.upper() for word in words if word.isupper() and len(word) <= 5]
            
            if not symbols:
                response = {"status": "error", "message": "No stock symbol found in query"}
            else:
                # Default to last 30 days
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                
                results = {}
                for symbol in symbols:
                    data = await self.fetch_market_data(symbol, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
                    results[symbol] = data
                
                response = {"status": "success", "data": results}
        
        else:
            response = {"status": "error", "message": "Unsupported query type"}
        
        self.state.add_message("assistant", response)
        self.update_status("idle")
        return response
    
    async def fetch_market_data(self, symbol: str, start_date: str = None, end_date: str = None, interval: str = "1d", market: str = "US") -> Dict[str, Any]:
        """Fetch market data for a given symbol"""
        # Check if data is in cache and still valid
        cache_key = f"{symbol}_{start_date}_{end_date}_{interval}_{market}"
        
        if (cache_key in self.state.cached_data and 
            self.state.last_cache_update and 
            (datetime.now() - self.state.last_cache_update).total_seconds() < self.state.cache_duration):
            return self.state.cached_data[cache_key]
        
        # If not in cache or expired, fetch new data
        try:
            # Try multiple symbol formats for better success rate
            yahoo_symbol, info = await self._try_multiple_symbol_formats(symbol, market)
            
            if not yahoo_symbol or not info:
                # Fallback to simple transformation
                yahoo_symbol = self._transform_symbol_for_yahoo(symbol, market)
                ticker = yf.Ticker(yahoo_symbol)
                info = ticker.info
            else:
                ticker = yf.Ticker(yahoo_symbol)
            
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            
            # Fetch historical data
            hist = ticker.history(start=start_date, end=end_date, interval=interval)
            
            # Check if we got valid historical data
            if hist.empty:
                return {
                    "symbol": symbol, 
                    "error": f"No historical data available for {symbol} in {market} market"
                }
            
            # Convert DataFrame to dict for JSON serialization
            hist_dict = hist.reset_index().to_dict(orient="records")
            
            # Prepare result
            result = {
                "symbol": symbol,
                "company_name": info.get("shortName", ""),
                "historical_data": hist_dict,
                "current_price": info.get("currentPrice", info.get("regularMarketPrice", None)),
                "market_cap": info.get("marketCap", None),
                "pe_ratio": info.get("trailingPE", None),
                "dividend_yield": info.get("dividendYield", None) * 100 if info.get("dividendYield") else None,
                "52_week_high": info.get("fiftyTwoWeekHigh", None),
                "52_week_low": info.get("fiftyTwoWeekLow", None),
                "timestamp": datetime.now().isoformat()
            }
            
            # Cache the result
            self.state.cached_data[cache_key] = result
            self.state.last_cache_update = datetime.now()
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error fetching market data for {symbol}: {str(e)}")
            return {"symbol": symbol, "error": str(e)}
    
    async def get_latest_price(self, symbol: str, market: str = "US") -> Dict[str, Any]:
        """Get the latest price for a symbol"""
        try:
            # Try multiple symbol formats for better success rate
            yahoo_symbol, info = await self._try_multiple_symbol_formats(symbol, market)
            
            if not yahoo_symbol or not info:
                # Fallback to simple transformation
                yahoo_symbol = self._transform_symbol_for_yahoo(symbol, market)
                ticker = yf.Ticker(yahoo_symbol)
                info = ticker.info
            
            # Check if we have valid price data
            current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            if current_price is None:
                return {
                    "symbol": symbol, 
                    "error": f"No price data available for {symbol} in {market} market"
                }
            
            result = {
                "symbol": symbol,
                "company_name": info.get("shortName", info.get("longName", "")),
                "current_price": current_price,
                "change": info.get("regularMarketChange", None),
                "change_percent": info.get("regularMarketChangePercent", None),
                "volume": info.get("regularMarketVolume", None),
                "market_cap": info.get("marketCap", None),
                "currency": info.get("currency", "USD" if market == "US" else "INR"),
                "exchange": info.get("exchange", ""),
                "timestamp": datetime.now().isoformat()
            }
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error getting latest price for {symbol}: {str(e)}")
            return {"symbol": symbol, "error": str(e)}
    
    def add_data_source(self, source: str):
        """Add a data source to the agent"""
        if source not in self.state.data_sources:
            self.state.data_sources.append(source)
    
    def remove_data_source(self, source: str):
        """Remove a data source from the agent"""
        if source in self.state.data_sources:
            self.state.data_sources.remove(source)
    
    def clear_cache(self):
        """Clear the agent's data cache"""
        self.state.cached_data = {}
        self.state.last_cache_update = None
    
    def _transform_symbol_for_yahoo(self, symbol: str, market: str = 'US') -> str:
        """Transform symbol for Yahoo Finance API based on market"""
        # List of known Indian stock symbols that need .NS suffix
        indian_stocks = {
            'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'HINDUNILVR', 
            'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK', 'LT', 'ASIANPAINT', 
            'MARUTI', 'TITAN', 'WIPRO', 'AXISBANK', 'BAJFINANCE', 'HCLTECH', 
            'TECHM', 'ADANIPORTS', 'ONGC', 'NESTLEIND', 'BRITANNIA', 'M&M', 
            'TATAMOTORS', 'BAJAJ-AUTO', 'ULTRACEMCO', 'SUNPHARMA', 'DRREDDY', 
            'TATASTEEL', 'HINDALCO', 'POWERGRID', 'NTPC', 'COALINDIA',
            'JSWSTEEL', 'GRASIM', 'CIPLA', 'DIVISLAB', 'EICHERMOT',
            'HEROMOTOCO', 'BAJAJFINSV', 'SHREECEM', 'INDUSINDBK', 'BPCL'
        }
        
        # If market is Indian or symbol is in Indian stocks list, add .NS suffix
        if (market == 'IN' or symbol.upper() in indian_stocks) and '.' not in symbol:
            return f"{symbol.upper()}.NS"
        
        # For US stocks or already formatted symbols, return as is
        return symbol.upper()
    
    async def _try_multiple_symbol_formats(self, symbol: str, market: str = 'US'):
        """Try multiple symbol formats for better data retrieval"""
        formats_to_try = []
        
        if market == 'IN':
            # For Indian market, try multiple formats
            formats_to_try = [
                f"{symbol.upper()}.NS",  # NSE format
                f"{symbol.upper()}.BO",  # BSE format
                symbol.upper()           # Raw symbol
            ]
        else:
            # For US market
            formats_to_try = [symbol.upper()]
        
        for format_symbol in formats_to_try:
            try:
                ticker = yf.Ticker(format_symbol)
                info = ticker.info
                
                # Check if we got valid data
                if info and (info.get('currentPrice') or info.get('regularMarketPrice')):
                    return format_symbol, info
                    
            except Exception as e:
                self.logger.debug(f"Failed to fetch data for {format_symbol}: {e}")
                continue
        
        # If all formats failed, return None
        return None, None 