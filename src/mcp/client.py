"""Model Context Protocol (MCP) Client Simulation.

Connects the agent to the MCP Server and handles tool discovery/execution.
"""
from typing import Dict, Any, List
from .server import MCPServer

class MCPClient:
    """Simulated MCP Client."""
    
    def __init__(self, server: MCPServer):
        self.server = server
        self.available_tools = self.server.list_tools()

    def discover_tools(self) -> List[Dict[str, Any]]:
        """Return tool definitions in Gemini Function format."""
        
        gemini_tools = []
        for tool in self.available_tools:
            gemini_tool = {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.input_schema
            }
            gemini_tools.append(gemini_tool)
        
        return gemini_tools

    def call_tool(self, name: str, args: Dict[str, Any]) -> Any:
        """Call a tool on the server."""
        print(f"MCP Client: Calling tool '{name}' with args {args}")
        try:
            return self.server.call_tool(name, args)
        except Exception as e:
            print(f"MCP Tool Error: {e}")
            return {"error": str(e)}

    def get_server_status(self):
        return self.server.get_quota_status()
