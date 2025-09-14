# Real web search implementation using Tavily API and web scraping
import asyncio
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import re
import time

@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    domain: str
    content: str = ""  # Full content when scraped

@dataclass 
class SearchResponse:
    results: List[SearchResult]
    total_results: int
    search_time: float

class RealWebSearch:
    def __init__(self):
        self.tavily_api_key = os.getenv('TAVILY_API_KEY')
        # Removed HTMLSession to avoid lxml.html.clean dependency
        self.session = requests.Session()
        
    async def search_tavily(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Search using Tavily API for high-quality results"""
        if not self.tavily_api_key:
            print("Warning: TAVILY_API_KEY not found, using fallback search")
            return await self.search_fallback(query, max_results)
            
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=self.tavily_api_key)
            
            # Search with Tavily
            response = client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_raw_content=True,
                include_answer=False
            )
            
            results = []
            for item in response.get('results', []):
                results.append(SearchResult(
                    title=item.get('title', ''),
                    url=item.get('url', ''),
                    snippet=item.get('content', ''),
                    domain=self._extract_domain(item.get('url', '')),
                    content=item.get('raw_content', item.get('content', ''))
                ))
            
            return results
            
        except Exception as e:
            print(f"Tavily search error: {e}")
            return await self.search_fallback(query, max_results)
    
    async def search_fallback(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Fallback search using DuckDuckGo when Tavily is not available"""
        try:
            # Use DuckDuckGo search as fallback
            search_url = f"https://duckduckgo.com/html/?q={query}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            result_elements = soup.find_all('div', class_='result__body')[:max_results]
            
            for elem in result_elements:
                title_elem = elem.find('a', class_='result__a')
                snippet_elem = elem.find('a', class_='result__snippet')
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    domain = self._extract_domain(url)
                    
                    results.append(SearchResult(
                        title=title,
                        url=url,
                        snippet=snippet,
                        domain=domain
                    ))
            
            return results
            
        except Exception as e:
            print(f"Fallback search error: {e}")
            return self._get_demo_results(query)
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            if url.startswith('http'):
                return url.split('/')[2]
            else:
                return url.split('/')[0]
        except:
            return url
    
    def _get_demo_results(self, query: str) -> List[SearchResult]:
        """Generate demo results when all search methods fail"""
        return [
            SearchResult(
                title=f"Search Results for: {query}",
                url=f"https://example.com/search?q={query.replace(' ', '+')}",
                snippet=f"This is a demo result for '{query}'. Real search results would appear here when properly configured with API keys.",
                domain="example.com",
                content=f"Demo content for {query}. In a real implementation, this would contain the full scraped content from the webpage."
            ),
            SearchResult(
                title=f"{query} - Research and Analysis",
                url=f"https://research.example.com/{query.replace(' ', '-')}",
                snippet=f"Comprehensive analysis and research findings on {query}. This demonstrates how real search results would be structured.",
                domain="research.example.com",
                content=f"Extended content about {query} that would be extracted from actual web pages."
            )
        ]
    
    async def scrape_content(self, url: str) -> str:
        """Optimized content scraping with faster timeouts and better extraction"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Reduced timeout for faster response
            response = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Enhanced content extraction with priority selectors
            content_selectors = [
                'article', 'main', '[role="main"]', '.content', '.post-content', 
                '.entry-content', '.article-body', '.story-body', '.post-body',
                'section', '.container', '.wrapper'
            ]
            
            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = elements[0].get_text(strip=True, separator=' ')
                    if len(content) > 100:  # Only use if substantial content
                        break
            
            # Fallback to body content if no structured content found
            if not content or len(content) < 100:
                body = soup.find('body')
                if body:
                    content = body.get_text(strip=True, separator=' ')
            
            # Enhanced content cleanup
            content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
            content = re.sub(r'[^\w\s.,!?;:()-]', '', content)  # Remove special chars
            
            # Return more content but still limited for performance
            return content[:3000]  # Increased from 5000 to 3000 for balance
            
        except Exception as e:
            print(f"Content scraping error for {url}: {e}")
            return ""
    
    async def search_web(self, query: str, max_results: int = 5, scrape_content: bool = True) -> SearchResponse:
        """Optimized search function with parallel processing and selective scraping"""
        import time
        start_time = time.time()
        
        # Get search results
        results = await self.search_tavily(query, max_results)
        
        # Parallel content scraping for speed - but only for top results
        if scrape_content and results:
            import asyncio
            
            # Only scrape content for results that don't already have substantial content
            scrape_tasks = []
            for result in results:
                if result.url and (not result.content or len(result.content) < 200):
                    scrape_tasks.append(self.scrape_content(result.url))
                else:
                    scrape_tasks.append(asyncio.create_task(asyncio.sleep(0)))  # No-op task
            
            # Execute scraping in parallel with timeout
            try:
                scraped_contents = await asyncio.wait_for(
                    asyncio.gather(*scrape_tasks, return_exceptions=True), 
                    timeout=15  # 15 second timeout for all scraping
                )
                
                # Update results with scraped content
                for i, (result, scraped_content) in enumerate(zip(results, scraped_contents)):
                    if isinstance(scraped_content, str) and scraped_content:
                        result.content = scraped_content
                    elif not result.content:
                        result.content = result.snippet
                        
            except asyncio.TimeoutError:
                print("Content scraping timed out, using snippets")
                # Fall back to snippets for all results
                for result in results:
                    if not result.content:
                        result.content = result.snippet
        
        search_time = time.time() - start_time
        
        return SearchResponse(
            results=results,
            total_results=len(results),
            search_time=search_time
        )

# Global instance
_web_search = None

def get_web_search() -> RealWebSearch:
    """Get or create web search instance"""
    global _web_search
    if _web_search is None:
        _web_search = RealWebSearch()
    return _web_search

# Convenience function for backward compatibility
async def search_web(query: str, max_results: int = 5) -> SearchResponse:
    """Search the web for a given query"""
    search_engine = get_web_search()
    return await search_engine.search_web(query, max_results)

# Test function
async def test_search():
    """Test the search functionality"""
    query = "latest developments in artificial intelligence 2025"
    print(f"Testing search for: {query}")
    
    results = await search_web(query, max_results=3)
    
    print(f"Found {results.total_results} results in {results.search_time:.2f}s")
    for i, result in enumerate(results.results, 1):
        print(f"\n{i}. {result.title}")
        print(f"   URL: {result.url}")
        print(f"   Domain: {result.domain}")
        print(f"   Snippet: {result.snippet[:100]}...")
        if result.content:
            print(f"   Content: {result.content[:150]}...")

if __name__ == "__main__":
    asyncio.run(test_search())