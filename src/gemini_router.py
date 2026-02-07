"""Gemini model router for intelligent model selection."""
import time
import os
# noinspection PyUnresolvedReference
from google import genai


class GeminiRouter:
    """Route to best Gemini model based on task and rate limits."""
    
    def __init__(self, client=None):
        """Initialize all Gemini models."""
        self.client = client or genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        # NOTE: These model IDs must exist for the API key.
        # We use IDs returned by `client.models.list()`.
        self.flash_model = "models/gemini-2.0-flash"
        self.pro_model = "models/gemini-pro-latest"
        self.thinking_model = "models/gemini-2.0-flash-thinking-exp-01-21"
        
        # Simple rate limiting (calls in last 60 seconds)
        self.flash_calls = []
        self.pro_calls = []
        self.thinking_calls = []
    
    def _check_rate_limit(self, calls_list: list, max_rpm: int) -> bool:
        """Check if rate limit is not exceeded."""
        now = time.time()
        # Remove calls older than 1 minute
        calls_list[:] = [t for t in calls_list if now - t < 60]
        return len(calls_list) < max_rpm
    
    def route(self, task_type: str, prompt: str):
        """Smart routing based on task type."""
        
        # Quick classification → Flash (fastest, 15 RPM)
        if task_type in ["classify", "extract", "quick"]:
            if self._check_rate_limit(self.flash_calls, 15):
                self.flash_calls.append(time.time())
                return self.client.models.generate_content(model=self.flash_model, contents=prompt)
            else:
                return self.client.models.generate_content(model=self.flash_model, contents=prompt)
        
        # Complex reasoning → Pro (smartest, 2 RPM)
        elif task_type in ["analyze", "reason", "complex"]:
            if self._check_rate_limit(self.pro_calls, 2):
                self.pro_calls.append(time.time())
                return self.client.models.generate_content(model=self.pro_model, contents=prompt)
            else:
                return self.client.models.generate_content(model=self.flash_model, contents=prompt)
        
        # Decision making → Thinking (10 RPM, reasoning)
        elif task_type == "decide":
            if self._check_rate_limit(self.thinking_calls, 10):
                self.thinking_calls.append(time.time())
                try:
                    return self.client.models.generate_content(model=self.thinking_model, contents=prompt)
                except Exception:
                     # Fallback if thinking model fails
                    return self.client.models.generate_content(model=self.flash_model, contents=prompt)
            else:
                return self.client.models.generate_content(model=self.flash_model, contents=prompt)
        
        # Default → Flash
        else:
            return self.client.models.generate_content(model=self.flash_model, contents=prompt)
    
    def get_stats(self) -> dict:
        """Get rate limiting statistics."""
        now = time.time()
        flash_recent = len([t for t in self.flash_calls if now - t < 60])
        pro_recent = len([t for t in self.pro_calls if now - t < 60])
        thinking_recent = len([t for t in self.thinking_calls if now - t < 60])
        
        return {
            "flash": {"used": flash_recent, "limit": 15},
            "pro": {"used": pro_recent, "limit": 2},
            "thinking": {"used": thinking_recent, "limit": 10}
        }
