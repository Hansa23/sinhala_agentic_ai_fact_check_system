"""Multi-source search with fallback strategy."""
import os
# noinspection PyUnresolvedReference
from ddgs import DDGS


class MultiSourceSearch:
    """Search across multiple providers with automatic fallback."""
    
    def __init__(self):
        """Initialize search providers."""
        # Tavily: 1000/month free
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        self.tavily_count = 0
        self.tavily_limit = 1000
        
        # Brave: 2000/month free
        self.brave_api_key = os.getenv("BRAVE_API_KEY")
        self.brave_count = 0
        self.brave_limit = 2000
        
        # DuckDuckGo: unlimited free
        self.ddg = DDGS()
        
        # Recommended domains for Sinhala queries
        self.recommended_domains = [
            "bbc.com",
            "wikipedia.org",
            "news.lk",
            "lankabusinessonline.com"
        ]
    
    def search(self, query: str) -> dict:
        """Try Tavily → Brave → DuckDuckGo."""
        
        # Try Tavily first (best quality)
        if self.tavily_count < self.tavily_limit and self.tavily_api_key:
            try:
                return self._tavily_search(query)
            except ImportError:
                pass
        
        # Fallback to Brave
        if self.brave_api_key and self.brave_count < self.brave_limit:
            try:
                return self._brave_search(query)
            except (ImportError, ValueError):
                pass
        
        # Final fallback to DuckDuckGo (always works!)
        try:
            return self._duckduckgo_search(query)
        except RuntimeError:
            return {
                "results": [],
                "source": "none",
                "remaining": "unknown"
            }
    
    def _tavily_search(self, query: str) -> dict:
        """Search using Tavily API."""
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=self.tavily_api_key)
            results = client.search(
                query + " Sri Lanka",
                include_domains=self.recommended_domains
            )
            self.tavily_count += 1
            return {
                "results": results.get("results", []),
                "source": "tavily",
                "remaining": self.tavily_limit - self.tavily_count
            }
        except ImportError as e:
            raise ImportError("tavily-python not installed") from e
    
    def _brave_search(self, query: str) -> dict:
        """Search using Brave Search API."""
        import requests
        
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {"X-Subscription-Token": self.brave_api_key}
        params = {"q": query + " Sri Lanka", "count": 10}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()
        
        results = [
            {
                "title": r.get("title", ""),
                "content": r.get("description", ""),
                "url": r.get("url", "")
            }
            for r in data.get("web", {}).get("results", [])
        ]
        
        self.brave_count += 1
        return {
            "results": results,
            "source": "brave",
            "remaining": self.brave_limit - self.brave_count
        }
    
    def _duckduckgo_search(self, query: str) -> dict:
        """Search using DuckDuckGo (unlimited)."""
        results_list = list(
            self.ddg.text(query + " Sri Lanka", max_results=10)
        )
        
        results = [
            {
                "title": r.get("title", ""),
                "content": r.get("body", ""),
                "url": r.get("href", "")
            }
            for r in results_list
        ]
        
        return {
            "results": results,
            "source": "duckduckgo",
            "remaining": "unlimited"
        }
    
    def get_quota_status(self) -> dict:
        """Get remaining quota for each provider."""
        return {
            "tavily": {
                "used": self.tavily_count,
                "remaining": self.tavily_limit - self.tavily_count
            },
            "brave": {
                "used": self.brave_count,
                "remaining": self.brave_limit - self.brave_count
            },
            "duckduckgo": {
                "remaining": "unlimited"
            }
        }
