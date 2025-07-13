"""
Web Scraper Tool for the MSVA project.
Extracts information from websites using Playwright or BeautifulSoup.
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional, Union
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from .base_tool import BaseTool

class WebScraperTool(BaseTool):
    """
    Tool for scraping websites to extract information about competitors.
    Can extract text content, metadata, pricing information, and features.
    """
    
    def __init__(
        self, 
        use_playwright: bool = False,  # If True, use Playwright for JS-rendered sites
        max_pages: int = 5,           # Maximum number of pages to crawl per domain
        max_depth: int = 2,           # Maximum crawl depth
        verbose: bool = False
    ):
        super().__init__(
            name="Web Scraper Tool",
            description="Extracts information from websites using various scraping techniques",
            verbose=verbose
        )
        self.use_playwright = use_playwright
        self.max_pages = max_pages
        self.max_depth = max_depth
        self._visited_urls = set()
        
    async def run(
        self, 
        url: str, 
        scrape_type: str = "general",  # "general", "pricing", "features", "about"
        **kwargs
    ) -> Dict[str, Any]:
        """
        Scrape information from a website.
        
        Args:
            url: URL to scrape
            scrape_type: Type of information to focus on
            **kwargs: Additional parameters for customizing the scraping behavior
            
        Returns:
            Dictionary containing scraped data
        """
        self.log(f"Scraping {url} for {scrape_type} information")
        
        # Reset visited URLs for new scraping session
        self._visited_urls = set()
        
        # Normalize URL
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
            
        # Parse the URL to get the domain for scoping the crawl
        parsed_url = urlparse(url)
        base_domain = parsed_url.netloc
        
        try:
            # Choose scraping method based on configuration
            if self.use_playwright:
                result = await self._scrape_with_playwright(url, scrape_type, base_domain, **kwargs)
            else:
                result = await self._scrape_with_beautifulsoup(url, scrape_type, base_domain, **kwargs)
                
            return result
        except Exception as e:
            self.log(f"Error scraping {url}: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to scrape {url}",
                "error": str(e),
                "url": url
            }
    
    async def _scrape_with_beautifulsoup(
        self, 
        url: str, 
        scrape_type: str,
        base_domain: str,
        depth: int = 0,
        **kwargs
    ) -> Dict[str, Any]:
        """Scrape a website using BeautifulSoup."""
        # Check if we've already visited this URL or reached max depth
        if url in self._visited_urls or depth >= self.max_depth:
            return {}
            
        # Check if we've reached the maximum number of pages
        if len(self._visited_urls) >= self.max_pages:
            return {}
            
        # Add URL to visited set
        self._visited_urls.add(url)
        
        # Fetch the page content
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        self.log(f"Failed to fetch {url}, status code: {response.status}")
                        return {
                            "status": "error",
                            "message": f"Failed to fetch {url}",
                            "error": f"Status code: {response.status}",
                            "url": url
                        }
                        
                    html = await response.text()
                    
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract data based on the scrape type
            result = {
                "status": "success",
                "url": url,
                "title": self._extract_title(soup),
                "meta_description": self._extract_meta_description(soup)
            }
            
            if scrape_type == "general" or scrape_type == "about":
                result["main_content"] = self._extract_main_content(soup)
                result["company_info"] = self._extract_company_info(soup)
                
            if scrape_type == "general" or scrape_type == "pricing":
                result["pricing"] = self._extract_pricing_info(soup)
                
            if scrape_type == "general" or scrape_type == "features":
                result["features"] = self._extract_features(soup)
                
            # Find links for further crawling if depth allows
            if depth < self.max_depth and len(self._visited_urls) < self.max_pages:
                links = self._extract_internal_links(soup, base_domain, url)
                
                # Filter links based on scrape type to prioritize relevant pages
                filtered_links = self._filter_links_by_scrape_type(links, scrape_type)
                
                # Limit the number of links to avoid too many requests
                filtered_links = filtered_links[:min(3, self.max_pages - len(self._visited_urls))]
                
                # Recursively scrape linked pages
                sub_results = {}
                for link in filtered_links:
                    sub_result = await self._scrape_with_beautifulsoup(
                        link, 
                        scrape_type, 
                        base_domain,
                        depth + 1, 
                        **kwargs
                    )
                    if sub_result and "status" in sub_result and sub_result["status"] == "success":
                        page_type = self._infer_page_type(link)
                        sub_results[page_type] = sub_result
                        
                if sub_results:
                    result["related_pages"] = sub_results
                
            return result
            
        except Exception as e:
            self.log(f"Error scraping {url} with BeautifulSoup: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to scrape {url}",
                "error": str(e),
                "url": url
            }
    
    async def _scrape_with_playwright(
        self, 
        url: str, 
        scrape_type: str,
        base_domain: str,
        depth: int = 0, 
        **kwargs
    ) -> Dict[str, Any]:
        """
        Scrape a website using Playwright.
        Note: This is a placeholder for the Playwright implementation.
        In a production setting, you would implement this using Playwright.
        """
        try:
            # In a real implementation, you would use Playwright here
            # For now, we'll fall back to BeautifulSoup with a warning
            self.log("Playwright support not fully implemented, falling back to BeautifulSoup")
            return await self._scrape_with_beautifulsoup(url, scrape_type, base_domain, depth, **kwargs)
            
        except Exception as e:
            self.log(f"Error scraping {url} with Playwright: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to scrape {url} with Playwright",
                "error": str(e),
                "url": url
            }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract the title of the page."""
        title_tag = soup.find('title')
        return title_tag.text.strip() if title_tag else ""
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract the meta description of the page."""
        meta_desc = soup.find('meta', attrs={"name": "description"})
        return meta_desc["content"].strip() if meta_desc and "content" in meta_desc.attrs else ""
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract the main content of the page."""
        # Try to find the main content using common patterns
        main_content = ""
        
        # Look for main content containers
        content_elements = []
        for selector in ['main', 'article', '#content', '.content', '#main', '.main']:
            elements = soup.select(selector)
            if elements:
                content_elements.extend(elements)
                
        # If no specific content containers found, use the body
        if not content_elements:
            content_elements = [soup.find('body')]
            
        # Extract text from content elements, excluding scripts, styles, etc.
        for element in content_elements:
            if element:
                # Remove unwanted elements
                for unwanted in element.find_all(['script', 'style', 'nav', 'header', 'footer']):
                    unwanted.extract()
                    
                # Get text and clean it up
                text = element.get_text(separator=' ', strip=True)
                main_content += text + "\n\n"
                
        return main_content.strip()
    
    def _extract_company_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract information about the company."""
        company_info = {}
        
        # Try to find company name
        company_name_elements = soup.select('.company-name, .logo, .brand')
        if company_name_elements:
            company_info["name"] = company_name_elements[0].get_text(strip=True)
            
        # Try to find about information
        about_elements = []
        for selector in ['#about', '.about', 'section[id*="about"], div[id*="about"]',
                         'section[class*="about"], div[class*="about"]']:
            elements = soup.select(selector)
            if elements:
                about_elements.extend(elements)
                
        if about_elements:
            about_text = []
            for element in about_elements:
                about_text.append(element.get_text(separator=' ', strip=True))
            company_info["about"] = "\n\n".join(about_text)
            
        # Try to find contact information
        contact_elements = []
        for selector in ['#contact', '.contact', 'section[id*="contact"], div[id*="contact"]',
                        'section[class*="contact"], div[class*="contact"]']:
            elements = soup.select(selector)
            if elements:
                contact_elements.extend(elements)
                
        if contact_elements:
            contact_text = []
            for element in contact_elements:
                contact_text.append(element.get_text(separator=' ', strip=True))
            company_info["contact"] = "\n\n".join(contact_text)
            
        return company_info
    
    def _extract_pricing_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract pricing information from the page."""
        pricing_info = {
            "model": "",
            "has_free_tier": False,
            "tiers": []
        }
        
        # Look for pricing section
        pricing_elements = []
        for selector in ['#pricing', '.pricing', 'section[id*="pricing"], div[id*="pricing"]',
                         'section[class*="pricing"], div[class*="pricing"]',
                         'section[id*="plan"], div[id*="plan"]',
                         'section[class*="plan"], div[class*="plan"]']:
            elements = soup.select(selector)
            if elements:
                pricing_elements.extend(elements)
                
        if not pricing_elements:
            return pricing_info
            
        # Try to determine pricing model
        pricing_text = " ".join([el.get_text(separator=' ', strip=True).lower() for el in pricing_elements])
        
        if "free" in pricing_text:
            pricing_info["has_free_tier"] = True
            
        if "subscription" in pricing_text or "monthly" in pricing_text or "yearly" in pricing_text:
            pricing_info["model"] = "Subscription"
        elif "one-time" in pricing_text or "lifetime" in pricing_text:
            pricing_info["model"] = "One-time purchase"
        elif "freemium" in pricing_text:
            pricing_info["model"] = "Freemium"
        elif pricing_info["has_free_tier"]:
            pricing_info["model"] = "Freemium"
        else:
            pricing_info["model"] = "Unknown"
            
        # Try to extract pricing tiers
        tier_elements = []
        for pricing_element in pricing_elements:
            # Look for pricing cards/tiers
            for selector in ['.pricing-card', '.pricing-tier', '.pricing-plan',
                            '.card', '.tier', '.plan', '.price-card', '.price-box']:
                elements = pricing_element.select(selector)
                if elements:
                    tier_elements.extend(elements)
                    
        # If no specific tier elements found, try to infer from structure
        if not tier_elements and pricing_elements:
            # Use direct children of the pricing section as potential tiers
            parent = pricing_elements[0]
            children = parent.find_all(recursive=False)
            if len(children) >= 2:  # At least two children might be different tiers
                tier_elements = children
                
        # Extract information from tier elements
        for i, tier_element in enumerate(tier_elements[:4]):  # Limit to 4 tiers
            tier = {
                "name": "",
                "price": "",
                "features": []
            }
            
            # Try to extract tier name
            name_elements = tier_element.select('h2, h3, h4, .title, .name')
            if name_elements:
                tier["name"] = name_elements[0].get_text(strip=True)
            else:
                tier["name"] = f"Tier {i+1}"
                
            # Try to extract price
            price_elements = tier_element.select('.price, .cost, [class*="price"], [class*="cost"]')
            if price_elements:
                price_text = price_elements[0].get_text(strip=True)
                tier["price"] = price_text
                if "free" in price_text.lower() or "$0" in price_text:
                    pricing_info["has_free_tier"] = True
            
            # Try to extract features
            feature_elements = tier_element.select('ul li, .feature, .benefit')
            if feature_elements:
                for feature in feature_elements:
                    feature_text = feature.get_text(strip=True)
                    if feature_text:
                        tier["features"].append(feature_text)
                        
            pricing_info["tiers"].append(tier)
            
        return pricing_info
    
    def _extract_features(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract product features from the page."""
        features = []
        
        # Look for features section
        feature_sections = []
        for selector in ['#features', '.features', 'section[id*="feature"], div[id*="feature"]',
                        'section[class*="feature"], div[class*="feature"]']:
            elements = soup.select(selector)
            if elements:
                feature_sections.extend(elements)
                
        if not feature_sections:
            return features
            
        # Extract features from feature sections
        for section in feature_sections:
            # Look for feature cards/items
            feature_elements = []
            for selector in ['.feature-card', '.feature-item', '.feature',
                           '.card', '.item', '[class*="feature-"]']:
                elements = section.select(selector)
                if elements:
                    feature_elements.extend(elements)
                    
            # If no specific feature elements found, try headings and paragraphs
            if not feature_elements:
                headings = section.select('h2, h3, h4')
                for heading in headings:
                    feature_elements.append(heading.parent)
                    
            # Extract information from feature elements
            for element in feature_elements:
                feature = {
                    "name": "",
                    "description": ""
                }
                
                # Try to extract feature name
                name_elements = element.select('h2, h3, h4, h5, .title, .name, strong')
                if name_elements:
                    feature["name"] = name_elements[0].get_text(strip=True)
                    
                # If no name found, skip this feature
                if not feature["name"]:
                    continue
                    
                # Try to extract feature description
                desc_elements = element.select('p, .description, .desc')
                if desc_elements:
                    feature["description"] = desc_elements[0].get_text(strip=True)
                    
                features.append(feature)
                
        return features
    
    def _extract_internal_links(self, soup: BeautifulSoup, base_domain: str, current_url: str) -> List[str]:
        """Extract internal links from the page."""
        links = []
        
        # Find all anchor tags
        for a in soup.find_all('a', href=True):
            href = a['href']
            
            # Skip empty links, fragment links, and non-HTTP links
            if not href or href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                continue
                
            # Convert relative URLs to absolute
            if not href.startswith(('http://', 'https://')):
                href = urljoin(current_url, href)
                
            # Parse the URL
            parsed_href = urlparse(href)
            
            # Only include links to the same domain
            if parsed_href.netloc == base_domain and href not in self._visited_urls:
                links.append(href)
                
        return links
    
    def _filter_links_by_scrape_type(self, links: List[str], scrape_type: str) -> List[str]:
        """Filter links based on the scrape type to prioritize relevant pages."""
        if scrape_type == "general":
            return links
            
        filtered_links = []
        relevant_terms = {
            "pricing": ["pricing", "plans", "subscription", "cost", "buy"],
            "features": ["features", "product", "capabilities", "tour", "overview"],
            "about": ["about", "company", "team", "mission", "vision", "history"]
        }.get(scrape_type, [])
        
        # Filter links that might be relevant to the scrape type
        for link in links:
            link_lower = link.lower()
            for term in relevant_terms:
                if term in link_lower:
                    filtered_links.append(link)
                    break
                    
        # If no relevant links found, fall back to original links
        return filtered_links if filtered_links else links[:3]
    
    def _infer_page_type(self, url: str) -> str:
        """Infer the type of page from the URL."""
        url_lower = url.lower()
        
        if any(term in url_lower for term in ["pricing", "plans", "subscription", "cost", "buy"]):
            return "pricing"
        elif any(term in url_lower for term in ["features", "product", "capabilities", "tour", "overview"]):
            return "features"
        elif any(term in url_lower for term in ["about", "company", "team", "mission", "vision", "history"]):
            return "about"
        else:
            return "other"
    
    async def scrape(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        Alias for run method to provide a more intuitive API.
        
        Args:
            url: URL to scrape
            **kwargs: Additional parameters for customizing the scraping behavior
            
        Returns:
            Dictionary containing scraped data
        """
        return await self.run(url=url, **kwargs)
