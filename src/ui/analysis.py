import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import asyncio
from datetime import datetime, timedelta

from src.agents.market_data_agent import MarketDataAgent
from src.agents.news_sentiment_agent import NewsSentimentAgent
from src.agents.technical_analysis_agent import TechnicalAnalysisAgent

def render_analysis():
    st.title("Financial Analysis")
    
    # Sidebar for analysis options
    st.sidebar.subheader("Analysis Options")
    analysis_type = st.sidebar.selectbox(
        "Analysis Type",
        ["Technical Analysis", "Fundamental Analysis", "Sentiment Analysis", "Risk Analysis"]
    )
    
    # Symbol input
    symbol = st.sidebar.text_input("Symbol", value="AAPL")
    
    # Date range
    st.sidebar.subheader("Date Range")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=180))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now())
    
    # Run analysis button
    run_analysis = st.sidebar.button("Run Analysis")
    
    # Main content
    if analysis_type == "Technical Analysis":
        render_technical_analysis(symbol, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), run_analysis)
    elif analysis_type == "Fundamental Analysis":
        render_fundamental_analysis(symbol, run_analysis)
    elif analysis_type == "Sentiment Analysis":
        render_sentiment_analysis(symbol, run_analysis)
    elif analysis_type == "Risk Analysis":
        render_risk_analysis(symbol, run_analysis)

def render_technical_analysis(symbol, start_date, end_date, run_analysis):
    st.header(f"Technical Analysis for {symbol}")
    
    if run_analysis:
        # Initialize the market data agent
        market_data_agent = MarketDataAgent()
        
        # Use st.spinner to show loading state
        with st.spinner(f"Fetching market data for {symbol}..."):
            # Run the agent to get market data
            market_data = asyncio.run(market_data_agent.fetch_market_data(
                symbol, 
                start_date=start_date,
                end_date=end_date,
                interval="1d"
            ))
            
            if "error" in market_data:
                st.error(f"Error fetching data: {market_data['error']}")
                return
            
            # Convert historical data to DataFrame
            if market_data and "historical_data" in market_data:
                df = pd.DataFrame(market_data["historical_data"])
                
                # Handle Date column from yfinance
                if "Date" in df.columns:
                    df["Date"] = pd.to_datetime(df["Date"])
                elif "Datetime" in df.columns:
                    df["Date"] = pd.to_datetime(df["Datetime"])
                    df = df.rename(columns={"Datetime": "Date"})
                
                # Sort by date
                df = df.sort_values("Date")
                
                # Calculate moving averages
                df["MA20"] = df["Close"].rolling(window=20).mean()
                df["MA50"] = df["Close"].rolling(window=50).mean()
                df["MA200"] = df["Close"].rolling(window=200).mean()
                
                # Calculate RSI
                delta = df["Close"].diff()
                gain = delta.where(delta > 0, 0)
                loss = -delta.where(delta < 0, 0)
                avg_gain = gain.rolling(window=14).mean()
                avg_loss = loss.rolling(window=14).mean()
                rs = avg_gain / avg_loss
                df["RSI"] = 100 - (100 / (1 + rs))
                
                # Calculate MACD
                df["EMA12"] = df["Close"].ewm(span=12, adjust=False).mean()
                df["EMA26"] = df["Close"].ewm(span=26, adjust=False).mean()
                df["MACD"] = df["EMA12"] - df["EMA26"]
                df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
                df["Histogram"] = df["MACD"] - df["Signal"]
                
                # Create tabs for different technical analysis views
                tab1, tab2, tab3, tab4 = st.tabs(["Price & Volume", "Moving Averages", "Oscillators", "Advanced Analysis"])
                
                with tab1:
                    st.subheader("Price & Volume Analysis")
                    
                    # Create figure with secondary y-axis
                    fig = make_subplots(specs=[[{"secondary_y": True}]])
                    
                    # Add price line
                    fig.add_trace(
                        go.Scatter(x=df["Date"], y=df["Close"], name="Price"),
                        secondary_y=False,
                    )
                    
                    # Add volume bars
                    fig.add_trace(
                        go.Bar(x=df["Date"], y=df["Volume"], name="Volume", marker_color="rgba(0, 0, 255, 0.3)"),
                        secondary_y=True,
                    )
                    
                    # Add figure layout
                    fig.update_layout(
                        title_text=f"{symbol} Price and Volume",
                        xaxis_title="Date",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    
                    # Set y-axes titles
                    fig.update_yaxes(title_text="Price ($)", secondary_y=False)
                    fig.update_yaxes(title_text="Volume", secondary_y=True)
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Support and resistance levels
                    st.subheader("Support and Resistance Levels")
                    
                    # Calculate simple support and resistance levels
                    recent_df = df.tail(30)  # Last 30 days for recent levels
                    max_price = recent_df["High"].max()
                    min_price = recent_df["Low"].min()
                    current_price = df["Close"].iloc[-1]
                    
                    range_price = max_price - min_price
                    resistance1 = current_price + (range_price * 0.1)
                    resistance2 = current_price + (range_price * 0.2)
                    support1 = current_price - (range_price * 0.1)
                    support2 = current_price - (range_price * 0.2)
                    
                    levels = {
                        "Strong Resistance": f"${resistance2:.2f}",
                        "Resistance": f"${resistance1:.2f}",
                        "Current Price": f"${current_price:.2f}",
                        "Support": f"${support1:.2f}",
                        "Strong Support": f"${support2:.2f}"
                    }
                    
                    for level, price in levels.items():
                        st.write(f"**{level}:** {price}")
                
                with tab2:
                    st.subheader("Moving Averages")
                    
                    # Create figure
                    fig = go.Figure()
                    
                    # Add price line
                    fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], name="Price"))
                    
                    # Add moving averages
                    fig.add_trace(go.Scatter(x=df["Date"], y=df["MA20"], name="MA 20", line=dict(color='orange')))
                    fig.add_trace(go.Scatter(x=df["Date"], y=df["MA50"], name="MA 50", line=dict(color='green')))
                    fig.add_trace(go.Scatter(x=df["Date"], y=df["MA200"], name="MA 200", line=dict(color='red')))
                    
                    # Update layout
                    fig.update_layout(
                        title_text=f"{symbol} Moving Averages",
                        xaxis_title="Date",
                        yaxis_title="Price ($)",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Moving average analysis
                    st.subheader("Moving Average Analysis")
                    
                    # Get the last values
                    last_ma20 = df["MA20"].iloc[-1]
                    last_ma50 = df["MA50"].iloc[-1]
                    last_ma200 = df["MA200"].iloc[-1]
                    last_close = df["Close"].iloc[-1]
                    
                    # Check for crossovers
                    golden_cross = False
                    death_cross = False
                    short_term_cross = False
                    crossover_date = None
                    
                    # Check for MA crossovers in the last 30 days
                    recent_df = df.tail(30).copy()
                    
                    for i in range(1, len(recent_df)):
                        prev_ma50 = recent_df["MA50"].iloc[i-1]
                        curr_ma50 = recent_df["MA50"].iloc[i]
                        prev_ma200 = recent_df["MA200"].iloc[i-1]
                        curr_ma200 = recent_df["MA200"].iloc[i]
                        
                        if prev_ma50 < prev_ma200 and curr_ma50 > curr_ma200:
                            golden_cross = True
                            crossover_date = recent_df["Date"].iloc[i].strftime("%Y-%m-%d")
                        
                        if prev_ma50 > prev_ma200 and curr_ma50 < curr_ma200:
                            death_cross = True
                            crossover_date = recent_df["Date"].iloc[i].strftime("%Y-%m-%d")
                    
                    # Short term trend (MA20 crossing MA50)
                    for i in range(1, len(recent_df)):
                        prev_ma20 = recent_df["MA20"].iloc[i-1]
                        curr_ma20 = recent_df["MA20"].iloc[i]
                        prev_ma50 = recent_df["MA50"].iloc[i-1]
                        curr_ma50 = recent_df["MA50"].iloc[i]
                        
                        if prev_ma20 < prev_ma50 and curr_ma20 > curr_ma50:
                            short_term_cross = "Bullish"
                            crossover_date = recent_df["Date"].iloc[i].strftime("%Y-%m-%d")
                        
                        if prev_ma20 > prev_ma50 and curr_ma20 < curr_ma50:
                            short_term_cross = "Bearish"
                            crossover_date = recent_df["Date"].iloc[i].strftime("%Y-%m-%d")
                    
                    st.write("**MA Crossovers:**")
                    
                    if golden_cross:
                        st.write(f"- Golden Cross (MA 50 crossing above MA 200): Detected on {crossover_date}")
                    else:
                        st.write("- Golden Cross (MA 50 crossing above MA 200): Not detected")
                    
                    if death_cross:
                        st.write(f"- Death Cross (MA 50 crossing below MA 200): Detected on {crossover_date}")
                    else:
                        st.write("- Death Cross (MA 50 crossing below MA 200): Not detected")
                    
                    if short_term_cross:
                        st.write(f"- Short-term trend (MA 20 crossing MA 50): {short_term_cross} (occurred on {crossover_date})")
                    else:
                        st.write("- Short-term trend (MA 20 crossing MA 50): No recent crossover")
                
                with tab3:
                    st.subheader("Oscillators")
                    
                    # Create subplots
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                       vertical_spacing=0.1, row_heights=[0.7, 0.3])
                    
                    # Add RSI
                    fig.add_trace(
                        go.Scatter(x=df["Date"], y=df["RSI"], name="RSI"),
                        row=1, col=1
                    )
                    
                    # Add RSI overbought/oversold lines
                    fig.add_shape(type="line", x0=df["Date"].iloc[0], y0=70, x1=df["Date"].iloc[-1], y1=70,
                                 line=dict(color="red", width=1, dash="dash"), row=1, col=1)
                    fig.add_shape(type="line", x0=df["Date"].iloc[0], y0=30, x1=df["Date"].iloc[-1], y1=30,
                                 line=dict(color="green", width=1, dash="dash"), row=1, col=1)
                    
                    # Add MACD
                    fig.add_trace(
                        go.Scatter(x=df["Date"], y=df["MACD"], name="MACD"),
                        row=2, col=1
                    )
                    fig.add_trace(
                        go.Scatter(x=df["Date"], y=df["Signal"], name="Signal"),
                        row=2, col=1
                    )
                    fig.add_trace(
                        go.Bar(x=df["Date"], y=df["Histogram"], name="Histogram"),
                        row=2, col=1
                    )
                    
                    # Update layout
                    fig.update_layout(
                        title_text=f"{symbol} Oscillators",
                        xaxis_title="Date",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        height=600
                    )
                    
                    # Update y-axis labels
                    fig.update_yaxes(title_text="RSI", row=1, col=1)
                    fig.update_yaxes(title_text="MACD", row=2, col=1)
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Oscillator analysis
                    st.subheader("Oscillator Analysis")
                    
                    # Get latest RSI and MACD values
                    last_rsi = df["RSI"].iloc[-1]
                    last_macd = df["MACD"].iloc[-1]
                    last_signal = df["Signal"].iloc[-1]
                    
                    # RSI analysis
                    if last_rsi > 70:
                        rsi_status = "Overbought"
                    elif last_rsi < 30:
                        rsi_status = "Oversold"
                    else:
                        rsi_status = "Neutral"
                    
                    # MACD analysis
                    if last_macd > last_signal:
                        macd_status = "Bullish"
                    else:
                        macd_status = "Bearish"
                    
                    # Check for recent MACD crossover
                    macd_crossover = "No recent crossover"
                    for i in range(1, min(10, len(df))):
                        prev_macd = df["MACD"].iloc[-i-1]
                        prev_signal = df["Signal"].iloc[-i-1]
                        curr_macd = df["MACD"].iloc[-i]
                        curr_signal = df["Signal"].iloc[-i]
                        
                        if (prev_macd < prev_signal and curr_macd > curr_signal):
                            macd_crossover = f"Bullish crossover detected {i} days ago"
                            break
                        elif (prev_macd > prev_signal and curr_macd < curr_signal):
                            macd_crossover = f"Bearish crossover detected {i} days ago"
                            break
                    
                    st.write(f"**RSI (14):** {last_rsi:.2f} - {rsi_status}")
                    st.write(f"**MACD:** {macd_status} ({macd_crossover})")
                
                with tab4:
                    st.subheader("Advanced Technical Analysis")
                    
                    # Run the technical analysis agent to get advanced indicators and patterns
                    tech_analysis_agent = TechnicalAnalysisAgent()
                    
                    with st.spinner("Calculating advanced indicators and detecting patterns..."):
                        analysis_result = asyncio.run(tech_analysis_agent.run({
                            "symbol": symbol,
                            "indicators": ["bollinger", "ichimoku", "atr", "stochastic", "psar", "fibonacci", "patterns"],
                            "period": 200  # Need more data for reliable pattern detection
                        }))
                    
                    if analysis_result["status"] == "success":
                        analysis_data = analysis_result["data"]
                        
                        # Create subtabs for advanced analysis
                        adv_tab1, adv_tab2, adv_tab3 = st.tabs(["Advanced Indicators", "Patterns", "Fibonacci"])
                        
                        with adv_tab1:
                            st.subheader("Advanced Technical Indicators")
                            
                            # Bollinger Bands
                            if "bollinger" in analysis_data["indicators"]:
                                bb_data = analysis_data["indicators"]["bollinger"]
                                st.write("**Bollinger Bands**")
                                
                                # Create a figure with Bollinger Bands
                                fig = go.Figure()
                                
                                # Add price line
                                fig.add_trace(go.Scatter(
                                    x=df["Date"], 
                                    y=df["Close"], 
                                    name="Price",
                                    line=dict(color='blue')
                                ))
                                
                                # Add Bollinger Bands
                                # We need to calculate them for the entire period
                                from src.utils.advanced_indicators import calculate_bollinger_bands
                                bb_df = calculate_bollinger_bands(df.copy())
                                
                                fig.add_trace(go.Scatter(
                                    x=df["Date"], 
                                    y=bb_df["bb_high"], 
                                    name="Upper Band",
                                    line=dict(color='red', dash='dash')
                                ))
                                
                                fig.add_trace(go.Scatter(
                                    x=df["Date"], 
                                    y=bb_df["bb_mid"], 
                                    name="Middle Band",
                                    line=dict(color='green', dash='dash')
                                ))
                                
                                fig.add_trace(go.Scatter(
                                    x=df["Date"], 
                                    y=bb_df["bb_low"], 
                                    name="Lower Band",
                                    line=dict(color='red', dash='dash')
                                ))
                                
                                # Update layout
                                fig.update_layout(
                                    title=f"{symbol} Bollinger Bands",
                                    xaxis_title="Date",
                                    yaxis_title="Price ($)",
                                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Display current values
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Upper Band", f"${bb_data['upper_band']:.2f}")
                                with col2:
                                    st.metric("Middle Band", f"${bb_data['middle_band']:.2f}")
                                with col3:
                                    st.metric("Lower Band", f"${bb_data['lower_band']:.2f}")
                                
                                st.write(f"**Bandwidth:** {bb_data['width']:.2f}")
                                st.write(f"**%B:** {bb_data['percent_b']:.2f}")
                                
                                # Interpretation
                                st.subheader("Bollinger Bands Interpretation")
                                
                                if bb_data['percent_b'] > 1:
                                    st.warning("Price is above the upper band, suggesting overbought conditions.")
                                elif bb_data['percent_b'] < 0:
                                    st.warning("Price is below the lower band, suggesting oversold conditions.")
                                elif bb_data['percent_b'] > 0.8:
                                    st.info("Price is approaching the upper band, suggesting strong momentum.")
                                elif bb_data['percent_b'] < 0.2:
                                    st.info("Price is approaching the lower band, suggesting weak momentum.")
                                else:
                                    st.success("Price is within the bands, suggesting neutral trading conditions.")
                            
                            # Ichimoku Cloud
                            if "ichimoku" in analysis_data["indicators"]:
                                st.write("---")
                                st.write("**Ichimoku Cloud**")
                                
                                ichimoku_data = analysis_data["indicators"]["ichimoku"]
                                
                                # Create a figure with Ichimoku Cloud
                                fig = go.Figure()
                                
                                # Add price line
                                fig.add_trace(go.Scatter(
                                    x=df["Date"], 
                                    y=df["Close"], 
                                    name="Price",
                                    line=dict(color='black')
                                ))
                                
                                # Calculate Ichimoku components for the entire period
                                from src.utils.advanced_indicators import calculate_ichimoku_cloud
                                ichi_df = calculate_ichimoku_cloud(df.copy())
                                
                                # Add Ichimoku components
                                fig.add_trace(go.Scatter(
                                    x=df["Date"], 
                                    y=ichi_df["ichimoku_conversion_line"], 
                                    name="Conversion Line (Tenkan-sen)",
                                    line=dict(color='blue')
                                ))
                                
                                fig.add_trace(go.Scatter(
                                    x=df["Date"], 
                                    y=ichi_df["ichimoku_base_line"], 
                                    name="Base Line (Kijun-sen)",
                                    line=dict(color='red')
                                ))
                                
                                # Add the cloud
                                fig.add_trace(go.Scatter(
                                    x=df["Date"], 
                                    y=ichi_df["ichimoku_a"], 
                                    name="Leading Span A (Senkou Span A)",
                                    line=dict(color='green', width=0.5)
                                ))
                                
                                fig.add_trace(go.Scatter(
                                    x=df["Date"], 
                                    y=ichi_df["ichimoku_b"], 
                                    name="Leading Span B (Senkou Span B)",
                                    line=dict(color='red', width=0.5),
                                    fill='tonexty', 
                                    fillcolor='rgba(0, 250, 0, 0.1)'
                                ))
                                
                                # Update layout
                                fig.update_layout(
                                    title=f"{symbol} Ichimoku Cloud",
                                    xaxis_title="Date",
                                    yaxis_title="Price ($)",
                                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Display current values
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric("Conversion Line (Tenkan-sen)", f"${ichimoku_data['tenkan_sen']:.2f}")
                                    st.metric("Leading Span A (Senkou Span A)", f"${ichimoku_data['senkou_span_a']:.2f}")
                                with col2:
                                    st.metric("Base Line (Kijun-sen)", f"${ichimoku_data['kijun_sen']:.2f}")
                                    st.metric("Leading Span B (Senkou Span B)", f"${ichimoku_data['senkou_span_b']:.2f}")
                                
                                # Interpretation
                                st.subheader("Ichimoku Cloud Interpretation")
                                
                                if df["Close"].iloc[-1] > max(ichimoku_data['senkou_span_a'], ichimoku_data['senkou_span_b']):
                                    st.success("Price is above the cloud, suggesting a bullish trend.")
                                elif df["Close"].iloc[-1] < min(ichimoku_data['senkou_span_a'], ichimoku_data['senkou_span_b']):
                                    st.error("Price is below the cloud, suggesting a bearish trend.")
                                else:
                                    st.warning("Price is within the cloud, suggesting a neutral or transitioning market.")
                                
                                if ichimoku_data['tenkan_sen'] > ichimoku_data['kijun_sen']:
                                    st.success("Conversion line is above base line, indicating bullish momentum.")
                                elif ichimoku_data['tenkan_sen'] < ichimoku_data['kijun_sen']:
                                    st.error("Conversion line is below base line, indicating bearish momentum.")
                                
                                if ichimoku_data['senkou_span_a'] > ichimoku_data['senkou_span_b']:
                                    st.success("Leading Span A is above Leading Span B, creating a bullish cloud.")
                                else:
                                    st.error("Leading Span A is below Leading Span B, creating a bearish cloud.")
                            
                            # Additional advanced indicators
                            st.write("---")
                            st.subheader("Other Advanced Indicators")
                            
                            col1, col2 = st.columns(2)
                            
                            # Average True Range (ATR)
                            if "atr" in analysis_data["indicators"]:
                                atr_value = analysis_data["indicators"]["atr"]["atr_14"]
                                with col1:
                                    st.metric("ATR (14)", f"{atr_value:.2f}")
                                    st.write(f"The Average True Range indicates the level of volatility. Higher values (>{atr_value/df['Close'].iloc[-1]*100:.2f}% of price) suggest higher volatility.")
                            
                            # Stochastic Oscillator
                            if "stochastic" in analysis_data["indicators"]:
                                stoch_data = analysis_data["indicators"]["stochastic"]
                                with col2:
                                    st.metric("Stochastic K", f"{stoch_data['k_value']:.2f}")
                                    st.metric("Stochastic D", f"{stoch_data['d_value']:.2f}")
                                    
                                    if stoch_data['k_value'] > 80:
                                        st.error("Stochastic is in overbought territory.")
                                    elif stoch_data['k_value'] < 20:
                                        st.success("Stochastic is in oversold territory.")
                                    
                                    if stoch_data['k_value'] > stoch_data['d_value']:
                                        st.success("Stochastic K is above D, suggesting bullish momentum.")
                                    else:
                                        st.error("Stochastic K is below D, suggesting bearish momentum.")
                            
                            # Parabolic SAR
                            if "psar" in analysis_data["indicators"]:
                                psar_data = analysis_data["indicators"]["psar"]
                                st.write("---")
                                st.write(f"**Parabolic SAR:** {psar_data['psar_value']:.2f}")
                                st.write(f"**Trend (PSAR):** {psar_data['trend']}")
                                
                                if psar_data['trend'] == "Uptrend":
                                    st.success("Parabolic SAR indicates an uptrend.")
                                else:
                                    st.error("Parabolic SAR indicates a downtrend.")
                        
                        with adv_tab2:
                            st.subheader("Chart Pattern Recognition")
                            
                            if "patterns" in analysis_data:
                                patterns = analysis_data["patterns"]
                                
                                if patterns.get("summary", {}).get("detected_count", 0) > 0:
                                    st.success(f"Detected {patterns['summary']['detected_count']} patterns!")
                                    
                                    # Head and Shoulders
                                    if "head_and_shoulders" in patterns:
                                        hs_pattern = patterns["head_and_shoulders"]
                                        if hs_pattern.get("detected", False):
                                            st.write("---")
                                            pattern_type = hs_pattern.get("pattern_type", "")
                                            if pattern_type == "head_and_shoulders":
                                                st.warning("**Head and Shoulders Pattern Detected**")
                                                st.write("This is typically a bearish reversal pattern suggesting a potential downtrend.")
                                            elif pattern_type == "inverse_head_and_shoulders":
                                                st.success("**Inverse Head and Shoulders Pattern Detected**")
                                                st.write("This is typically a bullish reversal pattern suggesting a potential uptrend.")
                                    
                                    # Double Top/Bottom
                                    if "double_pattern" in patterns:
                                        double_pattern = patterns["double_pattern"]
                                        if double_pattern.get("detected", False):
                                            st.write("---")
                                            pattern_type = double_pattern.get("pattern_type", "")
                                            if pattern_type == "double_top":
                                                st.warning("**Double Top Pattern Detected**")
                                                st.write("This is typically a bearish reversal pattern suggesting a potential downtrend.")
                                            elif pattern_type == "double_bottom":
                                                st.success("**Double Bottom Pattern Detected**")
                                                st.write("This is typically a bullish reversal pattern suggesting a potential uptrend.")
                                    
                                    # Cup and Handle
                                    if "cup_and_handle" in patterns:
                                        cup_pattern = patterns["cup_and_handle"]
                                        if cup_pattern.get("detected", False):
                                            st.write("---")
                                            st.success("**Cup and Handle Pattern Detected**")
                                            st.write("This is typically a bullish continuation pattern suggesting a potential uptrend continuation.")
                                    
                                    # Flag/Pennant
                                    if "flag_pennant" in patterns:
                                        flag_pattern = patterns["flag_pennant"]
                                        if flag_pattern.get("detected", False):
                                            st.write("---")
                                            pattern_type = flag_pattern.get("pattern_type", "")
                                            direction = flag_pattern.get("direction", "")
                                            
                                            if pattern_type == "flag":
                                                st.write(f"**{direction.capitalize()} Flag Pattern Detected**")
                                            elif pattern_type == "pennant":
                                                st.write(f"**{direction.capitalize()} Pennant Pattern Detected**")
                                            
                                            if direction == "bullish":
                                                st.success("This is typically a bullish continuation pattern suggesting a potential uptrend continuation.")
                                            else:
                                                st.warning("This is typically a bearish continuation pattern suggesting a potential downtrend continuation.")
                                else:
                                    st.info("No significant chart patterns detected in the current time frame.")
                                    st.write("Chart patterns often require specific market conditions and may not be present at all times.")
                            else:
                                st.error("Pattern analysis data not available.")
                        
                        with adv_tab3:
                            st.subheader("Fibonacci Retracement Levels")
                            
                            if "fibonacci" in analysis_data["indicators"]:
                                fib_levels = analysis_data["indicators"]["fibonacci"]
                                
                                # Create a figure with Fibonacci levels
                                fig = go.Figure()
                                
                                # Add price line
                                fig.add_trace(go.Scatter(
                                    x=df["Date"], 
                                    y=df["Close"], 
                                    name="Price",
                                    line=dict(color='blue')
                                ))
                                
                                # Add Fibonacci levels as horizontal lines
                                colors = ['purple', 'red', 'orange', 'green', 'cyan', 'blue', 'magenta']
                                for i, (level_name, level_value) in enumerate(fib_levels.items()):
                                    fig.add_shape(
                                        type="line",
                                        x0=df["Date"].iloc[0],
                                        y0=level_value,
                                        x1=df["Date"].iloc[-1],
                                        y1=level_value,
                                        line=dict(
                                            color=colors[i % len(colors)],
                                            width=1,
                                            dash="dash",
                                        )
                                    )
                                    
                                    # Add annotations for the levels
                                    fig.add_annotation(
                                        x=df["Date"].iloc[-1],
                                        y=level_value,
                                        text=f"{level_name}: ${level_value:.2f}",
                                        showarrow=False,
                                        xshift=100,
                                        align="left"
                                    )
                                
                                # Update layout
                                fig.update_layout(
                                    title=f"{symbol} Fibonacci Retracement Levels",
                                    xaxis_title="Date",
                                    yaxis_title="Price ($)",
                                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Display Fibonacci levels
                                st.write("**Fibonacci Retracement Levels:**")
                                for level_name, level_value in fib_levels.items():
                                    st.write(f"**{level_name}:** ${level_value:.2f}")
                                
                                # Interpretation
                                st.subheader("Fibonacci Level Interpretation")
                                st.write("""
                                Fibonacci retracement levels represent potential support and resistance areas. Traders often watch these levels for potential reversal or continuation patterns.
                                
                                - The 23.6%, 38.2%, and 50% levels often act as minor support/resistance.
                                - The 61.8% level is considered a stronger support/resistance level.
                                - If price breaks below the 61.8% level, it may continue to the 78.6% or 100% level.
                                """)
                                
                                # Current price in relation to Fibonacci levels
                                current_price = df["Close"].iloc[-1]
                                for i, (level_name, level_value) in enumerate(sorted(fib_levels.items(), key=lambda x: float(x[1]))):
                                    if current_price > level_value:
                                        if i < len(fib_levels) - 1:
                                            next_level_name = list(sorted(fib_levels.items(), key=lambda x: float(x[1])))[i+1][0]
                                            next_level_value = list(sorted(fib_levels.items(), key=lambda x: float(x[1])))[i+1][1]
                                            st.write(f"Current price (${current_price:.2f}) is between {level_name} (${level_value:.2f}) and {next_level_name} (${next_level_value:.2f}).")
                                            break
                            else:
                                st.error("Fibonacci analysis data not available.")
                    else:
                        st.error(f"Error performing advanced technical analysis: {analysis_result.get('message', 'Unknown error')}")
                
                # Add overall analysis and recommendations
                st.subheader("Technical Analysis Summary")
                
                # Run technical analysis agent to get signals
                tech_analysis_agent = TechnicalAnalysisAgent()
                with st.spinner("Generating technical analysis summary..."):
                    analysis_result = asyncio.run(tech_analysis_agent.run({
                        "symbol": symbol,
                        "indicators": ["sma", "ema", "rsi", "macd", "bollinger", "stochastic", "ichimoku"],
                        "period": 100
                    }))
                
                if analysis_result["status"] == "success":
                    signals = analysis_result["data"]["signals"]
                    
                    # Display overall signal
                    overall_signal = signals.get("overall", {}).get("signal", "Neutral")
                    signal_colors = {
                        "Strong Buy": "green",
                        "Buy": "lightgreen",
                        "Neutral": "gray",
                        "Sell": "lightcoral",
                        "Strong Sell": "red"
                    }
                    
                    signal_color = signal_colors.get(overall_signal, "gray")
                    
                    st.markdown(f"<h3 style='color: {signal_color}'>Overall Signal: {overall_signal}</h3>", unsafe_allow_html=True)
                    
                    # Display signal counts
                    bullish_count = signals.get("overall", {}).get("bullish_count", 0)
                    bearish_count = signals.get("overall", {}).get("bearish_count", 0)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Bullish Signals", bullish_count)
                    with col2:
                        st.metric("Bearish Signals", bearish_count)
                    with col3:
                        confidence = signals.get("overall", {}).get("confidence", 0) * 100
                        st.metric("Signal Confidence", f"{confidence:.1f}%")
                    
                    # Display indicator signals
                    st.write("**Individual Indicator Signals:**")
                    
                    # Create a DataFrame for indicator signals
                    indicator_data = []
                    
                    if "moving_averages" in signals:
                        ma_signal = signals["moving_averages"]["trend"]
                        indicator_data.append(["Moving Averages", ma_signal])
                    
                    if "rsi" in signals:
                        rsi_signal = signals["rsi"]["signal"]
                        indicator_data.append(["RSI", rsi_signal])
                    
                    if "macd" in signals:
                        macd_signal = signals["macd"]["signal"]
                        indicator_data.append(["MACD", macd_signal])
                    
                    if "bollinger" in signals:
                        bb_signal = signals["bollinger"]["signal"]
                        indicator_data.append(["Bollinger Bands", bb_signal])
                    
                    if "stochastic" in signals:
                        stoch_signal = signals["stochastic"]["signal"]
                        indicator_data.append(["Stochastic", stoch_signal])
                    
                    if "ichimoku" in signals:
                        ichi_signal = signals["ichimoku"]["signal"]
                        indicator_data.append(["Ichimoku Cloud", ichi_signal])
                    
                    if "psar" in signals:
                        psar_signal = signals["psar"]["signal"]
                        indicator_data.append(["Parabolic SAR", psar_signal])
                    
                    if indicator_data:
                        # Create a DataFrame and display it
                        signal_df = pd.DataFrame(indicator_data, columns=["Indicator", "Signal"])
                        
                        # Apply color formatting based on signals
                        def color_signal(val):
                            if "Buy" in val:
                                return "background-color: lightgreen"
                            elif "Sell" in val:
                                return "background-color: lightcoral"
                            else:
                                return "background-color: lightgray"
                        
                        st.dataframe(signal_df.style.applymap(color_signal, subset=["Signal"]), use_container_width=True)
                else:
                    st.error(f"Error generating signals: {analysis_result.get('message', 'Unknown error')}")
            else:
                st.error("No historical data available for the selected symbol and date range.")
    else:
        st.info("Click 'Run Analysis' to generate technical analysis for the selected symbol.")

def render_fundamental_analysis(symbol, run_analysis):
    st.header(f"Fundamental Analysis for {symbol}")
    
    if run_analysis:
        # Initialize the market data agent
        market_data_agent = MarketDataAgent()
        
        # Use st.spinner to show loading state
        with st.spinner(f"Fetching fundamental data for {symbol}..."):
            # Run the agent to get market data
            market_data = asyncio.run(market_data_agent.fetch_market_data(
                symbol, 
                interval="1d"
            ))
            
            if "error" in market_data:
                st.error(f"Error fetching data: {market_data['error']}")
                return
            
            # Create columns for key metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Current Price", f"${market_data.get('current_price', 0):.2f}")
                
            with col2:
                market_cap = market_data.get('market_cap', 0)
                market_cap_display = f"${market_cap/1000000000:.2f}B" if market_cap > 1000000000 else f"${market_cap/1000000:.2f}M"
                st.metric("Market Cap", market_cap_display)
                
            with col3:
                pe_ratio = market_data.get('pe_ratio')
                pe_display = f"{pe_ratio:.2f}" if pe_ratio else "N/A"
                st.metric("P/E Ratio", pe_display)
            
            # Additional metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                div_yield = market_data.get('dividend_yield')
                div_display = f"{div_yield:.2f}%" if div_yield else "N/A"
                st.metric("Dividend Yield", div_display)
                
            with col2:
                week_high = market_data.get('52_week_high')
                high_display = f"${week_high:.2f}" if week_high else "N/A"
                st.metric("52-Week High", high_display)
                
            with col3:
                week_low = market_data.get('52_week_low')
                low_display = f"${week_low:.2f}" if week_low else "N/A"
                st.metric("52-Week Low", low_display)
            
            # Fetch historical data for financial ratios over time
            historical_data = pd.DataFrame(market_data.get("historical_data", []))
            if not historical_data.empty:
                # Ensure Date is datetime
                if "Date" in historical_data.columns:
                    historical_data["Date"] = pd.to_datetime(historical_data["Date"])
                elif "Datetime" in historical_data.columns:
                    historical_data["Date"] = pd.to_datetime(historical_data["Datetime"])
                    historical_data = historical_data.rename(columns={"Datetime": "Date"})
                
                # Create tabs for different analysis views
                tab1, tab2, tab3 = st.tabs(["Key Ratios", "Valuation", "Financial Summary"])
                
                with tab1:
                    st.subheader("Key Financial Ratios")
                    
                    # Display company info
                    st.info(f"**Company:** {market_data.get('company_name', symbol)}")
                    
                    # Financial ratios
                    ratios = {
                        "P/E Ratio": pe_display,
                        "Dividend Yield": div_display,
                        "Market Cap": market_cap_display,
                        "Price to Book": market_data.get('price_to_book', "N/A"),
                        "EPS": market_data.get('eps', "N/A"),
                        "Beta": market_data.get('beta', "N/A")
                    }
                    
                    # Display as a table
                    ratio_df = pd.DataFrame(list(ratios.items()), columns=["Ratio", "Value"])
                    st.table(ratio_df)
                
                with tab2:
                    st.subheader("Valuation Metrics")
                    
                    # Create dummy historical P/E data
                    # In a real implementation, you would fetch this from an API
                    if "Close" in historical_data.columns:
                        # Get last year of data
                        recent_data = historical_data.sort_values("Date").tail(252)  # ~1 year of trading days
                        
                        # Create a figure with P/E ratio over time (simulated)
                        fig = go.Figure()
                        
                        # Add historical price line
                        fig.add_trace(go.Scatter(
                            x=recent_data["Date"], 
                            y=recent_data["Close"],
                            name="Price"
                        ))
                        
                        # Update layout
                        fig.update_layout(
                            title=f"{symbol} Price History",
                            xaxis_title="Date",
                            yaxis_title="Price ($)",
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Peer comparison
                    st.subheader("Peer Comparison")
                    st.write("Comparison to industry peers:")
                    
                    # This would normally come from an API, using placeholder data
                    peer_data = {
                        "Company": [symbol, "Peer 1", "Peer 2", "Peer 3", "Industry Avg"],
                        "P/E Ratio": [pe_ratio or 0, 15.2, 18.7, 12.5, 16.8],
                        "Dividend Yield": [market_data.get('dividend_yield', 0) or 0, 1.8, 2.1, 1.5, 1.9],
                        "Market Cap ($B)": [market_cap/1000000000 if market_cap else 0, 250, 180, 120, 200]
                    }
                    
                    peer_df = pd.DataFrame(peer_data)
                    st.table(peer_df)
                
                with tab3:
                    st.subheader("Financial Summary")
                    
                    # Financial summary
                    if "Close" in historical_data.columns and len(historical_data) >= 252:
                        # Calculate yearly performance
                        recent_year = historical_data.sort_values("Date").tail(252)
                        start_price = recent_year["Close"].iloc[0]
                        end_price = recent_year["Close"].iloc[-1]
                        yearly_return = ((end_price / start_price) - 1) * 100
                        
                        # Calculate 3-month performance
                        recent_quarter = historical_data.sort_values("Date").tail(63)  # ~3 months
                        start_price_q = recent_quarter["Close"].iloc[0]
                        end_price_q = recent_quarter["Close"].iloc[-1]
                        quarter_return = ((end_price_q / start_price_q) - 1) * 100
                        
                        # Display performance metrics
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("1-Year Return", f"{yearly_return:.2f}%")
                        with col2:
                            st.metric("3-Month Return", f"{quarter_return:.2f}%")
                    
                    # Income statement highlights
                    st.subheader("Income Statement Highlights")
                    st.info("For detailed financial statements, please refer to the company's investor relations website or financial databases.")
            else:
                st.warning("Historical data not available for fundamental analysis.")
    else:
        st.info("Click 'Run Analysis' to generate fundamental analysis for the selected symbol.")

def render_sentiment_analysis(symbol, run_analysis):
    st.header(f"Sentiment Analysis for {symbol}")
    
    if run_analysis:
        # Initialize the news sentiment agent
        news_agent = NewsSentimentAgent()
        
        # Use st.spinner to show loading state
        with st.spinner(f"Analyzing news sentiment for {symbol}..."):
            # Run the agent to get sentiment data
            sentiment_data = asyncio.run(news_agent.process(f"What is the sentiment for {symbol} this week?"))
            
            if sentiment_data.get("status") == "error":
                st.error(f"Error analyzing sentiment: {sentiment_data.get('message', 'Unknown error')}")
                return
            
            sentiment_results = sentiment_data.get("data", {})
            
            if sentiment_results:
                # Create tabs for different sentiment views
                tab1, tab2 = st.tabs(["Sentiment Overview", "News Articles"])
                
                with tab1:
                    st.subheader("Sentiment Overview")
                    
                    # Display overall sentiment
                    overall_sentiment = sentiment_results.get("overall_sentiment", "neutral")
                    sentiment_score = sentiment_results.get("sentiment_score", 0)
                    
                    # Create a gauge chart for sentiment score
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = sentiment_score,
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': f"Sentiment Score for {symbol}"},
                        gauge = {
                            'axis': {'range': [-1, 1]},
                            'bar': {'color': "darkblue"},
                            'steps' : [
                                {'range': [-1, -0.3], 'color': "red"},
                                {'range': [-0.3, 0.3], 'color': "gray"},
                                {'range': [0.3, 1], 'color': "green"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': sentiment_score
                            }
                        }
                    ))
                    
                    fig.update_layout(height=250)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Sentiment distribution
                    st.subheader("Sentiment Distribution")
                    
                    sentiment_dist = sentiment_results.get("sentiment_distribution", {})
                    
                    # Create a pie chart
                    labels = list(sentiment_dist.keys())
                    values = list(sentiment_dist.values())
                    
                    if sum(values) > 0:
                        fig = go.Figure(data=[go.Pie(
                            labels=labels, 
                            values=values,
                            hole=.3,
                            marker_colors=['green', 'gray', 'red']
                        )])
                        
                        fig.update_layout(height=300)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No sentiment distribution data available.")
                    
                    # Article count
                    article_count = sentiment_results.get("article_count", 0)
                    st.metric("Total Articles Analyzed", article_count)
                    
                    # Sentiment summary
                    st.subheader("Sentiment Summary")
                    
                    if overall_sentiment == "positive":
                        st.success(f"The overall sentiment for {symbol} is positive, with a score of {sentiment_score:.2f}.")
                    elif overall_sentiment == "negative":
                        st.error(f"The overall sentiment for {symbol} is negative, with a score of {sentiment_score:.2f}.")
                    else:
                        st.info(f"The overall sentiment for {symbol} is neutral, with a score of {sentiment_score:.2f}.")
                
                with tab2:
                    st.subheader("News Articles")
                    
                    articles = sentiment_results.get("articles", [])
                    
                    if articles:
                        # Group articles by sentiment
                        positive_articles = [a for a in articles if a.get("sentiment") == "positive"]
                        neutral_articles = [a for a in articles if a.get("sentiment") == "neutral"]
                        negative_articles = [a for a in articles if a.get("sentiment") == "negative"]
                        
                        # Create expandable sections for each sentiment category
                        with st.expander(f"Positive Articles ({len(positive_articles)})", expanded=True):
                            for article in positive_articles:
                                st.markdown(f"""
                                **{article.get('title', 'No Title')}**  
                                Source: {article.get('source', 'Unknown')} | Score: {article.get('sentiment_score', 0):.2f}  
                                [Read More]({article.get('url', '#')})
                                """)
                                st.divider()
                        
                        with st.expander(f"Neutral Articles ({len(neutral_articles)})"):
                            for article in neutral_articles:
                                st.markdown(f"""
                                **{article.get('title', 'No Title')}**  
                                Source: {article.get('source', 'Unknown')} | Score: {article.get('sentiment_score', 0):.2f}  
                                [Read More]({article.get('url', '#')})
                                """)
                                st.divider()
                        
                        with st.expander(f"Negative Articles ({len(negative_articles)})"):
                            for article in negative_articles:
                                st.markdown(f"""
                                **{article.get('title', 'No Title')}**  
                                Source: {article.get('source', 'Unknown')} | Score: {article.get('sentiment_score', 0):.2f}  
                                [Read More]({article.get('url', '#')})
                                """)
                                st.divider()
                    else:
                        st.info(f"No news articles found for {symbol}.")
            else:
                st.warning(f"No sentiment data available for {symbol}.")
    else:
        st.info("Click 'Run Analysis' to generate sentiment analysis for the selected symbol.")

def render_risk_analysis(symbol, run_analysis):
    st.header(f"Risk Analysis for {symbol}")
    
    if run_analysis:
        # Create tabs for different risk views
        tab1, tab2, tab3 = st.tabs(["Risk Metrics", "Volatility Analysis", "Portfolio Impact"])
        
        with tab1:
            st.subheader("Key Risk Metrics")
            
            # Risk metrics table
            col1, col2 = st.columns(2)
            
            with col1:
                metrics1 = {
                    "Beta": "1.23",
                    "Alpha (1Y)": "5.67%",
                    "R-Squared": "0.85",
                    "Sharpe Ratio": "1.45",
                    "Treynor Ratio": "8.92"
                }
                
                for metric, value in metrics1.items():
                    st.metric(label=metric, value=value)
            
            with col2:
                metrics2 = {
                    "Standard Deviation (1Y)": "22.4%",
                    "Max Drawdown (1Y)": "-18.3%",
                    "VaR (95%, 1D)": "-2.8%",
                    "Sortino Ratio": "1.82",
                    "Information Ratio": "0.76"
                }
                
                for metric, value in metrics2.items():
                    st.metric(label=metric, value=value)
            
            # Risk assessment
            st.subheader("Risk Assessment")
            st.write("""
            The stock exhibits moderate to high risk characteristics with a beta of 1.23, indicating higher volatility than the market.
            However, the positive alpha suggests the stock has outperformed on a risk-adjusted basis. The Sharpe and Sortino ratios
            indicate good risk-adjusted returns. Investors should be prepared for potential drawdowns of up to 18% based on historical data.
            """)
        
        with tab2:
            st.subheader("Volatility Analysis")
            
            # Generate dummy data for volatility
            dates = pd.date_range(start="2022-01-01", end="2023-01-01", freq="B")
            market_volatility = np.random.normal(15, 3, size=len(dates))
            stock_volatility = market_volatility * 1.2 + np.random.normal(0, 2, size=len(dates))
            
            # Ensure volatility is positive
            market_volatility = np.abs(market_volatility)
            stock_volatility = np.abs(stock_volatility)
            
            # Apply some smoothing
            market_volatility = np.convolve(market_volatility, np.ones(20)/20, mode='same')
            stock_volatility = np.convolve(stock_volatility, np.ones(20)/20, mode='same')
            
            # Create volatility chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dates, y=stock_volatility, name=f"{symbol} Volatility"))
            fig.add_trace(go.Scatter(x=dates, y=market_volatility, name="Market Volatility", line=dict(dash='dash')))
            
            fig.update_layout(
                title="Historical Volatility Comparison",
                xaxis_title="Date",
                yaxis_title="Volatility (%)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Volatility distribution
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=stock_volatility, name=f"{symbol} Volatility", opacity=0.7))
            fig.add_trace(go.Histogram(x=market_volatility, name="Market Volatility", opacity=0.7))
            
            fig.update_layout(
                title="Volatility Distribution",
                xaxis_title="Volatility (%)",
                yaxis_title="Frequency",
                barmode='overlay',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("Portfolio Impact Analysis")
            
            # Portfolio allocation input
            st.write("Adjust the allocation to see the impact on portfolio risk:")
            allocation = st.slider("Allocation (%)", min_value=0, max_value=100, value=10, step=5)
            
            # Generate correlation matrix
            assets = [symbol, "MSFT", "GOOGL", "AMZN", "META", "SPY"]
            
            # Create a random correlation matrix (for demonstration)
            np.random.seed(42)
            corr_matrix = np.random.uniform(0.3, 0.9, size=(len(assets), len(assets)))
            np.fill_diagonal(corr_matrix, 1.0)
            corr_matrix = (corr_matrix + corr_matrix.T) / 2  # Make it symmetric
            
            # Convert to DataFrame for display
            corr_df = pd.DataFrame(corr_matrix, columns=assets, index=assets)
            
            # Display correlation matrix as heatmap
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix,
                x=assets,
                y=assets,
                colorscale='RdBu_r',
                zmin=-1,
                zmax=1
            ))
            
            fig.update_layout(
                title="Correlation Matrix",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Portfolio impact metrics
            st.subheader(f"Impact of {allocation}% Allocation")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(label="Portfolio Beta Change", value=f"+{0.02 * allocation:.2f}")
                st.metric(label="Expected Return Impact", value=f"+{0.05 * allocation:.2f}%")
            
            with col2:
                st.metric(label="Volatility Impact", value=f"+{0.03 * allocation:.2f}%")
                st.metric(label="Sharpe Ratio Impact", value=f"+{0.01 * allocation:.2f}")
    else:
        st.info("Click 'Run Analysis' to generate risk analysis for the selected symbol.") 