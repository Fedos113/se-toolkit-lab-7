# Bot Dockerfile
# Uses uv for dependency management

FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy all bot files
COPY . .

# Install dependencies using uv (without --frozen since we don't have uv.lock)
RUN uv sync --no-dev

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["uv", "run", "bot.py"]
