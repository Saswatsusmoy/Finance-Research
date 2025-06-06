from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
import logging
import json
import os
from pydantic import BaseModel, Field

from src.agents.base_agent import BaseAgent, AgentState
from src.agents.market_data_agent import MarketDataAgent
from src.agents.news_sentiment_agent import NewsSentimentAgent
from src.agents.technical_analysis_agent import TechnicalAnalysisAgent
from src.agents.risk_assessment_agent import RiskAssessmentAgent

class ReportGenerationState(AgentState):
    """State for the report generation agent"""
    cached_reports: Dict[str, Any] = Field(default_factory=dict)
    report_templates: Dict[str, str] = Field(default_factory=dict)
    last_cache_update: Optional[datetime] = None
    cache_duration: int = 3600  # Cache duration in seconds (default: 1 hour)

class ReportGenerationAgent(BaseAgent):
    """Agent responsible for generating investment reports"""
    
    def __init__(self, agent_id: str = "report_generation_agent", 
                 market_data_agent: MarketDataAgent = None,
                 news_sentiment_agent: NewsSentimentAgent = None,
                 technical_analysis_agent: TechnicalAnalysisAgent = None,
                 risk_assessment_agent: RiskAssessmentAgent = None):
        """Initialize the report generation agent"""
        super().__init__(agent_id, "report_generation")
        self.state = ReportGenerationState(agent_id=agent_id, agent_type="report_generation")
        self.logger = logging.getLogger(__name__)
        
        # Initialize sub-agents
        self.market_data_agent = market_data_agent or MarketDataAgent()
        self.news_sentiment_agent = news_sentiment_agent or NewsSentimentAgent()
        self.technical_analysis_agent = technical_analysis_agent or TechnicalAnalysisAgent()
        self.risk_assessment_agent = risk_assessment_agent or RiskAssessmentAgent()
        
        # Load report templates
        self._load_report_templates()
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the report generation agent's main functionality"""
        self.update_status("running")
        
        try:
            # Extract parameters from input data
            report_type = input_data.get("report_type", "stock_research")
            symbols = input_data.get("symbols", [])
            portfolio = input_data.get("portfolio", {})
            period = input_data.get("period", 30)  # Default to 30 days
            include_sections = input_data.get("include_sections", ["market_data", "news_sentiment", "technical_analysis", "risk_assessment"])
            
            # Validate input
            if report_type == "stock_research" and not symbols:
                raise ValueError("Symbols are required for stock research reports")
            
            if report_type == "portfolio_analysis" and not portfolio:
                raise ValueError("Portfolio is required for portfolio analysis reports")
            
            # Check cache for existing report
            cache_key = f"{report_type}_{','.join(symbols)}_{json.dumps(portfolio)}_{period}"
            if (cache_key in self.state.cached_reports and 
                self.state.last_cache_update and 
                (datetime.now() - self.state.last_cache_update).total_seconds() < self.state.cache_duration):
                return {"status": "success", "data": self.state.cached_reports[cache_key]}
            
            # Generate report based on type
            if report_type == "stock_research":
                report = await self._generate_stock_research_report(symbols[0], period, include_sections)
            elif report_type == "portfolio_analysis":
                report = await self._generate_portfolio_analysis_report(portfolio, period, include_sections)
            elif report_type == "market_overview":
                report = await self._generate_market_overview_report(period, include_sections)
            else:
                raise ValueError(f"Unsupported report type: {report_type}")
            
            # Cache the result
            self.state.cached_reports[cache_key] = report
            self.state.last_cache_update = datetime.now()
            
            self.update_status("idle")
            return {"status": "success", "data": report}
        
        except Exception as e:
            self.logger.error(f"Error in report generation agent: {str(e)}")
            self.update_status("error")
            self.state.add_message("system", f"Error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def process(self, query: str) -> Dict[str, Any]:
        """Process a specific query related to report generation"""
        self.update_status("processing")
        self.state.add_message("user", query)
        
        # Simple query processing logic
        query_lower = query.lower()
        
        # Extract potential symbols
        import re
        symbols = re.findall(r'\b[A-Z]{1,5}\b', query)
        
        # Determine report type
        report_type = "stock_research"  # Default
        if "portfolio" in query_lower or "holdings" in query_lower:
            report_type = "portfolio_analysis"
        elif "market" in query_lower or "overview" in query_lower:
            report_type = "market_overview"
        
        # Determine time period
        period = 30  # Default to 30 days
        if "year" in query_lower:
            period = 365
        elif "quarter" in query_lower:
            period = 90
        elif "month" in query_lower:
            period = 30
        elif "week" in query_lower:
            period = 7
        
        # Determine sections to include
        include_sections = ["market_data", "news_sentiment", "technical_analysis", "risk_assessment"]
        
        # Create portfolio if needed
        portfolio = {}
        if report_type == "portfolio_analysis":
            if symbols:
                # Equal weight portfolio
                weight = 1.0 / len(symbols)
                portfolio = {symbol: weight for symbol in symbols}
            else:
                # Default portfolio
                portfolio = {"AAPL": 0.2, "MSFT": 0.2, "GOOGL": 0.2, "AMZN": 0.2, "META": 0.2}
        
        # Run report generation
        input_data = {
            "report_type": report_type,
            "symbols": symbols,
            "portfolio": portfolio,
            "period": period,
            "include_sections": include_sections
        }
        
        result = await self.run(input_data)
        
        self.state.add_message("assistant", result)
        self.update_status("idle")
        return result
    
    async def _generate_stock_research_report(self, symbol: str, period: int, include_sections: List[str]) -> Dict[str, Any]:
        """Generate a stock research report"""
        self.state.add_message("system", f"Generating stock research report for {symbol}")
        
        report = {
            "report_type": "stock_research",
            "symbol": symbol,
            "generated_at": datetime.now().isoformat(),
            "period_days": period
        }
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period)
        
        # Fetch market data
        if "market_data" in include_sections:
            self.state.add_message("system", f"Fetching market data for {symbol}")
            market_data = await self.market_data_agent.fetch_market_data(
                symbol, 
                start_date.strftime("%Y-%m-%d"), 
                end_date.strftime("%Y-%m-%d")
            )
            report["market_data"] = market_data
        
        # Fetch news sentiment
        if "news_sentiment" in include_sections:
            self.state.add_message("system", f"Analyzing news sentiment for {symbol}")
            news_data = await self.news_sentiment_agent.run({
                "query": symbol,
                "symbols": [symbol],
                "days": period
            })
            report["news_sentiment"] = news_data.get("data", {})
        
        # Perform technical analysis
        if "technical_analysis" in include_sections:
            self.state.add_message("system", f"Performing technical analysis for {symbol}")
            ta_data = await self.technical_analysis_agent.run({
                "symbol": symbol,
                "period": period
            })
            report["technical_analysis"] = ta_data.get("data", {})
        
        # Perform risk assessment
        if "risk_assessment" in include_sections:
            self.state.add_message("system", f"Assessing risk for {symbol}")
            # Create a single-stock portfolio
            portfolio = {symbol: 1.0}
            risk_data = await self.risk_assessment_agent.run({
                "portfolio": portfolio,
                "period": period
            })
            report["risk_assessment"] = risk_data.get("data", {})
        
        # Generate summary and recommendations
        report["summary"] = await self._generate_stock_summary(report)
        report["recommendations"] = await self._generate_stock_recommendations(report)
        
        return report
    
    async def _generate_portfolio_analysis_report(self, portfolio: Dict[str, float], period: int, include_sections: List[str]) -> Dict[str, Any]:
        """Generate a portfolio analysis report"""
        self.state.add_message("system", "Generating portfolio analysis report")
        
        report = {
            "report_type": "portfolio_analysis",
            "portfolio": portfolio,
            "generated_at": datetime.now().isoformat(),
            "period_days": period
        }
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period)
        
        # Fetch market data for each symbol
        if "market_data" in include_sections:
            self.state.add_message("system", "Fetching market data for portfolio")
            market_data = {}
            for symbol in portfolio:
                data = await self.market_data_agent.fetch_market_data(
                    symbol, 
                    start_date.strftime("%Y-%m-%d"), 
                    end_date.strftime("%Y-%m-%d")
                )
                market_data[symbol] = data
            report["market_data"] = market_data
        
        # Fetch news sentiment for portfolio
        if "news_sentiment" in include_sections:
            self.state.add_message("system", "Analyzing news sentiment for portfolio")
            news_data = {}
            for symbol in portfolio:
                data = await self.news_sentiment_agent.run({
                    "query": symbol,
                    "symbols": [symbol],
                    "days": min(period, 30)  # Limit to 30 days for news
                })
                news_data[symbol] = data.get("data", {})
            report["news_sentiment"] = news_data
        
        # Perform technical analysis for each symbol
        if "technical_analysis" in include_sections:
            self.state.add_message("system", "Performing technical analysis for portfolio")
            ta_data = {}
            for symbol in portfolio:
                data = await self.technical_analysis_agent.run({
                    "symbol": symbol,
                    "period": period
                })
                ta_data[symbol] = data.get("data", {})
            report["technical_analysis"] = ta_data
        
        # Perform risk assessment for portfolio
        if "risk_assessment" in include_sections:
            self.state.add_message("system", "Assessing portfolio risk")
            risk_data = await self.risk_assessment_agent.run({
                "portfolio": portfolio,
                "period": period
            })
            report["risk_assessment"] = risk_data.get("data", {})
        
        # Generate summary and recommendations
        report["summary"] = await self._generate_portfolio_summary(report)
        report["recommendations"] = await self._generate_portfolio_recommendations(report)
        
        return report
    
    async def _generate_market_overview_report(self, period: int, include_sections: List[str]) -> Dict[str, Any]:
        """Generate a market overview report"""
        self.state.add_message("system", "Generating market overview report")
        
        report = {
            "report_type": "market_overview",
            "generated_at": datetime.now().isoformat(),
            "period_days": period
        }
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period)
        
        # Define market indices
        indices = ["SPY", "QQQ", "DIA", "IWM"]
        
        # Fetch market data for indices
        if "market_data" in include_sections:
            self.state.add_message("system", "Fetching market data for indices")
            market_data = {}
            for symbol in indices:
                data = await self.market_data_agent.fetch_market_data(
                    symbol, 
                    start_date.strftime("%Y-%m-%d"), 
                    end_date.strftime("%Y-%m-%d")
                )
                market_data[symbol] = data
            report["market_data"] = market_data
        
        # Fetch news sentiment for market
        if "news_sentiment" in include_sections:
            self.state.add_message("system", "Analyzing market news sentiment")
            news_data = await self.news_sentiment_agent.run({
                "query": "stock market economy",
                "days": min(period, 30)  # Limit to 30 days for news
            })
            report["news_sentiment"] = news_data.get("data", {})
        
        # Perform technical analysis for indices
        if "technical_analysis" in include_sections:
            self.state.add_message("system", "Performing technical analysis for indices")
            ta_data = {}
            for symbol in indices:
                data = await self.technical_analysis_agent.run({
                    "symbol": symbol,
                    "period": period
                })
                ta_data[symbol] = data.get("data", {})
            report["technical_analysis"] = ta_data
        
        # Generate summary and outlook
        report["summary"] = await self._generate_market_summary(report)
        report["outlook"] = await self._generate_market_outlook(report)
        
        return report
    
    async def _generate_stock_summary(self, report: Dict[str, Any]) -> str:
        """Generate a summary for a stock research report"""
        # This would use LLM in a real implementation
        # For now, we'll create a simple template-based summary
        
        symbol = report.get("symbol", "")
        market_data = report.get("market_data", {})
        news_sentiment = report.get("news_sentiment", {})
        technical_analysis = report.get("technical_analysis", {})
        
        company_name = market_data.get("company_name", symbol)
        current_price = market_data.get("current_price", "N/A")
        
        # Get sentiment
        sentiment = "neutral"
        sentiment_score = 0
        if news_sentiment:
            sentiment = news_sentiment.get("overall_sentiment", "neutral")
            sentiment_score = news_sentiment.get("sentiment_score", 0)
        
        # Get technical signals
        signal = "neutral"
        if technical_analysis and "signals" in technical_analysis:
            signal = technical_analysis["signals"].get("overall", "neutral")
        
        summary = f"{company_name} ({symbol}) is currently trading at ${current_price}. "
        summary += f"News sentiment is {sentiment} with a score of {sentiment_score:.2f}. "
        summary += f"Technical indicators suggest a {signal} outlook. "
        
        return summary
    
    async def _generate_stock_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate recommendations for a stock research report"""
        # This would use LLM in a real implementation
        # For now, we'll create simple template-based recommendations
        
        recommendations = []
        
        technical_analysis = report.get("technical_analysis", {})
        news_sentiment = report.get("news_sentiment", {})
        risk_assessment = report.get("risk_assessment", {})
        
        # Technical analysis based recommendation
        if technical_analysis and "signals" in technical_analysis:
            signal = technical_analysis["signals"].get("overall", "neutral")
            if signal == "bullish":
                recommendations.append("Consider a buy position based on positive technical indicators.")
            elif signal == "bearish":
                recommendations.append("Consider reducing exposure based on negative technical indicators.")
            else:
                recommendations.append("Hold current position as technical indicators are neutral.")
        
        # News sentiment based recommendation
        if news_sentiment:
            sentiment = news_sentiment.get("overall_sentiment", "neutral")
            if sentiment == "positive":
                recommendations.append("News sentiment is positive, suggesting potential upside.")
            elif sentiment == "negative":
                recommendations.append("News sentiment is negative, suggesting caution.")
        
        # Risk assessment based recommendation
        if risk_assessment and "risk_report" in risk_assessment:
            risk_level = risk_assessment["risk_report"].get("risk_level", "moderate")
            if risk_level in ["high", "very high"]:
                recommendations.append("This stock shows high risk characteristics. Consider position sizing accordingly.")
            elif risk_level in ["low", "very low"]:
                recommendations.append("This stock shows low risk characteristics, suitable for conservative portfolios.")
        
        return recommendations
    
    async def _generate_portfolio_summary(self, report: Dict[str, Any]) -> str:
        """Generate a summary for a portfolio analysis report"""
        # This would use LLM in a real implementation
        # For now, we'll create a simple template-based summary
        
        portfolio = report.get("portfolio", {})
        risk_assessment = report.get("risk_assessment", {})
        
        num_assets = len(portfolio)
        
        summary = f"Portfolio consists of {num_assets} assets. "
        
        if risk_assessment and "risk_report" in risk_assessment:
            risk_level = risk_assessment["risk_report"].get("risk_level", "moderate")
            risk_summary = risk_assessment["risk_report"].get("summary", "")
            
            summary += f"Risk profile is {risk_level}. {risk_summary}"
        
        return summary
    
    async def _generate_portfolio_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate recommendations for a portfolio analysis report"""
        # This would use LLM in a real implementation
        # For now, we'll use risk assessment recommendations if available
        
        recommendations = []
        
        risk_assessment = report.get("risk_assessment", {})
        
        if risk_assessment and "risk_report" in risk_assessment:
            risk_recommendations = risk_assessment["risk_report"].get("recommendations", [])
            recommendations.extend(risk_recommendations)
        
        # Add a generic recommendation if none from risk assessment
        if not recommendations:
            recommendations.append("Consider regular portfolio rebalancing to maintain target allocations.")
        
        return recommendations
    
    async def _generate_market_summary(self, report: Dict[str, Any]) -> str:
        """Generate a summary for a market overview report"""
        # This would use LLM in a real implementation
        # For now, we'll create a simple template-based summary
        
        market_data = report.get("market_data", {})
        news_sentiment = report.get("news_sentiment", {})
        
        # Get SPY data as proxy for market
        spy_data = market_data.get("SPY", {})
        current_price = spy_data.get("current_price", "N/A")
        
        # Get sentiment
        sentiment = "neutral"
        if news_sentiment:
            sentiment = news_sentiment.get("overall_sentiment", "neutral")
        
        summary = f"The S&P 500 is currently at {current_price}. "
        summary += f"Overall market sentiment is {sentiment} based on recent news. "
        
        return summary
    
    async def _generate_market_outlook(self, report: Dict[str, Any]) -> str:
        """Generate a market outlook for a market overview report"""
        # This would use LLM in a real implementation
        # For now, we'll create a simple template-based outlook
        
        technical_analysis = report.get("technical_analysis", {})
        news_sentiment = report.get("news_sentiment", {})
        
        # Get SPY technical analysis as proxy for market
        spy_ta = technical_analysis.get("SPY", {})
        
        outlook = "The market outlook is neutral based on current indicators. "
        
        # Add technical analysis insight
        if spy_ta and "signals" in spy_ta:
            signal = spy_ta["signals"].get("overall", "neutral")
            outlook += f"Technical indicators for the S&P 500 are {signal}. "
        
        # Add sentiment insight
        if news_sentiment:
            sentiment = news_sentiment.get("overall_sentiment", "neutral")
            outlook += f"News sentiment is {sentiment}, which could influence market direction. "
        
        return outlook
    
    def _load_report_templates(self):
        """Load report templates from files or use defaults"""
        # In a real implementation, this would load templates from files
        # For now, we'll use simple default templates
        
        self.state.report_templates = {
            "stock_research": "Stock Research Report for {symbol}",
            "portfolio_analysis": "Portfolio Analysis Report",
            "market_overview": "Market Overview Report"
        }
    
    def add_report_template(self, template_name: str, template: str):
        """Add or update a report template"""
        self.state.report_templates[template_name] = template
    
    def get_report_template(self, template_name: str) -> str:
        """Get a report template by name"""
        return self.state.report_templates.get(template_name, "")
    
    def clear_cache(self):
        """Clear the agent's report cache"""
        self.state.cached_reports = {}
        self.state.last_cache_update = None 