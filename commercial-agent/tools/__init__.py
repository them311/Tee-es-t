from .hubspot import HUBSPOT_TOOLS, execute_hubspot_tool
from .gmail import GMAIL_TOOLS, execute_gmail_tool

ALL_TOOLS = HUBSPOT_TOOLS + GMAIL_TOOLS

def execute_tool(name: str, input_data: dict) -> str:
    """Route tool execution to the right handler."""
    if name.startswith("hubspot_"):
        return execute_hubspot_tool(name, input_data)
    elif name.startswith("gmail_"):
        return execute_gmail_tool(name, input_data)
    else:
        return f"Error: Unknown tool '{name}'"
