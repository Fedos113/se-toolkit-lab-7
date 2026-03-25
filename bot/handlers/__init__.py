"""Command handlers for the Telegram bot.

Handlers are plain functions that take input and return text.
They don't depend on Telegram — same function works from --test mode,
unit tests, or the actual Telegram bot.
"""

from .commands import (
    handle_health,
    handle_help,
    handle_labs,
    handle_scores,
    handle_start,
)

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
]
