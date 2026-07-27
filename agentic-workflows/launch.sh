#!/usr/bin/env bash

if [[ -f ".env" ]]; then
    # Sets ANTHROPIC_AUTH_TOKEN, JUPYTERHUB_API_TOKEN, and JUPYTER_MCP_URL
    . .env
else
    echo -e "\n# Error: .env file not found. Please create a .env file using the ./env-template as an example."
    exit 1
fi

export ANTHROPIC_BASE_URL="https://ellm.nrp-nautilus.io/anthropic"
# Map all Claude Code model slots to the NRP-hosted model
export ANTHROPIC_DEFAULT_OPUS_MODEL="qwen3"
export ANTHROPIC_DEFAULT_SONNET_MODEL="qwen3"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="qwen3"
# Avoid nonessential traffic to Anthropic services from a non-Anthropic endpoint
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1"
export CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY="1"
export CLAUDE_CODE_ENABLE_TELEMETRY="0"
export DISABLE_TELEMETRY="1"
# Allow long request timeouts for slower self-hosted models
export API_TIMEOUT_MS="3000000"
# Claude Code uses ANTHROPIC_AUTH_TOKEN when ANTHROPIC_API_KEY is absent.
# Unsetting it ensures the NRP token is used correctly without triggering a
# login prompt.
unset ANTHROPIC_API_KEY

claude
