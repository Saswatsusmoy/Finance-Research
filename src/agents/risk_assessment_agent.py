from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
import logging
from pydantic import BaseModel, Field

from src.agents.base_agent import BaseAgent, AgentState
from src.agents.market_data_agent import MarketDataAgent

class RiskAssessmentState(AgentState):
    """State for the risk assessment agent"""
    cached_assessments: Dict[str, Any] = Field(default_factory=dict)
    risk_metrics: List[str] = Field(default_factory=lambda: ["beta", "volatility", "var", "sharpe", "sortino", "drawdown"])
    last_cache_update: Optional[datetime] = None
    cache_duration: int = 3600  # Cache duration in seconds (default: 1 hour)
    benchmark: str = "SPY"  # Default benchmark

class RiskAssessmentAgent(BaseAgent):
    """Agent responsible for assessing portfolio risk"""
    
    def __init__(self, agent_id: str = "risk_assessment_agent", market_data_agent: MarketDataAgent = None):
        """Initialize the risk assessment agent"""
        super().__init__(agent_id, "risk_assessment")
        self.state = RiskAssessmentState(agent_id=agent_id, agent_type="risk_assessment")
        self.logger = logging.getLogger(__name__)
        self.market_data_agent = market_data_agent or MarketDataAgent()
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the risk assessment agent's main functionality"""
        self.update_status("running")
        
        try:
            # Extract parameters from input data
            portfolio = input_data.get("portfolio", {})
            benchmark = input_data.get("benchmark", self.state.benchmark)
            period = input_data.get("period", 365)  # Default to 1 year
            metrics = input_data.get("metrics", self.state.risk_metrics)
            
            if not portfolio:
                raise ValueError("Portfolio is required")
            
            # Calculate date range
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=period)).strftime("%Y-%m-%d")
            
            # Fetch historical data for portfolio assets and benchmark
            self.state.add_message("system", "Fetching historical data for portfolio and benchmark")
            
            symbols = list(portfolio.keys())
            symbols.append(benchmark)
            
            # Fetch data for each symbol
            historical_data = {}
            for symbol in symbols:
                self.state.add_message("system", f"Fetching data for {symbol}")
                data = await self.market_data_agent.fetch_market_data(symbol, start_date, end_date)
                if "error" in data:
                    self.logger.warning(f"Error fetching data for {symbol}: {data['error']}")
                    continue
                
                # Extract price data
                prices = []
                dates = []
                for item in data.get("historical_data", []):
                    if "Close" in item:
                        prices.append(item["Close"])
                        dates.append(item.get("Date", ""))
                    elif "close" in item:
                        prices.append(item["close"])
                        dates.append(item.get("date", ""))
                
                if prices:
                    historical_data[symbol] = {"prices": prices, "dates": dates}
            
            # Calculate portfolio returns
            self.state.add_message("system", "Calculating portfolio returns")
            portfolio_returns, benchmark_returns = self._calculate_returns(historical_data, portfolio, benchmark)
            
            # Calculate risk metrics
            self.state.add_message("system", "Calculating risk metrics")
            risk_metrics = await self._calculate_risk_metrics(portfolio_returns, benchmark_returns, metrics)
            
            # Generate risk report
            self.state.add_message("system", "Generating risk report")
            risk_report = await self._generate_risk_report(risk_metrics, portfolio)
            
            # Combine results
            result = {
                "portfolio": portfolio,
                "benchmark": benchmark,
                "analysis_date": datetime.now().isoformat(),
                "risk_metrics": risk_metrics,
                "risk_report": risk_report
            }
            
            # Cache the result
            cache_key = f"{','.join(portfolio.keys())}_{benchmark}_{period}"
            self.state.cached_assessments[cache_key] = result
            self.state.last_cache_update = datetime.now()
            
            self.update_status("idle")
            return {"status": "success", "data": result}
        
        except Exception as e:
            self.logger.error(f"Error in risk assessment agent: {str(e)}")
            self.update_status("error")
            self.state.add_message("system", f"Error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def process(self, query: str) -> Dict[str, Any]:
        """Process a specific query related to risk assessment"""
        self.update_status("processing")
        self.state.add_message("user", query)
        
        # Simple query processing logic
        query_lower = query.lower()
        
        # Extract potential portfolio symbols
        import re
        symbols = re.findall(r'\b[A-Z]{1,5}\b', query)
        
        # Create a simple portfolio with equal weights
        if symbols:
            portfolio = {symbol: 1.0/len(symbols) for symbol in symbols}
        else:
            # Default portfolio for demonstration
            portfolio = {"AAPL": 0.2, "MSFT": 0.2, "GOOGL": 0.2, "AMZN": 0.2, "META": 0.2}
        
        # Determine benchmark
        benchmark = self.state.benchmark
        if "against" in query_lower or "compare" in query_lower or "vs" in query_lower:
            # Look for benchmark in query
            benchmark_candidates = ["SPY", "QQQ", "DIA", "IWM"]
            for candidate in benchmark_candidates:
                if candidate in query:
                    benchmark = candidate
                    break
        
        # Determine time period
        period = 365  # Default to 1 year
        if "5 year" in query_lower or "five year" in query_lower:
            period = 365 * 5
        elif "3 year" in query_lower or "three year" in query_lower:
            period = 365 * 3
        elif "2 year" in query_lower or "two year" in query_lower:
            period = 365 * 2
        elif "1 year" in query_lower or "one year" in query_lower:
            period = 365
        elif "6 month" in query_lower or "six month" in query_lower:
            period = 180
        elif "3 month" in query_lower or "three month" in query_lower:
            period = 90
        elif "month" in query_lower:
            period = 30
        
        # Determine metrics to calculate
        metrics = []
        if "all" in query_lower:
            metrics = self.state.risk_metrics
        else:
            if "beta" in query_lower:
                metrics.append("beta")
            if "volatility" in query_lower or "standard deviation" in query_lower:
                metrics.append("volatility")
            if "var" in query_lower or "value at risk" in query_lower:
                metrics.append("var")
            if "sharpe" in query_lower:
                metrics.append("sharpe")
            if "sortino" in query_lower:
                metrics.append("sortino")
            if "drawdown" in query_lower:
                metrics.append("drawdown")
        
        # If no specific metrics mentioned, use all
        if not metrics:
            metrics = self.state.risk_metrics
        
        # Run risk assessment
        result = await self.run({
            "portfolio": portfolio,
            "benchmark": benchmark,
            "period": period,
            "metrics": metrics
        })
        
        self.state.add_message("assistant", result)
        self.update_status("idle")
        return result
    
    def _calculate_returns(self, historical_data: Dict[str, Dict[str, List]], 
                           portfolio: Dict[str, float], 
                           benchmark: str) -> tuple:
        """Calculate portfolio and benchmark returns"""
        # Check if we have data for all symbols
        for symbol in portfolio:
            if symbol not in historical_data:
                self.logger.warning(f"No data for {symbol}, removing from portfolio")
                del portfolio[symbol]
        
        if not portfolio:
            raise ValueError("No valid symbols in portfolio")
        
        if benchmark not in historical_data:
            raise ValueError(f"No data for benchmark {benchmark}")
        
        # Normalize weights to sum to 1
        total_weight = sum(portfolio.values())
        normalized_portfolio = {k: v/total_weight for k, v in portfolio.items()}
        
        # Calculate daily returns for each asset
        returns = {}
        for symbol in normalized_portfolio:
            prices = historical_data[symbol]["prices"]
            daily_returns = [0]
            for i in range(1, len(prices)):
                daily_return = (prices[i] - prices[i-1]) / prices[i-1]
                daily_returns.append(daily_return)
            returns[symbol] = daily_returns
        
        # Calculate benchmark returns
        benchmark_prices = historical_data[benchmark]["prices"]
        benchmark_returns = [0]
        for i in range(1, len(benchmark_prices)):
            daily_return = (benchmark_prices[i] - benchmark_prices[i-1]) / benchmark_prices[i-1]
            benchmark_returns.append(daily_return)
        
        # Calculate weighted portfolio returns
        portfolio_returns = []
        min_length = min(len(returns[symbol]) for symbol in normalized_portfolio)
        for i in range(min_length):
            weighted_return = sum(returns[symbol][i] * normalized_portfolio[symbol] for symbol in normalized_portfolio)
            portfolio_returns.append(weighted_return)
        
        # Trim benchmark returns to match portfolio length
        benchmark_returns = benchmark_returns[:min_length]
        
        return portfolio_returns, benchmark_returns
    
    async def _calculate_risk_metrics(self, portfolio_returns: List[float], 
                                     benchmark_returns: List[float], 
                                     metrics: List[str]) -> Dict[str, Any]:
        """Calculate risk metrics for the portfolio"""
        result = {}
        
        # Convert to numpy arrays for calculations
        portfolio_returns_np = np.array(portfolio_returns)
        benchmark_returns_np = np.array(benchmark_returns)
        
        # Calculate beta
        if "beta" in metrics:
            # Calculate covariance between portfolio and benchmark
            covariance = np.cov(portfolio_returns_np, benchmark_returns_np)[0, 1]
            # Calculate variance of benchmark
            benchmark_variance = np.var(benchmark_returns_np)
            # Calculate beta
            beta = covariance / benchmark_variance if benchmark_variance != 0 else 1.0
            result["beta"] = beta
        
        # Calculate volatility (annualized standard deviation)
        if "volatility" in metrics:
            # Assuming 252 trading days in a year
            daily_std = np.std(portfolio_returns_np)
            annualized_volatility = daily_std * np.sqrt(252)
            result["volatility"] = annualized_volatility
        
        # Calculate Value at Risk (VaR)
        if "var" in metrics:
            # 95% VaR
            var_95 = np.percentile(portfolio_returns_np, 5)
            # 99% VaR
            var_99 = np.percentile(portfolio_returns_np, 1)
            result["var"] = {
                "var_95": var_95,
                "var_99": var_99
            }
        
        # Calculate Sharpe Ratio
        if "sharpe" in metrics:
            # Assuming risk-free rate of 0.02 (2%)
            risk_free_rate = 0.02 / 252  # Daily risk-free rate
            excess_returns = portfolio_returns_np - risk_free_rate
            mean_excess_return = np.mean(excess_returns)
            daily_std = np.std(portfolio_returns_np)
            sharpe_ratio = (mean_excess_return / daily_std) * np.sqrt(252) if daily_std != 0 else 0
            result["sharpe"] = sharpe_ratio
        
        # Calculate Sortino Ratio
        if "sortino" in metrics:
            # Assuming risk-free rate of 0.02 (2%)
            risk_free_rate = 0.02 / 252  # Daily risk-free rate
            excess_returns = portfolio_returns_np - risk_free_rate
            mean_excess_return = np.mean(excess_returns)
            # Calculate downside deviation (standard deviation of negative returns only)
            negative_returns = portfolio_returns_np[portfolio_returns_np < 0]
            downside_deviation = np.std(negative_returns) if len(negative_returns) > 0 else 0.0001
            sortino_ratio = (mean_excess_return / downside_deviation) * np.sqrt(252) if downside_deviation != 0 else 0
            result["sortino"] = sortino_ratio
        
        # Calculate Maximum Drawdown
        if "drawdown" in metrics:
            # Calculate cumulative returns
            cumulative_returns = np.cumprod(1 + portfolio_returns_np)
            # Calculate running maximum
            running_max = np.maximum.accumulate(cumulative_returns)
            # Calculate drawdown
            drawdown = (cumulative_returns - running_max) / running_max
            # Calculate maximum drawdown
            max_drawdown = np.min(drawdown)
            result["max_drawdown"] = max_drawdown
        
        return result
    
    async def _generate_risk_report(self, risk_metrics: Dict[str, Any], portfolio: Dict[str, float]) -> Dict[str, Any]:
        """Generate a risk assessment report based on the calculated metrics"""
        report = {
            "summary": "",
            "risk_level": "",
            "recommendations": []
        }
        
        # Determine overall risk level
        risk_level = "moderate"  # Default
        
        if "volatility" in risk_metrics:
            volatility = risk_metrics["volatility"]
            if volatility > 0.25:  # 25% annualized volatility
                risk_level = "high"
            elif volatility < 0.15:  # 15% annualized volatility
                risk_level = "low"
        
        if "beta" in risk_metrics:
            beta = risk_metrics["beta"]
            if beta > 1.2:
                risk_level = "high" if risk_level != "high" else "very high"
            elif beta < 0.8:
                risk_level = "low" if risk_level != "low" else "very low"
        
        report["risk_level"] = risk_level
        
        # Generate summary
        summary = f"The portfolio has a {risk_level} risk profile. "
        
        if "beta" in risk_metrics:
            beta = risk_metrics["beta"]
            summary += f"With a beta of {beta:.2f}, it "
            if beta > 1:
                summary += "is more volatile than the market. "
            elif beta < 1:
                summary += "is less volatile than the market. "
            else:
                summary += "moves in line with the market. "
        
        if "volatility" in risk_metrics:
            volatility = risk_metrics["volatility"]
            summary += f"The portfolio has an annualized volatility of {volatility*100:.2f}%. "
        
        if "sharpe" in risk_metrics:
            sharpe = risk_metrics["sharpe"]
            summary += f"The Sharpe ratio is {sharpe:.2f}, indicating "
            if sharpe > 1:
                summary += "good "
            elif sharpe > 0.5:
                summary += "acceptable "
            else:
                summary += "poor "
            summary += "risk-adjusted returns. "
        
        if "max_drawdown" in risk_metrics:
            drawdown = risk_metrics["max_drawdown"]
            summary += f"The maximum historical drawdown is {drawdown*100:.2f}%. "
        
        report["summary"] = summary
        
        # Generate recommendations
        recommendations = []
        
        # Diversification recommendation
        if len(portfolio) < 5:
            recommendations.append("Consider increasing portfolio diversification by adding more assets.")
        
        # Beta-based recommendation
        if "beta" in risk_metrics:
            beta = risk_metrics["beta"]
            if beta > 1.2:
                recommendations.append("The portfolio has high market sensitivity. Consider adding defensive stocks or bonds to reduce market risk.")
            elif beta < 0.8:
                recommendations.append("The portfolio has low market sensitivity. Consider adding growth stocks if you want to increase potential returns.")
        
        # Sharpe ratio recommendation
        if "sharpe" in risk_metrics:
            sharpe = risk_metrics["sharpe"]
            if sharpe < 0.5:
                recommendations.append("The risk-adjusted returns are low. Consider rebalancing the portfolio to improve the risk-return profile.")
        
        # Drawdown recommendation
        if "max_drawdown" in risk_metrics:
            drawdown = risk_metrics["max_drawdown"]
            if drawdown < -0.2:
                recommendations.append("The portfolio has experienced significant drawdowns. Consider adding assets with lower correlation to reduce drawdown risk.")
        
        report["recommendations"] = recommendations
        
        return report
    
    def set_benchmark(self, benchmark: str):
        """Set the benchmark for risk calculations"""
        self.state.benchmark = benchmark
    
    def add_risk_metric(self, metric: str):
        """Add a risk metric to the agent"""
        if metric not in self.state.risk_metrics:
            self.state.risk_metrics.append(metric)
    
    def remove_risk_metric(self, metric: str):
        """Remove a risk metric from the agent"""
        if metric in self.state.risk_metrics:
            self.state.risk_metrics.remove(metric)
    
    def clear_cache(self):
        """Clear the agent's assessment cache"""
        self.state.cached_assessments = {}
        self.state.last_cache_update = None 