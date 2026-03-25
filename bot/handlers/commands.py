"""Command handler implementations.

Each handler is a plain function that takes arguments and returns a text response.
No Telegram dependency — same function works from --test mode, tests, or Telegram.
"""

from services.api_client import LMSAPI, APIError


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
        Backend connection status with item count or error message.
    """
    api = LMSAPI()
    try:
        items = api.get_items()
        item_count = len(items)
        return f"Backend is healthy. {item_count} items available."
    except APIError as e:
        return f"Backend error: {e.message}. Check that the services are running."


def handle_labs() -> str:
    """Handle /labs command.

    Returns:
        List of available labs with their titles.
    """
    api = LMSAPI()
    try:
        items = api.get_items()
        # Filter for labs (type="lab" and no parent_id)
        labs = [item for item in items if item.get("type") == "lab" and item.get("parent_id") is None]
        
        if not labs:
            return "No labs available."
        
        result = ["Available labs:"]
        for lab in labs:
            result.append(f"- {lab.get('title', 'Unknown')}")
        return "\n".join(result)
    except APIError as e:
        return f"Backend error: {e.message}. Check that the services are running."


def handle_scores(lab_id: str | None = None) -> str:
    """Handle /scores command.

    Args:
        lab_id: Optional lab identifier to filter scores.

    Returns:
        Scores information for the specified lab or all labs.
    """
    if not lab_id:
        return "Please specify a lab, e.g., /scores lab-04"
    
    api = LMSAPI()
    try:
        tasks = api.get_pass_rates(lab_id)
        
        if not tasks:
            return f"No pass rate data available for {lab_id}."
        
        # Format lab title from lab_id (e.g., "lab-04" -> "Lab 04")
        lab_title = lab_id.replace("lab-", "Lab ").title()
        
        result = [f"Pass rates for {lab_title}:"]
        for task in tasks:
            task_name = task.get("task", "Unknown task")
            pass_rate = task.get("avg_score", 0)
            attempts = task.get("attempts", 0)
            result.append(f"- {task_name}: {pass_rate:.1f}% ({attempts} attempts)")
        
        return "\n".join(result)
    except APIError as e:
        return f"Backend error: {e.message}. Check that the services are running."
