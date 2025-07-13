"""
Competitor Analyzer Agent for the MSVA project.
Responsible for finding and analyzing competitors for a startup idea.
"""

import asyncio
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from .base_agent import BaseAgent

class CompetitorFeature(BaseModel):
    """Model to represent a competitor's feature."""
    name: str
    description: str
    strength: int = Field(description="Rating from 1-10 of how strong this feature is")
    
class CompetitorPricing(BaseModel):
    """Model to represent a competitor's pricing model."""
    model_type: str = Field(description="e.g., 'Freemium', 'Subscription', 'One-time purchase'")
    tiers: List[Dict[str, Any]] = Field(description="List of pricing tiers")
    has_free_tier: bool
    
class Competitor(BaseModel):
    """Model to represent a competitor in the market."""
    name: str
    url: str
    description: str
    features: List[CompetitorFeature]
    strengths: List[str]
    weaknesses: List[str]
    pricing: Optional[CompetitorPricing] = None
    market_share: Optional[float] = None
    founded_year: Optional[int] = None
    
class CompetitorAnalyzerAgent(BaseAgent):
    """
    Agent that searches for and analyzes competitors for a startup idea.
    Uses web scraping and RAG tools to gather and compare competitive intelligence.
    """
    
    def __init__(
        self,
        scraper_tool=None,
        rag_tool=None,
        **kwargs
    ):
        super().__init__(
            name="Competitor Analyzer",
            description="Analyzes competitors for startup ideas",
            **kwargs
        )
        self.scraper_tool = scraper_tool
        self.rag_tool = rag_tool
        
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the startup idea to identify and analyze competitors.
        
        Args:
            input_data: Dictionary containing 'idea', possibly 'market_analysis', and other parameters
            
        Returns:
            Dictionary containing competitor analysis results
        """
        idea = input_data.get("idea")
        market_analysis = input_data.get("market_analysis", {})
        
        if not idea:
            return {
                "status": "error",
                "message": "No startup idea provided",
                "data": None
            }
            
        self.log(f"Analyzing competitors for idea: {idea}")
        
        # Step 1: Identify potential competitors
        competitors = await self._identify_competitors(idea, market_analysis)
        
        # Step 2: Scrape data from competitor websites
        competitor_data = await self._scrape_competitor_data(competitors)
        
        # Step 3: Analyze competitors to extract features, strengths, weaknesses
        analyzed_competitors = await self._analyze_competitors(competitor_data)
        
        # Step 4: Compare competitors and identify market gaps
        market_gaps = await self._identify_market_gaps(idea, analyzed_competitors)
        
        # Store the results in memory
        self.add_to_memory({
            "idea": idea,
            "competitors": analyzed_competitors,
            "market_gaps": market_gaps
        })
        
        return {
            "status": "success",
            "message": "Competitor analysis completed successfully",
            "data": {
                "competitors": [comp.dict() for comp in analyzed_competitors],
                "market_gaps": market_gaps,
                "total_competitors_found": len(analyzed_competitors)
            }
        }
    
    async def _identify_competitors(
        self, 
        idea: str, 
        market_analysis: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Identify potential competitors for the startup idea."""
        # In a full implementation, this would use search APIs or the scraper tool
        # For now, we'll simulate finding 2-3 competitors
        
        # In production, this would use LLM to identify competitors based on the idea
        
        from langchain.llms import OpenAI
        from langchain.prompts import PromptTemplate
        
        # Extract search terms from market analysis if available
        search_terms = []
        if market_analysis and "search_terms" in market_analysis:
            search_terms = market_analysis.get("search_terms", [])
        
        prompt = PromptTemplate(
            input_variables=["idea", "search_terms"],
            template="""
            Identify 3 potential competitors for the following startup idea.
            For each competitor, provide their name and website URL.
            
            Startup idea: {idea}
            Related terms: {search_terms}
            
            Return the information in the following format:
            Company 1: [name], [url]
            Company 2: [name], [url]
            Company 3: [name], [url]
            """
        )
        
        # In production, we'd use self.llm which would be properly configured
        llm = OpenAI(model=self.llm_model)
        result = llm.invoke(prompt.format(
            idea=idea, 
            search_terms=", ".join(search_terms) if search_terms else "N/A"
        ))
        
        # Parse the result
        competitors = []
        for line in result.strip().split('\n'):
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    comp_data = parts[1].strip()
                    if ',' in comp_data:
                        name, url = comp_data.split(',', 1)
                        competitors.append({
                            "name": name.strip(),
                            "url": url.strip()
                        })
        
        return competitors
    
    async def _scrape_competitor_data(self, competitors: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Scrape data from competitor websites."""
        # In a full implementation, this would use the scraper_tool
        # For now, we'll simulate the scraped data
        
        competitor_data = []
        
        if self.scraper_tool:
            for competitor in competitors:
                try:
                    scraped_data = await self.scraper_tool.scrape(competitor["url"])
                    competitor_data.append({
                        **competitor,
                        "scraped_data": scraped_data
                    })
                except Exception as e:
                    self.log(f"Error scraping {competitor['url']}: {str(e)}")
                    competitor_data.append({
                        **competitor,
                        "scraped_data": None,
                        "error": str(e)
                    })
        else:
            self.log("Scraper tool not available, returning simulated results")
            # Create some simulated data
            for competitor in competitors:
                competitor_data.append({
                    **competitor,
                    "scraped_data": {
                        "description": f"Simulated description for {competitor['name']}",
                        "features": [
                            "Feature 1: Description of feature 1",
                            "Feature 2: Description of feature 2",
                            "Feature 3: Description of feature 3"
                        ],
                        "pricing": {
                            "model": "Freemium",
                            "tiers": [
                                {"name": "Free", "price": 0, "features": ["Basic feature 1"]},
                                {"name": "Pro", "price": 19.99, "features": ["Advanced feature 1"]}
                            ]
                        }
                    }
                })
                
        return competitor_data
    
    async def _analyze_competitors(self, competitor_data: List[Dict[str, Any]]) -> List[Competitor]:
        """Analyze competitor data to extract structured information."""
        # In a full implementation, this would use LLM to analyze the scraped data
        # For now, we'll create structured objects from the simulated data
        
        analyzed_competitors = []
        
        for comp in competitor_data:
            name = comp["name"]
            url = comp["url"]
            scraped = comp.get("scraped_data", {})
            
            if not scraped:
                continue
                
            # Extract description
            description = scraped.get("description", f"Description for {name}")
            
            # Extract features
            features = []
            for i, feat in enumerate(scraped.get("features", [])):
                if isinstance(feat, str) and ":" in feat:
                    feat_name, feat_desc = feat.split(":", 1)
                    features.append(CompetitorFeature(
                        name=feat_name.strip(),
                        description=feat_desc.strip(),
                        strength=7  # Default value, would be determined by LLM in production
                    ))
            
            # Extract pricing
            pricing_data = scraped.get("pricing", {})
            if pricing_data:
                has_free = any(tier.get("price", 1) == 0 for tier in pricing_data.get("tiers", []))
                pricing = CompetitorPricing(
                    model_type=pricing_data.get("model", "Unknown"),
                    tiers=pricing_data.get("tiers", []),
                    has_free_tier=has_free
                )
            else:
                pricing = None
            
            # In a full implementation, strengths and weaknesses would be derived by LLM
            # For now, we'll use placeholders
            strengths = [f"Simulated strength 1 for {name}", f"Simulated strength 2 for {name}"]
            weaknesses = [f"Simulated weakness 1 for {name}", f"Simulated weakness 2 for {name}"]
            
            # Create the competitor object
            competitor = Competitor(
                name=name,
                url=url,
                description=description,
                features=features,
                strengths=strengths,
                weaknesses=weaknesses,
                pricing=pricing
            )
            
            analyzed_competitors.append(competitor)
            
        return analyzed_competitors
    
    async def _identify_market_gaps(
        self, 
        idea: str, 
        competitors: List[Competitor]
    ) -> Dict[str, Any]:
        """Identify market gaps and opportunities based on competitor analysis."""
        # In a full implementation, this would use LLM to identify gaps
        # For now, we'll use a simplified approach
        
        # Collect all features across competitors
        all_features = []
        for comp in competitors:
            all_features.extend([f.name for f in comp.features])
        
        # Get unique features
        unique_features = list(set(all_features))
        
        # Count how many competitors have each feature
        feature_counts = {feat: 0 for feat in unique_features}
        for comp in competitors:
            for f in comp.features:
                if f.name in feature_counts:
                    feature_counts[f.name] += 1
        
        # Find potential gaps (features that are rare among competitors)
        potential_gaps = [
            f for f, count in feature_counts.items() 
            if count < len(competitors) / 2
        ]
        
        # In a full implementation, we would use LLM to analyze these gaps and generate insights
        
        return {
            "common_features": [f for f, c in feature_counts.items() if c >= len(competitors) / 2],
            "potential_gaps": potential_gaps,
            "pricing_insights": "Most competitors use a freemium model" if any(
                c.pricing and c.pricing.has_free_tier for c in competitors if c.pricing
            ) else "No clear pricing pattern detected",
            "differentiation_opportunities": [
                "This would be generated by an LLM based on the gaps analysis",
                "Second differentiation opportunity would go here"
            ]
        }
