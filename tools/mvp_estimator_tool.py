"""
MVP Estimator Tool for the MSVA project.
Estimates development costs, timelines, and resource requirements for MVPs.
"""

import os
import json
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from datetime import datetime, timedelta
from .base_tool import BaseTool

class ComplexityLevel(Enum):
    """Enum for complexity levels of features or MVPs."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class MVPEstimatorTool(BaseTool):
    """
    Tool for estimating MVP development costs, timelines, and resource requirements.
    Can use rule-based estimation or LLM-based estimation.
    """
    
    def __init__(
        self, 
        estimation_method: str = "rule_based",  # "rule_based" or "llm_based"
        cost_multiplier: float = 1.0,  # Regional cost adjustment (1.0 = US average)
        verbose: bool = False,
        llm_function: Optional[Any] = None  # LLM function for llm_based estimation
    ):
        super().__init__(
            name="MVP Estimator Tool",
            description="Estimates development costs, timelines, and resource requirements for MVPs",
            verbose=verbose
        )
        self.estimation_method = estimation_method.lower()
        self.cost_multiplier = cost_multiplier
        self.llm_function = llm_function
        
        # Base rates for different resource types (hourly rates in USD)
        self.base_rates = {
            "frontend_developer": 50,
            "backend_developer": 60,
            "fullstack_developer": 65,
            "designer": 55,
            "devops_engineer": 70,
            "project_manager": 65,
            "qa_tester": 45
        }
        
        # Base time estimates for different complexity levels (in hours)
        self.base_time_estimates = {
            ComplexityLevel.LOW: 40,        # 1 week
            ComplexityLevel.MEDIUM: 80,     # 2 weeks
            ComplexityLevel.HIGH: 160,      # 4 weeks
            ComplexityLevel.VERY_HIGH: 320  # 8 weeks
        }
        
        # Technology complexity multipliers
        self.tech_complexity = {
            # Frontend
            "html_css": 0.8,
            "react": 1.0,
            "angular": 1.1,
            "vue": 1.0,
            "flutter": 1.2,
            "react_native": 1.2,
            
            # Backend
            "node_js": 1.0,
            "express": 0.9,
            "django": 1.0,
            "flask": 0.9,
            "rails": 1.0,
            "laravel": 1.0,
            "spring_boot": 1.2,
            
            # Database
            "sqlite": 0.7,
            "mysql": 0.9,
            "postgresql": 1.0,
            "mongodb": 1.0,
            "firebase": 0.9,
            "dynamodb": 1.1,
            
            # Infrastructure
            "aws": 1.1,
            "azure": 1.1,
            "gcp": 1.1,
            "heroku": 0.8,
            "netlify": 0.8,
            "vercel": 0.8,
            
            # Other
            "ai_integration": 1.4,
            "payment_processing": 1.2,
            "authentication": 1.0,
            "third_party_apis": 1.1,
            "realtime_features": 1.3,
            "offline_support": 1.2
        }
        
    async def run(
        self, 
        features: List[Dict[str, Any]],
        tech_stack: List[str],
        complexity: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Estimate MVP development costs, timeline, and resource requirements.
        
        Args:
            features: List of features with name, description, and optionally complexity
            tech_stack: List of technologies to be used
            complexity: Overall project complexity (if not specified, will be calculated)
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing estimation results
        """
        self.log(f"Estimating MVP with {len(features)} features and {len(tech_stack)} technologies")
        
        if self.estimation_method == "rule_based":
            return await self._rule_based_estimation(features, tech_stack, complexity, **kwargs)
        elif self.estimation_method == "llm_based":
            return await self._llm_based_estimation(features, tech_stack, complexity, **kwargs)
        else:
            raise ValueError(f"Unsupported estimation method: {self.estimation_method}")
    
    async def _rule_based_estimation(
        self, 
        features: List[Dict[str, Any]],
        tech_stack: List[str],
        complexity: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform rule-based estimation for MVP development.
        
        Args:
            features: List of features
            tech_stack: List of technologies
            complexity: Overall project complexity
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing estimation results
        """
        # Calculate or use provided overall complexity
        overall_complexity = self._calculate_overall_complexity(features, tech_stack, complexity)
        
        # Determine technology complexity multiplier
        tech_multiplier = self._calculate_tech_multiplier(tech_stack)
        
        # Calculate base hours based on complexity
        base_hours = self.base_time_estimates[overall_complexity]
        
        # Apply tech stack multiplier
        adjusted_hours = base_hours * tech_multiplier
        
        # Calculate feature breakdown
        feature_estimates = self._calculate_feature_estimates(features, overall_complexity, tech_multiplier)
        
        # Calculate resource requirements
        resources = self._calculate_resource_requirements(feature_estimates, tech_stack)
        
        # Calculate total cost
        total_cost = self._calculate_total_cost(resources)
        
        # Calculate timeline
        timeline = self._calculate_timeline(resources)
        
        # Format results
        return {
            "status": "success",
            "overall_complexity": overall_complexity.value,
            "total_hours": adjusted_hours,
            "total_cost": total_cost,
            "timeline_weeks": timeline["weeks"],
            "timeline_months": timeline["months"],
            "estimated_launch_date": timeline["estimated_launch_date"],
            "feature_estimates": feature_estimates,
            "resource_requirements": resources,
            "assumptions_and_risks": self._generate_assumptions_and_risks(overall_complexity, tech_stack)
        }
    
    async def _llm_based_estimation(
        self, 
        features: List[Dict[str, Any]],
        tech_stack: List[str],
        complexity: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform LLM-based estimation for MVP development.
        
        Args:
            features: List of features
            tech_stack: List of technologies
            complexity: Overall project complexity
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing estimation results
        """
        if not self.llm_function:
            self.log("No LLM function provided, falling back to rule-based estimation")
            return await self._rule_based_estimation(features, tech_stack, complexity, **kwargs)
            
        try:
            # Prepare the prompt for the LLM
            prompt = self._generate_llm_prompt(features, tech_stack, complexity)
            
            # Call the LLM
            llm_response = await self._call_llm(prompt)
            
            # Parse the LLM response
            estimation_results = self._parse_llm_response(llm_response)
            
            # If parsing failed, fall back to rule-based
            if not estimation_results or "status" not in estimation_results:
                self.log("Failed to parse LLM response, falling back to rule-based estimation")
                return await self._rule_based_estimation(features, tech_stack, complexity, **kwargs)
                
            return estimation_results
            
        except Exception as e:
            self.log(f"Error in LLM-based estimation: {str(e)}. Falling back to rule-based.")
            return await self._rule_based_estimation(features, tech_stack, complexity, **kwargs)
    
    async def _call_llm(self, prompt: str) -> str:
        """Call the LLM with the given prompt."""
        if not self.llm_function:
            raise ValueError("No LLM function provided")
            
        if asyncio.iscoroutinefunction(self.llm_function):
            return await self.llm_function(prompt)
        else:
            return self.llm_function(prompt)
    
    def _generate_llm_prompt(
        self, 
        features: List[Dict[str, Any]],
        tech_stack: List[str],
        complexity: Optional[str]
    ) -> str:
        """Generate a prompt for the LLM to estimate MVP costs and timeline."""
        features_text = "\n".join([f"- {f['name']}: {f.get('description', '')}" for f in features])
        tech_stack_text = ", ".join(tech_stack)
        complexity_text = f"Overall complexity: {complexity}" if complexity else "Please determine the overall complexity"
        
        prompt = f"""
        As an MVP development expert, please provide a detailed estimation for the following MVP project:
        
        FEATURES:
        {features_text}
        
        TECH STACK:
        {tech_stack_text}
        
        {complexity_text}
        
        Please provide the following information in your response:
        1. Overall complexity assessment (low, medium, high, or very high)
        2. Total development hours
        3. Cost estimate range (in USD)
        4. Timeline in weeks and months
        5. Resource requirements (types of developers needed)
        6. Brief breakdown of time required for each feature
        7. Key assumptions and potential risks
        
        Format your response as a structured JSON object with the following keys:
        - overall_complexity
        - total_hours
        - total_cost_min
        - total_cost_max
        - timeline_weeks
        - timeline_months
        - resource_requirements (array of objects with role, hours, and cost)
        - feature_estimates (array of objects with feature name, hours, and cost)
        - assumptions_and_risks (array of strings)
        """
        
        return prompt
    
    def _parse_llm_response(self, llm_response: str) -> Dict[str, Any]:
        """Parse the LLM response into a structured format."""
        try:
            # Try to extract JSON from the response
            start_idx = llm_response.find("{")
            end_idx = llm_response.rfind("}") + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = llm_response[start_idx:end_idx]
                result = json.loads(json_str)
                
                # Convert the result to our standard format
                standardized = {
                    "status": "success",
                    "overall_complexity": result.get("overall_complexity", "medium"),
                    "total_hours": result.get("total_hours", 0),
                    "total_cost": {
                        "min": result.get("total_cost_min", 0),
                        "max": result.get("total_cost_max", 0),
                        "currency": "USD"
                    },
                    "timeline_weeks": result.get("timeline_weeks", 0),
                    "timeline_months": result.get("timeline_months", 0),
                    "estimated_launch_date": self._calculate_launch_date(result.get("timeline_weeks", 0)),
                    "feature_estimates": result.get("feature_estimates", []),
                    "resource_requirements": result.get("resource_requirements", []),
                    "assumptions_and_risks": result.get("assumptions_and_risks", [])
                }
                
                return standardized
            else:
                return {}
                
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            self.log(f"Error parsing LLM response: {str(e)}")
            return {}
    
    def _calculate_overall_complexity(
        self, 
        features: List[Dict[str, Any]], 
        tech_stack: List[str],
        provided_complexity: Optional[str] = None
    ) -> ComplexityLevel:
        """Calculate the overall complexity of the MVP based on features and tech stack."""
        if provided_complexity:
            try:
                return ComplexityLevel(provided_complexity.lower())
            except ValueError:
                # If invalid complexity provided, calculate it
                pass
                
        # Calculate complexity based on features and tech stack
        feature_complexity_scores = []
        for feature in features:
            if "complexity" in feature:
                try:
                    complexity = ComplexityLevel(feature["complexity"].lower())
                    feature_complexity_scores.append(self._complexity_to_score(complexity))
                except ValueError:
                    # If invalid complexity, use medium as default
                    feature_complexity_scores.append(2)  # Medium = 2
            else:
                feature_complexity_scores.append(2)  # Medium = 2
                
        # Calculate average feature complexity
        avg_feature_complexity = sum(feature_complexity_scores) / len(feature_complexity_scores) if feature_complexity_scores else 2
        
        # Calculate tech stack complexity
        tech_complexity_score = 0
        tech_count = 0
        for tech in tech_stack:
            tech_key = self._normalize_tech_name(tech)
            if tech_key in self.tech_complexity:
                tech_complexity_score += self.tech_complexity[tech_key]
                tech_count += 1
                
        avg_tech_complexity = tech_complexity_score / tech_count if tech_count > 0 else 1.0
        
        # Combine feature and tech complexity
        combined_complexity_score = (avg_feature_complexity * 0.7) + (avg_tech_complexity * 0.3 * 4)
        
        # Map score to complexity level
        if combined_complexity_score < 1.5:
            return ComplexityLevel.LOW
        elif combined_complexity_score < 2.5:
            return ComplexityLevel.MEDIUM
        elif combined_complexity_score < 3.5:
            return ComplexityLevel.HIGH
        else:
            return ComplexityLevel.VERY_HIGH
    
    def _complexity_to_score(self, complexity: ComplexityLevel) -> int:
        """Convert complexity level to numeric score."""
        mapping = {
            ComplexityLevel.LOW: 1,
            ComplexityLevel.MEDIUM: 2,
            ComplexityLevel.HIGH: 3,
            ComplexityLevel.VERY_HIGH: 4
        }
        return mapping[complexity]
    
    def _normalize_tech_name(self, tech: str) -> str:
        """Normalize technology name to match our dictionary keys."""
        tech = tech.lower().replace(' ', '_').replace('-', '_').replace('.', '_')
        
        # Common mappings
        mappings = {
            "react_js": "react",
            "reactjs": "react",
            "nodejs": "node_js",
            "node": "node_js",
            "postgres": "postgresql",
            "mongo": "mongodb",
            "firebase_firestore": "firebase",
            "aws_dynamodb": "dynamodb",
            "google_cloud": "gcp",
            "google_cloud_platform": "gcp"
        }
        
        return mappings.get(tech, tech)
    
    def _calculate_tech_multiplier(self, tech_stack: List[str]) -> float:
        """Calculate technology complexity multiplier based on the tech stack."""
        if not tech_stack:
            return 1.0
            
        total_multiplier = 0.0
        recognized_techs = 0
        
        for tech in tech_stack:
            tech_key = self._normalize_tech_name(tech)
            if tech_key in self.tech_complexity:
                total_multiplier += self.tech_complexity[tech_key]
                recognized_techs += 1
                
        # If no technologies were recognized, use default multiplier of 1.0
        if recognized_techs == 0:
            return 1.0
            
        # Average the multipliers
        avg_multiplier = total_multiplier / recognized_techs
        
        # Add slight complexity for using multiple technologies
        stack_size_factor = 1.0 + (min(len(tech_stack) - 1, 5) * 0.03)
        
        return avg_multiplier * stack_size_factor
    
    def _calculate_feature_estimates(
        self, 
        features: List[Dict[str, Any]],
        overall_complexity: ComplexityLevel,
        tech_multiplier: float
    ) -> List[Dict[str, Any]]:
        """Calculate time and cost estimates for each feature."""
        feature_estimates = []
        
        for feature in features:
            # Determine feature complexity
            if "complexity" in feature:
                try:
                    feature_complexity = ComplexityLevel(feature["complexity"].lower())
                except ValueError:
                    feature_complexity = overall_complexity
            else:
                feature_complexity = overall_complexity
                
            # Calculate base hours for the feature based on its complexity
            feature_base_hours = self.base_time_estimates[feature_complexity] / 4  # Divide by 4 as features are smaller than full MVPs
            
            # Adjust hours based on tech multiplier
            feature_hours = feature_base_hours * tech_multiplier
            
            # Calculate cost
            feature_cost = self._calculate_feature_cost(feature_hours, overall_complexity)
            
            # Create feature estimate
            feature_estimates.append({
                "name": feature["name"],
                "description": feature.get("description", ""),
                "complexity": feature_complexity.value,
                "hours": round(feature_hours, 1),
                "cost": {
                    "min": round(feature_cost * 0.8, -2),  # Round to nearest hundred
                    "max": round(feature_cost * 1.2, -2),  # Round to nearest hundred
                    "currency": "USD"
                }
            })
            
        return feature_estimates
    
    def _calculate_feature_cost(self, hours: float, complexity: ComplexityLevel) -> float:
        """Calculate the cost for a feature based on hours and complexity."""
        # Base hourly rate depends on complexity
        base_rate = {
            ComplexityLevel.LOW: 50,
            ComplexityLevel.MEDIUM: 60,
            ComplexityLevel.HIGH: 70,
            ComplexityLevel.VERY_HIGH: 80
        }[complexity]
        
        # Apply regional cost multiplier
        adjusted_rate = base_rate * self.cost_multiplier
        
        # Calculate cost
        return hours * adjusted_rate
    
    def _calculate_resource_requirements(
        self, 
        feature_estimates: List[Dict[str, Any]],
        tech_stack: List[str]
    ) -> List[Dict[str, Any]]:
        """Calculate resource requirements based on features and tech stack."""
        # Determine if we need specialized roles
        has_frontend = any(tech in map(str.lower, tech_stack) for tech in ["react", "angular", "vue", "html", "css", "frontend"])
        has_backend = any(tech in map(str.lower, tech_stack) for tech in ["node", "express", "django", "flask", "rails", "backend", "api"])
        has_mobile = any(tech in map(str.lower, tech_stack) for tech in ["flutter", "react native", "ios", "android", "mobile"])
        
        # Calculate total hours from feature estimates
        total_hours = sum(feature["hours"] for feature in feature_estimates)
        
        # Initialize resource allocation
        resources = []
        
        # Case 1: Small project - use fullstack developer
        if total_hours < 120:  # Less than 3 weeks of work
            resources.append({
                "role": "Fullstack Developer",
                "hours": round(total_hours * 1.1, 1),  # 10% overhead
                "cost": round(self.base_rates["fullstack_developer"] * total_hours * 1.1 * self.cost_multiplier, -2)
            })
            
        # Case 2: Medium to large project - use specialized roles
        else:
            # Add design resources (10-15% of total hours)
            design_hours = total_hours * 0.15
            resources.append({
                "role": "UI/UX Designer",
                "hours": round(design_hours, 1),
                "cost": round(self.base_rates["designer"] * design_hours * self.cost_multiplier, -2)
            })
            
            # Add frontend developer if needed
            if has_frontend or has_mobile:
                frontend_hours = total_hours * 0.35
                resources.append({
                    "role": "Frontend Developer" if has_frontend else "Mobile Developer",
                    "hours": round(frontend_hours, 1),
                    "cost": round(self.base_rates["frontend_developer"] * frontend_hours * self.cost_multiplier, -2)
                })
                
            # Add backend developer if needed
            if has_backend:
                backend_hours = total_hours * 0.4
                resources.append({
                    "role": "Backend Developer",
                    "hours": round(backend_hours, 1),
                    "cost": round(self.base_rates["backend_developer"] * backend_hours * self.cost_multiplier, -2)
                })
                
            # If neither specialized frontend nor backend were added, add fullstack
            if not (has_frontend or has_mobile or has_backend):
                fullstack_hours = total_hours * 0.75
                resources.append({
                    "role": "Fullstack Developer",
                    "hours": round(fullstack_hours, 1),
                    "cost": round(self.base_rates["fullstack_developer"] * fullstack_hours * self.cost_multiplier, -2)
                })
                
            # Add project management (10-20% of total hours)
            pm_hours = total_hours * 0.15
            resources.append({
                "role": "Project Manager",
                "hours": round(pm_hours, 1),
                "cost": round(self.base_rates["project_manager"] * pm_hours * self.cost_multiplier, -2)
            })
            
            # Add QA testing (10-15% of total hours)
            qa_hours = total_hours * 0.1
            resources.append({
                "role": "QA Tester",
                "hours": round(qa_hours, 1),
                "cost": round(self.base_rates["qa_tester"] * qa_hours * self.cost_multiplier, -2)
            })
            
        return resources
    
    def _calculate_total_cost(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate total cost based on resource requirements."""
        total_cost = sum(resource["cost"] for resource in resources)
        
        # Add contingency
        contingency = total_cost * 0.15
        
        # Add infrastructure and tooling costs (estimated)
        infra_cost = max(500, total_cost * 0.05)
        
        # Final cost range
        min_cost = round(total_cost, -2)  # Round to nearest hundred
        max_cost = round(total_cost + contingency + infra_cost, -2)  # Round to nearest hundred
        
        return {
            "min": min_cost,
            "max": max_cost,
            "currency": "USD",
            "breakdown": {
                "labor": round(total_cost, -2),
                "contingency": round(contingency, -2),
                "infrastructure": round(infra_cost, -2)
            }
        }
    
    def _calculate_timeline(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate project timeline based on resource requirements."""
        # Get total hours
        total_hours = sum(resource["hours"] for resource in resources)
        
        # Calculate developer weeks (assuming 40 hours per week per developer)
        developer_weeks = total_hours / 40
        
        # Determine parallel work factor based on team composition
        team_size = sum(1 for resource in resources if resource["role"] in 
                        ["Frontend Developer", "Backend Developer", "Fullstack Developer", "Mobile Developer"])
        
        # Adjust for parallel work (diminishing returns for larger teams)
        if team_size <= 1:
            parallel_factor = 1.0
        else:
            parallel_factor = 1 + (team_size - 1) * 0.6  # Diminishing returns for larger teams
            
        # Calculate calendar weeks
        calendar_weeks = developer_weeks / parallel_factor
        
        # Add time for project setup, coordination, and buffer (higher for larger projects)
        if calendar_weeks < 4:
            buffer_weeks = 1
        elif calendar_weeks < 8:
            buffer_weeks = 2
        else:
            buffer_weeks = 3
            
        total_weeks = calendar_weeks + buffer_weeks
        
        # Convert weeks to months (4.33 weeks per month)
        months = total_weeks / 4.33
        
        # Calculate estimated launch date
        launch_date = self._calculate_launch_date(total_weeks)
        
        return {
            "weeks": round(total_weeks, 1),
            "months": round(months, 1),
            "estimated_launch_date": launch_date
        }
    
    def _calculate_launch_date(self, weeks: float) -> str:
        """Calculate estimated launch date based on weeks from now."""
        current_date = datetime.now()
        launch_date = current_date + timedelta(weeks=weeks)
        return launch_date.strftime("%Y-%m-%d")
    
    def _generate_assumptions_and_risks(
        self, 
        complexity: ComplexityLevel,
        tech_stack: List[str]
    ) -> List[Dict[str, str]]:
        """Generate assumptions and risks based on project characteristics."""
        assumptions_and_risks = []
        
        # Common assumptions
        assumptions = [
            "The client will provide timely feedback during development.",
            "The scope of the MVP will remain fixed during development.",
            "The estimates assume normal business hours and no unexpected delays."
        ]
        
        # Add technology-specific assumptions
        tech_stack_lower = [tech.lower() for tech in tech_stack]
        
        if any(tech in " ".join(tech_stack_lower) for tech in ["react", "angular", "vue"]):
            assumptions.append("Front-end developers have experience with the specified JavaScript framework.")
            
        if any(tech in " ".join(tech_stack_lower) for tech in ["flutter", "react native"]):
            assumptions.append("Mobile app development will target both iOS and Android through cross-platform framework.")
            
        if any(tech in " ".join(tech_stack_lower) for tech in ["aws", "azure", "gcp", "cloud"]):
            assumptions.append("Cloud infrastructure costs are not included in the development estimate.")
            
        # Common risks
        risks = [
            "Scope creep could extend the timeline and increase costs.",
            "Integration with third-party services may introduce unexpected challenges."
        ]
        
        # Add complexity-specific risks
        if complexity in [ComplexityLevel.HIGH, ComplexityLevel.VERY_HIGH]:
            risks.append("The high complexity of the project increases the risk of unforeseen technical challenges.")
            risks.append("The timeline may need to be extended if technical difficulties arise.")
            
        if "payment" in " ".join(tech_stack_lower) or "stripe" in " ".join(tech_stack_lower):
            risks.append("Payment processing integration requires additional security considerations and testing.")
            
        if "ai" in " ".join(tech_stack_lower) or "machine learning" in " ".join(tech_stack_lower):
            risks.append("AI/ML features may require additional refinement and data to achieve desired performance.")
            
        # Format as objects with type
        formatted_assumptions = [{"type": "assumption", "description": a} for a in assumptions]
        formatted_risks = [{"type": "risk", "description": r} for r in risks]
        
        return formatted_assumptions + formatted_risks
    
    async def estimate(self, features: List[Dict[str, Any]], tech_stack: List[str], **kwargs) -> Dict[str, Any]:
        """
        Alias for run method to provide a more intuitive API.
        
        Args:
            features: List of features
            tech_stack: List of technologies
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing estimation results
        """
        return await self.run(features=features, tech_stack=tech_stack, **kwargs)
