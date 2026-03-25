"""LLM client for intent routing.

This module handles communication with the LLM API for natural language
intent understanding. The LLM receives tool descriptions and decides which
tools to call based on the user's message.
"""

import json
import httpx
from config import config


class LLMError(Exception):
    """Exception raised when LLM request fails."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class LLMClient:
    """Client for the LLM API.

    Supports tool calling: the LLM receives tool schemas and returns
    tool calls that the bot executes.
    """

    def __init__(self):
        self.base_url = config.llm_api_base_url.rstrip("/")
        self.api_key = config.llm_api_key
        self.model = config.llm_api_model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        """Send a chat request to the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: Optional list of tool schemas

        Returns:
            LLM response dict with 'content' and/or 'tool_calls'

        Raises:
            LLMError: If the request fails
        """
        url = f"{self.base_url}/chat/completions"
        body = {
            "model": self.model,
            "messages": messages,
        }
        if tools:
            body["tools"] = tools
            body["tool_choice"] = "auto"

        try:
            with httpx.Client() as client:
                response = client.post(url, headers=self.headers, json=body, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]
        except httpx.HTTPStatusError as e:
            raise LLMError(f"HTTP {e.response.status_code}: {e.response.text}")
        except httpx.ConnectError as e:
            raise LLMError(f"Connection error: {str(e)}")
        except httpx.TimeoutException as e:
            raise LLMError(f"Request timed out: {str(e)}")
        except Exception as e:
            raise LLMError(f"Unexpected error: {str(e)}")

    def get_tool_definitions(self) -> list[dict]:
        """Return tool definitions for the LLM.

        These are the 9 backend endpoints wrapped as LLM tools.
        The LLM uses these descriptions to decide which tool to call.

        Returns:
            List of tool schemas
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_items",
                    "description": "Get the list of all labs and tasks. Use this to find what labs exist or to get lab IDs.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_learners",
                    "description": "Get the list of all enrolled learners and their groups. Use this to find student information.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_scores",
                    "description": "Get score distribution (4 buckets) for a specific lab. Use when asked about score distribution or grade breakdown.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                            },
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_pass_rates",
                    "description": "Get per-task pass rates and attempt counts for a specific lab. Use when asked about task difficulty, pass rates, or which tasks are hardest.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                            },
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_timeline",
                    "description": "Get submission timeline (submissions per day) for a specific lab. Use when asked about submission patterns or activity over time.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                            },
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_groups",
                    "description": "Get per-group performance and student counts for a specific lab. Use when asked about group comparisons or which group is doing best.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                            },
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_top_learners",
                    "description": "Get top N learners by score for a specific lab. Use when asked about top students, leaderboard, or best performers.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of top learners to return, default 5",
                            },
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_completion_rate",
                    "description": "Get completion rate percentage for a specific lab. Use when asked about how many students finished a lab.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                            },
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "trigger_sync",
                    "description": "Trigger ETL sync to refresh data from autochecker. Use when asked to update or refresh the data.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
        ]
