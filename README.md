# Google Tasks MCP Server (Python)

A Model Context Protocol (MCP) server for Google Tasks, written in Python and running with FastMCP.
Mirrors the functionality of [google-tasks-mcp-js](https://github.com/modelcontextprotocol/servers/tree/main/src/google-tasks).

## Features
- Manage Task Lists
- Create, Update, Delete Tasks
- Filter tasks (Due today, Overdue)
- Dockerized deployment

## Setup

### Prerequisites
1. **Google Cloud Project**: Enable "Tasks API".
2. **Credentials**:
   - **Option A (Environment Variables)**: Set `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_REFRESH_TOKEN`.
   - **Option B (File-based)**: Place `credentials.json` (OAuth Client Secrets) in the root. The server will launch an interactive flow to generate `token.json` on first run.

### Local Development

1. Install dependencies:
   ```bash
   pip install -r pyproject.toml
   # OR using uv
   uv run python -m src.server
   ```

2. Run the server:
   ```bash
   python -m src.server
   ```
   Server will listen on port 3333.

### Docker

1. Build:
   ```bash
   docker build -t google-tasks-mcp .
   ```

2. Run (Env Vars):
   ```bash
   docker run -p 3333:3333 \
     -e GOOGLE_CLIENT_ID=... \
     -e GOOGLE_CLIENT_SECRET=... \
     -e GOOGLE_REFRESH_TOKEN=... \
     google-tasks-mcp
   ```

3. Run (Binder Mount for Token):
   ```bash
   touch token.json # Ensure it exists or mount folder
   docker run -p 3333:3333 \
     -v $(pwd)/credentials.json:/app/credentials.json \
     -v $(pwd)/token.json:/app/token.json \
     google-tasks-mcp
   ```

## Tools available
- `list_task_lists`
- `create_task`
- `get_current_tasks`
- `update_task`
- `delete_task`
- `search_tasks`
