"""Command handler implementations.

Each handler is a plain function that takes arguments and returns a text response.
No Telegram dependency — same function works from --test mode, tests, or Telegram.
"""


def handle_start() -> str:
    """Handle /start command.
    
    Returns:
        Welcome message for new users.
    """
    return "Welcome to the LMS Bot! I can help you check your labs, scores, and more. Use /help to see available commands."


def handle_help() -> str:
    """Handle /help command.
    
    Returns:
        List of available commands with descriptions.
    """
    return """Available commands:
/start - Welcome message and introduction
/help - Show this help message
/health - Check backend connection status
/labs - List available labs
/scores <lab_id> - Get scores for a specific lab"""


def handle_health() -> str:
    """Handle /health command.
    
    Returns:
        Backend connection status.
    """
    # TODO: Task 2 - implement real health check against LMS API
    return "Backend status: OK (placeholder)"


def handle_labs() -> str:
    """Handle /labs command.
    
    Returns:
        List of available labs.
    """
    # TODO: Task 2 - implement real labs fetch from LMS API
    return "Available labs will be shown here (placeholder)"


def handle_scores(lab_id: str | None = None) -> str:
    """Handle /scores command.
    
    Args:
        lab_id: Optional lab identifier to filter scores.
        
    Returns:
        Scores information for the specified lab or all labs.
    """
    # TODO: Task 2 - implement real scores fetch from LMS API
    if lab_id:
        return f"Scores for {lab_id} will be shown here (placeholder)"
    return "Your scores will be shown here (placeholder)"
