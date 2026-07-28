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
