# Jupyter MCP Server - Usage Guide for AI Assistants

## ⚠️ CRITICAL: Remote JupyterHub Instance

This project connects to a **remote JupyterHub server** on the UChicago
Scalable Systems Lab (SSL). The Jupyter server is **NOT** running locally.
Local file tools (`Read`, `Write`, `Edit`, `Bash`) operate on a filesystem the
Jupyter server cannot see. **Always use the `mcp__jupyter__*` tools for
anything that should exist or run on the server.**

| ✅ Correct | ❌ Wrong |
|------------|----------|
| `mcp__jupyter__write(file_path="/home/jovyan/notebook.ipynb", ...)` | `Write(file_path="./notebook.ipynb", ...)` |
| `mcp__jupyter__read_notebook(file_path="example.ipynb")` | `Read(file_path="./example.ipynb")` |
| `mcp__jupyter__bash(command="python -m pip list")` | `Bash("pip list")` (runs locally) |

## Connection Details

- **JupyterHub URL**: `https://jupyterhub.ssl-hep.org`
- **Remote home / Jupyter root**: `/home/jovyan/`
- **Kernel**: Python 3 (`python3` via ipykernel) — verify with
  `list_available_kernelspecs`
- **MCP server**: registered with Claude Code as `jupyter` (HTTP transport,
  served by the `jupyter-server-mcp` extension). Its tools appear with the
  `mcp__jupyter__` prefix.
- **Auth**: a Jupyter server token in the `?token=` query parameter of the MCP
  URL, preconfigured by the user. There is **no OAuth** — never attempt an
  OAuth flow and never `curl` the endpoint directly; the MCP tools
  authenticate internally. If the tools fail to connect at all, that is
  user-side setup — see [README.md](README.md).

## Path Conventions

All paths refer to the **remote server's** filesystem:

- Filesystem tools (`write`, `read`, `ls`) take **absolute** paths:
  `/home/jovyan/example.ipynb`
- Notebook and cell tools (`read_notebook`, `add_cell`, `edit_cell`, …) and
  `open_file` take paths **relative to the Jupyter root**: `example.ipynb`
- `glob` and `grep` default to the Jupyter root when `path` is omitted

## Cell Addressing

Every `cell_id` parameter accepts **either** a cell UUID **or a numeric index
passed as a string** — `cell_id="0"` targets the first cell. Use
`get_cell_id_from_index` when you need the stable UUID.

## Execution Semantics — read before running anything

1. **The run tools return no outputs.** After `run_all_cells` or `run_cell`,
   read results back with `read_notebook(file_path=..., include_outputs=True)`
   or `read_cell` (outputs included by default). An output-free notebook after
   a run usually means `include_outputs` was left at its `False` default in
   `read_notebook` — not that execution failed. (The run tools' own
   descriptions mention a `read_notebook_cells` tool; it does not exist — use
   `read_notebook`/`read_cell`.)
2. **The execution wait is capped at 10 seconds** (`timeout` default and
   maximum). **A timeout does NOT mean the cell failed — the kernel keeps
   running.** For long-running cells (remote file reads, fits): run, tolerate
   the timeout, then poll with `read_cell`/`read_notebook` until outputs
   appear.
3. **`create_notebook` starts with one empty code cell.** Edit cell `"0"`
   instead of adding a new first cell, or skip `create_notebook` and `write`
   complete notebook JSON directly (most reliable for new notebooks).

## Expected MCP Tools

The `jupyter` MCP server is expected to expose all of the tools below. If no
`mcp__jupyter__*` tools are available in the session, the MCP connection is
not set up — stop and ask the user to check `/mcp` (setup is described in
[README.md](README.md)); do **not** fall back to local file tools.

| Group | Tool | Notes |
|-------|------|-------|
| Notebook | `create_notebook` | New notebook; starts with one empty cell (see above) |
| | `write` | Write complete notebook JSON (or any file); absolute path |
| | `read_notebook` | Whole notebook as markdown; `include_outputs` defaults to **False** |
| | `open_file` | Open a file in the JupyterLab UI for the user |
| Cells | `add_cell` | Add a cell above/below a cell, or at the end |
| | `insert_cell` | Insert a cell at a specific index |
| | `edit_cell` | Replace a cell's content and/or type |
| | `delete_cell` | Remove a cell |
| | `read_cell` | One cell as markdown; `include_outputs` defaults to **True** |
| | `get_cell_id_from_index` | Map cell index → UUID |
| Execution | `run_all_cells` | Run the whole notebook; returns no outputs |
| | `run_cell` | Run one cell by `cell_id`; returns no outputs |
| Filesystem | `ls`, `glob`, `grep`, `read` | Explore and read the remote filesystem |
| Shell | `bash` | Run a shell command on the remote server |
| JupyterLab | `list_available_kernelspecs` | List available kernels |
| | `list_all_commands`, `execute_command` | Discover and run JupyterLab frontend commands |

## Which Tool for Which Task

| Task | Tools |
|------|-------|
| Create a notebook with content | `write` complete notebook JSON to `/home/jovyan/<name>.ipynb`; or `create_notebook` + `edit_cell(cell_id="0", ...)` + `add_cell` |
| Run everything and inspect results | `run_all_cells` → `read_notebook(include_outputs=True)` |
| Fix and re-run one cell | `edit_cell` → `run_cell(cell_id=...)` → `read_cell` |
| Locate a notebook or data file | `ls(path="/home/jovyan")` or `glob(pattern="**/*.ipynb")` |
| Search file contents on the server | `grep(pattern=..., include="*.ipynb")` |
| Check installed packages/versions | `bash(command="python -m pip list")` |
| Restart the kernel | `list_all_commands(query="restart")` → `execute_command(command_id=...)` |
| Show the user a file in JupyterLab | `open_file(file_path="example.ipynb")` |

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `file_id_manager` error | Notebook doesn't exist on the server yet, or MCP connection dropped | Create it with `write` first, then use cell tools |
| `404` from notebook tools | Wrong remote path | Locate the file with `ls`/`glob`; notebook paths are relative to `/home/jovyan/` |
| Run "succeeds" but notebook shows no outputs | `read_notebook` defaults to `include_outputs=False` | Re-read with `include_outputs=True` |
| Timeout from `run_cell`/`run_all_cells` | Cell takes longer than the 10 s cap | Not a failure — the kernel continues; poll outputs until they appear |
| OAuth2 redirect / login HTML | Direct HTTP access (e.g. `curl`) to the server | Never curl; the MCP tools handle the token internally |
| Notebook JSON parse error on `write` | Malformed notebook JSON (escaping, invalid characters) | Generate the JSON programmatically and validate before writing |

## Server Libraries

The remote server has the Scikit-HEP stack installed (`awkward`, `numpy`,
`uproot`, `hist`, …). The exact set can change between Binder launches —
verify with `bash(command="python -m pip list")` before assuming a package
exists.
