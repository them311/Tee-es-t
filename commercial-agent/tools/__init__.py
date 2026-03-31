from .hubspot import HUBSPOT_TOOLS, execute_hubspot_tool
from .gmail import GMAIL_TOOLS, execute_gmail_tool
from .notion import NOTION_TOOLS, execute_notion_tool
from .github_tools import GITHUB_TOOLS, execute_github_tool

ALL_TOOLS = HUBSPOT_TOOLS + GMAIL_TOOLS + NOTION_TOOLS + GITHUB_TOOLS

def execute_tool(name: str, input_data: dict) -> str:
    """Route tool execution to the right handler."""
    if name.startswith("hubspot_"):
        return execute_hubspot_tool(name, input_data)
    elif name.startswith("gmail_"):
        return execute_gmail_tool(name, input_data)
    elif name.startswith("notion_"):
        return execute_notion_tool(name, input_data)
    elif name.startswith("github_"):
        return execute_github_tool(name, input_data)
    else:
        return f"Error: Unknown tool '{name}'"
