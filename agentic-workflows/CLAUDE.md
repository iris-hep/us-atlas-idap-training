# Agentic workflows — Jupyter MCP usage guide

## ⚠️ CRITICAL: Remote JupyterHub Instance

This project connects Claude Code to a **remote JupyterHub server** on the
UChicago Scalable Systems Lab (SSL). The Jupyter server is **NOT** running
locally. Local file tools (`Read`, `Write`, `Edit`, `Bash`) operate on a
filesystem the Jupyter server cannot see. **Always use the `mcp__jupyter__*`
tools for anything that should exist or run on the server.**

| ✅ Correct | ❌ Wrong |
|------------|----------|
| `mcp__jupyter__use_notebook(notebook_path="example.ipynb", mode="create", ...)` | `Write(file_path="./example.ipynb", ...)` |
| `mcp__jupyter__read_cell(cell_index=0)` | `Read(file_path="./example.ipynb")` |
| `mcp__jupyter__execute_code(code="!python -m pip list")` | `Bash("pip list")` (runs locally) |

## Connection Details

- **JupyterHub URL**: `https://jupyterhub.ssl-hep.org`
- **Remote home / Jupyter root**: `/home/jovyan/`
- **Kernel**: Python 3 (`python3` via ipykernel) — verify with `list_kernels`
- **MCP server**: registered with Claude Code as `jupyter` (HTTP transport,
  served by [`jupyter-mcp-server`](https://github.com/datalayer/jupyter-mcp-server)
  on port 3001, proxied through JupyterHub). Its tools appear with the
  `mcp__jupyter__` prefix.
- **Auth**: a Jupyter token in the `?token=` query parameter of the MCP URL,
  preconfigured by the user. There is **no OAuth** — never attempt an OAuth
  flow and never `curl` the endpoint directly; the MCP tools authenticate
  internally. If only `mcp__jupyter__authenticate` /
  `mcp__jupyter__complete_authentication` stubs are visible instead of the
  real tools, the connection is broken on the user's side (stale token, or a
  relaunched Binder pod with a new URL) — stop and ask the user to re-run
  `launch.sh` (see [README.md](README.md)); do **not** start the OAuth flow
  and do **not** fall back to local file tools.

## Core Workflow — activate a notebook first

`jupyter-mcp-server` is notebook-session-centric. The cell tools take **no
path parameter** — they operate on the currently **active** notebook:

1. `use_notebook(notebook_name=..., notebook_path=..., mode="connect")` to
   work on an existing notebook, or `mode="create"` for a new one. This
   starts (or attaches) a kernel and makes the notebook active.
2. Do cell operations (insert, edit, execute, read).
3. Optionally `restart_notebook` for a fresh kernel, `unuse_notebook` to
   disconnect when done.

`notebook_name` is a logical handle you choose (e.g. `"analysis"`); the
management tools (`read_notebook`, `restart_notebook`, `unuse_notebook`) take
the **name**, not the path. `list_notebooks` shows every connected notebook
and marks the active one with ✓.

## Path Conventions

All paths refer to the **remote server's** filesystem, **relative to the
Jupyter root** `/home/jovyan/`:

- `use_notebook(notebook_path="example.ipynb", ...)`
- `list_files(path="")` starts at the root; `max_depth` defaults to 1 (max 3)
- New kernels start with the notebook's directory as their working directory
  (matching JupyterLab behavior)

## Cell Addressing

- Cells are addressed by **0-based integer index** (`cell_index`) — there are
  no cell UUIDs.
- `insert_cell` / `insert_execute_code_cell`: `cell_index=-1` **appends** at
  the end of the notebook.
- **Indices shift** after `insert_cell`, `delete_cell`, and `move_cell` —
  re-read the structure with `read_notebook(response_format="brief")` after
  structural edits before doing more index-based operations.
- `delete_cell` takes a **list** (`cell_indices`); when deleting several
  cells, list them in **descending** index order to avoid index shifting.

## Execution Semantics — read before running anything

1. **Execution tools return outputs directly** (text, HTML, and images) — no
   separate read-back step is needed. To re-inspect saved outputs later, use
   `read_cell(cell_index=...)` (`include_outputs` defaults to `True`).
2. **Timeouts**: `execute_cell` defaults to the server-side limit
   (`JUPYTER_MCP_EXECUTION_TIMEOUT`, 120 s unless reconfigured; max 3600 s).
   For long-running cells (remote file reads, fits), pass a generous
   `timeout` up front and set `stream=True` to get progress updates instead
   of silence. If a timeout does occur, do not assume the cell failed —
   `read_cell` to check whether outputs landed before re-running.
3. **`execute_code` runs code directly on the kernel without touching the
   notebook** — use it for scratch checks, variable inspection, `%` magics,
   and `!` shell commands (default timeout 30 s). Do **not** use it for
   imports or assignments the notebook depends on: the kernel state changes
   but no cell records it, so the notebook won't reproduce.
4. **There is no bulk "run all" tool in the base tool set** — run a whole
   notebook by calling `execute_cell` for each index 0…N−1 in order (get N
   from `read_notebook(response_format="brief")`). If an optional
   JupyterLab-integration tool such as `notebook_run-all-cells` is exposed,
   you may use it instead.

## Expected MCP Tools

The `jupyter` MCP server is expected to expose the tools below. If none of
them are available in the session, the MCP connection is not set up — see the
auth note above; do **not** fall back to local file tools.

| Group | Tool | Notes |
|-------|------|-------|
| Server | `list_files` | Browse the remote filesystem; paginated (default `limit=25`, `0` = unlimited), `max_depth` ≤ 3, glob `pattern` filter |
| | `list_kernels` | List running/available kernel sessions |
| Notebook | `use_notebook` | Connect to or create a notebook and make it active; `mode="connect"` or `"create"` |
| | `list_notebooks` | Connected notebooks, kernel status, active marker ✓ |
| | `read_notebook` | Cell listing by `notebook_name`; `response_format="brief"` (first line + line count) or `"detailed"`; paginated (default `limit=20` cells, `0` = unlimited) |
| | `restart_notebook` | Restart the notebook's kernel (clears all state) |
| | `unuse_notebook` | Disconnect and release the kernel |
| Cells | `insert_cell` | Insert code/markdown cell at index; `-1` appends |
| | `insert_execute_code_cell` | Insert a code cell and execute it in one step |
| | `overwrite_cell_source` | Replace a cell's full source; returns a diff |
| | `edit_cell_source` | Targeted find-and-replace within a cell (`old_string`/`new_string`) |
| | `delete_cell` | Delete cells by index list — descending order! |
| | `move_cell` | Move a cell from one index to another |
| | `clear_cell_output` | Clear one cell's outputs and execution count |
| | `read_cell` | One cell's metadata, source, and outputs |
| Execution | `execute_cell` | Run one cell by index; returns outputs; `timeout`, `stream`, `progress_interval` |
| | `execute_code` | Run code on the kernel without saving it to the notebook |

A `connect_to_jupyter` tool may also be exposed — never use it here; the
connection is preconfigured by `launch.sh`.

## Which Tool for Which Task

| Task | Tools |
|------|-------|
| Create a notebook with content | `use_notebook(mode="create")` → `insert_cell(cell_index=-1, ...)` per cell, or `insert_execute_code_cell` to run while building |
| Work on an existing notebook | `use_notebook(mode="connect")` → cell tools |
| Run everything and inspect results | `execute_cell` for each index in order — outputs come back directly |
| Fix and re-run one cell | `overwrite_cell_source` (or `edit_cell_source`) → `execute_cell` |
| Locate a notebook or data file | `list_files(pattern="*.ipynb", max_depth=3, limit=0)` |
| Search file contents on the server | `execute_code(code="!grep -rn 'pattern' .")` |
| Check installed packages/versions | `execute_code(code="!python -m pip list")` |
| Quick variable/state inspection | `execute_code` (not saved to the notebook) |
| Restart the kernel | `restart_notebook(notebook_name=...)` |

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Only `authenticate`/`complete_authentication` tools visible | MCP connection not established (stale token, or Binder relaunch changed the URL) | Do **not** start OAuth; ask the user to re-run `launch.sh` — see [README.md](README.md) |
| Cell tools error with no/unknown notebook | No active notebook in this MCP session | `use_notebook` first; check with `list_notebooks` |
| `404` / "not found" from `use_notebook` | Wrong remote path | Locate the file with `list_files`; paths are relative to `/home/jovyan/` |
| Timeout from `execute_cell` | Cell exceeds the timeout (default 120 s) | `read_cell` to check whether outputs landed; re-run with a larger `timeout` and `stream=True` |
| Edits land in the wrong cell | Indices shifted after insert/delete/move | Re-read with `read_notebook(response_format="brief")` before more index-based edits; delete in descending order |
| `list_files` output looks incomplete | Pagination (default 25 items) or `max_depth` (default 1) | Set `limit=0`, raise `max_depth` (≤ 3), or filter with `pattern` |
| Login HTML / OAuth redirect | Direct HTTP access (e.g. `curl`) to the server | Never curl; the MCP tools handle the token internally |

## Server Libraries

The remote server has the Scikit-HEP stack installed (`awkward`, `numpy`,
`uproot`, `hist`, …). The exact set can change between Binder launches —
verify with `execute_code(code="!python -m pip list")` before assuming a
package exists.
