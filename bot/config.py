"""Configuration loading from environment variables."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the directory where bot.py is located
BOT_DIR = Path(__file__).parent
# .env.bot.secret is in the parent directory (repo root)
ENV_FILE = BOT_DIR.parent / ".env.bot.secret"


class BotConfig(BaseSettings):
    """Bot configuration loaded from .env.bot.secret."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram bot token
    bot_token: str = Field(default="", alias="BOT_TOKEN")

    # LMS API configuration
    lms_api_base_url: str = Field(default="http://localhost:42002", alias="LMS_API_BASE_URL")
    lms_api_key: str = Field(default="", alias="LMS_API_KEY")

    # LLM configuration
    llm_api_model: str = Field(default="coder-model", alias="LLM_API_MODEL")
    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    llm_api_base_url: str = Field(default="http://localhost:42005/v1", alias="LLM_API_BASE_URL")


config = BotConfig()
