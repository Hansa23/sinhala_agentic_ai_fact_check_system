"""Configuration and validation module."""
import os
from pathlib import Path


def validate_environment() -> bool:
    """Validate that all required environment variables are set."""
    required = ["GOOGLE_API_KEY"]
    optional = ["TAVILY_API_KEY", "BRAVE_API_KEY"]
    
    missing = []
    for var in required:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        print("   Create a .env file with these variables. See .env.example")
        return False
    
    print("✓ Environment variables validated")
    
    # Warn about optional
    for var in optional:
        if not os.getenv(var):
            print(f"⚠️ Optional {var} not set. Using fallback search provider.")
    
    return True


def ensure_directories() -> bool:
    """Ensure required directories exist."""
    dirs = [
        "./qdrant_data",
        "./data",
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(exist_ok=True)
    
    print("✓ Directories ensured")
    return True


if __name__ == "__main__":
    validate_environment()
    ensure_directories()
