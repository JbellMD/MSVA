"""
Startup Validator Orchestrator for the MSVA project.
Implements workflows for startup idea validation using multiple agents.
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
import logging
from pathlib import Path

from .base_orchestrator import BaseOrchestrator, OrchestratorConfig, AgentOutput

class StartupIdea(BaseModel):
    """Model for a startup idea."""
    name: str
    description: str
    target_audience: Optional[str] = None
    industry: Optional[str] = None
    problem_statement: Optional[str] = None
    solution: Optional[str] = None
    revenue_model: Optional[str] = None
    initial_thoughts: Optional[str] = None

class StartupValidationReport(BaseModel):
    """Model for the final startup validation report."""
    idea: StartupIdea
    market_analysis: Dict[str, Any] = Field(default_factory=dict)
    competitor_analysis: Dict[str, Any] = Field(default_factory=dict)
    customer_personas: List[Dict[str, Any]] = Field(default_factory=list)
    mvp_plan: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    validation_score: Optional[float] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class StartupValidatorOrchestrator(BaseOrchestrator):
    """
    Orchestrator for validating startup ideas using a multi-agent approach.
    Coordinates the workflow between Market Researcher, Competitor Analyzer, 
    Customer Persona Generator, and MVP Planner agents.
    """
    
    def __init__(self, config: Optional[OrchestratorConfig] = None):
        """
        Initialize the startup validator orchestrator.
        
        Args:
            config: Configuration for the orchestrator
        """
        super().__init__(config)
        
        # Register workflows
        self.register_workflow("full_validation", self.workflow_full_validation)
        self.register_workflow("market_only", self.workflow_market_only)
        self.register_workflow("mvp_only", self.workflow_mvp_only)
    
    async def workflow_full_validation(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the full validation workflow for a startup idea.
        This workflow runs all four agents in sequence, with each agent building on previous results.
        
        Args:
            input_data: Dictionary containing the startup idea
            
        Returns:
            Dictionary containing the validation results from all agents
        """
        self.logger.info("Starting full validation workflow")
        
        # Parse and validate input
        startup_idea = self._parse_startup_idea(input_data)
        self.logger.debug(f"Validating startup idea: {startup_idea.name}")
        
        # Stage 1: Market Research
        market_result = await self.run_agent("market_researcher", {
            "idea": startup_idea.dict(),
            "search_terms": input_data.get("search_terms", [])
        })
        
        if not market_result.success:
            self.logger.error("Market research failed")
            return self._generate_error_report("Market research failed", startup_idea)
            
        market_data = market_result.content
        
        # Save intermediate result
        self._save_result("market_research", market_data)
        
        # Stage 2: Competitor Analysis
        competitor_result = await self.run_agent("competitor_analyzer", {
            "idea": startup_idea.dict(),
            "market_data": market_data
        })
        
        if not competitor_result.success:
            self.logger.error("Competitor analysis failed")
            return self._generate_error_report("Competitor analysis failed", startup_idea, market_data=market_data)
            
        competitor_data = competitor_result.content
        
        # Save intermediate result
        self._save_result("competitor_analysis", competitor_data)
        
        # Stage 3: Customer Persona Generation
        persona_result = await self.run_agent("customer_persona_generator", {
            "idea": startup_idea.dict(),
            "market_data": market_data,
            "competitor_data": competitor_data
        })
        
        if not persona_result.success:
            self.logger.error("Customer persona generation failed")
            return self._generate_error_report(
                "Customer persona generation failed", 
                startup_idea, 
                market_data=market_data,
                competitor_data=competitor_data
            )
            
        persona_data = persona_result.content
        
        # Save intermediate result
        self._save_result("customer_personas", persona_data)
        
        # Stage 4: MVP Planning
        # Check if human approval is needed before MVP planning
        if self.config.human_in_the_loop:
            approval = await self.get_human_feedback(
                "Review the market research, competitor analysis, and customer personas. Proceed with MVP planning?",
                options=["proceed", "stop"]
            )
            
            if approval != "proceed":
                self.logger.info("MVP planning stopped by human")
                return self._generate_interim_report(
                    startup_idea, 
                    market_data, 
                    competitor_data, 
                    persona_data
                )
        
        mvp_result = await self.run_agent("mvp_planner", {
            "idea": startup_idea.dict(),
            "market_data": market_data,
            "competitor_data": competitor_data,
            "customer_personas": persona_data
        })
        
        if not mvp_result.success:
            self.logger.error("MVP planning failed")
            return self._generate_error_report(
                "MVP planning failed", 
                startup_idea, 
                market_data=market_data,
                competitor_data=competitor_data,
                persona_data=persona_data
            )
            
        mvp_data = mvp_result.content
        
        # Save intermediate result
        self._save_result("mvp_plan", mvp_data)
        
        # Generate final validation report
        report = self._generate_validation_report(
            startup_idea, 
            market_data, 
            competitor_data, 
            persona_data, 
            mvp_data
        )
        
        # Save final report
        report_path = self._save_validation_report(report)
        self.logger.info(f"Validation report saved to: {report_path}")
        
        return report.dict()
    
    async def workflow_market_only(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a partial workflow focusing only on market research.
        
        Args:
            input_data: Dictionary containing the startup idea
            
        Returns:
            Dictionary containing the market research results
        """
        self.logger.info("Starting market-only validation workflow")
        
        # Parse and validate input
        startup_idea = self._parse_startup_idea(input_data)
        self.logger.debug(f"Validating market for startup idea: {startup_idea.name}")
        
        # Run market research only
        market_result = await self.run_agent("market_researcher", {
            "idea": startup_idea.dict(),
            "search_terms": input_data.get("search_terms", [])
        })
        
        if not market_result.success:
            self.logger.error("Market research failed")
            return self._generate_error_report("Market research failed", startup_idea)
            
        market_data = market_result.content
        
        # Generate simplified report
        report = {
            "idea": startup_idea.dict(),
            "market_analysis": market_data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save report
        self._save_result("market_only_report", report)
        
        return report
    
    async def workflow_mvp_only(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a partial workflow focusing only on MVP planning.
        This assumes market research, competitor analysis, and personas are provided.
        
        Args:
            input_data: Dictionary containing the startup idea and previous analyses
            
        Returns:
            Dictionary containing the MVP planning results
        """
        self.logger.info("Starting MVP-only workflow")
        
        # Parse and validate input
        startup_idea = self._parse_startup_idea(input_data)
        
        # Ensure required data is provided
        required_keys = ["market_data", "competitor_data", "customer_personas"]
        missing_keys = [key for key in required_keys if key not in input_data]
        
        if missing_keys:
            error_msg = f"Missing required data: {', '.join(missing_keys)}"
            self.logger.error(error_msg)
            return {"error": error_msg, "success": False}
        
        # Run MVP planning
        mvp_result = await self.run_agent("mvp_planner", {
            "idea": startup_idea.dict(),
            "market_data": input_data["market_data"],
            "competitor_data": input_data["competitor_data"],
            "customer_personas": input_data["customer_personas"]
        })
        
        if not mvp_result.success:
            self.logger.error("MVP planning failed")
            return {"error": "MVP planning failed", "success": False}
            
        mvp_data = mvp_result.content
        
        # Generate simplified report
        report = {
            "idea": startup_idea.dict(),
            "mvp_plan": mvp_data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save report
        self._save_result("mvp_only_report", report)
        
        return report
    
    def _parse_startup_idea(self, input_data: Dict[str, Any]) -> StartupIdea:
        """Parse and validate the startup idea from input data."""
        if "idea" in input_data:
            idea_data = input_data["idea"]
            # If idea is provided as a dictionary, parse it
            if isinstance(idea_data, dict):
                return StartupIdea(**idea_data)
            # If idea is already a StartupIdea instance, use it
            elif isinstance(idea_data, StartupIdea):
                return idea_data
                
        # Try to parse from root level keys
        try:
            return StartupIdea(**input_data)
        except Exception as e:
            self.logger.error(f"Failed to parse startup idea: {str(e)}")
            raise ValueError("Invalid startup idea format")
    
    def _generate_validation_report(
        self, 
        idea: StartupIdea,
        market_data: Dict[str, Any],
        competitor_data: Dict[str, Any],
        persona_data: Dict[str, Any],
        mvp_data: Dict[str, Any]
    ) -> StartupValidationReport:
        """
        Generate a complete validation report from all agent outputs.
        
        Args:
            idea: The startup idea
            market_data: Market research data
            competitor_data: Competitor analysis data
            persona_data: Customer persona data
            mvp_data: MVP plan data
            
        Returns:
            A StartupValidationReport instance
        """
        # Generate recommendations based on all data
        recommendations = self._generate_recommendations(
            market_data, 
            competitor_data, 
            persona_data, 
            mvp_data
        )
        
        # Calculate a validation score
        validation_score = self._calculate_validation_score(
            market_data, 
            competitor_data, 
            persona_data, 
            mvp_data
        )
        
        # Create and return the report
        return StartupValidationReport(
            idea=idea,
            market_analysis=market_data,
            competitor_analysis=competitor_data,
            customer_personas=persona_data.get("personas", []),
            mvp_plan=mvp_data,
            recommendations=recommendations,
            validation_score=validation_score
        )
    
    def _generate_recommendations(
        self,
        market_data: Dict[str, Any],
        competitor_data: Dict[str, Any],
        persona_data: Dict[str, Any],
        mvp_data: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on all collected data."""
        recommendations = []
        
        # Market-based recommendations
        if "market_trends" in market_data:
            trends = market_data["market_trends"]
            if "growth_rate" in trends and trends["growth_rate"] < 5:
                recommendations.append(
                    "Consider pivoting to a higher-growth market segment as the current market shows low growth."
                )
            elif "growth_rate" in trends and trends["growth_rate"] > 20:
                recommendations.append(
                    "The market is growing rapidly. Consider securing funding quickly to capitalize on growth opportunities."
                )
                
        # Competitor-based recommendations
        if "market_gaps" in competitor_data:
            gaps = competitor_data["market_gaps"]
            if gaps:
                recommendations.append(
                    f"Focus on these identified gaps in the market: {', '.join(gaps[:3])}"
                )
                
        # Persona-based recommendations
        if "personas" in persona_data and persona_data["personas"]:
            primary_persona = persona_data["personas"][0]
            if "pain_points" in primary_persona:
                pain_points = primary_persona["pain_points"]
                recommendations.append(
                    f"Prioritize addressing these customer pain points: {', '.join(pain_points[:3])}"
                )
                
        # MVP-based recommendations
        if "features" in mvp_data and mvp_data["features"]:
            recommendations.append(
                "Focus on building and validating the core MVP features before expanding scope."
            )
            
        if "assumptions_and_risks" in mvp_data:
            risks = [item for item in mvp_data["assumptions_and_risks"] if item["type"] == "risk"]
            if risks:
                recommendations.append(
                    f"Mitigate key risks early: {risks[0]['description'] if risks else ''}"
                )
                
        # Add general recommendations if we have few specific ones
        if len(recommendations) < 3:
            recommendations.append(
                "Validate your assumptions with real customer interviews before building the MVP."
            )
            recommendations.append(
                "Consider running small experiments to test key hypotheses about your target market."
            )
            
        return recommendations
    
    def _calculate_validation_score(
        self,
        market_data: Dict[str, Any],
        competitor_data: Dict[str, Any],
        persona_data: Dict[str, Any],
        mvp_data: Dict[str, Any]
    ) -> float:
        """
        Calculate a validation score between 0-100.
        Higher score indicates a more promising startup idea.
        """
        score = 50  # Start with neutral score
        
        # Market factors (up to +/- 20 points)
        if "market_trends" in market_data:
            trends = market_data["market_trends"]
            
            # Market size and growth
            if "market_size" in trends:
                market_size = trends["market_size"]
                if market_size > 1000000000:  # >$1B
                    score += 10
                elif market_size > 100000000:  # >$100M
                    score += 5
                elif market_size < 10000000:  # <$10M
                    score -= 5
                    
            if "growth_rate" in trends:
                growth_rate = trends["growth_rate"]
                if growth_rate > 20:  # >20%
                    score += 10
                elif growth_rate > 10:  # >10%
                    score += 5
                elif growth_rate < 5:  # <5%
                    score -= 5
                elif growth_rate < 0:  # Negative
                    score -= 10
                    
        # Competitor factors (up to +/- 15 points)
        if "competitors" in competitor_data:
            competitors = competitor_data["competitors"]
            
            # Number of direct competitors
            num_direct = sum(1 for c in competitors if c.get("type") == "direct")
            if num_direct == 0:
                score += 5  # No direct competitors could be good (blue ocean)
            elif num_direct > 10:
                score -= 5  # Too crowded
                
            # Market gaps
            if "market_gaps" in competitor_data and competitor_data["market_gaps"]:
                score += 5
                if len(competitor_data["market_gaps"]) > 3:
                    score += 5  # Multiple opportunities
                    
        # Customer persona factors (up to +/- 15 points)
        if "personas" in persona_data and persona_data["personas"]:
            personas = persona_data["personas"]
            
            # Customer pain level
            if "pain_level" in personas[0]:
                pain_level = personas[0]["pain_level"]
                if pain_level == "high":
                    score += 10
                elif pain_level == "medium":
                    score += 5
                elif pain_level == "low":
                    score -= 5
                    
            # Willingness to pay
            if "willingness_to_pay" in personas[0]:
                wtp = personas[0]["willingness_to_pay"]
                if wtp == "high":
                    score += 5
                elif wtp == "low":
                    score -= 5
                    
        # MVP factors (up to +/- 10 points)
        if "development_time" in mvp_data:
            # Shorter time to market is better
            dev_time = mvp_data["development_time"]["weeks"]
            if dev_time < 6:
                score += 5
            elif dev_time > 12:
                score -= 5
                
        if "cost_estimate" in mvp_data:
            # Lower cost is better for initial validation
            min_cost = mvp_data["cost_estimate"].get("min", 0)
            if min_cost < 15000:
                score += 5
            elif min_cost > 50000:
                score -= 5
        
        # Clamp the score to 0-100
        return max(0, min(100, score))
    
    def _generate_error_report(
        self, 
        error_message: str,
        idea: StartupIdea,
        market_data: Optional[Dict[str, Any]] = None,
        competitor_data: Optional[Dict[str, Any]] = None,
        persona_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate an error report with whatever data we have so far."""
        report = {
            "success": False,
            "error": error_message,
            "idea": idea.dict(),
            "timestamp": datetime.now().isoformat()
        }
        
        if market_data:
            report["market_analysis"] = market_data
            
        if competitor_data:
            report["competitor_analysis"] = competitor_data
            
        if persona_data:
            report["customer_personas"] = persona_data.get("personas", [])
            
        return report
    
    def _generate_interim_report(
        self,
        idea: StartupIdea,
        market_data: Dict[str, Any],
        competitor_data: Dict[str, Any],
        persona_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate an interim report without MVP planning."""
        report = {
            "success": True,
            "idea": idea.dict(),
            "market_analysis": market_data,
            "competitor_analysis": competitor_data,
            "customer_personas": persona_data.get("personas", []),
            "timestamp": datetime.now().isoformat(),
            "status": "interim",
            "message": "MVP planning was skipped due to user request"
        }
        
        # Save interim report
        self._save_result("interim_report", report)
        
        return report
    
    def _save_validation_report(self, report: StartupValidationReport) -> str:
        """
        Save the validation report to a file.
        
        Args:
            report: The validation report to save
            
        Returns:
            Path to the saved report file
        """
        # Create reports directory if it doesn't exist
        reports_dir = os.path.join(self.config.output_dir, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        # Create a filename with timestamp and idea name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        idea_name = report.idea.name.replace(" ", "_").lower()
        filename = f"validation_report_{idea_name}_{timestamp}.json"
        
        file_path = os.path.join(reports_dir, filename)
        
        # Write the report to file
        with open(file_path, 'w') as f:
            json.dump(report.dict(), f, indent=2)
            
        return file_path
