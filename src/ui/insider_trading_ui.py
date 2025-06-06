import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json

def display_insider_trading_ui():
    """Display the insider trading analysis UI"""
    st.title("Insider Trading Analysis")
    
    # Input section
    st.subheader("Stock Selection")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        symbol = st.text_input("Enter Stock Symbol", value="AAPL").upper()
    
    with col2:
        lookback_period = st.selectbox(
            "Lookback Period",
            options=["30 Days", "90 Days", "180 Days", "1 Year"],
            index=1
        )
    
    # Convert lookback period to days
    lookback_map = {
        "30 Days": 30,
        "90 Days": 90,
        "180 Days": 180,
        "1 Year": 365
    }
    lookback_days = lookback_map[lookback_period]
    
    # Add analyze button
    analyze_btn = st.button("Analyze Insider Trading")
    
    if analyze_btn or 'insider_data' in st.session_state:
        with st.spinner("Analyzing insider trading activities..."):
            # Use session state to store the data
            if analyze_btn or 'insider_data' not in st.session_state:
                # This is where we would call the InsiderTradingAgent in a real implementation
                from src.agents.insider_trading_agent import InsiderTradingAgent
                import asyncio
                
                # Create agent and run analysis
                agent = InsiderTradingAgent()
                result = asyncio.run(agent.run({"symbol": symbol, "lookback_days": lookback_days}))
                
                if result["status"] == "success":
                    st.session_state.insider_data = result["data"]
                else:
                    st.error(f"Error: {result.get('message', 'Failed to retrieve insider trading data')}")
                    return
            
            # Display the results
            display_insider_results(st.session_state.insider_data)
            
            # Add a button to clear the data and start over
            if st.button("Start New Analysis"):
                if 'insider_data' in st.session_state:
                    del st.session_state.insider_data

def display_insider_results(data):
    """Display the insider trading analysis results"""
    # Extract the data
    symbol = data["symbol"]
    analysis = data["analysis"]
    insider_data = data["insider_data"]
    
    # Display data source info
    data_source = insider_data.get("source", "unknown")
    
    source_colors = {
        "sec": "#1E88E5",       # Blue for SEC
        "finnhub": "#4CAF50",   # Green for Finnhub
        "synthetic": "#FFC107", # Yellow for synthetic data
        "unknown": "#757575"    # Gray for unknown
    }
    
    source_color = source_colors.get(data_source, source_colors["unknown"])
    
    st.markdown(
        f"""
        <div style="background-color: {source_color}; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
            <h3 style="color: white; margin: 0;">Data Source: {data_source.upper()}</h3>
            <p style="color: white; margin: 0;">
                {
                    "Official SEC Form 4 filings" if data_source == "sec" else
                    "Finnhub insider trading API" if data_source == "finnhub" else
                    "Synthetic data (for demonstration purposes)" if data_source == "synthetic" else
                    "Unknown data source"
                }
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Display overall sentiment and key metrics
    st.header(f"Insider Trading Analysis for {symbol}")
    
    # Show overall sentiment
    sentiment = analysis["sentiment"]
    sentiment_color = get_sentiment_color(sentiment)
    
    st.markdown(
        f"""
        <div style="background-color: {sentiment_color}; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
            <h2 style="color: white; margin: 0;">Overall Sentiment: {sentiment.title()}</h2>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Show key metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Buy/Sell Ratio", 
            f"{analysis.get('buy_sell_ratio', 0):.2f}",
            delta=None
        )
    
    with col2:
        buy_value = analysis.get("total_buy_value", 0)
        st.metric(
            "Total Buy Value", 
            f"${buy_value:,.2f}" if buy_value else "N/A",
            delta=None
        )
    
    with col3:
        sell_value = analysis.get("total_sell_value", 0)
        st.metric(
            "Total Sell Value", 
            f"${sell_value:,.2f}" if sell_value else "N/A",
            delta=None
        )
    
    # Show insights
    st.subheader("Key Insights")
    insights = analysis.get("insights", [])
    if insights:
        for insight in insights:
            st.markdown(f"• {insight}")
    else:
        st.info("No specific insights available for this analysis")
    
    # Show transactions if available
    if "transactions" in insider_data and insider_data["transactions"]:
        st.subheader("Recent Insider Transactions")
        transactions = insider_data["transactions"]
        
        # Convert to DataFrame for easier display
        df = pd.DataFrame(transactions)
        
        if not df.empty:
            # Create a summary chart of buy/sell transactions
            create_transaction_charts(df, symbol)
            
            # Display the table of transactions
            st.subheader("Transaction Details")
            
            # Clean up the DataFrame for display
            display_cols = [
                "transaction_date", "insider_name", "role", 
                "transaction_type", "shares", "share_price", "value"
            ]
            
            # Rename columns for better display
            rename_map = {
                "transaction_date": "Date",
                "insider_name": "Insider",
                "role": "Position",
                "transaction_type": "Type",
                "shares": "Shares",
                "share_price": "Price",
                "value": "Value ($)"
            }
            
            # Filter and rename columns
            if all(col in df.columns for col in display_cols):
                display_df = df[display_cols].rename(columns=rename_map)
                
                # Format transaction type
                if "Type" in display_df.columns:
                    display_df["Type"] = display_df["Type"].apply(format_transaction_type)
                
                # Format values
                if "Value ($)" in display_df.columns:
                    display_df["Value ($)"] = display_df["Value ($)"].apply(lambda x: f"${x:,.2f}")
                
                if "Price" in display_df.columns:
                    display_df["Price"] = display_df["Price"].apply(lambda x: f"${x:.2f}")
                
                # Display the table
                st.dataframe(display_df, use_container_width=True)
            else:
                st.warning("Transaction data format is not as expected")
    else:
        st.info("No transaction data available for this analysis")

def create_transaction_charts(df, symbol):
    """Create charts to visualize insider transactions"""
    # Add a column for formatted transaction dates (for better plotting)
    if "transaction_date" in df.columns:
        df["date"] = pd.to_datetime(df["transaction_date"])
    else:
        # If no transaction date, use filing date or today
        if "filing_date" in df.columns:
            df["date"] = pd.to_datetime(df["filing_date"])
        else:
            df["date"] = datetime.now()
    
    # Sort by date
    df = df.sort_values("date")
    
    # Prepare buy/sell data
    if "shares" in df.columns:
        buys = df[df["shares"] > 0].copy()
        sells = df[df["shares"] < 0].copy()
        sells["shares"] = sells["shares"].abs()  # Convert to positive for visualization
    else:
        buys = df[df["transaction_type"] == "P"].copy()
        sells = df[df["transaction_type"].isin(["S", "D"])].copy()
    
    # Create a timeline chart of transactions
    fig = go.Figure()
    
    # Add buy transactions
    if not buys.empty and "value" in buys.columns:
        fig.add_trace(go.Bar(
            x=buys["date"],
            y=buys["value"],
            name="Buy Transactions",
            marker_color="green",
            hovertemplate=
            "<b>Date:</b> %{x|%Y-%m-%d}<br>" +
            "<b>Value:</b> $%{y:,.2f}<br>" +
            "<extra></extra>"
        ))
    
    # Add sell transactions
    if not sells.empty and "value" in sells.columns:
        fig.add_trace(go.Bar(
            x=sells["date"],
            y=sells["value"],
            name="Sell Transactions",
            marker_color="red",
            hovertemplate=
            "<b>Date:</b> %{x|%Y-%m-%d}<br>" +
            "<b>Value:</b> $%{y:,.2f}<br>" +
            "<extra></extra>"
        ))
    
    # Update layout
    fig.update_layout(
        title=f"Insider Transaction Timeline - {symbol}",
        xaxis_title="Date",
        yaxis_title="Transaction Value ($)",
        barmode="group",
        hovermode="closest"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Create a pie chart of buy vs sell
    total_buy_value = buys["value"].sum() if not buys.empty else 0
    total_sell_value = sells["value"].sum() if not sells.empty else 0
    
    if total_buy_value > 0 or total_sell_value > 0:
        fig_pie = go.Figure(data=[go.Pie(
            labels=["Buy", "Sell"],
            values=[total_buy_value, total_sell_value],
            hole=.4,
            marker_colors=["green", "red"]
        )])
        
        fig_pie.update_layout(
            title=f"Insider Buy/Sell Ratio - {symbol}"
        )
        
        # Cumulative Insider Trading Activity
        dates = pd.date_range(
            start=df["date"].min() if not df.empty else datetime.now() - timedelta(days=90),
            end=df["date"].max() if not df.empty else datetime.now(),
            freq="D"
        )
        
        # Create a cumulative chart
        if not df.empty and "value" in df.columns and "transaction_type" in df.columns:
            # Create a new dataframe with daily net values
            daily_data = []
            
            for date in dates:
                day_df = df[df["date"] <= date]
                buy_sum = day_df[day_df["transaction_type"] == "P"]["value"].sum()
                sell_sum = day_df[day_df["transaction_type"].isin(["S", "D"])]["value"].sum()
                net = buy_sum - sell_sum
                daily_data.append({
                    "date": date,
                    "net_value": net,
                    "cumulative": net
                })
            
            daily_df = pd.DataFrame(daily_data)
            
            # Create cumulative chart
            fig_cum = px.line(
                daily_df, 
                x="date", 
                y="cumulative",
                title=f"Cumulative Insider Trading Activity - {symbol}"
            )
            
            fig_cum.update_layout(
                xaxis_title="Date",
                yaxis_title="Cumulative Net Value ($)",
                hovermode="x unified"
            )
            
            # Display charts in columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                st.plotly_chart(fig_cum, use_container_width=True)

def format_transaction_type(code):
    """Format transaction type code into a readable format"""
    type_map = {
        "P": "Purchase",
        "S": "Sale",
        "A": "Award/Grant",
        "D": "Sale to Cover",
        "M": "Option Exercise",
        "F": "Tax Payment",
        "X": "Option Exercise",
        "G": "Gift",
        "I": "Discretionary",
        "C": "Conversion",
        "O": "Other"
    }
    
    return type_map.get(code, code)

def get_sentiment_color(sentiment):
    """Get color based on sentiment"""
    sentiment_colors = {
        "very bullish": "#00C853",  # Strong green
        "bullish": "#4CAF50",       # Green
        "neutral": "#FFC107",       # Yellow
        "bearish": "#FF5722",       # Orange
        "very bearish": "#D32F2F"   # Red
    }
    
    return sentiment_colors.get(sentiment.lower(), "#FFC107")  # Default to yellow 