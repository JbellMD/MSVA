"""
Base Tool class for the MSVA project.
All specialized tools will inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseTool(ABC):
    """Base tool class that all specialized tools will inherit from."""
    
    def __init__(self, name: str, description: str, verbose: bool = False):
        self.name = name
        self.description = description
        self.verbose = verbose
        
    @abstractmethod
    async def run(self, **kwargs) -> Dict[str, Any]:
        """
        Run the tool with the provided parameters.
        Must be implemented by all tool subclasses.
        
        Returns:
            Dictionary containing the tool's output
        """
        pass
    
    def log(self, message: str) -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            print(f"[{self.name}] {message}")
