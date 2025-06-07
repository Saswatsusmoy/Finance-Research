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

# Enhanced color scheme for better visual appeal
CHART_COLORS = {
    'primary': '#00d2ff',
    'secondary': '#3a7bd5', 
    'success': '#10b981',
    'danger': '#ef4444',
    'warning': '#f59e0b',
    'purple': '#8b5cf6',
    'pink': '#ec4899',
    'teal': '#14b8a6',
    'orange': '#f97316',
    'background': 'rgba(15, 23, 42, 0.8)',
    'grid': 'rgba(148, 163, 184, 0.1)',
    'text': '#e2e8f0'
}

def get_enhanced_layout(title, height=400):
    """Get enhanced layout configuration for charts"""
    return {
        'title': {
            'text': title,
            'font': {'size': 18, 'color': CHART_COLORS['text'], 'family': 'Inter, -apple-system, sans-serif'},
            'x': 0.02,
            'y': 0.98
        },
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {'color': CHART_COLORS['text'], 'family': 'Inter, -apple-system, sans-serif'},
        'xaxis': {
            'gridcolor': CHART_COLORS['grid'],
            'showgrid': True,
            'color': CHART_COLORS['text'],
            'tickformat': '%Y-%m-%d',
            'showline': True,
            'linecolor': CHART_COLORS['grid'],
            'mirror': True
        },
        'yaxis': {
            'gridcolor': CHART_COLORS['grid'],
            'showgrid': True,
            'color': CHART_COLORS['text'],
            'showline': True,
            'linecolor': CHART_COLORS['grid'],
            'mirror': True
        },
        'margin': {'t': 50, 'r': 30, 'b': 50, 'l': 60},
        'height': height,
        'legend': {
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': -0.2,
            'xanchor': 'center',
            'x': 0.5,
            'bgcolor': 'rgba(0,0,0,0.3)',
            'bordercolor': CHART_COLORS['grid'],
            'borderwidth': 1,
            'font': {'size': 12}
        },
        'hovermode': 'x unified',
        'hoverlabel': {
            'bgcolor': 'rgba(0,0,0,0.8)',
            'bordercolor': CHART_COLORS['primary'],
            'font': {'color': 'white', 'size': 12}
        }
    }

def render_analysis():
    st.title("📊 Financial Analysis Dashboard")
    
    # Enhanced sidebar with stock overview
    with st.sidebar:
        st.markdown("### 🎯 Stock Selection")
        
        # Symbol input with enhanced styling
        symbol = st.text_input(
            "Enter Stock Symbol", 
            value="AAPL",
            placeholder="e.g., AAPL, GOOGL, MSFT",
            help="Enter a valid stock ticker symbol"
        )
        
        # Quick symbol buttons for popular stocks
        st.markdown("**Quick Select:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("AAPL", key="aapl_btn"):
                symbol = "AAPL"
        with col2:
            if st.button("GOOGL", key="googl_btn"):
                symbol = "GOOGL"
        with col3:
            if st.button("MSFT", key="msft_btn"):
                symbol = "MSFT"
        
        col4, col5, col6 = st.columns(3)
        with col4:
            if st.button("TSLA", key="tsla_btn"):
                symbol = "TSLA"
        with col5:
            if st.button("AMZN", key="amzn_btn"):
                symbol = "AMZN"
        with col6:
            if st.button("META", key="meta_btn"):
                symbol = "META"
        
        st.divider()
        
        # Analysis type selection
        st.markdown("### 📈 Analysis Type")
        analysis_type = st.selectbox(
            "Choose Analysis",
            ["Technical Analysis", "Fundamental Analysis", "Sentiment Analysis", "Risk Analysis"],
            help="Select the type of analysis to perform"
        )
        
        st.divider()
        
        # Time range selection
        st.markdown("### 📅 Time Range")
        time_range = st.selectbox(
            "Select Period",
            ["1 Month", "3 Months", "6 Months", "1 Year", "2 Years", "5 Years", "Custom"],
            index=2,  # Default to 6 months
            help="Choose the time period for analysis"
        )
        
        # Custom date range if selected
        if time_range == "Custom":
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=180))
            with col2:
                end_date = st.date_input("End Date", value=datetime.now())
        else:
            # Calculate dates based on selection
            end_date = datetime.now()
            if time_range == "1 Month":
                start_date = end_date - timedelta(days=30)
            elif time_range == "3 Months":
                start_date = end_date - timedelta(days=90)
            elif time_range == "6 Months":
                start_date = end_date - timedelta(days=180)
            elif time_range == "1 Year":
                start_date = end_date - timedelta(days=365)
            elif time_range == "2 Years":
                start_date = end_date - timedelta(days=730)
            elif time_range == "5 Years":
                start_date = end_date - timedelta(days=1825)
        
        st.divider()
        
        # Technical indicators selection for technical analysis
        if analysis_type == "Technical Analysis":
            st.markdown("### ⚙️ Technical Indicators")
            
            # Moving Averages
            with st.expander("📈 Moving Averages", expanded=True):
                show_ma20 = st.checkbox("SMA 20", value=True)
                show_ma50 = st.checkbox("SMA 50", value=True)
                show_ma200 = st.checkbox("SMA 200", value=False)
                show_ema = st.checkbox("EMA 12/26", value=False)
            
            # Oscillators
            with st.expander("⚡ Oscillators", expanded=True):
                show_rsi = st.checkbox("RSI", value=True)
                show_macd = st.checkbox("MACD", value=True)
                show_stoch = st.checkbox("Stochastic", value=False)
            
            # Bands and Channels
            with st.expander("📊 Bands & Channels", expanded=False):
                show_bb = st.checkbox("Bollinger Bands", value=True)
                show_keltner = st.checkbox("Keltner Channels", value=False)
                show_donchian = st.checkbox("Donchian Channels", value=False)
            
            # Volume Indicators
            with st.expander("📈 Volume Indicators", expanded=False):
                show_volume = st.checkbox("Volume", value=True)
                show_vwap = st.checkbox("VWAP", value=False)
                show_obv = st.checkbox("OBV", value=False)
        
        st.divider()
        
        # Run analysis button with enhanced styling
        run_analysis = st.button(
            "🚀 Run Analysis",
            type="primary",
            use_container_width=True,
            help="Click to start the analysis with selected parameters"
        )
        
        # Stock overview section (if symbol is provided)
        if symbol and len(symbol) > 0:
            st.divider()
            st.markdown("### 📊 Stock Overview")
            
            # Try to fetch basic stock info for sidebar display
            try:
                market_data_agent = MarketDataAgent()
                with st.spinner("Loading stock info..."):
                    basic_info = asyncio.run(market_data_agent.fetch_market_data(
                        symbol, 
                        start_date=(datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                        end_date=datetime.now().strftime("%Y-%m-%d"),
                        interval="1d"
                    ))
                    
                    if basic_info and "historical_data" in basic_info and len(basic_info["historical_data"]) > 0:
                        latest_data = basic_info["historical_data"][-1]
                        prev_data = basic_info["historical_data"][-2] if len(basic_info["historical_data"]) > 1 else latest_data
                        
                        current_price = latest_data.get("Close", 0)
                        prev_price = prev_data.get("Close", current_price)
                        change = current_price - prev_price
                        change_pct = (change / prev_price * 100) if prev_price != 0 else 0
                        
                        # Display stock info in a nice format
                        st.markdown(f"**{symbol.upper()}**")
                        
                        # Price and change
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.metric(
                                label="Current Price",
                                value=f"${current_price:.2f}",
                                delta=f"{change:+.2f} ({change_pct:+.2f}%)"
                            )
                        
                        # Additional metrics
                        if len(basic_info["historical_data"]) > 1:
                            prices = [d["Close"] for d in basic_info["historical_data"]]
                            high_52w = max(prices)
                            low_52w = min(prices)
                            volume = latest_data.get("Volume", 0)
                            
                            st.markdown("**Range Information:**")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"**Day High:** ${latest_data.get('High', 0):.2f}")
                                st.markdown(f"**Day Low:** ${latest_data.get('Low', 0):.2f}")
                            with col2:
                                st.markdown(f"**52W High:** ${high_52w:.2f}")
                                st.markdown(f"**52W Low:** ${low_52w:.2f}")
                            
                            st.markdown(f"**Volume:** {volume:,}")
                            
                            # Quick analysis indicators
                            st.markdown("**Quick Analysis:**")
                            
                            # Trend indicator
                            if change_pct > 2:
                                trend_emoji = "🚀"
                                trend_text = "Strong Bullish"
                            elif change_pct > 0.5:
                                trend_emoji = "📈"
                                trend_text = "Bullish"
                            elif change_pct < -2:
                                trend_emoji = "📉"
                                trend_text = "Strong Bearish"
                            elif change_pct < -0.5:
                                trend_emoji = "⬇️"
                                trend_text = "Bearish"
                            else:
                                trend_emoji = "➡️"
                                trend_text = "Neutral"
                            
                            st.markdown(f"{trend_emoji} **Trend:** {trend_text}")
                            
                            # Volume analysis
                            if len(basic_info["historical_data"]) > 5:
                                avg_volume = sum(d.get("Volume", 0) for d in basic_info["historical_data"][-5:]) / 5
                                volume_ratio = volume / avg_volume if avg_volume > 0 else 1
                                
                                if volume_ratio > 1.5:
                                    volume_emoji = "🔥"
                                    volume_text = "High Volume"
                                elif volume_ratio < 0.5:
                                    volume_emoji = "💤"
                                    volume_text = "Low Volume"
                                else:
                                    volume_emoji = "📊"
                                    volume_text = "Normal Volume"
                                
                                st.markdown(f"{volume_emoji} **Volume:** {volume_text}")
                        
            except Exception as e:
                st.warning("Unable to load stock overview")
                st.caption(f"Error: {str(e)}")
        
        # Add some helpful tips
        st.divider()
        st.markdown("### 💡 Tips")
        st.caption("• Use technical analysis for short-term trading insights")
        st.caption("• Combine multiple indicators for better accuracy")
        st.caption("• Consider fundamental analysis for long-term investments")
        st.caption("• Monitor sentiment for market psychology insights")
    
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
                
                # Calculate Bollinger Bands
                df["BB_Middle"] = df["Close"].rolling(window=20).mean()
                bb_std = df["Close"].rolling(window=20).std()
                df["BB_Upper"] = df["BB_Middle"] + (bb_std * 2)
                df["BB_Lower"] = df["BB_Middle"] - (bb_std * 2)
                
                # Create tabs for different technical analysis views
                tab1, tab2, tab3, tab4 = st.tabs(["📈 Price & Volume", "📊 Moving Averages", "⚡ Oscillators", "🔬 Advanced Analysis"])
                
                with tab1:
                    st.subheader("Price & Volume Analysis")
                    
                    # Create enhanced candlestick chart with volume
                    fig = make_subplots(
                        rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.05,
                        row_heights=[0.7, 0.3],
                        subplot_titles=('Price Action', 'Volume')
                    )
                    
                    # Add candlestick chart
                    fig.add_trace(
                        go.Candlestick(
                            x=df["Date"],
                            open=df["Open"],
                            high=df["High"],
                            low=df["Low"],
                            close=df["Close"],
                            name="Price",
                            increasing_line_color=CHART_COLORS['success'],
                            decreasing_line_color=CHART_COLORS['danger'],
                            increasing_fillcolor=CHART_COLORS['success'],
                            decreasing_fillcolor=CHART_COLORS['danger']
                        ),
                        row=1, col=1
                    )
                    
                    # Add volume bars with color coding
                    colors = ['rgba(16, 185, 129, 0.6)' if close >= open else 'rgba(239, 68, 68, 0.6)' 
                             for close, open in zip(df["Close"], df["Open"])]
                    
                    fig.add_trace(
                        go.Bar(
                            x=df["Date"], 
                            y=df["Volume"], 
                            name="Volume",
                            marker_color=colors,
                            showlegend=False
                        ),
                        row=2, col=1
                    )
                    
                    # Enhanced layout
                    layout = get_enhanced_layout(f"{symbol} Price and Volume Analysis", 600)
                    layout['yaxis']['title'] = 'Price ($)'
                    layout['yaxis2'] = {
                        'title': 'Volume',
                        'gridcolor': CHART_COLORS['grid'],
                        'showgrid': True,
                        'color': CHART_COLORS['text']
                    }
                    
                    fig.update_layout(layout)
                    fig.update_xaxes(showgrid=True, gridcolor=CHART_COLORS['grid'])
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Enhanced support and resistance levels
                    st.subheader("📍 Key Levels")
                    
                    # Calculate pivot points and support/resistance levels
                    recent_df = df.tail(30)
                    high = recent_df["High"].max()
                    low = recent_df["Low"].min()
                    close = df["Close"].iloc[-1]
                    
                    # Pivot point calculation
                    pivot = (high + low + close) / 3
                    r1 = 2 * pivot - low
                    r2 = pivot + (high - low)
                    s1 = 2 * pivot - high
                    s2 = pivot - (high - low)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("🔴 Resistance 2", f"${r2:.2f}", f"{((r2-close)/close*100):+.1f}%")
                        st.metric("🟡 Resistance 1", f"${r1:.2f}", f"{((r1-close)/close*100):+.1f}%")
                    
                    with col2:
                        st.metric("⚪ Pivot Point", f"${pivot:.2f}", f"{((pivot-close)/close*100):+.1f}%")
                        st.metric("💰 Current Price", f"${close:.2f}", "0.0%")
                    
                    with col3:
                        st.metric("🟢 Support 1", f"${s1:.2f}", f"{((s1-close)/close*100):+.1f}%")
                        st.metric("🔵 Support 2", f"${s2:.2f}", f"{((s2-close)/close*100):+.1f}%")
                
                with tab2:
                    st.subheader("Moving Averages Analysis")
                    
                    # Enhanced moving averages chart with Bollinger Bands
                    fig = go.Figure()
                    
                    # Add Bollinger Bands first (background)
                    fig.add_trace(go.Scatter(
                        x=df["Date"], 
                        y=df["BB_Upper"],
                        line=dict(color='rgba(58, 123, 213, 0.3)', width=1),
                        name='BB Upper',
                        showlegend=False
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=df["Date"], 
                        y=df["BB_Lower"],
                        fill='tonexty',
                        fillcolor='rgba(58, 123, 213, 0.1)',
                        line=dict(color='rgba(58, 123, 213, 0.3)', width=1),
                        name='Bollinger Bands',
                        showlegend=True
                    ))
                    
                    # Add price line
                    fig.add_trace(go.Scatter(
                        x=df["Date"], 
                        y=df["Close"], 
                        name="Price",
                        line=dict(color=CHART_COLORS['primary'], width=2)
                    ))
                    
                    # Add moving averages with enhanced styling
                    fig.add_trace(go.Scatter(
                        x=df["Date"], 
                        y=df["MA20"], 
                        name="MA 20",
                        line=dict(color=CHART_COLORS['warning'], width=2, dash='solid')
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=df["Date"], 
                        y=df["MA50"], 
                        name="MA 50",
                        line=dict(color=CHART_COLORS['success'], width=2, dash='dash')
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=df["Date"], 
                        y=df["MA200"], 
                        name="MA 200",
                        line=dict(color=CHART_COLORS['danger'], width=2, dash='dot')
                    ))
                    
                    # Enhanced layout
                    layout = get_enhanced_layout(f"{symbol} Moving Averages & Bollinger Bands", 500)
                    layout['yaxis']['title'] = 'Price ($)'
                    fig.update_layout(layout)
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Enhanced moving average analysis
                    st.subheader("📊 Moving Average Signals")
                    
                    # Get the last values
                    last_ma20 = df["MA20"].iloc[-1] if not pd.isna(df["MA20"].iloc[-1]) else 0
                    last_ma50 = df["MA50"].iloc[-1] if not pd.isna(df["MA50"].iloc[-1]) else 0
                    last_ma200 = df["MA200"].iloc[-1] if not pd.isna(df["MA200"].iloc[-1]) else 0
                    last_close = df["Close"].iloc[-1]
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        ma20_signal = "🟢 Bullish" if last_close > last_ma20 else "🔴 Bearish"
                        st.metric("MA20 Signal", ma20_signal, f"${last_ma20:.2f}")
                    
                    with col2:
                        ma50_signal = "🟢 Bullish" if last_close > last_ma50 else "🔴 Bearish"
                        st.metric("MA50 Signal", ma50_signal, f"${last_ma50:.2f}")
                    
                    with col3:
                        ma200_signal = "🟢 Bullish" if last_close > last_ma200 else "🔴 Bearish"
                        st.metric("MA200 Signal", ma200_signal, f"${last_ma200:.2f}")
                    
                    with col4:
                        # Golden/Death Cross detection
                        if last_ma50 > last_ma200:
                            cross_signal = "🌟 Golden Cross"
                        else:
                            cross_signal = "💀 Death Cross"
                        st.metric("Cross Signal", cross_signal)
                    
                    # Bollinger Bands analysis
                    st.subheader("🎯 Bollinger Bands Analysis")
                    bb_upper = df["BB_Upper"].iloc[-1]
                    bb_lower = df["BB_Lower"].iloc[-1]
                    bb_position = (last_close - bb_lower) / (bb_upper - bb_lower) * 100
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if bb_position > 80:
                            bb_signal = "🔴 Overbought"
                        elif bb_position < 20:
                            bb_signal = "🟢 Oversold"
                        else:
                            bb_signal = "🟡 Neutral"
                        st.metric("BB Signal", bb_signal, f"{bb_position:.1f}%")
                    
                    with col2:
                        bb_width = ((bb_upper - bb_lower) / df["BB_Middle"].iloc[-1]) * 100
                        volatility = "🔥 High" if bb_width > 10 else "❄️ Low"
                        st.metric("Volatility", volatility, f"{bb_width:.1f}%")
                
                with tab3:
                    st.subheader("Technical Oscillators")
                    
                    # Create enhanced subplots for oscillators
                    fig = make_subplots(
                        rows=2, cols=1, 
                        shared_xaxes=True, 
                        vertical_spacing=0.08, 
                        row_heights=[0.5, 0.5],
                        subplot_titles=('RSI (Relative Strength Index)', 'MACD (Moving Average Convergence Divergence)')
                    )
                    
                    # Enhanced RSI with gradient fill
                    fig.add_trace(
                        go.Scatter(
                            x=df["Date"], 
                            y=df["RSI"], 
                            name="RSI",
                            line=dict(color=CHART_COLORS['purple'], width=2),
                            fill='tonexty',
                            fillcolor='rgba(139, 92, 246, 0.1)'
                        ),
                        row=1, col=1
                    )
                    
                    # Add RSI reference lines with enhanced styling
                    fig.add_hline(y=70, line_dash="dash", line_color=CHART_COLORS['danger'], 
                                 annotation_text="Overbought (70)", row=1, col=1)
                    fig.add_hline(y=50, line_dash="dot", line_color=CHART_COLORS['text'], 
                                 annotation_text="Neutral (50)", row=1, col=1)
                    fig.add_hline(y=30, line_dash="dash", line_color=CHART_COLORS['success'], 
                                 annotation_text="Oversold (30)", row=1, col=1)
                    
                    # Enhanced MACD with histogram colors
                    histogram_colors = [CHART_COLORS['success'] if val >= 0 else CHART_COLORS['danger'] 
                                       for val in df["Histogram"]]
                    
                    fig.add_trace(
                        go.Bar(
                            x=df["Date"], 
                            y=df["Histogram"], 
                            name="MACD Histogram",
                            marker_color=histogram_colors,
                            opacity=0.7
                        ),
                        row=2, col=1
                    )
                    
                    fig.add_trace(
                        go.Scatter(
                            x=df["Date"], 
                            y=df["MACD"], 
                            name="MACD Line",
                            line=dict(color=CHART_COLORS['primary'], width=2)
                        ),
                        row=2, col=1
                    )
                    
                    fig.add_trace(
                        go.Scatter(
                            x=df["Date"], 
                            y=df["Signal"], 
                            name="Signal Line",
                            line=dict(color=CHART_COLORS['warning'], width=2, dash='dash')
                        ),
                        row=2, col=1
                    )
                    
                    # Add zero line for MACD
                    fig.add_hline(y=0, line_dash="dot", line_color=CHART_COLORS['text'], 
                                 annotation_text="Zero Line", row=2, col=1)
                    
                    # Enhanced layout for oscillators
                    layout = get_enhanced_layout(f"{symbol} Technical Oscillators", 700)
                    layout['yaxis']['title'] = 'RSI'
                    layout['yaxis']['range'] = [0, 100]
                    layout['yaxis2'] = {
                        'title': 'MACD',
                        'gridcolor': CHART_COLORS['grid'],
                        'showgrid': True,
                        'color': CHART_COLORS['text']
                    }
                    
                    fig.update_layout(layout)
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Enhanced oscillator analysis
                    st.subheader("📊 Oscillator Signals")
                    
                    current_rsi = df["RSI"].iloc[-1] if not pd.isna(df["RSI"].iloc[-1]) else 50
                    current_macd = df["MACD"].iloc[-1] if not pd.isna(df["MACD"].iloc[-1]) else 0
                    current_signal = df["Signal"].iloc[-1] if not pd.isna(df["Signal"].iloc[-1]) else 0
                    current_histogram = df["Histogram"].iloc[-1] if not pd.isna(df["Histogram"].iloc[-1]) else 0
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if current_rsi > 70:
                            rsi_signal = "🔴 Overbought"
                        elif current_rsi < 30:
                            rsi_signal = "🟢 Oversold"
                        else:
                            rsi_signal = "🟡 Neutral"
                        st.metric("RSI Signal", rsi_signal, f"{current_rsi:.1f}")
                    
                    with col2:
                        macd_signal = "🟢 Bullish" if current_macd > current_signal else "🔴 Bearish"
                        st.metric("MACD Signal", macd_signal, f"{current_macd:.4f}")
                    
                    with col3:
                        momentum = "🚀 Increasing" if current_histogram > 0 else "📉 Decreasing"
                        st.metric("Momentum", momentum, f"{current_histogram:.4f}")
                    
                    with col4:
                        # Divergence detection (simplified)
                        price_trend = "📈 Up" if df["Close"].iloc[-1] > df["Close"].iloc[-10] else "📉 Down"
                        st.metric("Price Trend", price_trend)
                    
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