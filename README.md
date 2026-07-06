# Local MCP Gemini Automation Engine

A highly responsive, production-grade local AI agent workspace built on Anthropics' **Model Context Protocol (MCP)** and powered by the modern **Google GenAI SDK**. 

This system intercepts custom markdown slash commands (`/format`) and relative resource targeting context syntax (`@`) directly from an asynchronous terminal user interface thread to read, reformat, and manipulate local simulated data files autonomously via background tool chains.

---

## 🛠️ System Architecture

The application is engineered using a decoupled, four-phase micro-process architecture to maximize scalability and isolate runtime concerns:

```text
[Your Terminal UI Input] ──> Catch / or @ Shortcuts (cli.py)
         │
         ▼
[Orchestration Engine]  ──> Intercepts Prompt Template History (cli_chat.py)
         │
         ▼
[Gemini Cloud Engine]   ──> Reads context and returns autonomous Tool Action requests (gemini.py)
         │
         ▼
[Tool Schema Router]    ──> Maps parameters and selects correct target pipeline (tools.py)
         │
         ▼
[MCP Process Gateway]   ──> Streams arguments through background OS text pipes (mcp_client.py)
         │
         ▼
[Local Secure Server]   ──> Edits or Reads your local memory data blocks securely (mcp_server.py)
