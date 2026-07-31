#!/usr/bin/env bash

# Static Claude Code configuration (NRP endpoint, model mapping, telemetry
# opt-outs, timeouts) lives in .claude/settings.json. All user secrets
# (NRP token, JupyterHub token) live in .env. The only per-launch step remaining
# is (re)registering the Jupyter MCP server, whose URL changes on every Binder
# relaunch.
# Windows users: skip this script, set ANTHROPIC_AUTH_TOKEN in your environment
# and manually register:
#   claude mcp remove jupyter
#   claude mcp add -s local -t http jupyter "https://jupyterhub.ssl-hep.org/user/<email>/<server-name>/proxy/3001/mcp?token=<token>"
# then run 'claude'.

if [[ -f "${HOME}/.secrets/.env" ]]; then
    # Sets ANTHROPIC_AUTH_TOKEN, JUPYTERHUB_API_TOKEN, and JUPYTER_MCP_URL
    . "${HOME}/.secrets/.env"
else
    echo -e "\n# Error: ${HOME}/.secrets/.env file not found. Please create a .env file using the ./env-template as an example."
    exit 1
fi

# Re-register the Jupyter MCP server for the current Binder server.
# 'claude mcp add' errors if the name is already registered, so remove first.
claude mcp remove jupyter > /dev/null 2>&1
claude mcp add -s local -t http jupyter "${JUPYTER_MCP_URL}"

# Add IRIS-HEP marketplace
claude plugin marketplace add --scope local https://github.com/iris-hep/marketplace

# Claude Code uses ANTHROPIC_AUTH_TOKEN when ANTHROPIC_API_KEY is absent.
# Unsetting it ensures the NRP token is used correctly without triggering a
# login prompt.
unset ANTHROPIC_API_KEY

claude
