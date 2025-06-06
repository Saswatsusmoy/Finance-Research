import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

def render_dashboard():
    st.title("Financial Research Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Market Overview")
        market_metrics = {
            "S&P 500": 4782.82,
            "NASDAQ": 16740.39,
            "Dow Jones": 38239.98,
            "VIX": 13.21
        }
        
        # Create a placeholder for real data
        df = pd.DataFrame({
            'Index': list(market_metrics.keys()),
            'Value': list(market_metrics.values()),
            'Change': [0.32, 0.58, 0.17, -2.14]
        })
        
        st.dataframe(df, hide_index=True, use_container_width=True)
        
        st.subheader("Recent News Sentiment")
        sentiment_data = {
            'Positive': 65,
            'Neutral': 25,
            'Negative': 10
        }
        
        fig = go.Figure(data=[go.Pie(
            labels=list(sentiment_data.keys()),
            values=list(sentiment_data.values()),
            hole=.3,
            marker_colors=['#76c893', '#caf0f8', '#e76f51']
        )])
        
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Portfolio Performance")
        
        # Generate dummy data for chart
        dates = [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(30, 0, -1)]
        portfolio_values = [10000 + (x * 25) + (x * x) for x in range(30)]
        benchmark_values = [10000 + (x * 20) for x in range(30)]
        
        df = pd.DataFrame({
            'Date': dates,
            'Portfolio': portfolio_values,
            'Benchmark': benchmark_values
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Portfolio'], name='Portfolio', line=dict(color='#4c9be8')))
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Benchmark'], name='Benchmark', line=dict(color='#bdbdbd')))
        
        fig.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=30, b=40),
            xaxis_title="Date",
            yaxis_title="Value ($)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Risk Assessment")
        risk_metrics = {
            "Volatility": "12.3%",
            "Sharpe Ratio": "1.8",
            "Max Drawdown": "-8.2%",
            "Beta": "0.85"
        }
        
        for metric, value in risk_metrics.items():
            st.metric(label=metric, value=value)
    
    st.subheader("Recent Agent Activities")
    activities = [
        {"agent": "Market Data", "action": "Updated price data for AAPL, MSFT, GOOGL", "time": "5 minutes ago"},
        {"agent": "News Sentiment", "action": "Analyzed 24 recent articles about tech sector", "time": "12 minutes ago"},
        {"agent": "Technical Analysis", "action": "Detected bullish pattern on TSLA", "time": "27 minutes ago"},
        {"agent": "Risk Assessment", "action": "Updated portfolio risk metrics", "time": "43 minutes ago"}
    ]
    
    for activity in activities:
        with st.container():
            cols = st.columns([1, 3, 1])
            with cols[0]:
                st.write(f"**{activity['agent']} Agent**")
            with cols[1]:
                st.write(activity['action'])
            with cols[2]:
                st.write(activity['time']) 