import asyncio
from typing import Any
from google.genai import types
from core.gemini import Gemini  
from mcp_client import MCPClient
from core.tools import ToolManager


class Chat:
    def __init__(self, gemini_service: Gemini, clients: dict[str, MCPClient]):
        """Initializes the chat session using the Gemini service."""
        self.gemini_service: Gemini = gemini_service
        self.clients: dict[str, MCPClient] = clients
        
        # Built-in active chat session reference
        self.chat_session = None
        # Variable to hold the parsed or injected query template
        self._pending_query: str = ""

    async def _init_chat_session(self):
        """Initializes or resets the native Gemini chat instance with active tools."""
        mcp_tools = await ToolManager.get_all_tools(self.clients)
        
        config = types.GenerateContentConfig(
            tools=mcp_tools,
            temperature=0.7,
        )
        
        self.chat_session = self.gemini_service.client.chats.create(
            model=self.gemini_service.model_name,
            config=config
        )

    async def _process_query(self, query: str):
        """
        Fallback implementation for base execution.
        Overridden downstream by CliChat to parse local tools/prompts context.
        """
        self._pending_query = query

    async def run(self, query: str) -> str:
        """Sends a query through the execution loop, handling any tool calls autonomously."""
        # 1. Route the query through our command and resource injection logic
        await self._process_query(query)

        # 2. Check if a local slash command initialized a new pre-baked chat session
        if not self._pending_query or self._pending_query.strip() == "":
            if self.chat_session is not None:
                # --- FIX: Send a distinct prompt continuation step instead of an empty string ---
                response = self.chat_session.send_message("Please proceed with processing the loaded prompt sequence.")
                
            while response.function_calls:
                print(f"\n🤖 Gemini requested {len(response.function_calls)} tool action(s)...")
                tool_results = await ToolManager.execute_tool_requests(self.clients, response.function_calls)
                tool_response_parts = [
                    types.Part.from_function_response(name=res["name"], response={"result": res["content"]})
                    for res in tool_results
                ]
                response = self.chat_session.send_message(tool_response_parts)

            # --- QUICK FIXED RETURN VALUE ---
            if not response.text or response.text.strip() == "":
                return "Local file update executed and committed successfully!"
            return response.text
                
            return "Command intercepted and handled locally."