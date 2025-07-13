"""
Web Search Tool for the MSVA project.
Provides search capabilities using either Serper or SerpApi.
"""

import os
import json
import aiohttp
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from .base_tool import BaseTool

class WebSearchTool(BaseTool):
    """
    Tool for performing web searches using either Serper or SerpApi.
    Provides real-time market and competitor information.
    """
    
    def __init__(
        self, 
        search_engine: str = "serper",  # "serper" or "serpapi"
        max_results: int = 10,
        verbose: bool = False
    ):
        super().__init__(
            name="Web Search Tool",
            description="Performs web searches to find market trends and competitor information",
            verbose=verbose
        )
        self.search_engine = search_engine.lower()
        self.max_results = max_results
        
        # Load environment variables
        load_dotenv()
        
        # Get API keys based on the selected search engine
        if self.search_engine == "serper":
            self.api_key = os.getenv("SERPER_API_KEY")
            if not self.api_key:
                raise ValueError("SERPER_API_KEY not found in environment variables")
        elif self.search_engine == "serpapi":
            self.api_key = os.getenv("SERPAPI_API_KEY")
            if not self.api_key:
                raise ValueError("SERPAPI_API_KEY not found in environment variables")
        else:
            raise ValueError(f"Unsupported search engine: {search_engine}")
            
    async def run(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Run a web search for the given query.
        
        Args:
            query: The search query
            **kwargs: Additional parameters for the search API
            
        Returns:
            Dictionary containing search results
        """
        self.log(f"Searching for: {query}")
        
        if self.search_engine == "serper":
            return await self._search_with_serper(query, **kwargs)
        elif self.search_engine == "serpapi":
            return await self._search_with_serpapi(query, **kwargs)
        else:
            raise ValueError(f"Unsupported search engine: {self.search_engine}")
    
    async def _search_with_serper(self, query: str, **kwargs) -> Dict[str, Any]:
        """Perform a search using Serper API."""
        url = "https://google.serper.dev/search"
        
        # Prepare the payload
        payload = {
            "q": query,
            "gl": kwargs.get("country", "us"),
            "num": min(self.max_results, 100)
        }
        
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return self._format_serper_results(result)
                    else:
                        error_text = await response.text()
                        self.log(f"Error from Serper API: {error_text}")
                        return {
                            "status": "error",
                            "message": f"Search failed with status code: {response.status}",
                            "error": error_text
                        }
        except Exception as e:
            self.log(f"Exception during Serper search: {str(e)}")
            return {
                "status": "error",
                "message": "Search failed due to an exception",
                "error": str(e)
            }
    
    async def _search_with_serpapi(self, query: str, **kwargs) -> Dict[str, Any]:
        """Perform a search using SerpAPI."""
        url = "https://serpapi.com/search"
        
        # Prepare the parameters
        params = {
            "q": query,
            "api_key": self.api_key,
            "engine": "google",
            "gl": kwargs.get("country", "us"),
            "num": min(self.max_results, 100),
            "output": "json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        return self._format_serpapi_results(result)
                    else:
                        error_text = await response.text()
                        self.log(f"Error from SerpAPI: {error_text}")
                        return {
                            "status": "error",
                            "message": f"Search failed with status code: {response.status}",
                            "error": error_text
                        }
        except Exception as e:
            self.log(f"Exception during SerpAPI search: {str(e)}")
            return {
                "status": "error",
                "message": "Search failed due to an exception",
                "error": str(e)
            }
    
    def _format_serper_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """Format Serper API results into a standardized format."""
        formatted_results = {
            "status": "success",
            "query": raw_results.get("searchParameters", {}).get("q", ""),
            "organic": [],
            "knowledge_graph": {},
            "related_searches": []
        }
        
        # Extract organic search results
        if "organic" in raw_results:
            for result in raw_results["organic"]:
                formatted_results["organic"].append({
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "position": result.get("position", 0),
                    "source": "serper"
                })
                
        # Extract knowledge graph if available
        if "knowledgeGraph" in raw_results:
            kg = raw_results["knowledgeGraph"]
            formatted_results["knowledge_graph"] = {
                "title": kg.get("title", ""),
                "type": kg.get("type", ""),
                "description": kg.get("description", ""),
                "attributes": kg.get("attributes", {}),
                "source": "serper"
            }
            
        # Extract related searches
        if "relatedSearches" in raw_results:
            formatted_results["related_searches"] = raw_results["relatedSearches"]
            
        return formatted_results
    
    def _format_serpapi_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """Format SerpAPI results into a standardized format."""
        formatted_results = {
            "status": "success",
            "query": raw_results.get("search_parameters", {}).get("q", ""),
            "organic": [],
            "knowledge_graph": {},
            "related_searches": []
        }
        
        # Extract organic search results
        if "organic_results" in raw_results:
            for result in raw_results["organic_results"]:
                formatted_results["organic"].append({
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "position": result.get("position", 0),
                    "source": "serpapi"
                })
                
        # Extract knowledge graph if available
        if "knowledge_graph" in raw_results:
            kg = raw_results["knowledge_graph"]
            formatted_results["knowledge_graph"] = {
                "title": kg.get("title", ""),
                "type": kg.get("type", ""),
                "description": kg.get("description", ""),
                "attributes": kg.get("attributes", {}),
                "source": "serpapi"
            }
            
        # Extract related searches
        if "related_searches" in raw_results:
            related = []
            for item in raw_results["related_searches"]:
                related.append(item.get("query", ""))
            formatted_results["related_searches"] = related
            
        return formatted_results
        
    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Alias for run method to provide a more intuitive API.
        
        Args:
            query: The search query
            **kwargs: Additional parameters for the search API
            
        Returns:
            Dictionary containing search results
        """
        return await self.run(query=query, **kwargs)
