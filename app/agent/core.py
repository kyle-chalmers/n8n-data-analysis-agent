"""Agent core orchestration using Ollama."""
import ollama
from typing import Dict, List, Any, Optional
import pandas as pd
import json
import logging

from config import settings
from agent.tools import TOOLS, execute_tool
from agent.prompts import SYSTEM_PROMPT, INITIAL_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)


class ProductionAnalystAgent:
    """AI agent for analyzing production line data using Ollama."""

    def __init__(self):
        self.model = settings.ollama_model
        self.sessions: Dict[str, Dict] = {}
        self._client = None

    @property
    def client(self):
        """Lazy initialization of Ollama client."""
        if self._client is None:
            self._client = ollama.Client(host=settings.ollama_host)
        return self._client

    def check_ollama_connection(self) -> bool:
        """Check if Ollama is reachable."""
        try:
            self.client.list()
            return True
        except Exception as e:
            logger.error(f"Ollama connection failed: {e}")
            return False

    def get_or_create_session(self, session_id: str) -> Dict:
        """Get existing session or create new one."""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "df": None,
                "messages": [],
                "analysis_cache": {},
                "charts": []
            }
        return self.sessions[session_id]

    def load_data(self, session_id: str, df: pd.DataFrame) -> None:
        """Load DataFrame into session."""
        session = self.get_or_create_session(session_id)
        session["df"] = df
        session["analysis_cache"] = {}
        session["charts"] = []
        session["messages"] = []  # Reset conversation for new data

    def run_initial_analysis(self, session_id: str) -> Dict[str, Any]:
        """Run initial analysis when data is first uploaded."""
        session = self.get_or_create_session(session_id)

        if session["df"] is None:
            return {"error": "No data loaded for this session"}

        # Add data context to the prompt
        df = session["df"]
        data_context = f"""
The uploaded dataset contains:
- {len(df)} records
- Columns: {', '.join(df.columns.tolist())}
- Numeric columns: {', '.join(df.select_dtypes(include=['number']).columns.tolist())}
"""

        session["messages"] = [
            {"role": "user", "content": data_context + "\n\n" + INITIAL_ANALYSIS_PROMPT}
        ]

        return self._run_agent_loop(session_id)

    def chat(self, session_id: str, message: str) -> Dict[str, Any]:
        """Process a follow-up chat message."""
        session = self.get_or_create_session(session_id)

        if session["df"] is None:
            return {"error": "No data loaded. Please upload a CSV file first."}

        session["messages"].append({"role": "user", "content": message})

        return self._run_agent_loop(session_id)

    def _run_agent_loop(self, session_id: str, max_iterations: int = 10) -> Dict[str, Any]:
        """Run the agent loop until completion or max iterations."""
        session = self.sessions[session_id]
        charts_generated = []
        iterations = 0

        while iterations < max_iterations:
            iterations += 1

            try:
                response = self.client.chat(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        *session["messages"]
                    ],
                    tools=TOOLS,
                    options={"temperature": 0.7}
                )
            except Exception as e:
                logger.error(f"Ollama API error: {e}")
                return {"error": f"LLM API error: {str(e)}"}

            message = response.get("message", {})
            content = message.get("content", "")
            tool_calls = message.get("tool_calls", [])

            # Add assistant response to history
            session["messages"].append({
                "role": "assistant",
                "content": content,
                "tool_calls": tool_calls if tool_calls else None
            })

            # If no tool calls, we're done
            if not tool_calls:
                break

            # Process tool calls
            for tool_call in tool_calls:
                func = tool_call.get("function", {})
                tool_name = func.get("name")
                tool_args = func.get("arguments", {})

                # Handle string arguments (some models return JSON string)
                if isinstance(tool_args, str):
                    try:
                        tool_args = json.loads(tool_args)
                    except json.JSONDecodeError:
                        tool_args = {}

                logger.info(f"Executing tool: {tool_name} with args: {tool_args}")

                # Execute the tool
                result = execute_tool(
                    tool_name,
                    tool_args,
                    session["df"],
                    session["analysis_cache"]
                )

                # Track charts
                if result.get("type") == "chart" and result.get("image"):
                    charts_generated.append(result["image"])

                # Add tool result to messages
                session["messages"].append({
                    "role": "tool",
                    "content": json.dumps(result, default=str)
                })

        # Store charts in session
        session["charts"].extend(charts_generated)

        # Get final text response
        final_response = ""
        for msg in reversed(session["messages"]):
            if msg["role"] == "assistant" and msg.get("content"):
                final_response = msg["content"]
                break

        return {
            "response": final_response,
            "charts": charts_generated,
            "session_id": session_id
        }


# Global agent instance
agent = ProductionAnalystAgent()
