from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
import logging
import requests
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

from src.agents.base_agent import BaseAgent, AgentState

# Load environment variables
load_dotenv()

class InsiderTradingState(AgentState):
    """State for the insider trading agent"""
    cached_data: Dict[str, Any] = Field(default_factory=dict)
    last_cache_update: Optional[datetime] = None
    cache_duration: int = 3600  # Cache duration in seconds (default: 1 hour)

class InsiderTradingAgent(BaseAgent):
    """Agent responsible for monitoring and analyzing insider trading activities"""
    
    def __init__(self, agent_id: str = "insider_trading_agent"):
        """Initialize the insider trading agent"""
        super().__init__(agent_id, "insider_trading")
        self.state = InsiderTradingState(agent_id=agent_id, agent_type="insider_trading")
        self.logger = logging.getLogger(__name__)
        self.finnhub_api_key = os.getenv("FINNHUB_API_KEY", "")
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY", "")
        self.sec_api_key = os.getenv("SEC_API_KEY", "")
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the insider trading agent's main functionality"""
        self.update_status("running")
        
        try:
            # Extract parameters from input data
            symbol = input_data.get("symbol", "")
            lookback_days = input_data.get("lookback_days", 90)
            
            if not symbol:
                raise ValueError("Symbol is required")
            
            # Calculate cache key
            cache_key = f"{symbol}_{lookback_days}"
            
            # Check if we have cached data that's still valid
            if (cache_key in self.state.cached_data and 
                self.state.last_cache_update and 
                (datetime.now() - self.state.last_cache_update).total_seconds() < self.state.cache_duration):
                self.update_status("idle")
                return {"status": "success", "data": self.state.cached_data[cache_key]}
            
            # Fetch insider trading data
            self.state.add_message("system", f"Fetching insider trading data for {symbol}")
            insider_data = await self.fetch_insider_data(symbol, lookback_days)
            
            if "error" in insider_data:
                raise ValueError(f"Error fetching insider data: {insider_data['error']}")
            
            # Analyze the insider trading activity
            self.state.add_message("system", "Analyzing insider trading patterns")
            analysis = await self.analyze_insider_activity(insider_data, symbol)
            
            # Compile results
            result = {
                "symbol": symbol,
                "analysis_date": datetime.now().isoformat(),
                "insider_data": insider_data,
                "analysis": analysis
            }
            
            # Cache the result
            self.state.cached_data[cache_key] = result
            self.state.last_cache_update = datetime.now()
            
            self.update_status("idle")
            return {"status": "success", "data": result}
        
        except Exception as e:
            self.logger.error(f"Error in insider trading agent: {str(e)}")
            self.update_status("error")
            self.state.add_message("system", f"Error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def fetch_insider_data(self, symbol: str, lookback_days: int = 90) -> Dict[str, Any]:
        """Fetch insider trading data for a specific symbol"""
        try:
            # First try to use SEC API if key is available (most official source)
            if self.sec_api_key:
                sec_data = await self.fetch_from_sec(symbol, lookback_days)
                if sec_data and "transactions" in sec_data and sec_data["transactions"]:
                    return sec_data
            
            # Then try to use Finnhub API if key is available
            if self.finnhub_api_key:
                finnhub_data = await self.fetch_from_finnhub(symbol, lookback_days)
                if finnhub_data and "transactions" in finnhub_data and finnhub_data["transactions"]:
                    return finnhub_data
            
            # Try to use Alpha Vantage API if key is available
            if self.alpha_vantage_key:
                alpha_data = await self.fetch_from_alpha_vantage(symbol)
                if alpha_data and not alpha_data.get("limited_data", True):
                    return alpha_data
            
            # Fall back to synthetic data if no API keys are available or no data returned
            return self.generate_synthetic_insider_data(symbol, lookback_days)
            
        except Exception as e:
            self.logger.error(f"Error fetching insider data: {str(e)}")
            return {"error": str(e)}
    
    async def fetch_from_sec(self, symbol: str, lookback_days: int = 90) -> Dict[str, Any]:
        """Fetch insider trading data from SEC API"""
        if not self.sec_api_key:
            return {"error": "SEC API key not configured"}
            
        try:
            # Calculate start date
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)
            
            # Format dates
            from_date = start_date.strftime("%Y-%m-%d")
            to_date = end_date.strftime("%Y-%m-%d")
            
            # SEC API endpoint for Form 4 filings (insider transactions)
            url = "https://api.sec-api.io/insider-trading"
            
            # Prepare the query payload
            payload = {
                "query": f"issuer.tradingSymbol:{symbol} AND periodOfReport:[{from_date} TO {to_date}]",
                "from": "0",
                "size": "50",
                "sort": [{"filedAt": {"order": "desc"}}]
            }
            
            # Make API request with payload as JSON
            headers = {"Authorization": self.sec_api_key}
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code != 200:
                self.logger.warning(f"SEC API error: {response.status_code} - {response.text}")
                return {"error": f"SEC API error: {response.status_code}"}
                
            data = response.json()
            
            # Process the data into a standard format
            insider_transactions = []
            
            # Check if we have transactions data
            if "transactions" in data and data["transactions"]:
                for filing in data["transactions"]:
                    # Process each filing
                    if "nonDerivativeTable" in filing and "transactions" in filing["nonDerivativeTable"]:
                        for transaction in filing["nonDerivativeTable"]["transactions"]:
                            # Extract transaction details
                            if "coding" in transaction and "code" in transaction["coding"]:
                                # Get transaction code (P=purchase, S=sale, etc.)
                                transaction_code = transaction["coding"].get("code", "")
                                
                                # Skip if not a transaction we're interested in
                                if transaction_code not in ["P", "S", "A", "D"]:
                                    continue
                                
                                # Get shares and price
                                if "amounts" in transaction:
                                    shares = transaction["amounts"].get("shares", 0)
                                    price = transaction["amounts"].get("pricePerShare", 0)
                                    acquired_disposed = transaction["amounts"].get("acquiredDisposedCode", "")
                                    
                                    # For sales, make shares negative
                                    if acquired_disposed == "D":
                                        shares = -abs(shares)
                                    
                                    # Calculate value
                                    value = abs(shares) * price
                                    
                                    # Get post-transaction amounts
                                    shares_owned_after = 0
                                    if "postTransactionAmounts" in transaction:
                                        shares_owned_after = transaction["postTransactionAmounts"].get(
                                            "sharesOwnedFollowingTransaction", 0
                                        )
                                    
                                    # Get ownership nature
                                    ownership_type = "direct"
                                    if "ownershipNature" in transaction:
                                        direct_or_indirect = transaction["ownershipNature"].get("directOrIndirectOwnership", "D")
                                        ownership_type = "indirect" if direct_or_indirect == "I" else "direct"
                                        
                                    # Add insider information
                                    insider_name = filing["reportingOwner"]["name"] if "reportingOwner" in filing and "name" in filing["reportingOwner"] else ""
                                    insider_role = ""
                                    if "reportingOwner" in filing and "relationship" in filing["reportingOwner"]:
                                        relationship = filing["reportingOwner"]["relationship"]
                                        if relationship.get("isDirector", False):
                                            insider_role = "Director"
                                        elif relationship.get("isOfficer", False):
                                            insider_role = relationship.get("officerTitle", "Officer")
                                        elif relationship.get("isTenPercentOwner", False):
                                            insider_role = "10% Owner"
                                    
                                    # Format transaction date
                                    transaction_date = transaction.get("transactionDate", filing.get("periodOfReport", ""))
                                    filing_date = filing.get("filedAt", "").split("T")[0] if "filedAt" in filing else ""
                                    
                                    insider_transactions.append({
                                        "filing_date": filing_date,
                                        "transaction_date": transaction_date,
                                        "insider_name": insider_name,
                                        "role": insider_role,
                                        "transaction_type": transaction_code,
                                        "shares": shares,
                                        "share_price": price,
                                        "value": value,
                                        "shares_owned_after": shares_owned_after,
                                        "source": "sec"
                                    })
            
            # If we have transactions, return them
            if insider_transactions:
                return {
                    "source": "sec",
                    "transactions": insider_transactions,
                    "symbol": symbol
                }
            else:
                return {"error": "No SEC insider trading data available", "symbol": symbol}
                
        except Exception as e:
            self.logger.error(f"Error fetching from SEC API: {str(e)}")
            return {"error": f"SEC API error: {str(e)}"}
    
    async def fetch_from_finnhub(self, symbol: str, lookback_days: int = 90) -> Dict[str, Any]:
        """Fetch insider trading data from Finnhub API"""
        # Calculate start date
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        # Format dates
        from_date = start_date.strftime("%Y-%m-%d")
        to_date = end_date.strftime("%Y-%m-%d")
        
        # Construct API URL
        url = f"https://finnhub.io/api/v1/stock/insider-transactions?symbol={symbol}&token={self.finnhub_api_key}&from={from_date}&to={to_date}"
        
        # Make API request
        response = requests.get(url)
        
        if response.status_code != 200:
            raise Exception(f"Finnhub API error: {response.status_code} - {response.text}")
        
        data = response.json()
        
        # Process the data into a standard format
        insider_transactions = []
        
        if "data" in data:
            for transaction in data["data"]:
                insider_transactions.append({
                    "filing_date": transaction.get("filingDate", ""),
                    "transaction_date": transaction.get("transactionDate", ""),
                    "insider_name": transaction.get("name", ""),
                    "role": transaction.get("position", ""),
                    "transaction_type": transaction.get("transactionCode", ""),
                    "shares": transaction.get("share", 0),
                    "share_price": transaction.get("price", 0),
                    "value": transaction.get("value", 0),
                    "shares_owned_after": transaction.get("sharesOwned", 0),
                    "source": "finnhub"
                })
        
        return {
            "source": "finnhub",
            "transactions": insider_transactions,
            "symbol": symbol
        }
    
    async def fetch_from_alpha_vantage(self, symbol: str) -> Dict[str, Any]:
        """Fetch insider trading data from Alpha Vantage API"""
        # Alpha Vantage API doesn't directly provide insider trading data
        # We'll use the overview endpoint to get some basic insider ownership data
        url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={self.alpha_vantage_key}"
        
        # Make API request
        response = requests.get(url)
        
        if response.status_code != 200:
            raise Exception(f"Alpha Vantage API error: {response.status_code} - {response.text}")
        
        data = response.json()
        
        # Extract insider ownership info
        insider_ownership_pct = data.get("PercentInsiders", "0")
        
        # Since Alpha Vantage doesn't provide detailed transaction data,
        # we'll return the limited information we have
        return {
            "source": "alpha_vantage",
            "insider_ownership_percentage": insider_ownership_pct,
            "symbol": symbol,
            "limited_data": True,
            "transactions": []  # No transaction details available
        }
    
    def generate_synthetic_insider_data(self, symbol: str, lookback_days: int = 90) -> Dict[str, Any]:
        """Generate synthetic insider trading data for demonstration purposes"""
        # List of common insider roles
        roles = ["CEO", "CFO", "COO", "CTO", "Director", "VP", "Chairman"]
        
        # List of common transaction types
        # P = Purchase, S = Sale, A = Grant/Award, D = Sale to Cover (tax obligations)
        transaction_types = ["P", "S", "A", "D"]
        
        # Generate random transactions
        insider_transactions = []
        
        # Create 5-15 random transactions within the lookback period
        num_transactions = np.random.randint(5, 16)
        
        for _ in range(num_transactions):
            # Random date within lookback period
            days_ago = np.random.randint(0, lookback_days)
            transaction_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            filing_date = (datetime.now() - timedelta(days=days_ago-2)).strftime("%Y-%m-%d")  # Filing usually happens 2 days after
            
            # Random price around $50 (adjust as needed)
            share_price = np.random.uniform(30.0, 70.0)
            
            # Random number of shares, typically in multiples of 100
            shares = np.random.randint(1, 50) * 100
            
            # Random transaction type (with bias toward sales)
            transaction_type = np.random.choice(transaction_types, p=[0.3, 0.4, 0.2, 0.1])
            
            # For sales, use negative shares
            if transaction_type in ["S", "D"]:
                shares = -shares
            
            # Random insider
            insider_name = f"Executive {np.random.randint(1, 10)}"
            role = np.random.choice(roles)
            
            # Calculate value
            value = abs(shares) * share_price
            
            # Random shares owned after transaction
            shares_owned_after = np.random.randint(1000, 100000) if shares > 0 else np.random.randint(100, 10000)
            
            insider_transactions.append({
                "filing_date": filing_date,
                "transaction_date": transaction_date,
                "insider_name": insider_name,
                "role": role,
                "transaction_type": transaction_type,
                "shares": shares,
                "share_price": round(share_price, 2),
                "value": round(value, 2),
                "shares_owned_after": shares_owned_after,
                "source": "synthetic"
            })
        
        # Sort by transaction date (most recent first)
        insider_transactions.sort(key=lambda x: x["transaction_date"], reverse=True)
        
        return {
            "source": "synthetic",
            "transactions": insider_transactions,
            "symbol": symbol,
            "is_synthetic": True
        }
    
    async def analyze_insider_activity(self, insider_data: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """Analyze insider trading patterns and sentiment"""
        # Check if we have transaction data to analyze
        if "transactions" not in insider_data or not insider_data["transactions"]:
            if insider_data.get("source") == "alpha_vantage" and "insider_ownership_percentage" in insider_data:
                # Limited analysis based on insider ownership percentage
                ownership_pct = float(insider_data["insider_ownership_percentage"].replace("%", ""))
                
                sentiment = "neutral"
                if ownership_pct > 15:
                    sentiment = "very positive"
                elif ownership_pct > 10:
                    sentiment = "positive"
                
                return {
                    "insider_ownership_pct": ownership_pct,
                    "sentiment": sentiment,
                    "limited_analysis": True,
                    "insights": [f"Insiders own {ownership_pct}% of {symbol} shares"]
                }
            
            return {
                "sentiment": "neutral",
                "insufficient_data": True,
                "insights": ["Insufficient insider trading data available for analysis"]
            }
        
        # Process transactions
        transactions = insider_data["transactions"]
        
        # Extract buy/sell transactions
        buys = [t for t in transactions if t["transaction_type"] == "P"]
        sells = [t for t in transactions if t["transaction_type"] == "S" or t["transaction_type"] == "D"]
        
        # Calculate total values
        total_buy_value = sum(t["value"] for t in buys) if buys else 0
        total_sell_value = sum(t["value"] for t in sells) if sells else 0
        
        # Calculate buy/sell ratio (avoid division by zero)
        buy_sell_ratio = 0
        if total_sell_value > 0:
            buy_sell_ratio = total_buy_value / total_sell_value
        elif total_buy_value > 0:
            buy_sell_ratio = float('inf')  # Infinite ratio if buys but no sells
        
        # Calculate total buy/sell volumes
        total_buy_shares = sum(t["shares"] for t in buys) if buys else 0
        total_sell_shares = sum(abs(t["shares"]) for t in sells) if sells else 0  # Use abs() as sell shares might be negative
        
        # Find notable transactions (large purchases or sales)
        notable_transactions = []
        for t in transactions:
            if abs(t["value"]) > 100000:  # Transactions over $100,000
                notable_transactions.append(t)
        
        # Determine overall sentiment
        sentiment = "neutral"
        if total_buy_value == 0 and total_sell_value == 0:
            sentiment = "neutral"
        elif buy_sell_ratio == float('inf'):
            sentiment = "very bullish"  # Only buys, no sells
        elif buy_sell_ratio > 5:
            sentiment = "very bullish"
        elif buy_sell_ratio > 2:
            sentiment = "bullish"
        elif buy_sell_ratio < 0.2 and total_sell_value > 0:
            sentiment = "very bearish"
        elif buy_sell_ratio < 0.5 and total_sell_value > 0:
            sentiment = "bearish"
        
        # Generate insights
        insights = []
        
        # Add data source information
        data_source = insider_data.get("source", "unknown")
        if data_source == "sec":
            insights.append("Analysis based on official SEC Form 4 filings")
        elif data_source == "finnhub":
            insights.append("Analysis based on Finnhub insider trading data")
        elif data_source == "synthetic":
            insights.append("Analysis based on synthetic data (for demonstration purposes)")
        
        if len(buys) > 0:
            insights.append(f"Insiders purchased {total_buy_shares:,} shares (${total_buy_value:,.2f}) in the past period")
        
        if len(sells) > 0:
            insights.append(f"Insiders sold {total_sell_shares:,} shares (${total_sell_value:,.2f}) in the past period")
        
        if buy_sell_ratio > 1 and total_sell_value > 0:
            insights.append(f"Insider buying exceeds selling by {buy_sell_ratio:.1f}x")
        elif buy_sell_ratio < 1 and buy_sell_ratio > 0:
            insights.append(f"Insider selling exceeds buying by {1/buy_sell_ratio:.1f}x")
        elif buy_sell_ratio == float('inf'):
            insights.append("Insiders only buying, no selling activity detected")
        elif total_buy_value == 0 and total_sell_value > 0:
            insights.append("Only insider selling detected, no buying activity")
        
        # Add insights about notable transactions
        if notable_transactions:
            for t in notable_transactions[:3]:  # Limit to top 3 notable transactions
                action = "purchased" if t["transaction_type"] == "P" else "sold"
                insights.append(
                    f"{t['role']} {t['insider_name']} {action} {abs(t['shares']):,} shares (${t['value']:,.2f}) on {t['transaction_date']}"
                )
        
        # Look for clusters of transactions
        recent_transactions = []
        for t in transactions:
            try:
                # Handle possible date format issues
                if t.get("transaction_date"):
                    transaction_date = t["transaction_date"]
                    # Try to parse date in different formats
                    try:
                        # Standard YYYY-MM-DD format
                        parsed_date = datetime.strptime(transaction_date, "%Y-%m-%d")
                    except ValueError:
                        try:
                            # Try MM/DD/YYYY format
                            parsed_date = datetime.strptime(transaction_date, "%m/%d/%Y")
                        except ValueError:
                            # Skip if can't parse date
                            continue
                    
                    # Check if transaction is recent
                    if parsed_date > datetime.now() - timedelta(days=30):
                        recent_transactions.append(t)
            except Exception:
                # Skip transactions with unparseable dates
                continue
                
        if len(recent_transactions) >= 3:
            insights.append(f"Cluster of {len(recent_transactions)} insider transactions in the past 30 days")
        
        # Check for transactions by key executives
        ceo_transactions = [t for t in transactions if t.get("role") and ("CEO" in t["role"] or "Chief Executive" in t["role"])]
        cfo_transactions = [t for t in transactions if t.get("role") and ("CFO" in t["role"] or "Chief Financial" in t["role"])]
        
        if ceo_transactions:
            ceo_buys = [t for t in ceo_transactions if t["transaction_type"] == "P"]
            ceo_sells = [t for t in ceo_transactions if t["transaction_type"] == "S" or t["transaction_type"] == "D"]
            
            if ceo_buys:
                insights.append(f"CEO purchased shares recently - potentially positive signal")
            elif ceo_sells:
                insights.append(f"CEO sold shares recently - may be routine or potential caution signal")
        
        if cfo_transactions:
            cfo_buys = [t for t in cfo_transactions if t["transaction_type"] == "P"]
            cfo_sells = [t for t in cfo_transactions if t["transaction_type"] == "S" or t["transaction_type"] == "D"]
            
            if cfo_buys:
                insights.append(f"CFO purchased shares recently - potentially positive signal")
        
        return {
            "sentiment": sentiment,
            "buy_sell_ratio": buy_sell_ratio if buy_sell_ratio != float('inf') else 999.99,  # Cap infinite ratio for display purposes
            "total_buy_value": total_buy_value,
            "total_sell_value": total_sell_value,
            "total_buy_shares": total_buy_shares,
            "total_sell_shares": total_sell_shares,
            "notable_transactions_count": len(notable_transactions),
            "insights": insights,
            "data_source": data_source
        }
    
    async def process(self, query: str) -> Dict[str, Any]:
        """Process a specific query related to insider trading"""
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
        
        # Determine lookback period
        lookback_days = 90  # Default to 90 days
        if "year" in query_lower:
            lookback_days = 365
        elif "month" in query_lower or "30 day" in query_lower:
            lookback_days = 30
        elif "quarter" in query_lower or "3 month" in query_lower:
            lookback_days = 90
        elif "6 month" in query_lower:
            lookback_days = 180
        
        # Run analysis
        result = await self.run({
            "symbol": symbol,
            "lookback_days": lookback_days
        })
        
        self.state.add_message("assistant", result)
        self.update_status("idle")
        return result
    
    def clear_cache(self):
        """Clear the agent's cache"""
        self.state.cached_data = {}
        self.state.last_cache_update = None 