import openai
import json
import asyncio
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
from dataclasses import dataclass

@dataclass
class TechnicalIndicators:
    """Data class for technical indicators"""
    rsi: float
    macd: Dict[str, float]
    bollinger_bands: Dict[str, float]
    moving_averages: Dict[str, float]
    volume_analysis: Dict[str, Any]
    support_resistance: Dict[str, float]

@dataclass
class StockData:
    """Data class for stock information"""
    symbol: str
    current_price: float
    price_change: float
    price_change_percent: float
    volume: int
    market_cap: Optional[str]
    day_range: Dict[str, float]
    week_52_range: Dict[str, float]

class AIAnalysisAgent:
    """AI-powered analysis agent using OpenAI API for natural language insights"""
    
    def __init__(self):
        self.client = None
        self.initialize_openai()
    
    def initialize_openai(self):
        """Initialize OpenAI client"""
        try:
            # Try to get API key from environment or settings
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                # Try to read from settings file
                try:
                    import json
                    with open('settings.json', 'r') as f:
                        settings = json.load(f)
                        api_key = settings.get('openai_api_key')
                except:
                    pass
            
            if api_key:
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key)
                print("OpenAI API initialized successfully")
            else:
                print("Warning: OpenAI API key not found. AI analysis will be disabled.")
                self.client = None
                
        except Exception as e:
            print(f"Error initializing OpenAI: {e}")
            self.client = None
    
    async def analyze_stock_comprehensive(
        self, 
        stock_data: StockData, 
        technical_indicators: TechnicalIndicators,
        time_period: str = "3M",
        market_context: Optional[Dict] = None
    ) -> Dict[str, str]:
        """
        Generate comprehensive AI analysis of stock and technical indicators
        
        Args:
            stock_data: Current stock information
            technical_indicators: Technical analysis data
            time_period: Analysis time period
            market_context: Additional market context
            
        Returns:
            Dictionary with different types of analysis
        """
        if not self.client:
            return self._get_fallback_analysis(stock_data, technical_indicators)
        
        try:
            # Prepare analysis prompt
            analysis_prompt = self._create_analysis_prompt(
                stock_data, technical_indicators, time_period, market_context
            )
            
            # Get AI analysis
            response = await self._get_openai_analysis(analysis_prompt)
            
            # Parse and structure the response
            return self._parse_ai_response(response)
            
        except Exception as e:
            print(f"Error in AI analysis: {e}")
            return self._get_fallback_analysis(stock_data, technical_indicators)
    
    def _create_analysis_prompt(
        self, 
        stock_data: StockData, 
        technical_indicators: TechnicalIndicators,
        time_period: str,
        market_context: Optional[Dict]
    ) -> str:
        """Create detailed technical prompt for comprehensive AI analysis"""
        
        # Calculate additional technical metrics for context
        price_position_52w = ((stock_data.current_price - stock_data.week_52_range['low']) / 
                             (stock_data.week_52_range['high'] - stock_data.week_52_range['low'])) * 100
        
        rsi_interpretation = self._get_rsi_interpretation(technical_indicators.rsi)
        macd_signal = self._get_macd_signal(technical_indicators.macd)
        bb_position = self._get_bollinger_position(stock_data.current_price, technical_indicators.bollinger_bands)
        
        prompt = f"""
You are a CFA-level quantitative analyst with expertise in technical analysis, market microstructure, and behavioral finance. Conduct a comprehensive technical and fundamental analysis of {stock_data.symbol} using advanced analytical frameworks.

=== MARKET DATA ANALYSIS ===
Symbol: {stock_data.symbol}
Current Price: ${stock_data.current_price:.2f}
Intraday Change: {stock_data.price_change:+.2f} ({stock_data.price_change_percent:+.2f}%)
Daily Range: ${stock_data.day_range['low']:.2f} - ${stock_data.day_range['high']:.2f}
52-Week Range: ${stock_data.week_52_range['low']:.2f} - ${stock_data.week_52_range['high']:.2f}
52W Position: {price_position_52w:.1f}% (0%=52W Low, 100%=52W High)
Market Capitalization: {stock_data.market_cap or 'N/A'}
Analysis Period: {time_period}

=== TECHNICAL INDICATOR MATRIX ===

MOMENTUM OSCILLATORS:
- RSI(14): {technical_indicators.rsi:.2f} [{rsi_interpretation}]
- RSI Divergence Analysis: Check for bullish/bearish divergences with price action
- Stochastic Implications: Assess overbought/oversold conditions in context

TREND FOLLOWING INDICATORS:
- MACD Line: {technical_indicators.macd.get('macd', 0):.4f}
- MACD Signal: {technical_indicators.macd.get('signal', 0):.4f}
- MACD Histogram: {technical_indicators.macd.get('histogram', 0):.4f}
- MACD Signal: {macd_signal}
- SMA(20): ${technical_indicators.moving_averages.get('sma20', 0):.2f}
- SMA(50): ${technical_indicators.moving_averages.get('sma50', 0):.2f}
- MA Cross Analysis: Price vs SMA20 vs SMA50 positioning

VOLATILITY & MEAN REVERSION:
- Bollinger Upper: ${technical_indicators.bollinger_bands.get('upper', 0):.2f}
- Bollinger Middle: ${technical_indicators.bollinger_bands.get('middle', 0):.2f}
- Bollinger Lower: ${technical_indicators.bollinger_bands.get('lower', 0):.2f}
- BB Position: {bb_position}
- Volatility Regime: Analyze band width and price position

VOLUME MICROSTRUCTURE:
- Current Volume: {technical_indicators.volume_analysis.get('current_volume', 0):,}
- Average Volume: {technical_indicators.volume_analysis.get('avg_volume', 0):,.0f}
- Volume Trend: {technical_indicators.volume_analysis.get('volume_trend', 'N/A')}
- Volume-Price Relationship: Analyze accumulation/distribution patterns

SUPPORT & RESISTANCE FRAMEWORK:
- Key Support: ${technical_indicators.support_resistance.get('support', 0):.2f}
- Key Resistance: ${technical_indicators.support_resistance.get('resistance', 0):.2f}
- S/R Strength: Evaluate historical test frequency and reaction strength

=== ANALYTICAL FRAMEWORK REQUIREMENTS ===

Apply the following advanced analytical methodologies:

1. MULTI-TIMEFRAME CONFLUENCE:
   - Analyze how {time_period} signals align with longer/shorter timeframes
   - Identify trend consistency across timeframes

2. MARKET REGIME ANALYSIS:
   - Determine current market regime (trending, ranging, volatile)
   - Assess regime-appropriate strategies

3. RISK-ADJUSTED METRICS:
   - Calculate implied volatility from price action
   - Assess risk-reward ratios for potential trades

4. BEHAVIORAL FINANCE CONSIDERATIONS:
   - Identify potential psychological levels
   - Analyze crowd sentiment indicators

5. INSTITUTIONAL FLOW ANALYSIS:
   - Evaluate volume patterns for institutional activity
   - Assess smart money vs retail money flows

=== OUTPUT REQUIREMENTS ===

Provide analysis in the following JSON structure with highly technical, actionable insights:

{{
    "overall_sentiment": "Comprehensive market sentiment with confidence level (e.g., 'Moderately Bullish (70% confidence)')",
    "price_analysis": "Detailed 3-4 sentence analysis of price action, trend structure, and momentum characteristics including specific price levels and percentage moves",
    "technical_summary": "Comprehensive 4-5 sentence technical analysis incorporating multiple indicator confluence, divergences, and signal strength with specific numerical thresholds",
    "volume_insights": "Detailed 2-3 sentence volume analysis including accumulation/distribution patterns, institutional vs retail activity, and volume-price relationship dynamics",
    "support_resistance": "Technical 2-3 sentence analysis of key levels including historical significance, test frequency, volume at levels, and breakout/breakdown probabilities",
    "risk_assessment": "Quantitative 2-3 sentence risk analysis including volatility assessment, maximum adverse excursion potential, and risk-reward ratios with specific percentages",
    "short_term_outlook": "Tactical 2-3 sentence outlook for next 1-2 weeks including specific price targets, probability assessments, and catalyst dependencies",
    "key_levels": "Precise numerical levels with context: 'Critical resistance at $X.XX (previous high, 61.8% Fib), Strong support at $Y.YY (200-day MA confluence)'",
    "trading_suggestion": "Detailed tactical trading framework including entry/exit criteria, position sizing recommendations, stop-loss levels, and profit targets with specific risk management parameters"
}}

=== ANALYTICAL STANDARDS ===
- Use precise numerical analysis with specific price levels and percentages
- Incorporate multiple timeframe analysis where relevant
- Reference specific technical patterns and formations
- Include probability assessments where appropriate
- Maintain institutional-grade analytical rigor
- Provide actionable insights with clear risk parameters
- Include educational context for complex concepts

IMPORTANT: This analysis is for educational and research purposes only. Include appropriate disclaimers about the speculative nature of technical analysis and the importance of comprehensive due diligence.
"""
        
        return prompt
    
    async def _get_openai_analysis(self, prompt: str) -> str:
        """Get analysis from OpenAI API"""
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional financial analyst providing educational stock market analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            raise
    
    def _parse_ai_response(self, response: str) -> Dict[str, str]:
        """Parse AI response into structured format"""
        try:
            # Try to parse as JSON first
            if response.strip().startswith('{'):
                return json.loads(response)
            
            # If not JSON, create structured response from text
            return {
                "overall_sentiment": "Neutral",
                "price_analysis": response[:200] + "..." if len(response) > 200 else response,
                "technical_summary": "Analysis based on current technical indicators.",
                "volume_insights": "Volume analysis indicates normal trading activity.",
                "support_resistance": "Key levels identified from recent price action.",
                "risk_assessment": "Standard market risks apply.",
                "short_term_outlook": "Monitor key technical levels for direction.",
                "key_levels": "See support and resistance analysis.",
                "trading_suggestion": "Educational analysis only - consult financial advisor."
            }
            
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return self._create_fallback_structured_response(response)
    
    def _create_fallback_structured_response(self, text: str) -> Dict[str, str]:
        """Create structured response from unstructured text"""
        sentences = text.split('. ')
        
        return {
            "overall_sentiment": "Neutral",
            "price_analysis": '. '.join(sentences[:2]) if len(sentences) >= 2 else text[:150],
            "technical_summary": '. '.join(sentences[2:4]) if len(sentences) >= 4 else "Technical analysis in progress.",
            "volume_insights": "Volume patterns suggest normal market activity.",
            "support_resistance": "Key levels identified from price action.",
            "risk_assessment": "Standard market risks apply to this position.",
            "short_term_outlook": "Monitor technical indicators for trend confirmation.",
            "key_levels": "Watch major support and resistance zones.",
            "trading_suggestion": "Educational analysis only - not financial advice."
        }
    
    def _get_fallback_analysis(
        self, 
        stock_data: StockData, 
        technical_indicators: TechnicalIndicators
    ) -> Dict[str, str]:
        """Provide detailed technical fallback analysis when AI is not available"""
        
        # Advanced sentiment calculation with confidence scoring
        sentiment_score = 0
        confidence_factors = []
        
        # RSI analysis
        if technical_indicators.rsi > 75:
            sentiment_score -= 2
            confidence_factors.append("RSI extremely overbought")
        elif technical_indicators.rsi > 65:
            sentiment_score -= 1
            confidence_factors.append("RSI overbought")
        elif technical_indicators.rsi < 25:
            sentiment_score += 2
            confidence_factors.append("RSI extremely oversold")
        elif technical_indicators.rsi < 35:
            sentiment_score += 1
            confidence_factors.append("RSI oversold")
        
        # MACD analysis
        macd_line = technical_indicators.macd.get('macd', 0)
        signal_line = technical_indicators.macd.get('signal', 0)
        if macd_line > signal_line:
            sentiment_score += 1
            confidence_factors.append("MACD bullish crossover")
        else:
            sentiment_score -= 1
            confidence_factors.append("MACD bearish crossover")
        
        # Price momentum
        if stock_data.price_change_percent > 3:
            sentiment_score += 1
            confidence_factors.append("Strong positive momentum")
        elif stock_data.price_change_percent < -3:
            sentiment_score -= 1
            confidence_factors.append("Strong negative momentum")
        
        # Moving average analysis
        sma20 = technical_indicators.moving_averages.get('sma20', stock_data.current_price)
        sma50 = technical_indicators.moving_averages.get('sma50', stock_data.current_price)
        if stock_data.current_price > sma20 > sma50:
            sentiment_score += 1
            confidence_factors.append("Price above rising MAs")
        elif stock_data.current_price < sma20 < sma50:
            sentiment_score -= 1
            confidence_factors.append("Price below falling MAs")
        
        # Determine final sentiment with confidence
        if sentiment_score >= 2:
            sentiment = "Bullish (High Confidence)"
        elif sentiment_score == 1:
            sentiment = "Moderately Bullish (65% confidence)"
        elif sentiment_score == -1:
            sentiment = "Moderately Bearish (65% confidence)"
        elif sentiment_score <= -2:
            sentiment = "Bearish (High Confidence)"
        else:
            sentiment = "Neutral (Mixed Signals)"
        
        # Calculate 52-week position
        week_52_position = ((stock_data.current_price - stock_data.week_52_range['low']) / 
                           (stock_data.week_52_range['high'] - stock_data.week_52_range['low'])) * 100
        
        # Enhanced price analysis
        price_direction = "higher" if stock_data.price_change > 0 else "lower"
        intraday_range = ((stock_data.current_price - stock_data.day_range['low']) / 
                         (stock_data.day_range['high'] - stock_data.day_range['low'])) * 100
        
        price_analysis = (f"{stock_data.symbol} closed {price_direction} at ${stock_data.current_price:.2f} "
                         f"({stock_data.price_change_percent:+.2f}%), positioned at {intraday_range:.1f}% of today's range. "
                         f"The stock trades at {week_52_position:.1f}% of its 52-week range "
                         f"(${stock_data.week_52_range['low']:.2f}-${stock_data.week_52_range['high']:.2f}). "
                         f"Current price is {((stock_data.current_price/sma20-1)*100):+.1f}% vs 20-day MA.")
        
        # Enhanced technical summary
        rsi_interpretation = self._get_rsi_interpretation(technical_indicators.rsi)
        macd_signal = self._get_macd_signal(technical_indicators.macd)
        bb_position = self._get_bollinger_position(stock_data.current_price, technical_indicators.bollinger_bands)
        
        technical_summary = (f"RSI(14) at {technical_indicators.rsi:.1f} shows {rsi_interpretation.lower()}. "
                           f"MACD analysis reveals {macd_signal.lower()}. "
                           f"Bollinger Bands indicate {bb_position.lower()}. "
                           f"Price-to-MA relationship: {stock_data.current_price:.2f} vs SMA20({sma20:.2f}) vs SMA50({sma50:.2f}) "
                           f"suggests {'bullish' if stock_data.current_price > sma20 > sma50 else 'bearish' if stock_data.current_price < sma20 < sma50 else 'mixed'} alignment.")
        
        # Enhanced volume analysis
        current_vol = technical_indicators.volume_analysis.get('current_volume', 0)
        avg_vol = technical_indicators.volume_analysis.get('avg_volume', 1)
        vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1
        vol_trend = technical_indicators.volume_analysis.get('volume_trend', 'neutral')
        
        volume_insights = (f"Volume analysis shows {current_vol:,} shares traded ({vol_ratio:.1f}x average volume). "
                          f"Volume trend is {vol_trend}, indicating {'institutional accumulation' if vol_trend == 'increasing' and stock_data.price_change_percent > 0 else 'distribution pressure' if vol_trend == 'increasing' and stock_data.price_change_percent < 0 else 'balanced participation'}. "
                          f"Volume-price relationship suggests {'confirmation' if (vol_trend == 'increasing' and abs(stock_data.price_change_percent) > 1) else 'divergence'} of price movement.")
        
        # Enhanced support/resistance
        support = technical_indicators.support_resistance.get('support', stock_data.current_price * 0.97)
        resistance = technical_indicators.support_resistance.get('resistance', stock_data.current_price * 1.03)
        support_distance = ((stock_data.current_price - support) / stock_data.current_price) * 100
        resistance_distance = ((resistance - stock_data.current_price) / stock_data.current_price) * 100
        
        support_resistance = (f"Technical support identified at ${support:.2f} ({support_distance:.1f}% below current), "
                             f"with resistance at ${resistance:.2f} ({resistance_distance:.1f}% above current). "
                             f"Risk-reward ratio for long positions: {resistance_distance/support_distance:.2f}:1. "
                             f"Key breakout level above ${resistance:.2f} could target {resistance * 1.05:.2f}, "
                             f"while breakdown below ${support:.2f} may test {support * 0.95:.2f}.")
        
        # Enhanced risk assessment
        volatility_estimate = abs(stock_data.price_change_percent) * 1.5  # Rough daily volatility
        max_adverse_excursion = min(support_distance, volatility_estimate * 2)
        
        risk_assessment = (f"Current volatility regime suggests {volatility_estimate:.1f}% daily moves. "
                          f"Maximum adverse excursion estimated at {max_adverse_excursion:.1f}% to support level. "
                          f"Risk-adjusted outlook: {'Favorable' if sentiment_score > 0 and vol_ratio < 2 else 'Elevated' if abs(sentiment_score) <= 1 else 'High'} risk environment. "
                          f"Position sizing should account for {max_adverse_excursion * 1.5:.1f}% potential drawdown.")
        
        # Enhanced short-term outlook
        momentum_strength = abs(sentiment_score) / 4 * 100  # Convert to percentage
        catalyst_dependency = "earnings" if week_52_position > 80 or week_52_position < 20 else "technical levels"
        
        short_term_outlook = (f"1-2 week tactical outlook: {sentiment} with {momentum_strength:.0f}% momentum strength. "
                             f"Primary catalyst dependency on {catalyst_dependency}. "
                             f"Probability matrix: {60 + sentiment_score * 10:.0f}% chance of direction continuation, "
                             f"{40 - sentiment_score * 10:.0f}% reversal probability. "
                             f"Key inflection point at {'resistance' if sentiment_score > 0 else 'support'} levels.")
        
        # Enhanced key levels
        fib_618 = stock_data.week_52_range['low'] + (stock_data.week_52_range['high'] - stock_data.week_52_range['low']) * 0.618
        fib_382 = stock_data.week_52_range['low'] + (stock_data.week_52_range['high'] - stock_data.week_52_range['low']) * 0.382
        
        key_levels = (f"Critical resistance: ${resistance:.2f} (technical), ${fib_618:.2f} (61.8% Fib retracement). "
                     f"Strong support: ${support:.2f} (technical), ${fib_382:.2f} (38.2% Fib), ${sma20:.2f} (20-day MA). "
                     f"Breakout targets: ${resistance * 1.05:.2f} (5% extension), ${stock_data.week_52_range['high']:.2f} (52W high). "
                     f"Breakdown targets: ${support * 0.95:.2f} (5% extension), ${stock_data.week_52_range['low']:.2f} (52W low).")
        
        # Enhanced trading suggestion
        entry_criteria = f"above ${resistance:.2f}" if sentiment_score > 0 else f"below ${support:.2f}"
        stop_loss = f"${support * 0.98:.2f}" if sentiment_score > 0 else f"${resistance * 1.02:.2f}"
        profit_target = f"${resistance * 1.08:.2f}" if sentiment_score > 0 else f"${support * 0.92:.2f}"
        position_size = "1-2%" if abs(sentiment_score) >= 2 else "0.5-1%"
        
        trading_suggestion = (f"Educational framework: {'Long' if sentiment_score > 0 else 'Short'} bias with entry {entry_criteria}. "
                             f"Risk management: Stop-loss at {stop_loss} ({max_adverse_excursion:.1f}% risk), "
                             f"profit target {profit_target} ({resistance_distance if sentiment_score > 0 else support_distance:.1f}% reward). "
                             f"Position sizing: {position_size} of portfolio given current risk profile. "
                             f"Time horizon: 1-2 weeks with daily monitoring of volume and momentum indicators. "
                             f"DISCLAIMER: This is educational analysis only - not investment advice.")
        
        return {
            "overall_sentiment": sentiment,
            "price_analysis": price_analysis,
            "technical_summary": technical_summary,
            "volume_insights": volume_insights,
            "support_resistance": support_resistance,
            "risk_assessment": risk_assessment,
            "short_term_outlook": short_term_outlook,
            "key_levels": key_levels,
            "trading_suggestion": trading_suggestion
        }
    
    async def analyze_chart_patterns(self, price_data: List[float], volume_data: List[float]) -> str:
        """Analyze chart patterns and provide insights"""
        if not self.client:
            return self._get_fallback_pattern_analysis(price_data, volume_data)
        
        try:
            # Analyze recent price action
            recent_prices = price_data[-20:] if len(price_data) >= 20 else price_data
            recent_volumes = volume_data[-20:] if len(volume_data) >= 20 else volume_data
            
            # Calculate basic pattern metrics
            price_trend = "upward" if recent_prices[-1] > recent_prices[0] else "downward"
            volatility = np.std(recent_prices) / np.mean(recent_prices) * 100
            
            prompt = f"""
You are a professional technical analyst specializing in chart pattern recognition and market microstructure analysis. Conduct a comprehensive pattern analysis using advanced technical methodologies.

=== PRICE ACTION ANALYSIS ===
Trend Direction: {price_trend} trend
Volatility Regime: {volatility:.2f}% (annualized)
Price Series (last 20 periods): {[round(p, 2) for p in recent_prices]}
Volume Series (last 20 periods): {[int(v) for v in recent_volumes]}

=== PATTERN RECOGNITION FRAMEWORK ===

Apply the following analytical methodologies:

1. CLASSICAL CHART PATTERNS:
   - Identify continuation patterns (flags, pennants, triangles)
   - Recognize reversal patterns (head & shoulders, double tops/bottoms)
   - Assess pattern completion and reliability scores

2. CANDLESTICK FORMATIONS:
   - Analyze single and multiple candlestick patterns
   - Evaluate reversal and continuation signals
   - Assess pattern context and confirmation

3. VOLUME ANALYSIS:
   - Volume-price relationship validation
   - Accumulation/distribution patterns
   - Volume breakout confirmation
   - Smart money vs retail participation

4. FIBONACCI & ELLIOTT WAVE:
   - Identify wave structures and counts
   - Calculate Fibonacci retracement/extension levels
   - Assess wave completion probabilities

5. MARKET MICROSTRUCTURE:
   - Order flow implications
   - Support/resistance strength testing
   - Breakout/breakdown probability assessment

=== REQUIRED OUTPUT ===

Provide detailed technical analysis covering:

1. PRIMARY PATTERN IDENTIFICATION:
   - Specific pattern name and classification
   - Pattern completion percentage
   - Reliability score (1-10) with justification

2. VOLUME CONFIRMATION ANALYSIS:
   - Volume trend during pattern formation
   - Breakout volume requirements
   - Institutional vs retail participation indicators

3. PRICE TARGETS & LEVELS:
   - Measured move calculations
   - Fibonacci-based targets
   - Key support/resistance levels

4. RISK ASSESSMENT:
   - Pattern failure probability
   - Stop-loss placement recommendations
   - Risk-reward ratio analysis

5. TIMING CONSIDERATIONS:
   - Expected pattern completion timeframe
   - Catalyst dependencies
   - Market regime suitability

Maintain institutional-grade analytical standards with specific numerical targets and probability assessments. Focus on actionable insights with clear risk parameters.
"""
            
            response = await self._get_openai_analysis(prompt)
            return response
            
        except Exception as e:
            print(f"Error in pattern analysis: {e}")
            return self._get_fallback_pattern_analysis(price_data, volume_data)
    
    def _get_fallback_pattern_analysis(self, price_data: List[float], volume_data: List[float]) -> str:
        """Fallback pattern analysis"""
        if len(price_data) < 5:
            return "Insufficient data for pattern analysis."
        
        recent_prices = price_data[-10:]
        trend = "upward" if recent_prices[-1] > recent_prices[0] else "downward"
        
        return f"Recent price action shows a {trend} trend. Volume patterns suggest {'increasing' if volume_data[-1] > volume_data[-5] else 'decreasing'} market participation. Monitor key levels for potential breakout opportunities."

    def _get_rsi_interpretation(self, rsi: float) -> str:
        """Get detailed RSI interpretation"""
        if rsi >= 80:
            return "Extremely Overbought - High probability reversal zone"
        elif rsi >= 70:
            return "Overbought - Potential reversal or consolidation"
        elif rsi >= 60:
            return "Bullish Momentum - Above neutral with upward bias"
        elif rsi >= 40:
            return "Neutral Zone - Balanced momentum"
        elif rsi >= 30:
            return "Bearish Momentum - Below neutral with downward bias"
        elif rsi >= 20:
            return "Oversold - Potential reversal or bounce"
        else:
            return "Extremely Oversold - High probability reversal zone"

    def _get_macd_signal(self, macd_data: Dict[str, float]) -> str:
        """Get detailed MACD signal interpretation"""
        macd_line = macd_data.get('macd', 0)
        signal_line = macd_data.get('signal', 0)
        histogram = macd_data.get('histogram', 0)
        
        if macd_line > signal_line:
            if histogram > 0:
                return "Bullish - MACD above signal with positive momentum"
            else:
                return "Bullish but weakening - MACD above signal but momentum declining"
        else:
            if histogram < 0:
                return "Bearish - MACD below signal with negative momentum"
            else:
                return "Bearish but improving - MACD below signal but momentum strengthening"

    def _get_bollinger_position(self, current_price: float, bb_data: Dict[str, float]) -> str:
        """Get detailed Bollinger Bands position analysis"""
        upper = bb_data.get('upper', 0)
        lower = bb_data.get('lower', 0)
        middle = bb_data.get('middle', 0)
        
        if not upper or not lower or not middle:
            return "Insufficient data for BB analysis"
        
        if current_price >= upper:
            return "Above Upper Band - Potential overbought, watch for reversal"
        elif current_price >= middle:
            bb_position = ((current_price - middle) / (upper - middle)) * 100
            return f"Upper Half ({bb_position:.1f}% to upper) - Bullish bias"
        elif current_price >= lower:
            bb_position = ((current_price - lower) / (middle - lower)) * 100
            return f"Lower Half ({bb_position:.1f}% to middle) - Bearish bias"
        else:
            return "Below Lower Band - Potential oversold, watch for bounce"

# Global instance
ai_analysis_agent = AIAnalysisAgent() 