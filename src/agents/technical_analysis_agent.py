from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
import logging
import ta
from pydantic import BaseModel, Field

from src.agents.base_agent import BaseAgent, AgentState
from src.agents.market_data_agent import MarketDataAgent
from src.utils.advanced_indicators import (
    calculate_all_indicators,
    calculate_bollinger_bands,
    calculate_ichimoku_cloud,
    calculate_atr,
    calculate_stochastic,
    calculate_parabolic_sar,
    calculate_fibonacci_levels,
    detect_head_and_shoulders,
    detect_double_top_bottom,
    detect_cup_and_handle,
    detect_flag_pennant
)

class TechnicalAnalysisState(AgentState):
    """State for the technical analysis agent"""
    cached_analysis: Dict[str, Any] = Field(default_factory=dict)
    indicators: List[str] = Field(default_factory=lambda: [
        "sma", "ema", "rsi", "macd", "bollinger", "ichimoku", "atr", 
        "stochastic", "psar", "fibonacci", "patterns"
    ])
    last_cache_update: Optional[datetime] = None
    cache_duration: int = 3600  # Cache duration in seconds (default: 1 hour)

class TechnicalAnalysisAgent(BaseAgent):
    """Agent responsible for performing technical analysis"""
    
    def __init__(self, agent_id: str = "technical_analysis_agent", market_data_agent: MarketDataAgent = None):
        """Initialize the technical analysis agent"""
        super().__init__(agent_id, "technical_analysis")
        self.state = TechnicalAnalysisState(agent_id=agent_id, agent_type="technical_analysis")
        self.logger = logging.getLogger(__name__)
        self.market_data_agent = market_data_agent or MarketDataAgent()
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the technical analysis agent's main functionality"""
        self.update_status("running")
        
        try:
            # Extract parameters from input data
            symbol = input_data.get("symbol", "")
            indicators = input_data.get("indicators", self.state.indicators)
            interval = input_data.get("interval", "1d")
            period = input_data.get("period", 100)  # Number of days to analyze
            
            if not symbol:
                raise ValueError("Symbol is required")
            
            # Fetch market data
            self.state.add_message("system", f"Fetching market data for {symbol}")
            
            # Calculate date range
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=period)).strftime("%Y-%m-%d")
            
            # Fetch data using the market data agent
            market_data = await self.market_data_agent.fetch_market_data(
                symbol, start_date, end_date, interval
            )
            
            if "error" in market_data:
                raise ValueError(f"Error fetching market data: {market_data['error']}")
            
            # Convert to DataFrame for analysis
            historical_data = market_data.get("historical_data", [])
            if not historical_data:
                raise ValueError("No historical data available")
            
            df = pd.DataFrame(historical_data)
            
            # Ensure date column is datetime
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"])
            
            # Perform technical analysis
            self.state.add_message("system", "Performing technical analysis")
            
            # For advanced analysis, we need more data points
            if any(ind in indicators for ind in ["patterns", "ichimoku", "fibonacci"]):
                # Ensure we have sufficient data for pattern detection
                if len(df) < 60:
                    self.state.add_message("system", "Warning: Limited data available for pattern detection")
            
            # Perform analysis based on requested indicators
            analysis_results = await self.analyze_data(df, indicators)
            
            # Detect patterns if requested
            patterns = {}
            if "patterns" in indicators:
                self.state.add_message("system", "Detecting chart patterns")
                patterns = await self.detect_patterns(df)
            
            # Generate signals
            self.state.add_message("system", "Generating signals")
            signals = await self.generate_signals(df, analysis_results)
            
            # Combine results
            result = {
                "symbol": symbol,
                "analysis_date": datetime.now().isoformat(),
                "indicators": analysis_results,
                "patterns": patterns,
                "signals": signals
            }
            
            # Cache the result
            cache_key = f"{symbol}_{interval}_{period}"
            self.state.cached_analysis[cache_key] = result
            self.state.last_cache_update = datetime.now()
            
            self.update_status("idle")
            return {"status": "success", "data": result}
        
        except Exception as e:
            self.logger.error(f"Error in technical analysis agent: {str(e)}")
            self.update_status("error")
            self.state.add_message("system", f"Error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def process(self, query: str) -> Dict[str, Any]:
        """Process a specific query related to technical analysis"""
        self.update_status("processing")
        self.state.add_message("user", query)
        
        # Simple query processing logic
        query_lower = query.lower()
        
        # Extract symbol from query
        import re
        symbols = re.findall(r'\b[A-Z]{1,5}\b', query)
        symbol = symbols[0] if symbols else None
        
        if not symbol:
            response = {"status": "error", "message": "No stock symbol found in query"}
            self.state.add_message("assistant", response)
            self.update_status("idle")
            return response
        
        # Determine indicators to analyze
        indicators = []
        if "all" in query_lower or "full" in query_lower or "advanced" in query_lower:
            indicators = self.state.indicators
        else:
            # Basic indicators
            if "sma" in query_lower or "moving average" in query_lower:
                indicators.append("sma")
            if "ema" in query_lower:
                indicators.append("ema")
            if "rsi" in query_lower:
                indicators.append("rsi")
            if "macd" in query_lower:
                indicators.append("macd")
            if "bollinger" in query_lower:
                indicators.append("bollinger")
            if "support" in query_lower or "resistance" in query_lower:
                indicators.append("support_resistance")
                
            # Advanced indicators
            if "ichimoku" in query_lower or "cloud" in query_lower:
                indicators.append("ichimoku")
            if "atr" in query_lower or "volatility" in query_lower:
                indicators.append("atr")
            if "stochastic" in query_lower or "stoch" in query_lower:
                indicators.append("stochastic")
            if "parabolic" in query_lower or "sar" in query_lower or "psar" in query_lower:
                indicators.append("psar")
            if "fibonacci" in query_lower or "fib" in query_lower or "retracement" in query_lower:
                indicators.append("fibonacci")
                
            # Pattern recognition
            if "pattern" in query_lower or "head" in query_lower or "shoulder" in query_lower or \
               "double" in query_lower or "cup" in query_lower or "handle" in query_lower or \
               "flag" in query_lower or "pennant" in query_lower or "formation" in query_lower:
                indicators.append("patterns")
        
        # If no specific indicators mentioned, use basic ones
        if not indicators:
            indicators = ["sma", "ema", "rsi", "macd", "bollinger"]
        
        # Determine time period
        period = 100  # Default to 100 days
        if "year" in query_lower:
            period = 365
        elif "month" in query_lower:
            period = 30
        elif "week" in query_lower:
            period = 7
        elif "long" in query_lower or "pattern" in query_lower:
            # Patterns need more data
            period = 200
        
        # Run analysis
        result = await self.run({
            "symbol": symbol,
            "indicators": indicators,
            "period": period
        })
        
        self.state.add_message("assistant", result)
        self.update_status("idle")
        return result
    
    async def analyze_data(self, df: pd.DataFrame, indicators: List[str]) -> Dict[str, Any]:
        """Perform technical analysis on the data"""
        results = {}
        
        # Ensure we have the necessary columns
        required_columns = ["Open", "High", "Low", "Close", "Volume"]
        for col in required_columns:
            if col not in df.columns:
                # Try lowercase
                lower_col = col.lower()
                if lower_col in df.columns:
                    df[col] = df[lower_col]
                else:
                    raise ValueError(f"Required column {col} not found in data")
        
        # Calculate Simple Moving Averages
        if "sma" in indicators:
            results["sma"] = {
                "sma_20": df["Close"].rolling(window=20).mean().iloc[-1],
                "sma_50": df["Close"].rolling(window=50).mean().iloc[-1],
                "sma_200": df["Close"].rolling(window=200).mean().iloc[-1]
            }
        
        # Calculate Exponential Moving Averages
        if "ema" in indicators:
            results["ema"] = {
                "ema_12": df["Close"].ewm(span=12, adjust=False).mean().iloc[-1],
                "ema_26": df["Close"].ewm(span=26, adjust=False).mean().iloc[-1],
                "ema_50": df["Close"].ewm(span=50, adjust=False).mean().iloc[-1]
            }
        
        # Calculate RSI
        if "rsi" in indicators:
            rsi = ta.momentum.RSIIndicator(df["Close"], window=14)
            results["rsi"] = {
                "rsi_14": rsi.rsi().iloc[-1]
            }
        
        # Calculate MACD
        if "macd" in indicators:
            macd = ta.trend.MACD(df["Close"])
            results["macd"] = {
                "macd_line": macd.macd().iloc[-1],
                "signal_line": macd.macd_signal().iloc[-1],
                "histogram": macd.macd_diff().iloc[-1]
            }
        
        # Calculate Bollinger Bands
        if "bollinger" in indicators:
            temp_df = calculate_bollinger_bands(df.copy())
            results["bollinger"] = {
                "upper_band": temp_df['bb_high'].iloc[-1],
                "middle_band": temp_df['bb_mid'].iloc[-1],
                "lower_band": temp_df['bb_low'].iloc[-1],
                "width": temp_df['bb_width'].iloc[-1],
                "percent_b": temp_df['bb_pct_b'].iloc[-1]
            }
        
        # Calculate Ichimoku Cloud
        if "ichimoku" in indicators:
            temp_df = calculate_ichimoku_cloud(df.copy())
            results["ichimoku"] = {
                "tenkan_sen": temp_df['ichimoku_conversion_line'].iloc[-1],
                "kijun_sen": temp_df['ichimoku_base_line'].iloc[-1],
                "senkou_span_a": temp_df['ichimoku_a'].iloc[-1],
                "senkou_span_b": temp_df['ichimoku_b'].iloc[-1],
                "chikou_span": temp_df['ichimoku_lagging_line'].iloc[-26] if len(temp_df) > 26 else None
            }
        
        # Calculate ATR
        if "atr" in indicators:
            temp_df = calculate_atr(df.copy())
            results["atr"] = {
                "atr_14": temp_df['atr'].iloc[-1]
            }
        
        # Calculate Stochastic Oscillator
        if "stochastic" in indicators:
            temp_df = calculate_stochastic(df.copy())
            results["stochastic"] = {
                "k_value": temp_df['stoch_k'].iloc[-1],
                "d_value": temp_df['stoch_d'].iloc[-1]
            }
        
        # Calculate Parabolic SAR
        if "psar" in indicators:
            temp_df = calculate_parabolic_sar(df.copy())
            results["psar"] = {
                "psar_value": temp_df['psar'].iloc[-1],
                "trend": "Uptrend" if temp_df['psar_up_indicator'].iloc[-1] else "Downtrend"
            }
        
        # Calculate Fibonacci Levels
        if "fibonacci" in indicators:
            results["fibonacci"] = calculate_fibonacci_levels(df)
        
        # Calculate Support and Resistance levels
        if "support_resistance" in indicators:
            support, resistance = self._calculate_support_resistance(df)
            results["support_resistance"] = {
                "support_levels": support,
                "resistance_levels": resistance
            }
        
        return results
    
    async def detect_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect chart patterns using the advanced pattern recognition functions"""
        patterns = {}
        
        # Detect head and shoulders pattern
        h_and_s = detect_head_and_shoulders(df)
        if h_and_s.get("detected", False):
            patterns["head_and_shoulders"] = h_and_s
        
        # Detect double top/bottom
        double_pattern = detect_double_top_bottom(df)
        if double_pattern.get("detected", False):
            patterns["double_pattern"] = double_pattern
        
        # Detect cup and handle
        cup_handle = detect_cup_and_handle(df)
        if cup_handle.get("detected", False):
            patterns["cup_and_handle"] = cup_handle
        
        # Detect flag/pennant
        flag_pennant = detect_flag_pennant(df)
        if flag_pennant.get("detected", False):
            patterns["flag_pennant"] = flag_pennant
        
        # Add a summary of detected patterns
        detected_patterns = [k for k, v in patterns.items() if v.get("detected", False)]
        patterns["summary"] = {
            "detected_count": len(detected_patterns),
            "detected_patterns": detected_patterns
        }
        
        return patterns
    
    async def generate_signals(self, df: pd.DataFrame, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading signals based on the technical analysis"""
        signals = {}
        
        # Current price
        current_price = df["Close"].iloc[-1]
        
        # Moving Average signals
        if "sma" in analysis_results and "ema" in analysis_results:
            sma_20 = analysis_results["sma"]["sma_20"]
            sma_50 = analysis_results["sma"]["sma_50"]
            sma_200 = analysis_results["sma"]["sma_200"]
            ema_12 = analysis_results["ema"]["ema_12"]
            ema_26 = analysis_results["ema"]["ema_26"]
            
            # Golden Cross / Death Cross
            golden_cross = sma_50 > sma_200 and sma_50 < sma_200 * 1.01  # SMA50 just crossed above SMA200
            death_cross = sma_50 < sma_200 and sma_50 > sma_200 * 0.99   # SMA50 just crossed below SMA200
            
            # EMA crossover
            ema_crossover_bullish = ema_12 > ema_26 and ema_12 < ema_26 * 1.01
            ema_crossover_bearish = ema_12 < ema_26 and ema_12 > ema_26 * 0.99
            
            # Price vs MA
            price_above_ma50 = current_price > sma_50
            price_above_ma200 = current_price > sma_200
            
            signals["moving_averages"] = {
                "golden_cross": golden_cross,
                "death_cross": death_cross,
                "ema_crossover_bullish": ema_crossover_bullish,
                "ema_crossover_bearish": ema_crossover_bearish,
                "price_above_ma50": price_above_ma50,
                "price_above_ma200": price_above_ma200,
                "trend": "Bullish" if price_above_ma50 and price_above_ma200 else 
                         "Bearish" if not price_above_ma50 and not price_above_ma200 else 
                         "Mixed"
            }
        
        # RSI signals
        if "rsi" in analysis_results:
            rsi_14 = analysis_results["rsi"]["rsi_14"]
            
            signals["rsi"] = {
                "value": rsi_14,
                "overbought": rsi_14 > 70,
                "oversold": rsi_14 < 30,
                "signal": "Sell" if rsi_14 > 70 else "Buy" if rsi_14 < 30 else "Neutral"
            }
        
        # MACD signals
        if "macd" in analysis_results:
            macd_line = analysis_results["macd"]["macd_line"]
            signal_line = analysis_results["macd"]["signal_line"]
            histogram = analysis_results["macd"]["histogram"]
            
            macd_crossover_bullish = macd_line > signal_line and macd_line < signal_line * 1.1
            macd_crossover_bearish = macd_line < signal_line and macd_line > signal_line * 0.9
            
            signals["macd"] = {
                "histogram_positive": histogram > 0,
                "macd_above_signal": macd_line > signal_line,
                "crossover_bullish": macd_crossover_bullish,
                "crossover_bearish": macd_crossover_bearish,
                "signal": "Buy" if macd_line > signal_line else "Sell"
            }
        
        # Bollinger Bands signals
        if "bollinger" in analysis_results:
            upper_band = analysis_results["bollinger"]["upper_band"]
            lower_band = analysis_results["bollinger"]["lower_band"]
            percent_b = analysis_results["bollinger"].get("percent_b", (current_price - lower_band) / (upper_band - lower_band) if upper_band != lower_band else 0.5)
            
            signals["bollinger"] = {
                "price_above_upper": current_price > upper_band,
                "price_below_lower": current_price < lower_band,
                "percent_b": percent_b,
                "signal": "Sell" if current_price > upper_band else "Buy" if current_price < lower_band else "Neutral"
            }
        
        # Stochastic signals
        if "stochastic" in analysis_results:
            k_value = analysis_results["stochastic"]["k_value"]
            d_value = analysis_results["stochastic"]["d_value"]
            
            stoch_crossover_bullish = k_value > d_value and k_value < d_value * 1.1
            stoch_crossover_bearish = k_value < d_value and k_value > d_value * 0.9
            
            signals["stochastic"] = {
                "overbought": k_value > 80,
                "oversold": k_value < 20,
                "k_above_d": k_value > d_value,
                "crossover_bullish": stoch_crossover_bullish,
                "crossover_bearish": stoch_crossover_bearish,
                "signal": "Sell" if k_value > 80 else "Buy" if k_value < 20 else "Neutral"
            }
        
        # Ichimoku Cloud signals
        if "ichimoku" in analysis_results:
            tenkan_sen = analysis_results["ichimoku"]["tenkan_sen"]
            kijun_sen = analysis_results["ichimoku"]["kijun_sen"]
            senkou_span_a = analysis_results["ichimoku"]["senkou_span_a"]
            senkou_span_b = analysis_results["ichimoku"]["senkou_span_b"]
            
            price_above_cloud = current_price > max(senkou_span_a, senkou_span_b)
            price_below_cloud = current_price < min(senkou_span_a, senkou_span_b)
            price_in_cloud = not price_above_cloud and not price_below_cloud
            bullish_cloud = senkou_span_a > senkou_span_b
            
            signals["ichimoku"] = {
                "price_above_cloud": price_above_cloud,
                "price_below_cloud": price_below_cloud,
                "price_in_cloud": price_in_cloud,
                "bullish_cloud": bullish_cloud,
                "tenkan_above_kijun": tenkan_sen > kijun_sen,
                "signal": "Strong Buy" if price_above_cloud and tenkan_sen > kijun_sen and bullish_cloud else
                         "Buy" if price_above_cloud or (tenkan_sen > kijun_sen and bullish_cloud) else
                         "Strong Sell" if price_below_cloud and tenkan_sen < kijun_sen and not bullish_cloud else
                         "Sell" if price_below_cloud or (tenkan_sen < kijun_sen and not bullish_cloud) else
                         "Neutral"
            }
        
        # Parabolic SAR signals
        if "psar" in analysis_results:
            psar_value = analysis_results["psar"]["psar_value"]
            psar_trend = analysis_results["psar"]["trend"]
            
            signals["psar"] = {
                "trend": psar_trend,
                "price_above_psar": current_price > psar_value,
                "signal": "Buy" if current_price > psar_value else "Sell"
            }
        
        # Overall signal based on multiple indicators
        overall_bullish = 0
        overall_bearish = 0
        
        # Count bullish/bearish signals
        if "moving_averages" in signals:
            if signals["moving_averages"]["trend"] == "Bullish":
                overall_bullish += 1
            elif signals["moving_averages"]["trend"] == "Bearish":
                overall_bearish += 1
        
        if "rsi" in signals:
            if signals["rsi"]["signal"] == "Buy":
                overall_bullish += 1
            elif signals["rsi"]["signal"] == "Sell":
                overall_bearish += 1
        
        if "macd" in signals:
            if signals["macd"]["signal"] == "Buy":
                overall_bullish += 1
            elif signals["macd"]["signal"] == "Sell":
                overall_bearish += 1
        
        if "bollinger" in signals:
            if signals["bollinger"]["signal"] == "Buy":
                overall_bullish += 1
            elif signals["bollinger"]["signal"] == "Sell":
                overall_bearish += 1
        
        if "stochastic" in signals:
            if signals["stochastic"]["signal"] == "Buy":
                overall_bullish += 1
            elif signals["stochastic"]["signal"] == "Sell":
                overall_bearish += 1
        
        if "ichimoku" in signals:
            if "Buy" in signals["ichimoku"]["signal"]:
                overall_bullish += 1
            elif "Sell" in signals["ichimoku"]["signal"]:
                overall_bearish += 1
        
        if "psar" in signals:
            if signals["psar"]["signal"] == "Buy":
                overall_bullish += 1
            elif signals["psar"]["signal"] == "Sell":
                overall_bearish += 1
        
        # Determine overall signal
        overall_signal = "Neutral"
        if overall_bullish > overall_bearish and overall_bullish >= 2:
            overall_signal = "Buy"
            if overall_bullish >= 4:
                overall_signal = "Strong Buy"
        elif overall_bearish > overall_bullish and overall_bearish >= 2:
            overall_signal = "Sell"
            if overall_bearish >= 4:
                overall_signal = "Strong Sell"
        
        signals["overall"] = {
            "signal": overall_signal,
            "bullish_count": overall_bullish,
            "bearish_count": overall_bearish,
            "confidence": max(overall_bullish, overall_bearish) / max(1, overall_bullish + overall_bearish)
        }
        
        return signals
    
    def _calculate_support_resistance(self, df: pd.DataFrame, window: int = 10) -> Tuple[List[float], List[float]]:
        """Calculate support and resistance levels"""
        try:
            # Use price data for calculations
            close_prices = df["Close"].values
            high_prices = df["High"].values
            low_prices = df["Low"].values
            
            # Find significant highs (potential resistance)
            highs = self._find_peaks(high_prices, window)
            high_values = [high_prices[i] for i in highs]
            
            # Find significant lows (potential support)
            lows = self._find_troughs(low_prices, window)
            low_values = [low_prices[i] for i in lows]
            
            # Filter out close levels
            resistance_levels = self._filter_levels(high_values)
            support_levels = self._filter_levels(low_values)
            
            # Sort levels
            resistance_levels.sort()
            support_levels.sort()
            
            return support_levels, resistance_levels
        
        except Exception as e:
            self.logger.error(f"Error calculating support/resistance: {str(e)}")
            return [], []
    
    def _find_peaks(self, data: np.ndarray, window: int = 5) -> List[int]:
        """Find peaks (local maxima) in the data"""
        peaks = []
        for i in range(window, len(data) - window):
            if data[i] == max(data[i-window:i+window+1]):
                peaks.append(i)
        return peaks
    
    def _find_troughs(self, data: np.ndarray, window: int = 5) -> List[int]:
        """Find troughs (local minima) in the data"""
        troughs = []
        for i in range(window, len(data) - window):
            if data[i] == min(data[i-window:i+window+1]):
                troughs.append(i)
        return troughs
    
    def _filter_levels(self, levels: List[float], threshold: float = 0.01) -> List[float]:
        """Filter out levels that are too close to each other"""
        if not levels:
            return []
        
        filtered = [levels[0]]
        for level in levels[1:]:
            # Check if the current level is significantly different from existing levels
            if all(abs(level - existing) / existing > threshold for existing in filtered):
                filtered.append(level)
        
        return filtered
    
    def add_indicator(self, indicator: str):
        """Add an indicator to the agent"""
        if indicator not in self.state.indicators:
            self.state.indicators.append(indicator)
    
    def remove_indicator(self, indicator: str):
        """Remove an indicator from the agent"""
        if indicator in self.state.indicators:
            self.state.indicators.remove(indicator)
    
    def clear_cache(self):
        """Clear the agent's analysis cache"""
        self.state.cached_analysis = {}
        self.state.last_cache_update = None 