"""Simple in-memory caching with TTL."""
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict


class SimpleCache:
    """In-memory cache without Redis dependency."""
    
    def __init__(self, ttl_hours: int = 24):
        """Initialize cache with time-to-live in hours."""
        self.cache: Dict[str, tuple] = {}
        self.ttl = timedelta(hours=ttl_hours)
    
    def _hash(self, statement: str) -> str:
        """Create hash of statement."""
        return hashlib.md5(statement.encode()).hexdigest()
    
    def get(self, statement: str) -> Optional[dict]:
        """Get cached result if not expired."""
        key = self._hash(statement)
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return data
            else:
                # Expired, remove it
                del self.cache[key]
        return None
    
    def set(self, statement: str, result: dict) -> None:
        """Store result in cache."""
        key = self._hash(statement)
        self.cache[key] = (result, datetime.now())
    
    def clear_old(self) -> int:
        """Remove expired entries and return count removed."""
        now = datetime.now()
        original_size = len(self.cache)
        self.cache = {
            k: v for k, v in self.cache.items()
            if now - v[1] < self.ttl
        }
        return original_size - len(self.cache)
    
    def clear_all(self) -> None:
        """Clear entire cache."""
        self.cache.clear()
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        self.clear_old()
        return {
            "size": len(self.cache),
            "ttl_hours": self.ttl.total_seconds() / 3600
        }
