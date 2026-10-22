# Guardian Angel read-only MCP server

Install the optional dependencies with `pip install -e ".[agents]"`, then run
`python mcp-server/server.py`. It exposes only sanitized evaluation cases and incident status.
It cannot read the application database, receipts, credentials, prompts, or raw incident logs.

