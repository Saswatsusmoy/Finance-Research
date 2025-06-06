from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os
from pydantic import BaseModel, Field

class AgentState(BaseModel):
    """Base state for all agents"""
    agent_id: str
    agent_type: str
    last_run: Optional[datetime] = None
    status: str = "idle"
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    memory: Dict[str, Any] = Field(default_factory=dict)
    
    def add_message(self, role: str, content: Any):
        """Add a message to the agent's message history"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_messages(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get the agent's message history, optionally limited to the last N messages"""
        if limit:
            return self.messages[-limit:]
        return self.messages
    
    def clear_messages(self):
        """Clear the agent's message history"""
        self.messages = []

class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, agent_id: str, agent_type: str):
        """Initialize the agent with an ID and type"""
        self.state = AgentState(agent_id=agent_id, agent_type=agent_type)
    
    @abstractmethod
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the agent's main functionality"""
        pass
    
    @abstractmethod
    async def process(self, query: str) -> Dict[str, Any]:
        """Process a specific query"""
        pass
    
    def update_status(self, status: str):
        """Update the agent's status"""
        self.state.status = status
        self.state.last_run = datetime.now()
    
    def get_status(self) -> Dict[str, Any]:
        """Get the agent's current status"""
        return {
            "agent_id": self.state.agent_id,
            "agent_type": self.state.agent_type,
            "status": self.state.status,
            "last_run": self.state.last_run.isoformat() if self.state.last_run else None
        }
    
    def save_state(self, path: str = None):
        """Save the agent's state to disk"""
        if not path:
            path = f"data/agent_states/{self.state.agent_id}.json"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, "w") as f:
            f.write(self.state.json())
    
    def load_state(self, path: str = None):
        """Load the agent's state from disk"""
        if not path:
            path = f"data/agent_states/{self.state.agent_id}.json"
        
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                self.state = AgentState(**data)
                return True
        
        return False 