"""
Customer Persona Generator Agent for the MSVA project.
Responsible for creating detailed user personas for a startup idea.
"""

import asyncio
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from .base_agent import BaseAgent

class UserNeed(BaseModel):
    """Model representing a specific user need or pain point."""
    description: str
    severity: int = Field(description="Rating from 1-10 of how severe this pain point is")
    current_solutions: List[str] = Field(description="How users currently solve this problem")
    
class UserBehavior(BaseModel):
    """Model representing a user behavior pattern."""
    context: str = Field(description="When/where this behavior occurs")
    frequency: str = Field(description="How often this behavior occurs")
    motivation: str = Field(description="Why the user engages in this behavior")
    friction_points: List[str] = Field(description="What makes this behavior difficult")
    
class CustomerPersona(BaseModel):
    """Model representing a customer persona."""
    name: str
    age: int
    occupation: str
    demographic_info: Dict[str, Any] = Field(description="Key demographic information")
    goals: List[str] = Field(description="Primary goals related to the product domain")
    needs: List[UserNeed] = Field(description="Specific needs and pain points")
    behaviors: List[UserBehavior] = Field(description="Relevant behavior patterns")
    tech_proficiency: int = Field(description="Rating from 1-10 of technical proficiency")
    buying_power: int = Field(description="Rating from 1-10 of purchasing capacity")
    quote: str = Field(description="Representative quote from this persona")
    
class CustomerPersonaGeneratorAgent(BaseAgent):
    """
    Agent that builds user personas and hypothesizes user needs for a startup idea.
    Uses demographic data and custom prompt templates to create realistic personas.
    """
    
    def __init__(
        self,
        demographic_tool=None,
        persona_synthesizer_tool=None,
        **kwargs
    ):
        super().__init__(
            name="Customer Persona Generator",
            description="Creates detailed user personas for startup ideas",
            **kwargs
        )
        self.demographic_tool = demographic_tool
        self.persona_synthesizer_tool = persona_synthesizer_tool
        
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the startup idea to generate detailed customer personas.
        
        Args:
            input_data: Dictionary containing 'idea', possibly 'market_analysis',
                       'competitor_analysis' and other parameters
            
        Returns:
            Dictionary containing generated personas and insights
        """
        idea = input_data.get("idea")
        market_analysis = input_data.get("market_analysis", {})
        competitor_analysis = input_data.get("competitor_analysis", {})
        
        if not idea:
            return {
                "status": "error",
                "message": "No startup idea provided",
                "data": None
            }
            
        self.log(f"Generating customer personas for idea: {idea}")
        
        # Step 1: Extract target audience characteristics from the idea and market analysis
        audience_characteristics = await self._extract_audience_characteristics(
            idea, 
            market_analysis
        )
        
        # Step 2: Get demographic data for the target audience if the tool is available
        demographic_data = await self._get_demographic_data(audience_characteristics)
        
        # Step 3: Generate personas based on the audience characteristics and demographic data
        personas = await self._generate_personas(
            idea, 
            audience_characteristics, 
            demographic_data, 
            competitor_analysis
        )
        
        # Step 4: Validate and refine the personas
        refined_personas = await self._refine_personas(
            idea, 
            personas, 
            competitor_analysis
        )
        
        # Store the results in memory
        self.add_to_memory({
            "idea": idea,
            "personas": refined_personas
        })
        
        return {
            "status": "success",
            "message": "Customer personas generated successfully",
            "data": {
                "personas": [persona.dict() for persona in refined_personas],
                "audience_characteristics": audience_characteristics
            }
        }
    
    async def _extract_audience_characteristics(
        self, 
        idea: str, 
        market_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract target audience characteristics from the idea and market analysis."""
        # In a full implementation, this would use LLM to extract characteristics
        # For now, we'll use a simplified approach
        
        from langchain.llms import OpenAI
        from langchain.prompts import PromptTemplate
        
        prompt = PromptTemplate(
            input_variables=["idea", "market_analysis"],
            template="""
            Based on the following startup idea and market analysis, identify key characteristics 
            of the target audience. Consider demographics, psychographics, behaviors, and needs.
            
            Startup idea: {idea}
            Market analysis: {market_analysis}
            
            Return the audience characteristics in the following format:
            Demographics: [key demographic traits]
            Psychographics: [key psychographic traits]
            Behaviors: [key behaviors]
            Needs: [key needs and pain points]
            """
        )
        
        # In production, we'd use self.llm which would be properly configured
        llm = OpenAI(model=self.llm_model)
        
        # Convert market_analysis to a string representation
        market_str = str(market_analysis)
        
        result = llm.invoke(prompt.format(
            idea=idea, 
            market_analysis=market_str
        ))
        
        # Parse the result into structured data
        characteristics = {}
        current_key = None
        
        for line in result.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                if key in ['demographics', 'psychographics', 'behaviors', 'needs']:
                    current_key = key
                    characteristics[current_key] = [item.strip() for item in value.strip().split(',')]
            elif current_key and line.strip():
                # Continuation of previous section
                characteristics[current_key].extend([item.strip() for item in line.strip().split(',')])
        
        return characteristics
    
    async def _get_demographic_data(self, audience_characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """Get demographic data for the target audience."""
        # In a full implementation, this would use the demographic_tool
        # For now, we'll simulate the data
        
        if self.demographic_tool:
            demographics = audience_characteristics.get("demographics", [])
            demo_data = await self.demographic_tool.get_data(demographics)
            return demo_data
        else:
            self.log("Demographic tool not available, returning simulated results")
            return {
                "age_distribution": {
                    "18-24": 15,
                    "25-34": 35,
                    "35-44": 25,
                    "45-54": 15,
                    "55+": 10
                },
                "gender_distribution": {
                    "male": 55,
                    "female": 43,
                    "other": 2
                },
                "income_levels": {
                    "low": 20,
                    "medium": 50,
                    "high": 30
                },
                "education_levels": {
                    "high_school": 15,
                    "bachelors": 45,
                    "masters": 30,
                    "phd": 10
                },
                "geographic_distribution": {
                    "urban": 65,
                    "suburban": 25,
                    "rural": 10
                }
            }
    
    async def _generate_personas(
        self, 
        idea: str,
        audience_characteristics: Dict[str, Any],
        demographic_data: Dict[str, Any],
        competitor_analysis: Dict[str, Any]
    ) -> List[CustomerPersona]:
        """Generate personas based on the audience characteristics and demographic data."""
        # In a full implementation, this would use LLM to generate detailed personas
        # For now, we'll use a simplified approach
        
        # Generate 2-3 personas
        personas = []
        
        # In production, we would use the persona_synthesizer_tool if available
        if self.persona_synthesizer_tool:
            raw_personas = await self.persona_synthesizer_tool.generate(
                idea=idea,
                audience=audience_characteristics,
                demographics=demographic_data,
                competitors=competitor_analysis
            )
            
            # Convert raw personas to CustomerPersona objects
            for p in raw_personas:
                personas.append(CustomerPersona(**p))
        else:
            # Create simulated personas
            # This would typically be done with an LLM in production
            
            # Persona 1: Primary user
            primary_needs = [
                UserNeed(
                    description="Need to quickly validate business ideas without extensive research",
                    severity=8,
                    current_solutions=["Manual research", "Hiring consultants", "Guesswork"]
                ),
                UserNeed(
                    description="Need for market insights without high costs",
                    severity=7,
                    current_solutions=["Free online resources", "Limited paid tools"]
                )
            ]
            
            primary_behaviors = [
                UserBehavior(
                    context="When starting a new business venture",
                    frequency="Every few months",
                    motivation="To minimize risk and maximize chances of success",
                    friction_points=["Cost of research tools", "Time required", "Uncertainty of results"]
                )
            ]
            
            primary = CustomerPersona(
                name="Alex Rivera",
                age=32,
                occupation="Serial Entrepreneur",
                demographic_info={
                    "location": "Urban center",
                    "education": "Bachelor's in Business",
                    "income": "Medium-high"
                },
                goals=[
                    "Launch successful startups with minimal wasted resources",
                    "Identify profitable market opportunities quickly",
                    "Stay ahead of market trends"
                ],
                needs=primary_needs,
                behaviors=primary_behaviors,
                tech_proficiency=8,
                buying_power=7,
                quote="I need to know if my idea has legs before I invest serious time and money."
            )
            personas.append(primary)
            
            # Persona 2: Secondary user
            secondary_needs = [
                UserNeed(
                    description="Need for structured approach to evaluate startup ideas",
                    severity=9,
                    current_solutions=["Spreadsheets", "General business frameworks"]
                ),
                UserNeed(
                    description="Need to understand potential customer base clearly",
                    severity=8,
                    current_solutions=["Social media research", "Informal surveys"]
                )
            ]
            
            secondary_behaviors = [
                UserBehavior(
                    context="When advising startup teams",
                    frequency="Weekly",
                    motivation="To provide data-backed guidance to founders",
                    friction_points=["Lack of standardized tools", "Fragmented information sources"]
                )
            ]
            
            secondary = CustomerPersona(
                name="Maya Johnson",
                age=41,
                occupation="Business Incubator Manager",
                demographic_info={
                    "location": "Suburban area near tech hub",
                    "education": "MBA",
                    "income": "High"
                },
                goals=[
                    "Help founders make data-driven decisions",
                    "Increase success rate of incubated startups",
                    "Efficiently allocate resources to promising ventures"
                ],
                needs=secondary_needs,
                behaviors=secondary_behaviors,
                tech_proficiency=7,
                buying_power=9,
                quote="Most founders have passion but lack the structured approach to validate their ideas properly."
            )
            personas.append(secondary)
        
        return personas
    
    async def _refine_personas(
        self, 
        idea: str, 
        personas: List[CustomerPersona],
        competitor_analysis: Dict[str, Any]
    ) -> List[CustomerPersona]:
        """Validate and refine the generated personas."""
        # In a full implementation, this would use LLM to refine the personas
        # For now, we'll return the personas as is
        
        # Here we would typically:
        # 1. Check if personas are diverse enough
        # 2. Ensure personas align with the startup idea
        # 3. Validate that personas have different needs and goals
        # 4. Make sure personas would realistically use the proposed solution
        
        return personas
