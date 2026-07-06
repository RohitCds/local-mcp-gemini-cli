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

Phase 1: Core Infrastructure (core/gemini.py, mcp_server.py) — Houses the authenticated cloud AI client wrapper and a standalone local micro-server running over system standard input/output (stdio) channels.
•	Phase 2: Gateway Clients (mcp_client.py, core/tools.py) — Establishes the background subprocess connection pipelines and translates local tool schema models into JSON configurations the AI natively understands.
•	Phase 3: Orchestration Brain (core/chat.py, core/cli_chat.py) — Handles conversational persistence, monitors tool calling queues, pre-seeds custom structural histories, and parses page-relative targets.
•	Phase 4: Interface Shell (core/cli.py, main.py) — Drives the asynchronous user interface buffer loops, keybindings, and reactive dropdown autocompletion filters.
🚀 Getting Started
Prerequisites
•	Python 3.10+
•	uv (Fast Python package installer and resolver)
•	A Google AI Studio API Key
Installation & Configuration
	1.	Clone this repository to your local machine:
git clone [https://github.com/YOUR_USERNAME/local-mcp-gemini-cli.git](https://github.com/YOUR_USERNAME/local-mcp-gemini-cli.git)
cd cli_project

	2.	Create a local environment configuration file named .env in the root directory:
GEMINI_API_KEY=your_actual_google_ai_studio_key_here
GEMINI_MODEL=gemini-2.5-flash
USE_UV=1

(Note: The .env file is explicitly protected via .gitignore and will never be tracked or exposed via public source control.)
	3.	Launch the application environment thread using uv:
uv run --active main.py

💻 Usage & Interactivity
Once the active application loop boots up, you can interact with the system via standard messaging or structural shortcuts:
•	Standard Context Mentioning (@): Type an @ symbol anywhere in your prompt line to dynamically open an autocompletion menu containing all exposed server documents. Selecting a file injects its text content straight into the background query layout context.
•	Slash Automation Command (/format): Type /format (e.g., /format report.pdf) to fetch pre-baked prompt instructions from the server. The client intercepts the turn, spins up a dedicated history thread, reads the file via background tools, converts it to clean markdown layout structures, and saves it directly back to the mock vault without any verbose text filler.
🗂️ Project Directory Structure
cli_project/
├── core/
│   ├── cli.py         # Terminal user interface buffer & keybind loops
│   ├── cli_chat.py    # Command interceptors & history translation engines
│   ├── chat.py        # Core chat loop & automated tool execution wheels
│   ├── tools.py       # JSON schema translators and route selectors
│   └── gemini.py      # Stateless model wrappers & payload serializers
├── main.py            # Master context stack bootloader & orchestrator
├── mcp_client.py      # Background stdio process management client
├── mcp_server.py      # FastMCP tool, resource, and prompt provider
├── .gitignore         # Secret file shield exclusions
├── .env               # Private configurations (Local only)
└── README.md          # Project blueprint documentation
