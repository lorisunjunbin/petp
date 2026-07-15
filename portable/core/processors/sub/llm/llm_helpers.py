import json
import logging
import re
from typing import Any, Dict, List, Optional, Set

try:
    import wx
except ImportError:
    wx = None


def read_json_from_markdown(markdown_content: str) -> Optional[Any]:
    if not markdown_content:
        return None
    try:
        clean_content = remove_think_tags(markdown_content)
        json_match = re.search(r'```json\n([\s\S]*?)\n```', clean_content)
        if json_match:
            return json.loads(json_match.group(1).strip())
        json_match = re.search(r'```\s*\n([\s\S]*?)\n```', clean_content)
        if json_match:
            return json.loads(json_match.group(1).strip())
        logging.warning("No JSON found in the response.")
        return None
    except json.JSONDecodeError as e:
        logging.warning(f"Failed to parse JSON: {e}")
        return None


def remove_think_tags(text: str) -> str:
    if not text:
        return ''
    return re.sub(r'<think>[\s\S]*?</think>', '', text).strip()


def show_notification(title: str, message: str):
    if wx is not None:
        wx.MessageDialog(None, message, title).ShowModal()
    else:
        logging.info(f"[Notification] {title}: {message}")


def build_tools_message_from_mcp(tools: List[Any]) -> str:
    """Build system prompt describing available MCP tools from McpTool objects."""
    if not tools:
        return "You are a helpful assistant. No external tools are available."

    tools_desc_parts = []
    for tool in tools:
        props = tool.input_schema.get('properties', {})
        required = tool.input_schema.get('required', [])
        params_desc = []
        for pname, pspec in props.items():
            req_marker = " (required)" if pname in required else " (optional)"
            ptype = pspec.get('type', 'string')
            pdesc = pspec.get('description', pspec.get('title', ''))
            params_desc.append(f'      - "{pname}": {ptype}{req_marker} — {pdesc}')

        params_block = '\n'.join(params_desc) if params_desc else '      (no parameters)'
        tools_desc_parts.append(
            f'  - Tool: "{tool.name}"\n'
            f'    Description: {tool.description}\n'
            f'    Parameters:\n{params_block}'
        )

    tools_text = '\n\n'.join(tools_desc_parts)

    return (
        "You are a helpful assistant with access to these tools:\n\n"
        f"{tools_text}\n\n"
        "Choose the appropriate tool based on the user's question. "
        "If no tool is needed, reply directly.\n\n"
        "IMPORTANT: When you need to use a tool, you must ONLY respond with "
        "the exact JSON markdown object format below, nothing else:\n"
        "```json\n"
        "{\n"
        '    "tool": "tool-name",\n'
        '    "arguments": {\n'
        '        "argument-name": "value"\n'
        "    }\n"
        "}\n"
        "```\n"
        "After receiving a tool's response:\n"
        "1. Transform the raw data into a natural, conversational response\n"
        "2. Keep responses concise but informative\n"
        "3. Focus on the most relevant information\n"
        "4. Use appropriate context from the user's question\n"
        "5. Make sure tool-name is identical to the tool name in the list\n"
        "6. Avoid simply repeating the raw data\n\n"
        "Please use only the tools that are explicitly defined above."
    )


def parse_tool_call_from_response(answer: str, tool_names: Set[str]) -> Optional[Dict[str, Any]]:
    """Parse a tool call JSON from LLM response. Returns dict with 'tool' and 'arguments', or None."""
    tool_call = read_json_from_markdown(answer)
    if not isinstance(tool_call, dict):
        return None
    if "tool" not in tool_call or "arguments" not in tool_call:
        return None
    if tool_call['tool'] not in tool_names:
        logging.warning(f"Tool '{tool_call['tool']}' not found in available tools: {tool_names}")
        return None
    return tool_call
