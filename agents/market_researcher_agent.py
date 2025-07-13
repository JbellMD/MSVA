"""
Market Researcher Agent for the MSVA project.
Responsible for analyzing market trends and interest for a startup idea.
"""

import asyncio
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from .base_agent import BaseAgent

class MarketTrend(BaseModel):
    """Model to represent market trend data."""
    keyword: str
    interest_level: float  # 0-100 scale
    growth_rate: float  # Negative for declining, positive for growing
    related_topics: List[str]
    source: str

class MarketResearcherAgent(BaseAgent):
    """
    Agent that conducts web search and trend analysis on startup ideas.
    Uses web search tools and trend analyzers to gather market intelligence.
    """
    
    def __init__(
        self,
        search_tool=None,
        trend_analyzer_tool=None,
        **kwargs
    ):
        super().__init__(
            name="Market Researcher",
            description="Analyzes market trends and interest for startup ideas",
            **kwargs
        )
        self.search_tool = search_tool
        self.trend_analyzer_tool = trend_analyzer_tool
        
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the startup idea to produce market research insights.
        
        Args:
            input_data: Dictionary containing 'idea' and other optional parameters
            
        Returns:
            Dictionary containing market research results
        """
        idea = input_data.get("idea")
        if not idea:
            return {
                "status": "error",
                "message": "No startup idea provided",
                "data": None
            }
            
        self.log(f"Researching market for idea: {idea}")
        
        # Step 1: Extract key search terms from the idea
        search_terms = await self._extract_search_terms(idea)
        
        # Step 2: Perform web searches on these terms
        search_results = await self._perform_searches(search_terms)
        
        # Step 3: Analyze market trends for these terms
        trend_results = await self._analyze_trends(search_terms)
        
        # Step 4: Synthesize findings into a coherent market analysis
        market_analysis = await self._synthesize_analysis(
            idea, 
            search_results, 
            trend_results
        )
        
        # Store the results in memory
        self.add_to_memory({
            "idea": idea,
            "search_terms": search_terms,
            "market_analysis": market_analysis
        })
        
        return {
            "status": "success",
            "message": "Market research completed successfully",
            "data": {
                "market_analysis": market_analysis,
                "trend_data": trend_results,
                "search_summary": search_results.get("summary")
            }
        }
    
    async def _extract_search_terms(self, idea: str) -> List[str]:
        """Extract key search terms from the startup idea."""
        # In a full implementation, this would use LLM to extract terms
        # For now, we'll use a simplified approach
        
        from langchain.llms import OpenAI
        from langchain.prompts import PromptTemplate
        
        prompt = PromptTemplate(
            input_variables=["idea"],
            template="""
            Extract 5-7 key search terms that would be most relevant for 
            researching market trends related to this startup idea:
            
            Startup idea: {idea}
            
            Return only the search terms, one per line.
            """
        )
        
        # In production, we'd use self.llm which would be properly configured
        llm = OpenAI(model=self.llm_model)
        result = llm.invoke(prompt.format(idea=idea))
        
        # Parse the result into a list of search terms
        search_terms = [term.strip() for term in result.strip().split('\n') if term.strip()]
        
        return search_terms
    
    async def _perform_searches(self, search_terms: List[str]) -> Dict[str, Any]:
        """Perform web searches on the extracted terms."""
        # In a full implementation, this would use the search_tool
        # For now, we'll simulate the results
        
        if self.search_tool:
            all_results = []
            for term in search_terms:
                results = await self.search_tool.search(term)
                all_results.append({
                    "term": term,
                    "results": results
                })
                
            # Use LLM to summarize the search results
            summary = "Summary of market search results would go here"
            
            return {
                "raw_results": all_results,
                "summary": summary
            }
        else:
            self.log("Search tool not available, returning simulated results")
            return {
                "raw_results": [],
                "summary": f"Simulated search results for terms: {', '.join(search_terms)}"
            }
    
    async def _analyze_trends(self, search_terms: List[str]) -> List[MarketTrend]:
        """Analyze market trends for the search terms."""
        # In a full implementation, this would use the trend_analyzer_tool
        # For now, we'll simulate the results
        
        if self.trend_analyzer_tool:
            trends = []
            for term in search_terms:
                trend_data = await self.trend_analyzer_tool.analyze_trend(term)
                trends.append(MarketTrend(
                    keyword=term,
                    interest_level=trend_data.get("interest_level", 0),
                    growth_rate=trend_data.get("growth_rate", 0),
                    related_topics=trend_data.get("related_topics", []),
                    source=trend_data.get("source", "simulated")
                ))
            return trends
        else:
            self.log("Trend analyzer tool not available, returning simulated results")
            import random
            
            # Return simulated trend data
            return [
                MarketTrend(
                    keyword=term,
                    interest_level=random.uniform(30, 90),
                    growth_rate=random.uniform(-0.2, 0.5),
                    related_topics=["topic1", "topic2", "topic3"],
                    source="simulated"
                )
                for term in search_terms
            ]
    
    async def _synthesize_analysis(
        self, 
        idea: str, 
        search_results: Dict[str, Any], 
        trend_results: List[MarketTrend]
    ) -> Dict[str, Any]:
        """Synthesize search and trend data into a coherent market analysis."""
        # In a full implementation, this would use LLM to create a coherent analysis
        # For now, we'll return a structured template
        
        # Calculate an overall market interest score (0-100)
        if trend_results:
            avg_interest = sum(t.interest_level for t in trend_results) / len(trend_results)
            avg_growth = sum(t.growth_rate for t in trend_results) / len(trend_results)
        else:
            avg_interest = 50  # Default moderate interest
            avg_growth = 0.1   # Default slight growth
        
        # Determine market direction
        if avg_growth > 0.2:
            direction = "Rapidly growing"
        elif avg_growth > 0:
            direction = "Growing"
        elif avg_growth > -0.1:
            direction = "Stable"
        else:
            direction = "Declining"
            
        # In a full implementation, we would use an LLM to generate insights and recommendations
        
        return {
            "idea_summary": f"Market analysis for: {idea}",
            "market_interest_score": round(avg_interest, 1),
            "market_direction": direction,
            "growth_rate": round(avg_growth * 100, 1),  # Convert to percentage
            "key_insights": [
                "This would be generated by an LLM based on the search and trend data",
                "Second insight would go here",
                "Third insight would go here"
            ],
            "recommendations": [
                "This would be generated by an LLM based on the data analysis",
                "Second recommendation would go here"
            ]
        }
