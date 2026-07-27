#!/usr/bin/env bash

if [[ -f ".env" ]]; then
    # Sets ANTHROPIC_AUTH_TOKEN
    . .env
else
    echo -e "\n# Error: .env file not found. Please create a .env file using the ./env-template as an example."
    exit 1
fi

export ANTHROPIC_BASE_URL="https://ellm.nrp-nautilus.io/anthropic"
# Claude Code uses ANTHROPIC_AUTH_TOKEN when ANTHROPIC_API_KEY is absent.
# Unsetting it ensures the NRP token is used correctly without triggering a
# login prompt.
unset ANTHROPIC_API_KEY

claude
