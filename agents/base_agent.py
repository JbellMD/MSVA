"""
Base Agent class for the MSVA project.
All specialized agents will inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class AgentMessage(BaseModel):
    """Standardized message format for agent communication (MCP-style)."""
    type: str = Field(description="Message type: REQ, CONFIRM, INFO, BLOCKED, FAIL")
    sender: str = Field(description="Name of the agent sending the message")
    receiver: str = Field(description="Name of the agent receiving the message, or 'all'")
    content: Dict[str, Any] = Field(description="Message content")
    timestamp: str = Field(description="ISO format timestamp")
    request_id: Optional[str] = Field(default=None, description="ID for tracking related messages")
    
class BaseAgent(ABC):
    """Base agent class that all specialized agents will inherit from."""
    
    def __init__(
        self,
        name: str,
        description: str,
        llm_model: str = "gpt-4o",
        tools: List[Any] = None,
        verbose: bool = False
    ):
        self.name = name
        self.description = description
        self.llm_model = llm_model
        self.tools = tools or []
        self.verbose = verbose
        self.memory = []  # Simple memory to store past interactions
        
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return results.
        Must be implemented by all agent subclasses.
        """
        pass
    
    def create_message(
        self,
        msg_type: str,
        receiver: str,
        content: Dict[str, Any],
        request_id: Optional[str] = None
    ) -> AgentMessage:
        """Create a standardized message to send to other agents."""
        import datetime
        
        return AgentMessage(
            type=msg_type,
            sender=self.name,
            receiver=receiver,
            content=content,
            timestamp=datetime.datetime.now().isoformat(),
            request_id=request_id
        )
    
    def log(self, message: str) -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            print(f"[{self.name}] {message}")
    
    def add_to_memory(self, data: Dict[str, Any]) -> None:
        """Add data to agent memory."""
        self.memory.append(data)
        
    def get_memory(self) -> List[Dict[str, Any]]:
        """Retrieve all memory items."""
        return self.memory
