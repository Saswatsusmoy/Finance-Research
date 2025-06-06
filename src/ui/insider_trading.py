import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import asyncio
from datetime import datetime, timedelta

from src.agents.insider_trading_agent import InsiderTradingAgent
from src.ui.insider_trading_ui import display_insider_trading_ui

def render_insider_trading():
    st.title("Insider Trading Monitor")
    
    # Tab options to choose between basic and advanced UI
    tab1, tab2 = st.tabs(["Standard View", "Advanced View"])
    
    with tab1:
        # Sidebar for insider trading options
        st.sidebar.subheader("Options")
        
        # Symbol input
        symbol = st.sidebar.text_input("Symbol", value="AAPL")
        
        # Lookback period
        lookback_options = {
            "1 Month": 30,
            "3 Months": 90,
            "6 Months": 180,
            "1 Year": 365
        }
        lookback = st.sidebar.selectbox("Lookback Period", list(lookback_options.keys()), index=1)
        lookback_days = lookback_options[lookback]
        
        # Run analysis button
        run_analysis = st.sidebar.button("Run Analysis")
        
        # Main content
        if run_analysis:
            # Initialize the insider trading agent
            insider_agent = InsiderTradingAgent()
            
            # Use st.spinner to show loading state
            with st.spinner(f"Fetching insider trading data for {symbol}..."):
                # Run the agent to get insider trading data and analysis
                result = asyncio.run(insider_agent.run({
                    "symbol": symbol,
                    "lookback_days": lookback_days
                }))
                
                if result["status"] != "success":
                    st.error(f"Error fetching data: {result.get('message', 'Unknown error')}")
                    return
                
                data = result["data"]
                insider_data = data["insider_data"]
                analysis = data["analysis"]
                
                # Display source information
                source = insider_data.get("source", "unknown")
                source_colors = {
                    "sec": "#1E88E5",       # Blue for SEC
                    "finnhub": "#4CAF50",   # Green for Finnhub
                    "synthetic": "#FFC107", # Yellow for synthetic data
                    "unknown": "#757575"    # Gray for unknown
                }
                source_color = source_colors.get(source, source_colors["unknown"])
                
                # Display data source prominently
                st.markdown(
                    f"""
                    <div style="background-color: {source_color}; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
                        <h3 style="color: white; margin: 0;">Data Source: {source.upper()}</h3>
                        <p style="color: white; margin: 0;">
                            {
                                "Official SEC Form 4 filings" if source == "sec" else
                                "Finnhub insider trading API" if source == "finnhub" else
                                "Alpha Vantage API (limited data)" if source == "alpha_vantage" else
                                "Synthetic data (for demonstration purposes)" if source == "synthetic" else
                                "Unknown data source"
                            }
                        </p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
                # Display analysis overview
                st.header("Insider Trading Analysis")
                
                # Display sentiment with appropriate color
                sentiment = analysis.get("sentiment", "neutral")
                sentiment_colors = {
                    "very bullish": "green",
                    "bullish": "lightgreen",
                    "neutral": "gray",
                    "bearish": "lightcoral",
                    "very bearish": "red"
                }
                sentiment_color = sentiment_colors.get(sentiment, "gray")
                
                st.markdown(f"<h3 style='color: {sentiment_color}'>Overall Sentiment: {sentiment.capitalize()}</h3>", unsafe_allow_html=True)
                
                # Display key metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Buy/Sell Ratio", f"{analysis.get('buy_sell_ratio', 0):.2f}")
                    st.metric("Buy Volume", f"{analysis.get('total_buy_shares', 0):,} shares")
                
                with col2:
                    buy_value = analysis.get('total_buy_value', 0)
                    sell_value = analysis.get('total_sell_value', 0)
                    st.metric("Buy Value", f"${buy_value:,.2f}")
                    st.metric("Sell Volume", f"{analysis.get('total_sell_shares', 0):,} shares")
                
                with col3:
                    notable_count = analysis.get('notable_transactions_count', 0)
                    st.metric("Notable Transactions", f"{notable_count}")
                    st.metric("Sell Value", f"${sell_value:,.2f}")
                
                # Display insights
                st.subheader("Key Insights")
                insights = analysis.get("insights", [])
                if insights:
                    for insight in insights:
                        st.write(f"• {insight}")
                else:
                    st.info("No significant insights detected from available data.")
                
                # Display transactions if available
                if "transactions" in insider_data and insider_data["transactions"]:
                    st.subheader("Recent Transactions")
                    
                    # Convert to DataFrame for display
                    transactions = insider_data["transactions"]
                    df = pd.DataFrame(transactions)
                    
                    # Add a formatted transaction description column
                    def format_transaction(row):
                        action = "purchased" if row["transaction_type"] == "P" else "sold" if row["transaction_type"] in ["S", "D"] else "awarded"
                        shares = abs(row["shares"])
                        return f"{row['insider_name']} ({row['role']}) {action} {shares:,} shares at ${row['share_price']:.2f} (${row['value']:,.2f})"
                    
                    if not df.empty:
                        df["description"] = df.apply(format_transaction, axis=1)
                        
                        # Keep only relevant columns for display
                        display_df = df[["transaction_date", "description", "shares_owned_after"]].copy()
                        display_df.columns = ["Date", "Transaction", "Shares Owned After"]
                        
                        st.dataframe(display_df, use_container_width=True)
                    
                    # Create buying/selling bar chart
                    st.subheader("Insider Trading Volume")
                    
                    # Group by transaction date and type
                    chart_data = []
                    
                    for t in transactions:
                        trans_type = "Buy" if t["transaction_type"] == "P" else "Sell" if t["transaction_type"] in ["S", "D"] else "Award"
                        shares = abs(t["shares"])
                        value = t["value"]
                        chart_data.append({
                            "date": t["transaction_date"],
                            "type": trans_type,
                            "shares": shares,
                            "value": value
                        })
                    
                    chart_df = pd.DataFrame(chart_data)
                    
                    if not chart_df.empty:
                        # Convert date to datetime for proper sorting
                        chart_df["date"] = pd.to_datetime(chart_df["date"])
                        chart_df = chart_df.sort_values("date")
                        
                        # Group by date and type, summing shares
                        grouped_df = chart_df.groupby(["date", "type"]).agg({"shares": "sum", "value": "sum"}).reset_index()
                        
                        # Create figure
                        fig = go.Figure()
                        
                        # Add buy transactions
                        buy_df = grouped_df[grouped_df["type"] == "Buy"]
                        if not buy_df.empty:
                            fig.add_trace(go.Bar(
                                x=buy_df["date"],
                                y=buy_df["shares"],
                                name="Buy",
                                marker_color="green"
                            ))
                        
                        # Add sell transactions
                        sell_df = grouped_df[grouped_df["type"] == "Sell"]
                        if not sell_df.empty:
                            fig.add_trace(go.Bar(
                                x=sell_df["date"],
                                y=sell_df["shares"],
                                name="Sell",
                                marker_color="red"
                            ))
                        
                        # Update layout
                        fig.update_layout(
                            title=f"{symbol} Insider Trading Volume",
                            xaxis_title="Date",
                            yaxis_title="Shares",
                            barmode="group",
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Enter a stock symbol and click 'Run Analysis' to view insider trading activity.")
            
            # Display Data Source Information
            st.subheader("Data Sources")
            st.markdown("""
            The Insider Trading Monitor uses multiple data sources, prioritized in the following order:
            
            1. **SEC Form 4 Filings** 🔵 - Most official source from the Securities and Exchange Commission
               - Requires SEC API key in `.env` file
               - Provides the most accurate and comprehensive insider trading data
               - Direct from official regulatory filings
            
            2. **Finnhub API** 🟢 - Alternative financial data source
               - Requires Finnhub API key in `.env` file
               - Aggregated insider trading data with good coverage
            
            3. **Alpha Vantage API** 🟡 - Limited insider ownership data
               - Requires Alpha Vantage API key in `.env` file
               - Provides only basic insider ownership percentage
            
            4. **Synthetic Data** 🟠 - Used for demonstration purposes
               - Generated when no API keys are available
               - For educational and demonstration purposes only
            """)
            
            # Display sample insights
            st.subheader("About Insider Trading Analysis")
            st.write("""
            Insider trading monitoring tracks the buying and selling activity of corporate insiders - directors, officers, and significant shareholders.
            
            **Why monitor insider trading?**
            
            * Insiders have unique knowledge about their company's prospects
            * Significant insider buying often precedes positive stock performance
            * Clusters of insider selling may signal caution
            * Executive (CEO, CFO) transactions tend to be particularly informative
            
            Enter a stock symbol and select a lookback period to analyze insider trading patterns.
            """)
    
    with tab2:
        # Use the advanced UI
        display_insider_trading_ui()
