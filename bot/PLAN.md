# Bot Development Plan

## Overview

This plan describes the approach for building a Telegram bot that integrates with the LMS backend to provide students with access to their labs, scores, and course information through a chat interface.

## Task 1: Scaffold and Testable Architecture

The foundation is a **testable handler architecture**. Handlers are plain Python functions that take input (command name and arguments) and return text responses. They have no dependency on Telegram — the same function can be called from `--test` mode, from unit tests, or from the actual Telegram bot. This is called **separation of concerns**: the business logic (handlers) is separated from the transport layer (Telegram).

The entry point `bot.py` supports a `--test` flag that bypasses Telegram entirely, calling handlers directly and printing results to stdout. This enables offline development and testing without needing a bot token or Telegram connection.

## Task 2: Backend Integration

Implement real API calls to the LMS backend. Create an API client service in `bot/services/` that handles HTTP requests with Bearer token authentication. The `/health` command will verify backend connectivity, `/labs` will fetch available labs, and `/scores` will retrieve student scores. All credentials (API URL, API key) come from environment variables via `config.py`.

## Task 3: LLM Intent Routing

Add natural language understanding using the Qwen LLM. Instead of requiring exact slash commands, the bot will understand queries like "what labs are available?" or "show my scores for lab-04". The LLM receives tool descriptions and decides which handler to invoke. The key insight is that **tool description quality matters more than prompt engineering** — clear, specific descriptions help the LLM make correct choices.

## Task 4: Docker Deployment

Containerize the bot and configure Docker networking. The bot container needs to reach both the LMS backend and the LLM API. Inside Docker, services communicate via service names (e.g., `backend`) rather than `localhost`. The docker-compose configuration orchestrates all services with proper environment variables and network settings.

## Directory Structure

```
bot/
├── bot.py           # Entry point with --test mode and Telegram startup
├── config.py        # Environment variable loading from .env.bot.secret
├── handlers/
│   ├── __init__.py  # Intent router
│   └── commands.py  # Command handlers (start, help, health, labs, scores)
├── services/
│   ├── __init__.py
│   ├── api_client.py    # LMS API client with Bearer auth
│   └── llm_client.py    # LLM client for intent routing
├── pyproject.toml   # Bot dependencies
└── PLAN.md          # This file
```
