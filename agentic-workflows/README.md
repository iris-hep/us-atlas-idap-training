# Agentic workflows with National Research Platform models and SSL JupyterHub

https://binderhub.ssl-hep.org/

https://binderhub.ssl-hep.org/v2/gh/matthewfeickert/nrp-jupyterhub-debug/HEAD

https://code.claude.com/docs/en/env-vars

https://github.com/fengpinghu/simple

https://<YOUR_JUPYTERHUB_URL>/user/<your-email>/proxy/3001/mcp?token=<YOUR_JUPYTER_TOKEN>

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
1. This token is will be used as `ANTHROPIC_AUTH_TOKEN` environmental variable.
