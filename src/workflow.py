"""LangGraph workflow for fact checking."""
import asyncio
import os
import json
from typing import Literal
from langgraph.graph import StateGraph, END
# noinspection PyUnresolvedReference
from google import genai

from .models import FactCheckState
from .vector_store import QdrantVectorStore
from .gemini_router import GeminiRouter
from .mcp.server import MCPServer
from .mcp.client import MCPClient


class FactCheckingWorkflow:
    """LangGraph-based fact checking workflow with 4-Agent Architecture."""
    
    def __init__(self, vector_store: QdrantVectorStore, client=None):
        """Initialize workflow with dependencies."""
        self.vector_store = vector_store
        # Initialize MCP Architecture
        self.mcp_server = MCPServer()
        self.mcp_client = MCPClient(self.mcp_server)
        
        self.client = client or genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.router = GeminiRouter(client=self.client)
        self.workflow = self._create_workflow()
    
    def _classify_agent(self, state: FactCheckState) -> FactCheckState:
        """Agent 1: Domain Classification Agent."""
        prompt = f"""You are an expert classification agent.
        Classify this Sinhala statement into ONE domain: politics, economics, or health.
        
        Statement: {state['statement']}
        
        Respond with ONLY the domain name in English (politics/economics/health).
        If uncertain, default to politics."""
        
        try:
            response = self.router.route("classify", prompt)
            domain = (response.text or "").strip().lower()
        except (RuntimeError, ValueError):
            domain = "politics"
        
        # Validate domain
        if domain not in ["politics", "economics", "health"]:
            domain = "politics"  # Default
        
        state["domain"] = domain
        return state
    
    def _retrieval_agent(self, state: FactCheckState) -> FactCheckState:
        """Agent 2: Data Retrieval Agent (Vector + Web via MCP)."""
        # 1. Search Vector Store (Historical/Context)
        docs = self.vector_store.search(
            state["statement"],
            state["domain"],
            limit=3
        )
        
        # 2. Web Search via MCP Client
        # The agent uses the MCP Client to call the 'search_web' tool.
        # This follows the MCP architecture: Agent -> Client -> Server -> Tool.
        search_res = self.mcp_client.call_tool("search_web", {"query": state["statement"]})
        
        state["retrieved_docs"] = docs
        state["search_results"] = search_res.get("results", [])
        state["search_source"] = search_res.get("source", "unknown")
        
        return state
    
    def _analysis_agent(self, state: FactCheckState) -> FactCheckState:
        """Agent 3: Fact Analysis Agent."""
        # Combine evidence
        evidence = state.get("search_results", []) + state.get("retrieved_docs", [])
        evidence_text = "\n\n".join([
            f"Source {i+1}: {e.get('text') or e.get('content') or ''} (URL: {e.get('url', 'N/A')})"
            for i, e in enumerate(evidence[:5])
        ])
        
        if not evidence_text:
            evidence_text = "No evidence found."

        prompt = f"""You are an expert Fact Analysis Agent. Analyze the following Sinhala statement against the provided evidence.
        
        Statement: {state['statement']}
        
        Evidence:
        {evidence_text[:4000]}
        
        Task:
        1. Compare the statement with the evidence.
        2. Identify ensuring facts and contradictions.
        3. Assess the credibility of the evidence.
        4. Provide a detailed analysis in Sinhala.
        
        Output ONLY the analysis in Sinhala."""
        
        try:
            # Use 'analyze' task type for smarter model
            response = self.router.route("analyze", prompt)
            state["analysis"] = response.text or "Error generating analysis."
        except Exception as e:
            state["analysis"] = f"Analysis failed: {str(e)}"
        
        return state
    
    def _verdict_agent(self, state: FactCheckState) -> FactCheckState:
        """Agent 4: Verdict Agent."""
        analysis = state.get("analysis", "")
        
        prompt = f"""You are the Final Verdict Agent. Based on the analysis provided, determine if the statement is True, False, or if there is Insufficient Information.
        
        Statement: {state['statement']}
        Analysis: {analysis}
        
        Respond with a JSON object in the following format:
        {{
            "verdict": "true" | "false" | "insufficient",
            "explanation": "A clear, concise explanation in Sinhala justifying the verdict."
        }}
        """
        
        try:
            # Use 'decide' or 'pro' for structured output
            response = self.router.route("decide", prompt)
            text = response.text or "{}"
            # cleanup json markdown
            text = text.replace("```json", "").replace("```", "").strip()
            
            data = json.loads(text)
            state["verdict"] = data.get("verdict", "insufficient").lower()
            # Append explanation to analysis or store separately. 
            # For now, we append it to analysis to show in UI easily without changing UI code too much.
            state["analysis"] = f"{analysis}\n\n**නිගමනය (Verdict):**\n{data.get('explanation', '')}"
            
        except Exception:
            # Fallback simple logic
            if "සත්‍ය" in analysis or "true" in analysis.lower():
                state["verdict"] = "true"
            elif "අසත්‍ය" in analysis or "false" in analysis.lower():
                state["verdict"] = "false"
            else:
                state["verdict"] = "insufficient"
                
        return state

    def _create_workflow(self):
        """Build the 4-Agent LangGraph workflow."""
        workflow = StateGraph(FactCheckState)
        
        # Add Agents
        workflow.add_node("classify_agent", self._classify_agent)
        workflow.add_node("retrieval_agent", self._retrieval_agent)
        workflow.add_node("analysis_agent", self._analysis_agent)
        workflow.add_node("verdict_agent", self._verdict_agent)
        
        # Define Flow
        workflow.set_entry_point("classify_agent")
        workflow.add_edge("classify_agent", "retrieval_agent")
        workflow.add_edge("retrieval_agent", "analysis_agent")
        workflow.add_edge("analysis_agent", "verdict_agent")
        workflow.add_edge("verdict_agent", END)
        
        return workflow.compile()
    
    def verify(self, statement: str) -> dict:
        """Verify a statement synchronously."""
        initial_state = {
            "statement": statement,
            "domain": "",
            "retrieved_docs": [],
            "search_results": [],
            "analysis": "",
            "verdict": "",
            "method_used": "4-agent-workflow-mcp",
            "sufficiency": None,
            "search_source": None,
            "cached": False
        }
        
        result = self.workflow.invoke(initial_state)
        return result
    
    async def verify_async(self, statement: str) -> dict:
        """Verify a statement asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.verify, statement)
