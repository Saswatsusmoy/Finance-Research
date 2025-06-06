from typing import Dict, Any, List, Optional, Callable, Awaitable
import asyncio
import logging
from datetime import datetime
from pydantic import BaseModel, Field
import json
from langgraph.graph import StateGraph, END

from src.agents.base_agent import BaseAgent
from src.agents.market_data_agent import MarketDataAgent
from src.agents.news_sentiment_agent import NewsSentimentAgent
from src.agents.technical_analysis_agent import TechnicalAnalysisAgent
from src.agents.risk_assessment_agent import RiskAssessmentAgent
from src.agents.report_generation_agent import ReportGenerationAgent

class OrchestratorState(BaseModel):
    """State for the agent orchestrator"""
    query: str = ""
    current_agent: str = ""
    agents_executed: List[str] = Field(default_factory=list)
    results: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    status: str = "idle"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class AgentOrchestrator:
    """Orchestrator for coordinating multiple agents"""
    
    def __init__(self):
        """Initialize the agent orchestrator"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize agents
        self.market_data_agent = MarketDataAgent()
        self.news_sentiment_agent = NewsSentimentAgent()
        self.technical_analysis_agent = TechnicalAnalysisAgent(market_data_agent=self.market_data_agent)
        self.risk_assessment_agent = RiskAssessmentAgent(market_data_agent=self.market_data_agent)
        self.report_generation_agent = ReportGenerationAgent(
            market_data_agent=self.market_data_agent,
            news_sentiment_agent=self.news_sentiment_agent,
            technical_analysis_agent=self.technical_analysis_agent,
            risk_assessment_agent=self.risk_assessment_agent
        )
        
        # Create agent map
        self.agents = {
            "market_data": self.market_data_agent,
            "news_sentiment": self.news_sentiment_agent,
            "technical_analysis": self.technical_analysis_agent,
            "risk_assessment": self.risk_assessment_agent,
            "report_generation": self.report_generation_agent
        }
        
        # Create the workflow graph
        self.graph = self._create_workflow_graph()
    
    def _create_workflow_graph(self) -> StateGraph:
        """Create the LangGraph workflow for agent orchestration"""
        # Define the graph
        workflow = StateGraph(OrchestratorState)
        
        # Add nodes for each agent
        workflow.add_node("router", self._route_query)
        workflow.add_node("market_data", self._run_market_data_agent)
        workflow.add_node("news_sentiment", self._run_news_sentiment_agent)
        workflow.add_node("technical_analysis", self._run_technical_analysis_agent)
        workflow.add_node("risk_assessment", self._run_risk_assessment_agent)
        workflow.add_node("report_generation", self._run_report_generation_agent)
        
        # Add edges
        workflow.add_edge("router", "market_data")
        workflow.add_edge("router", "news_sentiment")
        workflow.add_edge("router", "technical_analysis")
        workflow.add_edge("router", "risk_assessment")
        workflow.add_edge("router", "report_generation")
        
        # Define conditional edges from each agent
        workflow.add_conditional_edges(
            "market_data",
            self._determine_next_agent,
            {
                "news_sentiment": "news_sentiment",
                "technical_analysis": "technical_analysis",
                "risk_assessment": "risk_assessment",
                "report_generation": "report_generation",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "news_sentiment",
            self._determine_next_agent,
            {
                "market_data": "market_data",
                "technical_analysis": "technical_analysis",
                "risk_assessment": "risk_assessment",
                "report_generation": "report_generation",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "technical_analysis",
            self._determine_next_agent,
            {
                "market_data": "market_data",
                "news_sentiment": "news_sentiment",
                "risk_assessment": "risk_assessment",
                "report_generation": "report_generation",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "risk_assessment",
            self._determine_next_agent,
            {
                "market_data": "market_data",
                "news_sentiment": "news_sentiment",
                "technical_analysis": "technical_analysis",
                "report_generation": "report_generation",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "report_generation",
            self._determine_next_agent,
            {
                "market_data": "market_data",
                "news_sentiment": "news_sentiment",
                "technical_analysis": "technical_analysis",
                "risk_assessment": "risk_assessment",
                "end": END
            }
        )
        
        # Set the entry point
        workflow.set_entry_point("router")
        
        return workflow
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process a user query through the agent workflow"""
        # Initialize state
        state = OrchestratorState(
            query=query,
            status="running",
            start_time=datetime.now()
        )
        
        try:
            # Execute the workflow
            self.logger.info(f"Starting workflow for query: {query}")
            
            # Convert to async
            async_graph = await self._convert_graph_to_async()
            
            # Run the graph
            final_state = await async_graph.ainvoke(state)
            
            # Update final state
            final_state.status = "completed"
            final_state.end_time = datetime.now()
            
            return {
                "status": "success",
                "query": query,
                "results": final_state.results,
                "agents_executed": final_state.agents_executed,
                "execution_time": (final_state.end_time - final_state.start_time).total_seconds()
            }
        
        except Exception as e:
            self.logger.error(f"Error in workflow: {str(e)}")
            return {
                "status": "error",
                "query": query,
                "error": str(e),
                "agents_executed": state.agents_executed
            }
    
    async def _convert_graph_to_async(self) -> Any:
        """Convert the LangGraph StateGraph to be async-compatible"""
        # This is a simplified version - in a real implementation,
        # you would need to properly convert the graph to be async-compatible
        # For now, we'll just return the graph as is
        return self.graph
    
    def _route_query(self, state: OrchestratorState) -> OrchestratorState:
        """Route the query to the appropriate agent based on content"""
        query = state.query.lower()
        
        # Simple routing logic
        if "price" in query or "market" in query or "stock" in query:
            state.current_agent = "market_data"
        elif "news" in query or "sentiment" in query:
            state.current_agent = "news_sentiment"
        elif "technical" in query or "chart" in query or "pattern" in query:
            state.current_agent = "technical_analysis"
        elif "risk" in query or "portfolio" in query:
            state.current_agent = "risk_assessment"
        elif "report" in query or "summary" in query:
            state.current_agent = "report_generation"
        else:
            # Default to market data
            state.current_agent = "market_data"
        
        return state
    
    def _determine_next_agent(self, state: OrchestratorState) -> str:
        """Determine the next agent to execute based on current state"""
        # In a real implementation, this would use more sophisticated logic
        # based on the query and results so far
        
        # If we've executed all agents or this is the report generation agent, we're done
        if len(state.agents_executed) >= len(self.agents) or state.current_agent == "report_generation":
            return "end"
        
        # Simple sequential execution for demonstration
        if state.current_agent == "market_data" and "market_data" in state.agents_executed:
            return "news_sentiment"
        elif state.current_agent == "news_sentiment" and "news_sentiment" in state.agents_executed:
            return "technical_analysis"
        elif state.current_agent == "technical_analysis" and "technical_analysis" in state.agents_executed:
            return "risk_assessment"
        elif state.current_agent == "risk_assessment" and "risk_assessment" in state.agents_executed:
            return "report_generation"
        else:
            # Default to end if we can't determine the next agent
            return "end"
    
    async def _run_agent(self, agent_name: str, state: OrchestratorState) -> OrchestratorState:
        """Run the specified agent with the current state"""
        if agent_name not in self.agents:
            state.error = f"Unknown agent: {agent_name}"
            return state
        
        agent = self.agents[agent_name]
        
        try:
            # Process the query with the agent
            result = await agent.process(state.query)
            
            # Update state
            state.results[agent_name] = result
            if agent_name not in state.agents_executed:
                state.agents_executed.append(agent_name)
            
            return state
        
        except Exception as e:
            state.error = f"Error in {agent_name} agent: {str(e)}"
            self.logger.error(state.error)
            return state
    
    async def _run_market_data_agent(self, state: OrchestratorState) -> OrchestratorState:
        """Run the market data agent"""
        return await self._run_agent("market_data", state)
    
    async def _run_news_sentiment_agent(self, state: OrchestratorState) -> OrchestratorState:
        """Run the news sentiment agent"""
        return await self._run_agent("news_sentiment", state)
    
    async def _run_technical_analysis_agent(self, state: OrchestratorState) -> OrchestratorState:
        """Run the technical analysis agent"""
        return await self._run_agent("technical_analysis", state)
    
    async def _run_risk_assessment_agent(self, state: OrchestratorState) -> OrchestratorState:
        """Run the risk assessment agent"""
        return await self._run_agent("risk_assessment", state)
    
    async def _run_report_generation_agent(self, state: OrchestratorState) -> OrchestratorState:
        """Run the report generation agent"""
        return await self._run_agent("report_generation", state)
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get the status of all agents"""
        status = {}
        for name, agent in self.agents.items():
            status[name] = agent.get_status()
        return status 