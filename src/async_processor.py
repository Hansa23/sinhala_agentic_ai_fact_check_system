"""Async batch processing for multiple claims."""
import asyncio
from typing import List


class AsyncFactChecker:
    """Process multiple claims concurrently."""
    
    def __init__(self, workflow, max_concurrent: int = 10):
        """Initialize async processor."""
        self.workflow = workflow
        self.max_concurrent = max_concurrent
    
    async def verify_batch(self, statements: List[str]) -> List[dict]:
        """Verify multiple statements concurrently."""
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def verify_with_limit(statement: str):
            async with semaphore:
                try:
                    return await self.workflow.verify_async(statement)
                except (RuntimeError, ValueError) as e:
                    return {
                        "statement": statement,
                        "error": str(e),
                        "verdict": "error"
                    }
        
        # Run all in parallel (within limit)
        tasks = [verify_with_limit(s) for s in statements]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            r if not isinstance(r, Exception) else {
                "error": str(r),
                "verdict": "error"
            }
            for r in results
        ]
    
    async def verify_with_rate_limit(
        self,
        statements: List[str],
        rate_limit_per_second: float = 1.0
    ) -> List[dict]:
        """Verify with rate limiting (useful for API limits)."""
        results = []
        delay = 1.0 / rate_limit_per_second
        
        for i, statement in enumerate(statements):
            if i > 0:
                await asyncio.sleep(delay)
            
            try:
                result = await self.workflow.verify_async(statement)
                results.append(result)
            except (RuntimeError, ValueError) as e:
                results.append({
                    "statement": statement,
                    "error": str(e),
                    "verdict": "error"
                })
        
        return results
