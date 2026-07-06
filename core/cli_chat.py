from typing import List, Tuple, Any
from mcp.types import Prompt, PromptMessage
from core.tools import ToolManager
from core.chat import Chat
from core.gemini import Gemini  # Swapped from Claude
from mcp_client import MCPClient
from google.genai import types


class CliChat(Chat):
    def __init__(
        self,
        doc_client: MCPClient,
        clients: dict[str, MCPClient],
        gemini_service: Gemini,
    ):
        # Pass gemini_service upward to match our updated base Chat class
        super().__init__(clients=clients, gemini_service=gemini_service)
        self.doc_client: MCPClient = doc_client

    async def list_prompts(self) -> list[Prompt]:
        return await self.doc_client.list_prompts()

    async def list_docs_ids(self) -> list[str]:
        try:
            # Fetch whatever data format the mcp_client.py extracted
            raw_data = await self.doc_client.read_resource("docs://documents")
            
            # Case 1: It's already a clean list of document IDs
            if isinstance(raw_data, list):
                return [str(d).replace("docs://documents/", "") for d in raw_data]
            
            # Case 2: It's a string block (common if server sends raw text)
            if isinstance(raw_data, str):
                cleaned = raw_data.strip()
                
                # If the string contains a JSON array format string, decode it
                if cleaned.startswith("[") and cleaned.endswith("]"):
                    import json
                    try:
                        parsed = json.loads(cleaned)
                        if isinstance(parsed, list):
                            return [str(d).replace("docs://documents/", "") for d in parsed]
                    except Exception:
                        pass
                
                # Split common delimiters: newlines or commas
                if "\n" in cleaned:
                    return [d.strip().replace("docs://documents/", "") for d in cleaned.split("\n") if d.strip()]
                if "," in cleaned:
                    return [d.strip().replace("docs://documents/", "") for d in cleaned.split(",") if d.strip()]
                
                # Single document string fallback
                if cleaned:
                    return [cleaned.replace("docs://documents/", "")]
            
            return []
            
        except Exception as e:
            print(f"\n[CLI Chat Resource Resolution Error]: {e}")
            return []
    async def get_doc_content(self, doc_id: str) -> str:
        return await self.doc_client.read_resource(f"docs://documents/{doc_id}")

    async def get_prompt(
        self, command: str, doc_id: str
    ) -> list[PromptMessage]:
        return await self.doc_client.get_prompt(command, {"doc_id": doc_id})

    async def _extract_resources(self, query: str) -> str:
        mentions = [word[1:] for word in query.split() if word.startswith("@")]

        doc_ids = await self.list_docs_ids()
        mentioned_docs: list[Tuple[str, str]] = []

        for doc_id in doc_ids:
            if doc_id in mentions:
                content = await self.get_doc_content(doc_id)
                mentioned_docs.append((doc_id, content))

        return "".join(
            f'\n<document id="{doc_id}">\n{content}\n</document>\n'
            for doc_id, content in mentioned_docs
        )

    async def _process_command(self, query: str) -> bool:
        """Processes special '/' commands and pre-loads the model's history."""
        if not query.startswith("/"):
            return False

        print(f"\n[DIAGNOSTIC] Intercepted slash command: {query}") # <-- test line
        words = query.split()
        command = words[0].replace("/", "")

        if not command:
            print("\n[CLI System] No command specified. Try using a valid prompt format (e.g., /summarize doc.md)")
            return True

        if len(words) < 2:
            print(f"\n[CLI System] The /{command} command requires a document target. Usage: /{command} <document_id>")
            return True

        target_doc = words[1]

        try:
            available_prompts = await self.list_prompts()
            available_names = [p.name for p in available_prompts]
            print(f"[DIAGNOSTIC] Available prompts on your MCP server: {available_names}") # <-- test line
            
            if command not in available_names:
                print(f"\n[CLI System] Error: '{command}' is not a registered prompt on your MCP Server.")
                self._pending_query = ""
                raise ValueError("Invalid local command shortcut executed.")

            # Fetch the system/user messages preset defined by our MCP server prompt
            mcp_messages = await self.doc_client.get_prompt(
                command, {"doc_id": target_doc}
            )
            print(f"[DIAGNOSTIC] Successfully fetched prompt template from MCP server!") # <-- test line

            gemini_history = convert_mcp_prompts_to_gemini_contents(mcp_messages)

            # --- FIX: Remove 'await' from this synchronous SDK call ---
            mcp_tools = self.gemini_service.client.chats.create(
                model=self.gemini_service.model_name,
                history=gemini_history,
                config=types.GenerateContentConfig(
                    tools=await ToolManager.get_all_tools(self.clients),
                    temperature=0.7,
                )
            )
            self.chat_session = mcp_tools
            return True
            self.chat_session = mcp_tools
            return True

        except Exception as e:
            print(f"\n[MCP Prompt Execution Error]: {e}")
            self._pending_query = "" # Wipe out query so it doesn't leak to web API
            return True

    async def _process_query(self, query: str):
        """Prepares a text query with pre-loaded resource injection."""
        try:
            if await self._process_command(query):
                return
        except ValueError:
            # Intercepted local error - prevent cloud execution completely
            self._pending_query = "The user entered an invalid local slash command. Inform them briefly of the error."
            return
        # Fetch document references ahead of time from our server
        added_resources = await self._extract_resources(query)

        prompt = f"""
        The user has a question:
        <query>
        {query}
        </query>

        The following context may be useful in answering their question:
        <context>
        {added_resources}
        </context>

        Note the user's query might contain references to documents like "@report.docx". The "@" is only
        included as a way of mentioning the doc. The actual name of the document would be "report.docx".
        If the document content is included in this prompt, you don't need to use an additional tool to read the document.
        Answer the user's question directly and concisely. Start with the exact information they need. 
        Don't refer to or mention the provided context in any way - just use it to inform your answer.
        """

        # Instead of self.messages.append(), the execution string query is passed
        # down cleanly directly within the base run() method
        self._pending_query = prompt


def convert_mcp_prompts_to_gemini_contents(mcp_messages: List[PromptMessage]) -> List[types.Content]:
    """Translates MCP-standard PromptMessages into native Gemini Content blocks."""
    gemini_contents = []
    
    for msg in mcp_messages:
        role = "user" if msg.role == "user" else "model"
        text_content = ""
        
        # Safely extract text out of the dynamic MCP content block
        if isinstance(msg.content, str):
            text_content = msg.content
        elif isinstance(msg.content, list):
            # If it's a list of components, grab text components
            text_blocks = []
            for item in msg.content:
                if hasattr(item, "text"):
                    text_blocks.append(item.text)
                elif isinstance(item, dict) and "text" in item:
                    text_blocks.append(item["text"])
            text_content = " ".join(text_blocks)
        elif hasattr(msg.content, "text"):
            text_content = msg.content.text
            
        gemini_contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=text_content)]
            )
        )
        
    return gemini_contents