"""Jupyter Server configuration exposing notebook tools over MCP.

Registers tools from jupyter-ai-tools with the jupyter-server-mcp extension so
that MCP clients (e.g. Claude Code, see README-claude-code-nrp.md) can create,
edit, and run notebooks on this server.

To use in a BinderHub repo, add to requirements.txt:

    jupyter-server-proxy
    jupyter-server-mcp
    jupyter-ai-tools
    jupyterlab-commands-toolkit

repo2docker does not read Jupyter config from the repo root, so copy this file
into place with a postBuild script:

    #!/bin/bash
    mkdir -p ~/.jupyter
    cp jupyter_server_config.py ~/.jupyter/jupyter_server_config.py
"""

c = get_config()  # noqa: F821

c.MCPExtensionApp.mcp_name = "Jupyter MCP Server"
# Must match the /proxy/<port>/mcp segment of the MCP URL used by the client
c.MCPExtensionApp.mcp_port = 3001

# "module:function" specs resolved at server startup.
# Function names verified against jupyter-ai-tools 0.6.1.
c.MCPExtensionApp.mcp_tools = [
    # Notebook manipulation
    "jupyter_ai_tools.toolkits.notebook:create_notebook",
    "jupyter_ai_tools.toolkits.notebook:read_notebook",
    "jupyter_ai_tools.toolkits.notebook:read_cell",
    "jupyter_ai_tools.toolkits.notebook:add_cell",
    "jupyter_ai_tools.toolkits.notebook:insert_cell",
    "jupyter_ai_tools.toolkits.notebook:edit_cell",
    "jupyter_ai_tools.toolkits.notebook:delete_cell",
    "jupyter_ai_tools.toolkits.notebook:get_cell_id_from_index",
    "jupyter_ai_tools.toolkits.notebook:list_available_kernelspecs",
    # Cell execution through the live JupyterLab session
    # (requires jupyterlab-commands-toolkit and an open JupyterLab browser tab)
    "jupyter_ai_tools.toolkits.jupyterlab:open_file",
    "jupyter_ai_tools.toolkits.jupyterlab:run_cell",
    "jupyter_ai_tools.toolkits.jupyterlab:run_all_cells",
    # File system access within the user server
    "jupyter_ai_tools.toolkits.file_system:ls",
    "jupyter_ai_tools.toolkits.file_system:read",
    "jupyter_ai_tools.toolkits.file_system:write",
    "jupyter_ai_tools.toolkits.file_system:glob",
    "jupyter_ai_tools.toolkits.file_system:grep",
    # Arbitrary shell execution on the (ephemeral) Binder pod.
    # Uncomment if wanted for the training demo.
    # "jupyter_ai_tools.toolkits.code_execution:bash",
]
