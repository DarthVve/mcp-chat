# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MCP Chat is a CLI application that provides interactive chat with Claude models via the Anthropic API, using the Model Context Protocol (MCP) for document retrieval, command-based prompts, and extensible tool integrations.

## Setup & Running

```bash
# Install dependencies (uses uv)
uv pip install -e .

# Run the app
uv run main.py

# Run with additional MCP server scripts
uv run main.py path/to/server1.py path/to/server2.py

# Run without uv (set USE_UV=0 or omit it)
python main.py
```

Required environment variables in `.env`:

- `ANTHROPIC_API_KEY` — Anthropic API key
- `CLAUDE_MODEL` — model identifier (e.g. `claude-sonnet-4-20250514`)
- `USE_UV` — set to `1` to use `uv run` for the built-in MCP server (default: `0`, uses `python`)

No lint or test infrastructure exists yet.

## Architecture

The app has two main layers: an **MCP layer** (client/server for tools, resources, and prompts) and a **chat layer** (conversation management with Claude).

### MCP Layer

- `mcp_server.py` — FastMCP server exposing an in-memory document store via tools (`read_doc`, `edit_doc`), resources (`docs://documents`, `docs://documents/{doc_id}`), and prompts (`format_doc`). Runs as a subprocess communicating over stdio.
- `mcp_client.py` — `MCPClient` wraps an MCP `ClientSession` over stdio transport. Supports async context manager for lifecycle. Each MCP server gets its own client instance.

### Chat Layer

- `core/claude.py` — `Claude` class wraps the Anthropic SDK (`anthropic.Anthropic`). Handles message creation with support for tools, system prompts, and extended thinking.
- `core/chat.py` — `Chat` base class implements the agentic tool-use loop: sends messages to Claude, detects `tool_use` stop reason, executes tools via `ToolManager`, feeds results back, and loops until a text response.
- `core/cli_chat.py` — `CliChat` extends `Chat` with document resource extraction (`@doc_id` mentions) and command processing (`/command doc_id` dispatches to MCP prompts).
- `core/tools.py` — `ToolManager` aggregates tools from all MCP clients and routes tool execution requests to the correct client.

### CLI Layer

- `core/cli.py` — `CliApp` uses `prompt_toolkit` for the interactive REPL with tab-completion for `/commands` and `@resources`, auto-suggestions, and key bindings.
- `main.py` — Entry point. Loads env, creates Claude service, connects MCP clients (built-in doc server + any additional server scripts from CLI args), and starts the REPL.

### Key Data Flow

1. User types query in REPL → `CliApp` passes to `CliChat.run()`
2. `CliChat._process_query()` checks for `/command` or extracts `@doc` mentions into context
3. `Chat.run()` sends messages to Claude with all available tools
4. If Claude requests tool use → `ToolManager` finds the right MCP client and executes → result fed back → loop continues
5. Final text response printed to user
