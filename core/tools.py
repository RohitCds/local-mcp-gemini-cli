import json
from typing import Optional, List, Dict, Any
from mcp.types import CallToolResult, Tool, TextContent
from mcp_client import MCPClient
from google.genai import types


class ToolManager:
    @classmethod
    async def get_all_tools(cls, clients: dict[str, MCPClient]) -> list[types.FunctionDeclaration]:
        """Gets all tools from the provided clients and formats them for Gemini."""
        tools = []
        for client in clients.values():
            tool_models = await client.list_tools()
            for t in tool_models:
                # Map MCP tool definitions directly into Gemini Function Declarations
                tools.append(
                    types.FunctionDeclaration(
                        name=t.name,
                        description=t.description,
                        parameters=t.inputSchema,  # Schema definitions map identically
                    )
                )
        return tools

    @classmethod
    async def _find_client_with_tool(
        cls, clients: list[MCPClient], tool_name: str
    ) -> Optional[MCPClient]:
        """Finds the first client that has the specified tool."""
        for client in clients:
            tools = await client.list_tools()
            tool = next((t for t in tools if t.name == tool_name), None)
            if tool:
                return client
        return None

    @classmethod
    async def execute_tool_requests(
        cls, clients: dict[str, MCPClient], function_calls: List[types.FunctionCall]
    ) -> List[Dict[str, Any]]:
        """Executes a list of tool requests from Gemini against the MCP clients.
        
        Returns a structured dictionary matching our Chat execution loop requirements.
        """
        tool_results = []
        
        for call in function_calls:
            tool_name = call.name
            # Gemini wraps arguments inside a native map structure
            tool_input = call.args if call.args else {}

            client = await cls._find_client_with_tool(
                list(clients.values()), tool_name
            )

            if not client:
                tool_results.append({
                    "name": tool_name,
                    "content": "Could not find that tool"
                })
                continue

            try:
                tool_output: CallToolResult | None = await client.call_tool(
                    tool_name, tool_input
                )
                
                items = []
                if tool_output:
                    items = tool_output.content
                    
                content_list = [
                    item.text for item in items if isinstance(item, TextContent)
                ]
                
                # Combine output strings cleanly
                content_text = "\n".join(content_list) if content_list else ""
                
                tool_results.append({
                    "name": tool_name,
                    "content": content_text
                })
                
            except Exception as e:
                error_message = f"Error executing tool '{tool_name}': {e}"
                print(error_message)
                tool_results.append({
                    "name": tool_name,
                    "content": json.dumps({"error": error_message})
                })

        return tool_results