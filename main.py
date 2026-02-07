"""Main entry point and utility functions."""
import warnings

# Suppress pydantic v1 warning on Python 3.14+
warnings.filterwarnings(
    "ignore",
    message=r"Core Pydantic V1 functionality isn't compatible with Python 3\.14 or greater\.",
)

import os
from dotenv import load_dotenv
from google import genai  # type: ignore[attr-defined]

from src.vector_store import QdrantVectorStore
from src.search import MultiSourceSearch
from src.workflow import FactCheckingWorkflow
from src.cache import SimpleCache
from src.async_processor import AsyncFactChecker

# Load environment variables
load_dotenv()


def initialize():
    """Initialize all components."""
    # Configure Gemini API
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not set in .env file")
    # New SDK uses Client instance
    client = genai.Client(api_key=api_key)
    qdrant_path = os.getenv("Qdrant_PATH", "./qdrant_data")
    
    # Initialize components
    vector_store = QdrantVectorStore(qdrant_path)
    search = MultiSourceSearch()
    workflow = FactCheckingWorkflow(vector_store, search, client=client)
    cache = SimpleCache(ttl_hours=24)
    async_checker = AsyncFactChecker(workflow, max_concurrent=10)
    
    return {
        "vector_store": vector_store,
        "search": search,
        "workflow": workflow,
        "cache": cache,
        "async_checker": async_checker
    }


def verify_statement(statement: str, use_cache: bool = True) -> dict:
    """Verify a single statement."""
    components = initialize()
    cache = components["cache"]
    workflow = components["workflow"]
    
    if use_cache:
        cached = cache.get(statement)
        if cached:
            return {"cached": True, **cached}
    
    result = workflow.verify(statement)
    cache.set(statement, result)
    return {"cached": False, **result}


async def verify_batch(statements: list, use_rate_limit: bool = False) -> list:
    """Verify multiple statements."""
    components = initialize()
    async_checker = components["async_checker"]
    cache = components["cache"]
    
    results = []
    for stmt in statements:
        cached = cache.get(stmt)
        if cached:
            results.append({"cached": True, **cached})
        else:
            results.append({"cached": False})
    
    if use_rate_limit:
        batch_results = await async_checker.verify_with_rate_limit(
            statements,
            rate_limit_per_second=0.5
        )
    else:
        batch_results = await async_checker.verify_batch(statements)
    
    for i, result in enumerate(batch_results):
        if not results[i].get("cached"):
            results[i] = result
            cache.set(statements[i], result)
    
    return results


if __name__ == "__main__":
    # Example usage
    print("Initializing Sinhala Fact-Checking System...")
    components = initialize()
    print("✓ Components initialized")
    
    # Test with a sample statement
    test_statement = "ශ්‍රී ලංකාවේ ජිඩීපී වර්ධනය විය"
    print(f"\nTesting with: {test_statement}")
    
    result = verify_statement(test_statement)
    print(f"Verdict: {result.get('verdict')}")
    print(f"Analysis: {result.get('analysis')}")
