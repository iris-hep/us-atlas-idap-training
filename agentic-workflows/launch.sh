#!/usr/bin/env bash

# Static Claude Code configuration (NRP endpoint, model mapping, telemetry
# opt-outs, timeouts) lives in .claude/settings.json, and the NRP token in
# .claude/settings.local.json — see README-claude-code-nrp.md. The only
# per-launch step left is (re)registering the Jupyter MCP server, whose URL
# changes on every Binder relaunch. Windows users: skip this script and run
# the 'claude mcp add' command from the README manually, then run 'claude'.

if [[ -f ".env" ]]; then
    # Sets JUPYTERHUB_API_TOKEN and JUPYTER_MCP_URL
    . .env
else
    echo -e "\n# Error: .env file not found. Please create a .env file using the ./env-template as an example."
    exit 1
fi

# Re-register the Jupyter MCP server for the current Binder server.
# 'claude mcp add' errors if the name is already registered, so remove first.
claude mcp remove -s local jupyter > /dev/null 2>&1
claude mcp add -s local -t http jupyter "${JUPYTER_MCP_URL}"

claude
