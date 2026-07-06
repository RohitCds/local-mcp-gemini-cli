import os
from typing import Any
from google import genai
from google.genai import types


class Gemini:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        """Initializes the Gemini client using the official Google GenAI SDK."""
        # The SDK automatically looks for the GEMINI_API_KEY environment variable
        self.client = genai.Client()
        self.model_name = model_name

    def chat(self, messages: list[Any], tools: list[Any] = None) -> Any:
        """Sends a one-off structured message history block to the model.
        
        Note: While our Chat loop handles conversational state natively, 
        this method provides compatibility for direct, stateless execution.
        """
        config = types.GenerateContentConfig(
            tools=tools,
            temperature=0.7,
        )
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=messages,
            config=config,
        )
        return response

    @staticmethod
    def text_from_message(response: Any) -> str:
        """Extracts the final markdown/text content from Gemini's response object."""
        if response.text:
            return response.text
        return ""

    @staticmethod
    def add_assistant_message(messages: list[Any], response: Any):
        """Appends Gemini's response (including potential tool calls) to a manual history list."""
        # If Gemini generated an assistant turn, we append its candidates' content block
        if response.candidates:
            messages.append(response.candidates[0].content)

    @staticmethod
    def add_user_message(messages: list[Any], tool_response_parts: list[Any]):
        """Appends tool execution results back into a manual history list as a user turn."""
        # In Gemini, tool execution results are sent back as a collection of Parts
        messages.append(
            types.Content(
                role="user",
                parts=tool_response_parts
            )
        )