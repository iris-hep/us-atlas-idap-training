# Agentic workflows with National Research Platform models and SSL JupyterHub

## Prerequisites

* Claude Code installed locally (the harness, not the paid plan)
* NRP model access (account + API token)
* A BinderHub repo with `jupyter-server-proxy` and `jupyter-server-mcp` installed

## Account Creation

### National Research Platform (NRP)

1. Create an NRP account at https://nrp.ai.
   - You should have received an email invitation to do so already from the training event organizers
1. Get your LLM token from https://nrp.ai/llmtoken/.
   - **Save this in your password management system**
1. This token is will be used as environmental variable `ANTHROPIC_AUTH_TOKEN`.

### Scalable Systems Laboratory BinderHub

#### BinderHub API Token

1. Navigate to the Scalable Systems Laboratory (SSL) BinderHub https://binderhub.ssl-hep.org/ and click the "log in" button.
1. You will be prompted to select an authentication system.
   Select **CILogon** and select your institution.
1. After login navigate to https://jupyterhub.ssl-hep.org/hub/token.
1. Fill out a request for a new API token:
   - Note: SSL JupyterHub API token
   - Token expires in: 1 Year
   - Permissions: Leave blank.

   Click "Request new API token".
   - **Save the API key in your password management system**

#### Launching a Binder instance

1. Navigate to the Scalable Systems Laboratory (SSL) BinderHub https://binderhub.ssl-hep.org/ and click the "log in" button.
1. You will be prompted to select an authentication system.
   Select **CILogon** and select your institution.
1. After login you will be taken to the BinderHub dashboard.
   You can provide any public repository of your own, but for the purposes of this event enter `matthewfeickert/nrp-jupyterhub-debug` into the "GitHub repository name or URL" field and click the "launch" button.
1. After the Binder instance launches, visit your [Hub control panel](https://jupyterhub.ssl-hep.org/hub/home) and copy the **server name** for your Binder instance.

## Configure Claude Code harness

Download and install Claude Code on your system following [the documentation](https://code.claude.com/docs/en/overview).
Using the Claude Code harness **does not require an Anthropic paid account**.

To avoid having to manually set lots of things, we will use static Claude Code configuration files that will provide most information and then use user-specific configuration files for the rest.
In this directory there is `.claude/settings.json` which provides the settings needed for NRP.
Your user-specific **secrets** go in a `.env` file.
Create `.env` from the template with

```
cp env-template .env
```

and then edit `.env` to have

* `ANTHROPIC_AUTH_TOKEN`
* `JUPYTERHUB_API_TOKEN`
* `USER_EMAIL`
* `SERVER_NAME`

set to your particular information.

**Do NOT commit `.env` to version control.
It contains secrets.**

## Run

From this directory, run

```
bash launch.sh
```

Your Claude Code instance will now have access to the `qwen3` model on NRP and your SSL BinderHub instance.
You can now prompt your model to interact with your Binder instance.

### Example prompt

> Using MCP tools create a Jupyter notebook on the connected Jupyter Lab instance that gives examples of Awkward Array code.

Guidance for working with the remote Jupyter server over MCP lives in [`CLAUDE.md`](CLAUDE.md), which Claude Code loads automatically when launched from this directory.

## Configuration overview

| What | Where |
|------|-------|
| NRP token | https://nrp.ai/llmtoken/ → `.env` |
| BinderHub | https://binderhub.ssl-hep.org/ |
| JupyterHub token | https://jupyterhub.ssl-hep.org/hub/token |
| LLM endpoint | `https://ellm.nrp-nautilus.io/anthropic` |
| Model name | `qwen3` (for opus/sonnet/haiku slots) |
| Static Claude Code config | `.claude/settings.json` (checked in) |
| MCP config | `claude mcp add -s local` (stored per-project in `~/.claude.json`, native `http` transport) |
| MCP port | `3001` (proxied through JupyterHub) |
