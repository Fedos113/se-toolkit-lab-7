"""Telegram bot entry point.

Supports two modes:
- Test mode: `uv run bot.py --test "/command"` prints response to stdout
- Telegram mode: Connects to Telegram and handles real messages
"""

import argparse
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from config import config
from handlers import handle_health, handle_help, handle_labs, handle_scores, handle_start


def parse_command(text: str) -> tuple[str, str | None]:
    """Parse a command string into command and argument.

    Args:
        text: The command text, e.g., "/scores lab-04" or "/start"

    Returns:
        Tuple of (command_name, argument). Argument is None if not provided.
    """
    parts = text.strip().split(maxsplit=1)
    command = parts[0].lstrip("/").lower()
    argument = parts[1] if len(parts) > 1 else None
    return command, argument


def run_test_mode(command_text: str) -> None:
    """Run a command in test mode and print the result.

    Args:
        command_text: The command to run, e.g., "/start" or "/scores lab-04"
    """
    command, arg = parse_command(command_text)

    handlers = {
        "start": handle_start,
        "help": handle_help,
        "health": handle_health,
        "labs": handle_labs,
        "scores": lambda: handle_scores(arg),
    }

    handler = handlers.get(command)
    if handler is None:
        print(f"Unknown command: /{command}")
        print("Use /help to see available commands.")
        sys.exit(0)

    response = handler()
    print(response)


async def telegram_bot() -> None:
    """Run the bot in Telegram mode using aiogram."""
    if not config.bot_token:
        print("Error: BOT_TOKEN not set in .env.bot.secret")
        sys.exit(1)

    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

    # Register command handlers
    @dp.message(CommandStart())
    async def cmd_start(message: Message) -> None:
        """Handle /start command."""
        response = handle_start()
        await message.answer(response)

    @dp.message(Command("help"))
    async def cmd_help(message: Message) -> None:
        """Handle /help command."""
        response = handle_help()
        await message.answer(response)

    @dp.message(Command("health"))
    async def cmd_health(message: Message) -> None:
        """Handle /health command."""
        response = handle_health()
        await message.answer(response)

    @dp.message(Command("labs"))
    async def cmd_labs(message: Message) -> None:
        """Handle /labs command."""
        response = handle_labs()
        await message.answer(response)

    @dp.message(Command("scores"))
    async def cmd_scores(message: Message) -> None:
        """Handle /scores command with optional lab_id argument."""
        lab_id = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        response = handle_scores(lab_id)
        await message.answer(response)

    # Start polling
    logging.basicConfig(level=logging.INFO)
    print("Bot started. Press Ctrl+C to stop.")
    await dp.start_polling(bot)


def run_telegram_mode() -> None:
    """Run the bot in Telegram mode."""
    asyncio.run(telegram_bot())


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        metavar="COMMAND",
        help="Run a command in test mode (e.g., --test '/start')",
    )

    args = parser.parse_args()

    if args.test:
        run_test_mode(args.test)
    else:
        run_telegram_mode()


if __name__ == "__main__":
    main()
