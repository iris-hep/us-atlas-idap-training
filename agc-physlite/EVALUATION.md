# agc-physlite — upgrade evaluation & recommendations

**Status: evaluation only.** Per the task scope, no code, notebook, or `pixi`
files in `agc-physlite/` were modified. This document is the deliverable: an
assessment of what a migration to the modern stack (coffea 2026.7 virtual
arrays, current dask, pyhf, cabinetry) would involve, the risks, and a
recommended path. It complements the migrations already applied to `columnar/`,
`coffea/`, and `sample-game/`.

## 1. Summary

`agc-physlite` is an ATLAS top-quark Analysis Grand Challenge (single-top
s/t/tW, ttbar, W+jets) on ATLAS Open Data PHYSLITE, ending in a `cabinetry`/`pyhf`
statistical fit. It is the most involved notebook in the repository and the
**highest-risk** to upgrade, for three reasons:

1. It drives execution through the **legacy `processor.Runner` + `DaskExecutor`**
   chunked model plus an eager single-file `from_root(...).events()` — exactly
   the "dask-dag-compute" pattern being retired.
2. It reads data over **hard-coded, site-specific xrootd endpoints** (UChicago
   XCache / coffea-casa) and connects to a **fixed dask scheduler** address.
3. It couples a **cabinetry ⇄ pyhf** statistical model to an on-disk ROOT
   histogram contract described in `cabinetry_config.yml`.

None of these are blockers, but together they mean the migration is a genuine
rewrite of the execution section, not a find-and-replace. Estimated effort:
roughly a day of focused work plus validation against a real Analysis Facility
(the remote data is not reachable from a laptop/CI sandbox).

## 2. Current vs. target versions

| Library | Locked now | Target | Notes |
|---|---|---|---|
| coffea | 2025.7.1 | **2026.7.0** | virtual-array backend; `from_root` defaults to `mode="virtual"` |
| dask / distributed | 2025.3.0 | 2026.7.1 | now **optional** for coffea; only needed if you keep a cluster |
| dask-awkward | 2025.5.0 | 2026.2.1 | still required by released `preprocess`/`apply_to_fileset` |
| awkward | 2.8.5 | 2.11.0 | |
| uproot | 5.6.3 | 5.7.5 | |
| hist | 2.8.1 | 2.10.1 | |
| mplhep | 0.4.0 | 1.3.1 | major bump — check plotting calls |
| pyhf | 0.7.6 | **0.7.6 (already latest)** | no 0.8 on conda-forge; the `<0.8` pin is fine as-is |
| cabinetry | 0.6.0 | **0.6.0 (already latest)** | no newer release available; leave as-is |
| xrootd | 5.8.1 | 6.1.0 | client major bump |
| servicex | not a dep | (optional) | imported in one cell but never installed; only runs on coffea-casa |

Key point verified against coffea 2026.7.0: **pyhf and cabinetry are already at
their newest conda-forge releases**, so the statistical-inference half of the
notebook needs no version bump — only revalidation. The real work is the coffea
execution model and remote I/O.

## 3. The central change: execution model → virtual arrays

coffea 2026.7 reads into **virtual arrays** by default: each branch stays on
disk and materializes on demand, so there is no lazy dask graph and no
`.compute()`. In this repo's `coffea/` notebooks the migration reduced to
"remove `DaskExecutor`, keep `processor.Runner` with `Iterative`/`Futures`
executors, make `mode="virtual"` explicit." The same recipe applies here.

Cells to change (ids from `main_code.ipynb`):

- **`2e1eb49c`** — `client = Client("tls://localhost:8786")`. Remove, or make it
  clearly optional. Dask is no longer needed for the default path and is not
  installed unless requested.
- **`a13a46d3`** — single-file `NanoEventsFactory.from_root(..., iteritems_options=..., access_log=...).events()`.
  Add `mode="virtual"` for clarity. Verify `iteritems_options`/`access_log` still
  behave as intended under the virtual backend (they are tied to the uproot/eager
  read path; column pruning is now handled by the virtual/typetracer layer).
- **`1a82bcae`** — `processor.Runner(executor=processor.DaskExecutor(...), ...)`.
  Swap `DaskExecutor` → `FuturesExecutor(workers=N)` (multicore, no dask) or
  `IterativeExecutor` (single process). `savemetrics`, `chunksize`,
  `skipbadfiles` all still exist on `Runner`.
- **`303da95a`** — `run.preprocess(fileset)`. Still valid on `Runner`.
- **`443b01ad`** — the `ProcessorABC.process` body is backend-agnostic awkward
  and should carry over unchanged; events arrive as virtual arrays.
- **`9cd1bee4`** — `with performance_report(...): out, report = run(...)`.
  `performance_report` is a **dask.distributed** context manager; drop it when
  dropping dask, or gate it behind an "if using a cluster" branch. Also note the
  sum-of-weights normalization here divides filled histograms — that stays valid
  because the `Runner` path returns already-filled `hist` objects (not a graph).

### Optional modernization (beyond a minimal port)

The notebook uses the older `Runner` API rather than `coffea.dataset_tools`. If
you want the current idiom, `dataset_tools.preprocess` + `apply_to_fileset`
exist in 2026.7 — **but the released versions still import `dask_awkward`**, so
they do not remove the dask dependency. The dask-free preprocessing backends
(`preprocess(..., backend="iterative"|"futures")`) are still an **unreleased
draft** (coffea PR #1579), previewed in `coffea/coffea-04-scaleout.ipynb`. For a
stable upgrade today, prefer `Runner` + `FuturesExecutor`.

## 4. Remote I/O and infrastructure

- **`340eb48f` / `b9dff7f0` / `a13a46d3`** hard-code two xrootd prefixes
  (`root://xcache.af.uchicago.edu:1094//` and nested `root://eospublic.cern.ch//...`).
  These are reachable only from the UChicago AF / coffea-casa; they time out from
  a laptop or CI. With xrootd 6.x, revalidate the client + `fsspec-xrootd`
  interplay: `preprocess`/typetracer must open remote files to read schemas.
  Recommend factoring the XCache prefix into a single variable (already partly
  done) and documenting the "on-AF only" assumption.
- **ServiceX path (`ac43f11a`, `0d3ce94b`, `22fdd575`)** uses
  `query.UprootRaw` / `dataset.FileList` / `deliver`. `servicex` is not in
  `pixi.toml`, so this only ran on coffea-casa. The ServiceX API changes often;
  if this path is to be kept, add `servicex` to a dedicated environment and
  revalidate against the current release, otherwise consider clearly marking it
  optional/legacy.
- **`2babc372`** runs `!rm -f histograms/*`; the notebook writes
  `histograms.root`, `workspaces/…json`, and `measurements/<timestamp>/…`. These
  side effects are fine but worth calling out for reproducibility.

## 5. Statistical inference (cabinetry / pyhf)

Self-contained and file-driven, and — importantly — **already on the newest
pyhf (0.7.6) and cabinetry (0.6.0)**. Actions here are revalidation, not
upgrade:

- Re-run `templates.collect(method="uproot")`, `templates.postprocess`,
  `workspace.build`, `model_utils.model_and_data`, `fit.fit`,
  `visualize.pulls` / `visualize.data_mc` against hist 2.10 output and confirm
  the signatures are unchanged.
- The ROOT-path contract in `cabinetry_config.yml` (`hist_reco_mtop`, `hist_Ht`,
  `VariationPath: nominal`, sample paths) must exactly match what cell
  `f1678276` writes with `uproot.recreate`. Any change to the histogram naming
  ripples into this YAML — keep them in lock-step.
- `!pyhf inspect` (cell `a32882d2`) is a shell-out; it depends only on `pyhf`
  being on `PATH` in the environment.

## 6. Latent issues to fix while migrating

- **Operator-precedence bug (cell `91e147a5`, on both the electron *and* muon
  lines)**: `events.Electrons.pt > 30000 & (...)` parses as
  `events.Electrons.pt > (30000 & (...))` because `&` binds tighter than `>`.
  Since `30000 & 1 == 0`, the whole expression collapses to `pt > 0` — this does
  **not** "work by accident"; it silently voids *both* the 30 GeV pT cut and the
  |eta| cut on that object. Wrap each comparison in parentheses:
  `(pt > 30000) & (abs(eta) < ...)`.
- **mplhep 0.4 → 1.x** is a major version jump; re-check any `mplhep.style` /
  `histplot` calls used in the plotting cells.

## 7. Recommended upgrade path

1. Bump `pixi.toml`: coffea `>=2026.7`, awkward/uproot/hist/mplhep/xrootd to the
   versions in §2. Leave pyhf `<0.8` and cabinetry `<0.7` (already newest).
   Keep dask/distributed **only** if you intend to keep a cluster option;
   otherwise drop them. Note numpy will resolve to 2.4.x on Python 3.14 (numba
   0.66, pulled in transitively by coffea, requires numpy <2.5) — do not pin
   `numpy>=2.5`.
2. Remove the dask `Client` (`2e1eb49c`) and `performance_report` (`9cd1bee4`);
   swap `DaskExecutor` → `FuturesExecutor` (`1a82bcae`); add `mode="virtual"` to
   `from_root` (`a13a46d3`).
3. Fix the `&`/`>` precedence bug (`91e147a5`).
4. Validate end-to-end **on an Analysis Facility** (remote data is not reachable
   elsewhere): preprocessing, the processor run, histogram output, and the full
   cabinetry/pyhf fit + pull/data-MC plots.
5. Decide the fate of the ServiceX cells (keep behind an optional env, or mark
   legacy).
6. Optional/future: revisit once coffea PR #1579 (dask-free preprocess backends)
   and PR #1470 (`coffea.compute`) land, to drop dask-awkward entirely.

## 8. Effort & risk

| Area | Effort | Risk |
|---|---|---|
| Execution model (Runner/DaskExecutor → virtual + Futures) | High | High |
| Remote xrootd I/O under xrootd 6.x + virtual backend | Medium | High (needs AF) |
| ServiceX path | Medium | Medium (API churn) |
| cabinetry/pyhf stats | Low | Low (already newest; revalidate) |
| Physics/selection + plotting + `file_utils.py` | Low | Low (backend-agnostic) |

`file_utils.py` (metadata + `get_urls_from_index_file`, `MAX_NUM_OF_FILES=10`)
is pure pandas/string handling and needs no changes; `import requests` there is
unused and could be removed.
