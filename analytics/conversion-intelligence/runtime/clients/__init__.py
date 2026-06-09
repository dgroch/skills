"""API clients for the Conversion Intelligence Programme.

All clients talk to the underlying vendor APIs directly (no desktop/npx MCP
servers) so the loop can run headless on the VPS. Each client fails soft:
constructors validate config and raise a clear error, but per-call failures
return structured error payloads where practical so the loop can log a Partial
run rather than crashing.
"""
