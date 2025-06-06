import asyncio
import logging
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os
import json
from datetime import datetime

from src.agents.orchestrator import AgentOrchestrator
from src.agents.market_data_agent import MarketDataAgent
from src.agents.news_sentiment_agent import NewsSentimentAgent
from src.agents.technical_analysis_agent import TechnicalAnalysisAgent
from src.agents.risk_assessment_agent import RiskAssessmentAgent
from src.agents.report_generation_agent import ReportGenerationAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Financial Research Assistant API",
    description="API for the Financial Research Assistant",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create global agent instances
orchestrator = AgentOrchestrator()
market_data_agent = MarketDataAgent()
news_sentiment_agent = NewsSentimentAgent()
technical_analysis_agent = TechnicalAnalysisAgent()
risk_assessment_agent = RiskAssessmentAgent()
report_generation_agent = ReportGenerationAgent()

# Pydantic models for API requests and responses
class QueryRequest(BaseModel):
    query: str

class MarketDataRequest(BaseModel):
    symbols: List[str]
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    interval: Optional[str] = "1d"

class NewsRequest(BaseModel):
    query: str
    days: Optional[int] = 7

class TechnicalAnalysisRequest(BaseModel):
    symbol: str
    indicators: Optional[List[str]] = None
    period: Optional[int] = 100

class RiskAssessmentRequest(BaseModel):
    portfolio: Dict[str, float]
    benchmark: Optional[str] = "SPY"
    period: Optional[int] = 365

class ReportRequest(BaseModel):
    report_type: str
    symbols: Optional[List[str]] = None
    portfolio: Optional[Dict[str, float]] = None
    period: Optional[int] = 30

class ApiResponse(BaseModel):
    status: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Helper function to get the orchestrator
def get_orchestrator() -> AgentOrchestrator:
    return orchestrator

# API routes
@app.get("/")
async def root():
    return {"message": "Financial Research Assistant API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/query", response_model=ApiResponse)
async def process_query(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """Process a natural language query using the agent orchestrator"""
    try:
        result = await orchestrator.process_query(request.query)
        return ApiResponse(status="success", data=result)
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return ApiResponse(status="error", error=str(e))

@app.post("/market-data", response_model=ApiResponse)
async def get_market_data(request: MarketDataRequest):
    """Get market data for specified symbols"""
    try:
        results = {}
        for symbol in request.symbols:
            data = await market_data_agent.fetch_market_data(
                symbol,
                request.start_date,
                request.end_date,
                request.interval
            )
            results[symbol] = data
        
        return ApiResponse(status="success", data={"results": results})
    except Exception as e:
        logger.error(f"Error fetching market data: {str(e)}")
        return ApiResponse(status="error", error=str(e))

@app.post("/news-sentiment", response_model=ApiResponse)
async def analyze_news_sentiment(request: NewsRequest):
    """Analyze news sentiment for a query"""
    try:
        result = await news_sentiment_agent.run({
            "query": request.query,
            "days": request.days
        })
        
        return ApiResponse(status="success", data=result)
    except Exception as e:
        logger.error(f"Error analyzing news sentiment: {str(e)}")
        return ApiResponse(status="error", error=str(e))

@app.post("/technical-analysis", response_model=ApiResponse)
async def perform_technical_analysis(request: TechnicalAnalysisRequest):
    """Perform technical analysis for a symbol"""
    try:
        result = await technical_analysis_agent.run({
            "symbol": request.symbol,
            "indicators": request.indicators,
            "period": request.period
        })
        
        return ApiResponse(status="success", data=result)
    except Exception as e:
        logger.error(f"Error performing technical analysis: {str(e)}")
        return ApiResponse(status="error", error=str(e))

@app.post("/risk-assessment", response_model=ApiResponse)
async def assess_risk(request: RiskAssessmentRequest):
    """Assess portfolio risk"""
    try:
        result = await risk_assessment_agent.run({
            "portfolio": request.portfolio,
            "benchmark": request.benchmark,
            "period": request.period
        })
        
        return ApiResponse(status="success", data=result)
    except Exception as e:
        logger.error(f"Error assessing risk: {str(e)}")
        return ApiResponse(status="error", error=str(e))

@app.post("/generate-report", response_model=ApiResponse)
async def generate_report(request: ReportRequest):
    """Generate an investment report"""
    try:
        result = await report_generation_agent.run({
            "report_type": request.report_type,
            "symbols": request.symbols,
            "portfolio": request.portfolio,
            "period": request.period
        })
        
        return ApiResponse(status="success", data=result)
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return ApiResponse(status="error", error=str(e))

@app.get("/agent-status")
async def get_agent_status(orchestrator: AgentOrchestrator = Depends(get_orchestrator)):
    """Get the status of all agents"""
    try:
        status = orchestrator.get_agent_status()
        return ApiResponse(status="success", data={"agent_status": status})
    except Exception as e:
        logger.error(f"Error getting agent status: {str(e)}")
        return ApiResponse(status="error", error=str(e))

# Run the API with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True) 