"""Intent router for natural language queries.

This module implements the tool-calling loop:
1. User message → LLM with tool definitions
2. LLM returns tool calls
3. Bot executes tools
4. Results fed back to LLM
5. LLM produces final answer
"""

import json
import sys
from services.api_client import LMSAPI, APIError
from services.llm_client import LLMClient, LLMError


# System prompt that teaches the LLM how to use tools
SYSTEM_PROMPT = """You are a helpful assistant for a Learning Management System (LMS).
You have access to tools that let you fetch data about labs, students, scores, and analytics.

When a user asks a question:
1. Think about what data you need to answer
2. Call the appropriate tool(s) to get that data
3. Use the tool results to formulate your answer

If the user's message is a greeting or casual conversation, respond naturally without using tools.
If the user's message is unclear, ask for clarification about what they want to know.

Always base your answers on the actual data returned by tools, not assumptions."""


class IntentRouter:
    """Routes natural language queries to backend tools via LLM.

    The router maintains a conversation with the LLM, executing tool calls
    and feeding results back until the LLM produces a final answer.
    """

    def __init__(self):
        self.llm = LLMClient()
        self.api = LMSAPI()
        self.tools = self.llm.get_tool_definitions()
        
        # Map tool names to actual functions
        self.tool_handlers = {
            "get_items": self._handle_get_items,
            "get_learners": self._handle_get_learners,
            "get_scores": self._handle_get_scores,
            "get_pass_rates": self._handle_get_pass_rates,
            "get_timeline": self._handle_get_timeline,
            "get_groups": self._handle_get_groups,
            "get_top_learners": self._handle_get_top_learners,
            "get_completion_rate": self._handle_get_completion_rate,
            "trigger_sync": self._handle_trigger_sync,
        }

    def _handle_get_items(self, arguments: dict) -> list:
        """Execute get_items tool."""
        return self.api.get_items()

    def _handle_get_learners(self, arguments: dict) -> list:
        """Execute get_learners tool."""
        return self.api.get_learners()

    def _handle_get_scores(self, arguments: dict) -> dict:
        """Execute get_scores tool."""
        lab = arguments.get("lab")
        return self.api.get_scores(lab)

    def _handle_get_pass_rates(self, arguments: dict) -> list:
        """Execute get_pass_rates tool."""
        lab = arguments.get("lab")
        return self.api.get_pass_rates(lab)

    def _handle_get_timeline(self, arguments: dict) -> dict:
        """Execute get_timeline tool."""
        lab = arguments.get("lab")
        return self.api.get_timeline(lab)

    def _handle_get_groups(self, arguments: dict) -> dict:
        """Execute get_groups tool."""
        lab = arguments.get("lab")
        return self.api.get_groups(lab)

    def _handle_get_top_learners(self, arguments: dict) -> list:
        """Execute get_top_learners tool."""
        lab = arguments.get("lab")
        limit = arguments.get("limit", 5)
        return self.api.get_top_learners(lab, limit)

    def _handle_get_completion_rate(self, arguments: dict) -> dict:
        """Execute get_completion_rate tool."""
        lab = arguments.get("lab")
        return self.api.get_completion_rate(lab)

    def _handle_trigger_sync(self, arguments: dict) -> dict:
        """Execute trigger_sync tool."""
        return self.api.trigger_sync()

    def _execute_tool(self, tool_name: str, arguments: dict) -> str:
        """Execute a tool and return the result as a string.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments from LLM

        Returns:
            JSON string of the tool result
        """
        print(f"[tool] LLM called: {tool_name}({arguments})", file=sys.stderr)
        
        handler = self.tool_handlers.get(tool_name)
        if not handler:
            return f"Error: Unknown tool '{tool_name}'"
        
        try:
            result = handler(arguments)
            result_str = json.dumps(result, default=str)
            print(f"[tool] Result: {result_str[:100]}{'...' if len(result_str) > 100 else ''}", file=sys.stderr)
            return result_str
        except APIError as e:
            return f"API Error: {e.message}"
        except Exception as e:
            return f"Error: {str(e)}"

    def route(self, user_message: str) -> str:
        """Route a user message through the LLM tool-calling loop.

        Args:
            user_message: The user's natural language query

        Returns:
            Final response from the LLM
        """
        # Initialize conversation with system prompt and user message
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        max_iterations = 5  # Prevent infinite loops
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Call LLM with current conversation state
            try:
                response = self.llm.chat(messages, tools=self.tools)
            except LLMError as e:
                return f"LLM error: {e.message}"

            # Check if LLM wants to call tools
            tool_calls = response.get("tool_calls", [])
            
            if not tool_calls:
                # LLM produced a final answer
                return response.get("content", "I don't have information to answer that question.")

            # Execute each tool call
            tool_results = []
            for tool_call in tool_calls:
                function = tool_call.get("function", {})
                tool_name = function.get("name", "")
                arguments_str = function.get("arguments", "{}")
                
                try:
                    arguments = json.loads(arguments_str) if isinstance(arguments_str, str) else arguments_str
                except json.JSONDecodeError:
                    arguments = {}
                
                result = self._execute_tool(tool_name, arguments)
                tool_results.append({
                    "tool_call_id": tool_call.get("id"),
                    "result": result,
                })

            # Feed tool results back to LLM
            print(f"[summary] Feeding {len(tool_results)} tool result(s) back to LLM", file=sys.stderr)
            
            # Add the assistant's tool call message
            messages.append({
                "role": "assistant",
                "content": response.get("content"),
                "tool_calls": tool_calls,
            })
            
            # Add tool results as separate messages
            for tool_result in tool_results:
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_result["tool_call_id"],
                    "content": tool_result["result"],
                })

        return "I'm having trouble answering this question. Please try rephrasing."


def route_intent(user_message: str) -> str:
    """Route a user message to the appropriate tool(s) via LLM.

    This is the main entry point for intent routing.

    Args:
        user_message: The user's natural language query

    Returns:
        Response to show the user
    """
    router = IntentRouter()
    return router.route(user_message)
