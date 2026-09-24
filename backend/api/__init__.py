"""Application layer (FastAPI ``/api/v1``) for the Admin/Coach frontend.

``backend/reporting`` stays pure (no DB/HTTP); this package adds persistence,
authentication, permissions and HTTP routes around it. The ChatGPT bridge
(``mcp/openapi_server.py``) and MCP stdio server are unaffected.
"""
