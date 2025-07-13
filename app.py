"""
Main application file for the MSVA project.
This file demonstrates how to initialize the agents, tools, and orchestrator,
and run a startup validation workflow.
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from pathlib import Path
import argparse

# Import agents
from agents.market_researcher_agent import MarketResearcherAgent
from agents.competitor_analyzer_agent import CompetitorAnalyzerAgent
from agents.customer_persona_agent import CustomerPersonaGeneratorAgent
from agents.mvp_planner_agent import MVPPlannerAgent

# Import tools
from tools.search_tool import WebSearchTool
from tools.scraper_tool import WebScraperTool
from tools.rag_tool import RAGRetrieverTool
from tools.mvp_estimator_tool import MVPEstimatorTool

# Import orchestration components
from orchestration.startup_validator import StartupValidatorOrchestrator, OrchestratorConfig, StartupIdea

async def initialize_tools(config: Dict[str, Any]) -> Dict[str, Any]:
    """Initialize all tools based on configuration."""
    tools = {}
    
    # Initialize search tool if API key is available
    if os.getenv("SERPER_API_KEY") or os.getenv("SERPAPI_API_KEY"):
        # Determine which search API to use based on available keys
        search_engine = "serper" if os.getenv("SERPER_API_KEY") else "serpapi"
        
        tools["search_tool"] = WebSearchTool(
            search_engine=search_engine,
            verbose=config.get("debug", False)
        )
    
    # Initialize scraper tool
    tools["scraper_tool"] = WebScraperTool(
        use_playwright=config.get("use_playwright", False),
        verbose=config.get("debug", False)
    )
    
    # Initialize RAG tool
    tools["rag_tool"] = RAGRetrieverTool(
        db_type=config.get("vector_db", "faiss"),
        verbose=config.get("debug", False)
    )
    
    # Initialize MVP estimator tool
    tools["mvp_estimator_tool"] = MVPEstimatorTool(
        estimation_method=config.get("estimation_method", "rule_based"),
        verbose=config.get("debug", False)
    )
    
    return tools

async def initialize_agents(tools: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Initialize all agents with their required tools."""
    agents = {}
    
    # Initialize MarketResearcherAgent
    agents["market_researcher"] = MarketResearcherAgent(
        search_tool=tools.get("search_tool"),
        verbose=config.get("debug", False)
    )
    
    # Initialize CompetitorAnalyzerAgent
    agents["competitor_analyzer"] = CompetitorAnalyzerAgent(
        search_tool=tools.get("search_tool"),
        scraper_tool=tools.get("scraper_tool"),
        verbose=config.get("debug", False)
    )
    
    # Initialize CustomerPersonaGeneratorAgent
    agents["customer_persona_generator"] = CustomerPersonaGeneratorAgent(
        verbose=config.get("debug", False)
    )
    
    # Initialize MVPPlannerAgent
    agents["mvp_planner"] = MVPPlannerAgent(
        rag_tool=tools.get("rag_tool"),
        cost_estimator_tool=tools.get("mvp_estimator_tool"),
        verbose=config.get("debug", False)
    )
    
    return agents

def load_example_idea() -> Dict[str, Any]:
    """Load an example startup idea for testing."""
    return {
        "name": "FreshMeal",
        "description": "A meal planning and grocery delivery service that focuses on fresh, local ingredients and reduces food waste by providing exact portions needed for each recipe.",
        "target_audience": "Busy professionals and families who want to eat healthy and reduce food waste",
        "industry": "Food Tech / Sustainability",
        "problem_statement": "People want to cook healthy meals but struggle with meal planning, food waste, and grocery shopping time",
        "solution": "AI-powered meal planning with precise ingredients delivered from local sources",
        "revenue_model": "Subscription + markup on grocery items"
    }

async def main(args):
    """Main entry point for the application."""
    # Load environment variables
    load_dotenv()
    
    # Create configuration
    config = {
        "debug": args.debug,
        "use_playwright": False,  # Set to True if you have Playwright installed
        "vector_db": "faiss",
        "estimation_method": "rule_based",
        "human_in_the_loop": args.interactive
    }
    
    # Create output directory
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize orchestrator config
    orchestrator_config = OrchestratorConfig(
        debug=config["debug"],
        log_level="DEBUG" if config["debug"] else "INFO",
        output_dir=output_dir,
        save_intermediate_results=True,
        human_in_the_loop=config["human_in_the_loop"]
    )
    
    # Initialize tools
    print("Initializing tools...")
    tools = await initialize_tools(config)
    
    # Initialize agents
    print("Initializing agents...")
    agents = await initialize_agents(tools, config)
    
    # Initialize orchestrator
    print("Initializing orchestrator...")
    orchestrator = StartupValidatorOrchestrator(config=orchestrator_config)
    
    # Register tools with orchestrator
    for name, tool in tools.items():
        orchestrator.register_tool(name, tool)
    
    # Register agents with orchestrator
    for name, agent in agents.items():
        orchestrator.register_agent(name, agent)
    
    # Determine input data
    if args.input_file:
        # Load from file
        try:
            with open(args.input_file, 'r') as f:
                input_data = json.load(f)
            print(f"Loaded startup idea from {args.input_file}")
        except Exception as e:
            print(f"Error loading input file: {e}")
            print("Using example idea instead.")
            input_data = load_example_idea()
    else:
        # Use example idea
        input_data = load_example_idea()
        print("Using example startup idea:")
        print(f"  Name: {input_data['name']}")
        print(f"  Description: {input_data['description']}")
    
    # Determine workflow
    workflow = args.workflow
    if workflow not in ["full_validation", "market_only", "mvp_only"]:
        print(f"Invalid workflow: {workflow}")
        print("Using full_validation workflow instead.")
        workflow = "full_validation"
    
    # Execute the workflow
    print(f"\nExecuting {workflow} workflow...")
    result = await orchestrator.execute_workflow(workflow, input_data)
    
    # Print results summary
    print("\n" + "=" * 50)
    print("STARTUP VALIDATION RESULTS")
    print("=" * 50)
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Startup Idea: {result.get('idea', {}).get('name', 'N/A')}")
        
        if "validation_score" in result:
            score = result["validation_score"]
            print(f"Validation Score: {score}/100")
            
            # Interpret the score
            if score >= 80:
                print("Assessment: Highly Promising")
            elif score >= 60:
                print("Assessment: Promising")
            elif score >= 40:
                print("Assessment: Moderate Potential")
            else:
                print("Assessment: Challenging")
        
        if "recommendations" in result and result["recommendations"]:
            print("\nKey Recommendations:")
            for i, rec in enumerate(result["recommendations"][:5], 1):
                print(f"  {i}. {rec}")
    
    print("\nFull results saved to:", output_dir)
    
    # Save full result to file
    timestamp = orchestrator_config.output_dir
    result_file = os.path.join(output_dir, "validation_result.json")
    with open(result_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"Full results saved to: {result_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MSVA - Multi-Agent Startup Validation Assistant")
    parser.add_argument("--input-file", type=str, help="Path to a JSON file containing startup idea data")
    parser.add_argument("--output-dir", type=str, default="./outputs", help="Directory to save output files")
    parser.add_argument("--workflow", type=str, default="full_validation", 
                        choices=["full_validation", "market_only", "mvp_only"],
                        help="Workflow to run")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--interactive", action="store_true", help="Enable human-in-the-loop mode")
    
    args = parser.parse_args()
    
    # Run the main function
    asyncio.run(main(args))
