# Jupyter MCP Server - Usage Guide for AI Assistants

## ⚠️ CRITICAL: Remote JupyterHub Instance

This project connects to a **remote JupyterHub server** hosted on NRP (National Research Platform). The Jupyter server is **NOT** running locally.

## Connection Details

- **JupyterHub URL**: `https://jupyterhub.ssl-hep.org`
- **MCP Endpoint**: Defined in `$JUPYTER_MCP_URL` environment variable (includes auth token)
- **Remote Home Directory**: `/home/jovyan/` (this is where notebooks are saved on the server)
- **Kernel**: Python 3 (ipykernel) - Python 3.10.19

## Key Rules for AI Assistants

### 1. Use MCP Tools, Not Local File Operations

When working with notebooks, **always use the `mcp__jupyter__*` tools**:

| ✅ Correct | ❌ Wrong |
|------------|----------|
| `mcp__jupyter__write(file_path="/home/jovyan/notebook.ipynb", ...)` | `Write(file_path="./notebook.ipynb", ...)` |
| `mcp__jupyter__read_notebook(file_path="example.ipynb")` | `Read(file_path="./example.ipynb")` |
| `mcp__jupyter__add_cell(file_path="example.ipynb", ...)` | Writing to local .ipynb file |

**Why**: Local file operations write to your filesystem, which is completely separate from the remote JupyterHub server. The MCP tools communicate directly with the remote server.

### 2. File Paths Are Remote Server Paths

All file paths in MCP tool calls refer to paths **on the JupyterHub server**:

```python
# Correct - absolute path on remote server
mcp__jupyter__write(file_path="/home/jovyan/my-notebook.ipynb", content=...)

# Correct - relative path from server working directory  
mcp__jupyter__write(file_path="my-notebook.ipynb", content=...)

# Wrong - this writes to local filesystem, invisible to Jupyter server
Write(file_path="/home/feickert/Code/.../my-notebook.ipynb", content=...)
```

### 3. Authentication Is Handled Automatically

The `$JUPYTER_MCP_URL` environment variable contains the OAuth2 authentication token. The MCP tools use this automatically.

```bash
# DO NOT do this - you'll get OAuth2 redirect issues
curl $JUPYTER_MCP_URL/api/contents/

# DO this - MCP tools handle auth internally
mcp__jupyter__read_notebook(file_path="...")
```

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `mcp__jupyter__list_available_kernelspecs` | List available Python kernels on server |
| `mcp__jupyter__create_notebook` | Create new notebook on remote server |
| `mcp__jupyter__read_notebook` | Read notebook contents as markdown |
| `mcp__jupyter__write` | Write complete notebook JSON to server |
| `mcp__jupyter__add_cell` | Add cell to existing notebook |
| `mcp__jupyter__edit_cell` | Edit cell content/type on existing notebook |
| `mcp__jupyter__run_all_cells` | Execute all cells in notebook |
| `mcp__jupyter__open_file` | Open file in JupyterLab UI |

## Typical Workflow

### Creating a New Notebook with Content

```
Step 1: Create notebook (optional - can also just write directly)
  → mcp__jupyter__create_notebook(file_path="example.ipynb", kernel_name="python3")

Step 2: Write content OR add/edit cells
  → mcp__jupyter__write(file_path="example.ipynb", content="{...notebook JSON...}")
  OR
  → mcp__jupyter__add_cell(file_path="example.ipynb", cell_type="code", content="...")

Step 3: Execute (optional)
  → mcp__jupyter__run_all_cells(file_path="example.ipynb")

Step 4: Read results
  → mcp__jupyter__read_notebook(file_path="example.ipynb")
```

### Recommended Approach for New Notebooks

Use `mcp__jupyter__write` with complete notebook JSON content. This is more reliable than creating an empty notebook and adding cells one at a time.

## Troubleshooting

### "file_id_manager" Error

**Cause**: The notebook file doesn't exist on the server yet, or MCP lost connection.

**Solution**: Use `mcp__jupyter__write` to create the notebook first, then use cell-editing tools if needed.

### 404 Errors on read_notebook

**Cause**: The file path is incorrect or the notebook doesn't exist on the server.

**Solution**: Verify the path. Use `/home/jovyan/` prefix or a simple relative filename.

### OAuth2 Redirect When Using curl

**Cause**: Trying to access the Jupyter API directly without proper authentication headers.

**Solution**: Don't use curl. The MCP tools handle authentication internally via the token in `$JUPYTER_MCP_URL`.

### Notebook JSON Parse Errors

**Cause**: Malformed notebook JSON (often from escaped quotes or invalid characters in source strings).

**Solution**: Use Python to generate valid JSON, or carefully escape special characters in notebook source strings.

## Environment Setup

The `.env` file contains:
- `JUPYTER_MCP_URL` - Full MCP endpoint with authentication token
- `ANTHROPIC_AUTH_TOKEN` - API token for NRP-hosted models  
- `ANTHROPIC_BASE_URL` - NRP API endpoint (`https://ellm.nrp-nautilus.io/anthropic`)

Source this file before running claude:
```bash
source .env
claude
```

## Server Libraries

The remote JupyterHub instance has the Scikit-HEP stack installed:
- `awkward` - Jagged array operations
- `numpy` - Numerical computing
- `uproot` - ROOT file I/O
- `vector` - Lorentz vectors
- `hist` - Histogramming
- `pyhf` - HistFactory in Python

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────┐
│  JUPYTER MCP - QUICK REFERENCE                                  │
├─────────────────────────────────────────────────────────────────┤
│  Remote Server: jupyterhub.ssl-hep.org                          │
│  Remote Home:   /home/jovyan/                                   │
│  Auth:          Via $JUPYTER_MCP_URL (automatic)                │
├─────────────────────────────────────────────────────────────────┤
│  DO:   mcp__jupyter__write(file_path="/home/jovyan/x.ipynb")    │
│  DON'T: Write() to local filesystem paths                       │
├─────────────────────────────────────────────────────────────────┤
│  DO:   Use MCP tools for all notebook operations                │
│  DON'T: Use curl or direct API calls                            │
├─────────────────────────────────────────────────────────────────┤
│  ERROR: "file_id_manager" → Create notebook with write() first  │
│  ERROR: 404 → Check file path is on remote server               │
└─────────────────────────────────────────────────────────────────┘
```