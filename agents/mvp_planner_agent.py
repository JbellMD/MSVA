"""
MVP Planner Agent for the MSVA project.
Responsible for defining a minimal feature set and suggesting tech stack.
"""

import asyncio
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from .base_agent import BaseAgent

class Feature(BaseModel):
    """Model representing a feature in the MVP."""
    name: str
    description: str
    priority: int = Field(description="Priority from 1-10, with 10 being highest")
    complexity: int = Field(description="Complexity from 1-10, with 10 being most complex")
    estimated_hours: int = Field(description="Estimated development hours")
    user_value: int = Field(description="Value to users from 1-10, with 10 being highest")
    
class TechStackComponent(BaseModel):
    """Model representing a component of the tech stack."""
    category: str = Field(description="E.g., 'Frontend', 'Backend', 'Database'")
    name: str = Field(description="Name of the technology")
    description: str
    alternatives: List[str] = Field(description="Alternative technologies that could be used")
    learning_curve: int = Field(description="Learning curve from 1-10, with 10 being steepest")
    
class Timeline(BaseModel):
    """Model representing a project timeline."""
    total_weeks: int
    phases: List[Dict[str, Any]] = Field(description="List of project phases")
    milestones: List[Dict[str, Any]] = Field(description="Key project milestones")
    
class CostEstimate(BaseModel):
    """Model representing a cost estimate for the MVP."""
    development_cost: Dict[str, float] = Field(description="Breakdown of development costs")
    infrastructure_cost: Dict[str, float] = Field(description="Breakdown of infrastructure costs")
    operational_cost: Dict[str, float] = Field(description="Breakdown of ongoing operational costs")
    total_cost: float = Field(description="Total estimated cost")
    
class MVPPlan(BaseModel):
    """Model representing a complete MVP plan."""
    features: List[Feature]
    tech_stack: List[TechStackComponent]
    timeline: Timeline
    cost_estimate: CostEstimate
    assumptions: List[str] = Field(description="Key assumptions made in the plan")
    risks: List[Dict[str, Any]] = Field(description="Potential risks and mitigations")
    
class MVPPlannerAgent(BaseAgent):
    """
    Agent that defines a minimal feature set and suggests tech stack for a startup idea.
    Uses vector search of prior MVPs and estimation tools to create realistic plans.
    """
    
    def __init__(
        self,
        vector_search_tool=None,
        cost_estimator_tool=None,
        **kwargs
    ):
        super().__init__(
            name="MVP Planner",
            description="Defines minimal feature sets and suggests tech stacks for startup ideas",
            **kwargs
        )
        self.vector_search_tool = vector_search_tool
        self.cost_estimator_tool = cost_estimator_tool
        
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the startup idea and analyses to generate an MVP plan.
        
        Args:
            input_data: Dictionary containing 'idea', 'market_analysis',
                       'competitor_analysis', 'personas', and other parameters
            
        Returns:
            Dictionary containing the MVP plan
        """
        idea = input_data.get("idea")
        market_analysis = input_data.get("market_analysis", {})
        competitor_analysis = input_data.get("competitor_analysis", {})
        personas = input_data.get("personas", [])
        
        if not idea:
            return {
                "status": "error",
                "message": "No startup idea provided",
                "data": None
            }
            
        self.log(f"Creating MVP plan for idea: {idea}")
        
        # Step 1: Research similar MVPs using vector search
        similar_mvps = await self._find_similar_mvps(idea, market_analysis)
        
        # Step 2: Define core features for the MVP
        features = await self._define_features(
            idea, 
            market_analysis, 
            competitor_analysis, 
            personas,
            similar_mvps
        )
        
        # Step 3: Suggest appropriate tech stack
        tech_stack = await self._suggest_tech_stack(idea, features)
        
        # Step 4: Create timeline for MVP development
        timeline = await self._create_timeline(features)
        
        # Step 5: Generate cost estimates
        cost_estimate = await self._estimate_costs(features, tech_stack, timeline)
        
        # Step 6: Identify assumptions and risks
        assumptions, risks = await self._identify_assumptions_and_risks(
            idea,
            features,
            tech_stack
        )
        
        # Create the complete MVP plan
        mvp_plan = MVPPlan(
            features=features,
            tech_stack=tech_stack,
            timeline=timeline,
            cost_estimate=cost_estimate,
            assumptions=assumptions,
            risks=risks
        )
        
        # Store the results in memory
        self.add_to_memory({
            "idea": idea,
            "mvp_plan": mvp_plan.dict()
        })
        
        return {
            "status": "success",
            "message": "MVP plan created successfully",
            "data": {
                "mvp_plan": mvp_plan.dict(),
                "requires_user_approval": True
            }
        }
    
    async def _find_similar_mvps(
        self, 
        idea: str, 
        market_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find similar MVPs using vector search."""
        # In a full implementation, this would use the vector_search_tool
        # For now, we'll return simulated results
        
        if self.vector_search_tool:
            search_results = await self.vector_search_tool.search(
                query=idea,
                additional_context=market_analysis,
                limit=5
            )
            return search_results
        else:
            self.log("Vector search tool not available, returning simulated results")
            # Return simulated similar MVPs
            return [
                {
                    "id": "mvp-001",
                    "name": "Similar App 1",
                    "description": "A mobile app for journaling with AI suggestions",
                    "features": [
                        "User authentication",
                        "Text entry with formatting",
                        "Daily reminders",
                        "AI-powered writing prompts",
                        "Mood tracking"
                    ],
                    "tech_stack": ["React Native", "Firebase", "Node.js"],
                    "development_time": "12 weeks",
                    "success_metrics": {
                        "user_retention": "65%",
                        "average_usage": "3 times per week"
                    }
                },
                {
                    "id": "mvp-002",
                    "name": "Similar App 2",
                    "description": "A web platform for guided journaling experiences",
                    "features": [
                        "Email signup",
                        "Journaling templates",
                        "Progress tracking",
                        "Social sharing options"
                    ],
                    "tech_stack": ["Vue.js", "Django", "PostgreSQL"],
                    "development_time": "8 weeks",
                    "success_metrics": {
                        "conversion_rate": "12%",
                        "paid_subscription_rate": "8%"
                    }
                }
            ]
    
    async def _define_features(
        self, 
        idea: str,
        market_analysis: Dict[str, Any],
        competitor_analysis: Dict[str, Any],
        personas: List[Dict[str, Any]],
        similar_mvps: List[Dict[str, Any]]
    ) -> List[Feature]:
        """Define core features for the MVP based on all available data."""
        # In a full implementation, this would use LLM to synthesize data and generate features
        # For now, we'll use a simplified approach
        
        from langchain.llms import OpenAI
        from langchain.prompts import PromptTemplate
        
        # In a full implementation, we would use LLM to analyze all the input data
        # and generate a comprehensive feature list
        
        # For now, create a simplified feature list based on the idea type
        if "app" in idea.lower() or "mobile" in idea.lower():
            features = [
                Feature(
                    name="User Authentication",
                    description="Allow users to create accounts and log in",
                    priority=10,
                    complexity=6,
                    estimated_hours=40,
                    user_value=8
                ),
                Feature(
                    name="Core Functionality",
                    description=f"Primary feature to deliver the main value proposition of {idea}",
                    priority=10,
                    complexity=8,
                    estimated_hours=80,
                    user_value=10
                ),
                Feature(
                    name="User Profile",
                    description="Allow users to customize their profile and preferences",
                    priority=7,
                    complexity=5,
                    estimated_hours=30,
                    user_value=6
                ),
                Feature(
                    name="Basic Analytics",
                    description="Track key user actions and app performance metrics",
                    priority=8,
                    complexity=7,
                    estimated_hours=40,
                    user_value=5
                ),
                Feature(
                    name="Notifications",
                    description="Send relevant notifications to users",
                    priority=6,
                    complexity=6,
                    estimated_hours=30,
                    user_value=7
                )
            ]
        elif "website" in idea.lower() or "web" in idea.lower() or "platform" in idea.lower():
            features = [
                Feature(
                    name="User Registration",
                    description="Allow users to register and manage their accounts",
                    priority=9,
                    complexity=6,
                    estimated_hours=40,
                    user_value=8
                ),
                Feature(
                    name="Core Platform Functionality",
                    description=f"Main feature set that delivers the core value of {idea}",
                    priority=10,
                    complexity=9,
                    estimated_hours=100,
                    user_value=10
                ),
                Feature(
                    name="Search and Discovery",
                    description="Allow users to find relevant content or services",
                    priority=8,
                    complexity=7,
                    estimated_hours=50,
                    user_value=9
                ),
                Feature(
                    name="Basic Dashboard",
                    description="Provide users with an overview of their activity and data",
                    priority=7,
                    complexity=6,
                    estimated_hours=40,
                    user_value=7
                ),
                Feature(
                    name="Integration with Payment Provider",
                    description="Allow users to make payments (if applicable)",
                    priority=8,
                    complexity=8,
                    estimated_hours=60,
                    user_value=9
                )
            ]
        else:
            # Generic features for any type of product
            features = [
                Feature(
                    name="User Account Management",
                    description="Allow users to create and manage their accounts",
                    priority=9,
                    complexity=6,
                    estimated_hours=40,
                    user_value=8
                ),
                Feature(
                    name="Core Value Proposition",
                    description=f"Main functionality that delivers the core value of {idea}",
                    priority=10,
                    complexity=8,
                    estimated_hours=80,
                    user_value=10
                ),
                Feature(
                    name="Basic User Interface",
                    description="Clean and intuitive interface for core functionality",
                    priority=9,
                    complexity=7,
                    estimated_hours=60,
                    user_value=9
                ),
                Feature(
                    name="Data Storage and Retrieval",
                    description="Store and retrieve user data securely",
                    priority=8,
                    complexity=6,
                    estimated_hours=40,
                    user_value=7
                ),
                Feature(
                    name="Feedback Mechanism",
                    description="Allow users to provide feedback on their experience",
                    priority=6,
                    complexity=4,
                    estimated_hours=20,
                    user_value=6
                )
            ]
            
        return features
    
    async def _suggest_tech_stack(
        self, 
        idea: str, 
        features: List[Feature]
    ) -> List[TechStackComponent]:
        """Suggest an appropriate tech stack based on the idea and features."""
        # In a full implementation, this would use LLM to suggest a tech stack
        # For now, we'll use a simplified approach
        
        # Create a basic tech stack for a modern web/mobile application
        tech_stack = [
            TechStackComponent(
                category="Frontend",
                name="React",
                description="JavaScript library for building user interfaces",
                alternatives=["Vue.js", "Angular", "Svelte"],
                learning_curve=7
            ),
            TechStackComponent(
                category="Backend",
                name="Node.js",
                description="JavaScript runtime for server-side applications",
                alternatives=["Python/Django", "Ruby on Rails", "Java Spring"],
                learning_curve=6
            ),
            TechStackComponent(
                category="Database",
                name="MongoDB",
                description="NoSQL database for flexible data storage",
                alternatives=["PostgreSQL", "MySQL", "Firebase Firestore"],
                learning_curve=5
            ),
            TechStackComponent(
                category="Authentication",
                name="Auth0",
                description="Identity platform for authentication and authorization",
                alternatives=["Firebase Auth", "AWS Cognito", "Custom JWT"],
                learning_curve=4
            ),
            TechStackComponent(
                category="Deployment",
                name="AWS",
                description="Cloud platform for hosting and infrastructure",
                alternatives=["Google Cloud", "Microsoft Azure", "Heroku"],
                learning_curve=8
            )
        ]
        
        # For mobile apps, add React Native
        if "app" in idea.lower() or "mobile" in idea.lower():
            tech_stack.append(
                TechStackComponent(
                    category="Mobile Framework",
                    name="React Native",
                    description="Framework for building native mobile apps with React",
                    alternatives=["Flutter", "Swift (iOS)", "Kotlin (Android)"],
                    learning_curve=8
                )
            )
            
        return tech_stack
    
    async def _create_timeline(self, features: List[Feature]) -> Timeline:
        """Create a development timeline based on the features."""
        # In a full implementation, this would use a more sophisticated approach
        # For now, we'll use a simplified calculation based on feature complexity
        
        # Calculate total development hours
        total_hours = sum(feature.estimated_hours for feature in features)
        
        # Assume a team of 2 developers working 30 productive hours per week each
        productive_hours_per_week = 2 * 30
        
        # Calculate number of weeks
        weeks = max(4, round(total_hours / productive_hours_per_week))
        
        # Create phases
        phases = [
            {
                "name": "Planning and Setup",
                "duration_weeks": max(1, round(weeks * 0.1)),
                "description": "Project planning, environment setup, and initial design"
            },
            {
                "name": "Core Development",
                "duration_weeks": max(2, round(weeks * 0.6)),
                "description": "Implementing core features and functionality"
            },
            {
                "name": "Testing and Refinement",
                "duration_weeks": max(1, round(weeks * 0.2)),
                "description": "Testing, bug fixing, and refining the user experience"
            },
            {
                "name": "Deployment and Launch",
                "duration_weeks": max(1, round(weeks * 0.1)),
                "description": "Final preparations, deployment, and product launch"
            }
        ]
        
        # Create milestones
        milestones = [
            {
                "name": "Project Kickoff",
                "week": 1,
                "description": "Team onboarding and project initialization"
            },
            {
                "name": "Design Approval",
                "week": max(2, round(weeks * 0.15)),
                "description": "Finalization and approval of UX/UI design"
            },
            {
                "name": "Alpha Release",
                "week": max(3, round(weeks * 0.5)),
                "description": "Internal testing version with core features implemented"
            },
            {
                "name": "Beta Release",
                "week": max(4, round(weeks * 0.8)),
                "description": "External testing version with most features implemented"
            },
            {
                "name": "MVP Launch",
                "week": weeks,
                "description": "Public release of the minimum viable product"
            }
        ]
        
        return Timeline(
            total_weeks=weeks,
            phases=phases,
            milestones=milestones
        )
    
    async def _estimate_costs(
        self, 
        features: List[Feature],
        tech_stack: List[TechStackComponent],
        timeline: Timeline
    ) -> CostEstimate:
        """Generate cost estimates for the MVP development."""
        # In a full implementation, this would use the cost_estimator_tool
        # For now, we'll use a simplified calculation
        
        if self.cost_estimator_tool:
            cost_data = await self.cost_estimator_tool.estimate(
                features=[f.dict() for f in features],
                tech_stack=[t.dict() for t in tech_stack],
                timeline=timeline.dict()
            )
            return CostEstimate(**cost_data)
        else:
            self.log("Cost estimator tool not available, generating simplified estimate")
            
            # Calculate development cost
            total_hours = sum(feature.estimated_hours for feature in features)
            avg_dev_rate = 75  # USD per hour
            dev_cost = total_hours * avg_dev_rate
            
            # Simplified development costs
            development_costs = {
                "engineering": round(dev_cost * 0.7, 2),
                "design": round(dev_cost * 0.15, 2),
                "project_management": round(dev_cost * 0.1, 2),
                "qa_testing": round(dev_cost * 0.05, 2)
            }
            
            # Simplified infrastructure costs based on tech stack
            monthly_infra_cost = 150  # Base infrastructure cost
            
            # Adjust based on tech stack complexity
            tech_complexity = sum(tech.learning_curve for tech in tech_stack) / len(tech_stack)
            if tech_complexity > 6:
                monthly_infra_cost = 300
            
            # Calculate for 6 months
            infrastructure_costs = {
                "hosting": round(monthly_infra_cost * 6 * 0.4, 2),
                "third_party_services": round(monthly_infra_cost * 6 * 0.3, 2),
                "storage_and_database": round(monthly_infra_cost * 6 * 0.2, 2),
                "cdn_and_network": round(monthly_infra_cost * 6 * 0.1, 2)
            }
            
            # Simplified operational costs
            monthly_ops_cost = 200
            operational_costs = {
                "maintenance": round(monthly_ops_cost * 6 * 0.4, 2),
                "monitoring": round(monthly_ops_cost * 6 * 0.2, 2),
                "updates_and_patches": round(monthly_ops_cost * 6 * 0.2, 2),
                "customer_support": round(monthly_ops_cost * 6 * 0.2, 2)
            }
            
            # Calculate total cost
            total_cost = (
                sum(development_costs.values()) + 
                sum(infrastructure_costs.values()) + 
                sum(operational_costs.values())
            )
            
            return CostEstimate(
                development_cost=development_costs,
                infrastructure_cost=infrastructure_costs,
                operational_cost=operational_costs,
                total_cost=round(total_cost, 2)
            )
    
    async def _identify_assumptions_and_risks(
        self,
        idea: str,
        features: List[Feature],
        tech_stack: List[TechStackComponent]
    ) -> tuple[List[str], List[Dict[str, Any]]]:
        """Identify key assumptions and risks in the MVP plan."""
        # In a full implementation, this would use LLM to generate assumptions and risks
        # For now, we'll return some common assumptions and risks
        
        assumptions = [
            f"Target users will find {idea} valuable enough to sign up and use regularly",
            "The proposed tech stack will be sufficient to handle expected initial user load",
            "Development team has or can quickly acquire the necessary skills for the tech stack",
            "The MVP feature set will demonstrate enough value to validate the core idea",
            "External services and APIs integrated in the MVP will remain stable and available"
        ]
        
        risks = [
            {
                "description": "Development timeline may extend beyond estimates",
                "probability": "Medium",
                "impact": "Medium",
                "mitigation": "Include buffer time in estimates and prioritize features strictly"
            },
            {
                "description": "User adoption may be slower than expected",
                "probability": "Medium",
                "impact": "High",
                "mitigation": "Plan for marketing and user acquisition strategies before launch"
            },
            {
                "description": "Critical technical issues may arise during development",
                "probability": "Medium",
                "impact": "High",
                "mitigation": "Build in time for technical spikes and prototyping of complex features"
            },
            {
                "description": "Competitors may release similar solutions before MVP launch",
                "probability": "Low",
                "impact": "Medium",
                "mitigation": "Monitor market closely and be prepared to adjust positioning"
            },
            {
                "description": "Cost overruns due to unforeseen complications",
                "probability": "Medium",
                "impact": "Medium",
                "mitigation": "Include contingency budget and identify non-essential features that could be cut"
            }
        ]
        
        return assumptions, risks
