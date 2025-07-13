"""
Base Orchestrator for the MSVA project.
Provides the foundation for coordinating agents and their interactions.
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional, Callable, Union
from pathlib import Path
from pydantic import BaseModel
import logging

class AgentOutput(BaseModel):
    """Model for standardized agent outputs."""
    agent_name: str
    message_type: str
    content: Dict[str, Any]
    success: bool
    metadata: Optional[Dict[str, Any]] = None

class OrchestratorConfig(BaseModel):
    """Configuration for the orchestrator."""
    debug: bool = False
    log_level: str = "INFO"
    output_dir: str = "./outputs"
    save_intermediate_results: bool = True
    human_in_the_loop: bool = False
    max_retries: int = 3
    timeout_seconds: int = 120

class BaseOrchestrator:
    """
    Base class for orchestrating multi-agent workflows.
    Handles agent initialization, communication, and workflow execution.
    """
    
    def __init__(self, config: Optional[OrchestratorConfig] = None):
        """
        Initialize the orchestrator.
        
        Args:
            config: Configuration for the orchestrator
        """
        self.config = config or OrchestratorConfig()
        self.agents = {}
        self.tools = {}
        self.workflows = {}
        self.current_workflow = None
        self.results_store = {}
        
        # Set up logging
        self._setup_logging()
        
        # Create output directory if it doesn't exist
        if self.config.save_intermediate_results:
            Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
    
    def _setup_logging(self):
        """Set up logging configuration."""
        log_level = getattr(logging, self.config.log_level.upper())
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        self.logger = logging.getLogger("Orchestrator")
        
        if self.config.debug:
            self.logger.setLevel(logging.DEBUG)
    
    def register_agent(self, agent_name: str, agent_instance: Any) -> None:
        """
        Register an agent with the orchestrator.
        
        Args:
            agent_name: Name to register the agent under
            agent_instance: Instance of the agent
        """
        self.agents[agent_name] = agent_instance
        self.logger.debug(f"Registered agent: {agent_name}")
    
    def register_tool(self, tool_name: str, tool_instance: Any) -> None:
        """
        Register a tool with the orchestrator.
        
        Args:
            tool_name: Name to register the tool under
            tool_instance: Instance of the tool
        """
        self.tools[tool_name] = tool_instance
        self.logger.debug(f"Registered tool: {tool_name}")
    
    def register_workflow(self, workflow_name: str, workflow_function: Callable) -> None:
        """
        Register a workflow with the orchestrator.
        
        Args:
            workflow_name: Name to register the workflow under
            workflow_function: Function implementing the workflow
        """
        self.workflows[workflow_name] = workflow_function
        self.logger.debug(f"Registered workflow: {workflow_name}")
    
    async def execute_workflow(self, workflow_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a registered workflow.
        
        Args:
            workflow_name: Name of the workflow to execute
            input_data: Input data for the workflow
            
        Returns:
            Dictionary containing the workflow results
        """
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow '{workflow_name}' not found")
            
        self.current_workflow = workflow_name
        self.results_store = {}
        
        self.logger.info(f"Executing workflow: {workflow_name}")
        
        try:
            workflow_function = self.workflows[workflow_name]
            result = await workflow_function(self, input_data)
            
            # Save the final result if configured
            if self.config.save_intermediate_results:
                self._save_result("final_result", result)
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing workflow '{workflow_name}': {str(e)}")
            raise
        finally:
            self.current_workflow = None
    
    async def run_agent(self, agent_name: str, input_data: Dict[str, Any]) -> AgentOutput:
        """
        Run an agent with the given input data.
        
        Args:
            agent_name: Name of the agent to run
            input_data: Input data for the agent
            
        Returns:
            AgentOutput containing the agent's response
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not found")
            
        agent = self.agents[agent_name]
        self.logger.debug(f"Running agent: {agent_name}")
        
        try:
            # Run the agent with retry logic
            for attempt in range(self.config.max_retries):
                try:
                    result = await asyncio.wait_for(
                        agent.process(input_data),
                        timeout=self.config.timeout_seconds
                    )
                    
                    # Save intermediate result if configured
                    if self.config.save_intermediate_results and self.current_workflow:
                        result_key = f"{self.current_workflow}_{agent_name}"
                        self._save_result(result_key, result)
                    
                    # Format the result as AgentOutput
                    if not isinstance(result, AgentOutput):
                        result = AgentOutput(
                            agent_name=agent_name,
                            message_type="result",
                            content=result,
                            success=True
                        )
                        
                    return result
                    
                except asyncio.TimeoutError:
                    self.logger.warning(f"Timeout executing agent '{agent_name}', attempt {attempt + 1}/{self.config.max_retries}")
                    if attempt == self.config.max_retries - 1:
                        raise
                except Exception as e:
                    self.logger.warning(f"Error executing agent '{agent_name}', attempt {attempt + 1}/{self.config.max_retries}: {str(e)}")
                    if attempt == self.config.max_retries - 1:
                        raise
                        
        except Exception as e:
            self.logger.error(f"Failed to execute agent '{agent_name}' after {self.config.max_retries} attempts: {str(e)}")
            return AgentOutput(
                agent_name=agent_name,
                message_type="error",
                content={"error": str(e)},
                success=False
            )
    
    async def run_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Run a tool with the given parameters.
        
        Args:
            tool_name: Name of the tool to run
            **kwargs: Parameters for the tool
            
        Returns:
            Dictionary containing the tool's output
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
            
        tool = self.tools[tool_name]
        self.logger.debug(f"Running tool: {tool_name}")
        
        try:
            # Run the tool with retry logic
            for attempt in range(self.config.max_retries):
                try:
                    result = await asyncio.wait_for(
                        tool.run(**kwargs),
                        timeout=self.config.timeout_seconds
                    )
                    
                    # Save intermediate result if configured
                    if self.config.save_intermediate_results and self.current_workflow:
                        result_key = f"{self.current_workflow}_{tool_name}"
                        self._save_result(result_key, result)
                        
                    return result
                    
                except asyncio.TimeoutError:
                    self.logger.warning(f"Timeout executing tool '{tool_name}', attempt {attempt + 1}/{self.config.max_retries}")
                    if attempt == self.config.max_retries - 1:
                        raise
                except Exception as e:
                    self.logger.warning(f"Error executing tool '{tool_name}', attempt {attempt + 1}/{self.config.max_retries}: {str(e)}")
                    if attempt == self.config.max_retries - 1:
                        raise
                        
        except Exception as e:
            self.logger.error(f"Failed to execute tool '{tool_name}' after {self.config.max_retries} attempts: {str(e)}")
            return {
                "status": "error",
                "message": f"Tool execution failed: {str(e)}"
            }
    
    def _save_result(self, key: str, result: Any) -> None:
        """Save a result to the results store and optionally to disk."""
        self.results_store[key] = result
        
        if self.config.save_intermediate_results:
            # Clean key for filename
            clean_key = key.replace("/", "_").replace("\\", "_")
            file_path = os.path.join(self.config.output_dir, f"{clean_key}.json")
            
            try:
                with open(file_path, 'w') as f:
                    json.dump(result, f, indent=2, default=lambda x: x.__dict__ if hasattr(x, "__dict__") else str(x))
            except Exception as e:
                self.logger.warning(f"Failed to save result to file: {str(e)}")
    
    def get_result(self, key: str) -> Optional[Any]:
        """Get a result from the results store."""
        return self.results_store.get(key)
    
    async def get_human_feedback(self, message: str, options: Optional[List[str]] = None) -> str:
        """
        Get feedback from a human.
        Only used if human_in_the_loop is enabled.
        
        Args:
            message: Message to display to the human
            options: Optional list of options to present
            
        Returns:
            The human's response
        """
        if not self.config.human_in_the_loop:
            self.logger.warning("Human-in-the-loop is disabled, returning default response")
            return options[0] if options and len(options) > 0 else "approved"
            
        self.logger.info(f"Requesting human feedback: {message}")
        
        # In a real implementation, this would integrate with a UI
        # For now, we'll just use console input
        print("\n" + "=" * 50)
        print("HUMAN FEEDBACK REQUIRED")
        print("=" * 50)
        print(message)
        
        if options:
            print("\nOptions:")
            for i, option in enumerate(options):
                print(f"[{i+1}] {option}")
                
            while True:
                try:
                    choice = int(input("\nEnter your choice (number): "))
                    if 1 <= choice <= len(options):
                        return options[choice - 1]
                    else:
                        print(f"Please enter a number between 1 and {len(options)}")
                except ValueError:
                    print("Please enter a valid number")
        else:
            return input("\nEnter your response: ")
