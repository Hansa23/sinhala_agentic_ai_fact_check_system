"""Model Context Protocol (MCP) Server Simulation.

This module simulates an MCP Server that exposes tools to the agent.
See: https://modelcontextprotocol.io/
"""
from typing import List, Dict, Any, Optional
from ..search import MultiSourceSearch

class Tool:
    """Definition of an MCP Tool."""
    def __init__(self, name: str, description: str, input_schema: Dict[str, Any]):
        self.name = name
        self.description = description
        self.input_schema = input_schema

class MCPServer:
    """Simulated MCP Server for Search Tools."""
    
    def __init__(self):
        self.search_engine = MultiSourceSearch()
        self.tools = [
            Tool(
                name="search_web",
                description="Search the web for Sinhala fact checking using multiple sources (Tavily, Brave, DDG). Use this to find evidence for a claim.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query in Sinhala or English."
                        }
                    },
                    "required": ["query"]
                }
            )
        ]

    def list_tools(self) -> List[Tool]:
        """List available tools."""
        return self.tools

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool call."""
        if tool_name == "search_web":
            query = arguments.get("query")
            if not query:
                raise ValueError("Query argument is required for search_web")
            return self.search_engine.search(query)
        
        raise ValueError(f"Tool {tool_name} not found")

    def get_quota_status(self):
         return self.search_engine.get_quota_status()
