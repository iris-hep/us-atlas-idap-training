#!/usr/bin/env python
"""physlite_tui.py -- a rich + textual showcase driven by a small coffea analysis.

Launch this from a terminal *inside* JupyterLab (File > New > Terminal) in the
coffea Pixi environment. It reads a couple of the same ATLAS Open Data PHYSLITE
files as the notebooks, runs a small per-event multiplicity analysis with the
regular (Iterative) coffea executor -- no dask -- and shows the results off
through the rich and Textual terminal-UI machinery.

    pixi run tui                     # interactive Textual TUI (default)
    pixi run tui --rich              # non-interactive rich report
    pixi run tui --local             # use the bundled local ROOT file (offline)
    pixi run tui --workers 4         # scale the *regular* run out with FuturesExecutor
    pixi run tui --files 3           # how many remote PHYSLITE files to read

Equivalently: `pixi run python physlite_tui.py [flags]`.

The baseline uses `processor.IterativeExecutor`; `--workers N` swaps in
`FuturesExecutor` (still a "regular", non-dask executor).
"""

from __future__ import annotations

import argparse
import time
import warnings
from pathlib import Path

import awkward as ak
import hist
from coffea import processor

warnings.filterwarnings("ignore", message="Skipping ", category=UserWarning)

# --- data ------------------------------------------------------------------

XCACHE = "root://xcache.af.uchicago.edu:1094//"
EOS = "root://eospublic.cern.ch//eos/opendata/atlas/rucio/mc20_13TeV/"
# The HZZ->4l PHYSLITE sample used by coffea-04-scaleout.ipynb.
_PHYSLITE_INDICES = [1, 2, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

# Offline fallback: the ROOT file bundled with the columnar lesson.
LOCAL_FILE = Path(__file__).resolve().parent.parent / "columnar" / "data" / "SMHiggsToZZTo4L.root"


def build_fileset(local: bool, n_files: int):
    """Return (fileset, treename, schemaclass, count_fn, object_label)."""
    if local:
        from coffea.nanoevents import BaseSchema

        fileset = {
            # the Runner injects the "dataset" metadata key from this name
            "H->ZZ->4l (local)": {"files": {str(LOCAL_FILE): "Events"}, "metadata": {}}
        }
        # per-event muon multiplicity (this file is CMS-style NanoAOD)
        return fileset, "Events", BaseSchema, (lambda ev: ak.num(ev.Muon_pt, axis=1)), "muons"

    from coffea.nanoevents import PHYSLITESchema

    files = {
        f"{XCACHE}{EOS}DAOD_PHYSLITE.38191712._{i:06d}.pool.root.1": "CollectionTree"
        for i in _PHYSLITE_INDICES[: max(1, n_files)]
    }
    fileset = {"H->ZZ->4l (PHYSLITE)": {"files": files, "metadata": {}}}
    # per-event jet multiplicity
    return fileset, "CollectionTree", PHYSLITESchema, (lambda ev: ak.num(ev.Jets, axis=1)), "jets"


# --- analysis (regular executor, virtual arrays) ---------------------------

NBINS = 6


def _make_processor(count_fn, label):
    class MultiplicityProcessor(processor.ProcessorABC):
        def process(self, events):
            dataset = events.metadata["dataset"]
            per_event = ak.fill_none(count_fn(events), 0)
            h = hist.Hist.new.Reg(
                NBINS, 0, NBINS, name="mult", label=f"# {label} / event"
            ).Int64()
            h.fill(mult=ak.to_numpy(per_event))
            return {
                dataset: {"events": len(events), "objects": int(ak.sum(per_event)), "hist": h}
            }

        def postprocess(self, accumulator):
            return accumulator

    return MultiplicityProcessor


def run_analysis(local, n_files, workers, max_files, status, log):
    """Run the multiplicity analysis with a *regular* coffea executor."""
    fileset, _tree, schema, count_fn, label = build_fileset(local, n_files)
    if workers and workers > 0:
        log(f"executor: FuturesExecutor(workers={workers})")
        executor = processor.FuturesExecutor(workers=workers, compression=None, status=status)
    else:
        log("executor: IterativeExecutor (regular, single process)")
        executor = processor.IterativeExecutor(compression=None, status=status)

    run = processor.Runner(
        executor=executor,
        schema=schema,
        savemetrics=True,
        maxchunks=max_files,
    )
    log("reading virtual arrays and filling histograms ...")
    t0 = time.time()
    out, metrics = run(fileset, processor_instance=_make_processor(count_fn, label)())
    elapsed = time.time() - t0
    log(f"done in {elapsed:.1f}s")
    return out, metrics, label, elapsed


# --- shared rendering helper -----------------------------------------------


def hist_bar_lines(h, width=32):
    """A compact horizontal bar chart of a 1D hist, as text (used by rich + Textual)."""
    values = h.values()
    edges = h.axes[0].edges
    peak = max(values.max(), 1)
    lines = []
    for i, v in enumerate(values):
        lo = int(edges[i])
        label = f"{lo}+" if i == len(values) - 1 else f"{lo}"
        bar = "█" * int(round(width * v / peak))
        lines.append(f"{label:>3} │ {bar} {int(v)}")
    return "\n".join(lines)


# --- rich (non-interactive) mode -------------------------------------------


def rich_report(local, n_files, workers, max_files):
    import coffea
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()
    exe = f"FuturesExecutor(workers={workers})" if workers else "IterativeExecutor"
    console.print(
        Panel.fit(
            f"[bold]coffea {coffea.__version__}[/bold]  •  virtual arrays  •  {exe}\n"
            f"source: {'local ROOT file' if local else f'{n_files} remote PHYSLITE file(s) via XCache'}",
            title="PHYSLITE multiplicity demo",
            border_style="cyan",
        )
    )

    with console.status("[bold green]processing ...", spinner="dots"):
        out, metrics, label, elapsed = run_analysis(
            local, n_files, workers, max_files, status=False, log=lambda *_: None
        )

    table = Table(title="Results", header_style="bold magenta")
    table.add_column("dataset")
    table.add_column("events", justify="right")
    table.add_column(f"total {label}", justify="right")
    table.add_column(f"mean {label}/event", justify="right")
    for name, res in out.items():
        mean = res["objects"] / res["events"] if res["events"] else 0.0
        table.add_row(name, f"{res['events']:,}", f"{res['objects']:,}", f"{mean:.2f}")
    console.print(table)

    for name, res in out.items():
        console.print(
            Panel(hist_bar_lines(res["hist"]), title=f"{label}/event — {name}", border_style="green")
        )

    entries = metrics.get("entries", "?") if isinstance(metrics, dict) else "?"
    console.print(f"[dim]processed {entries} entries in {elapsed:.1f}s[/dim]")


# --- Textual (interactive TUI) mode ----------------------------------------


def make_tui_app(local, n_files, workers, max_files):
    from textual import work
    from textual.app import App, ComposeResult
    from textual.containers import Horizontal, Vertical
    from textual.widgets import DataTable, Footer, Header, ProgressBar, RichLog, Static

    class PhysliteTUI(App):
        CSS = """
        #body { height: 1fr; }
        #left { width: 55%; }
        #right { width: 45%; }
        DataTable { height: auto; }
        #hist { height: 1fr; border: round green; padding: 0 1; }
        RichLog { height: 1fr; border: round cyan; }
        """
        BINDINGS = [("r", "rerun", "Re-run"), ("q", "quit", "Quit")]
        TITLE = "coffea PHYSLITE demo"
        SUB_TITLE = "regular executor • virtual arrays • rich + Textual"

        def compose(self) -> ComposeResult:
            yield Header(show_clock=True)
            with Horizontal(id="body"):
                with Vertical(id="left"):
                    yield DataTable(id="results")
                    yield Static("(run to fill)", id="hist")
                with Vertical(id="right"):
                    yield RichLog(id="log", highlight=True, markup=True)
            yield ProgressBar(id="prog", total=100, show_eta=False)
            yield Footer()

        def on_mount(self) -> None:
            table = self.query_one("#results", DataTable)
            table.add_columns("dataset", "events", "total", "mean/evt")
            self._log("[bold]ready[/bold] — press [b]r[/b] to run, [b]q[/b] to quit")
            self.action_rerun()

        def _log(self, msg: str) -> None:
            self.query_one("#log", RichLog).write(msg)

        def action_rerun(self) -> None:
            self.query_one("#prog", ProgressBar).update(total=None)  # indeterminate
            self._log("[green]starting analysis ...[/green]")
            self._analyze()

        @work(thread=True, exclusive=True)
        def _analyze(self) -> None:
            def log(msg):
                self.call_from_thread(self._log, str(msg))

            try:
                out, metrics, label, elapsed = run_analysis(
                    local, n_files, workers, max_files, status=False, log=log
                )
            except Exception as exc:  # network / data issues shouldn't crash the UI
                self.call_from_thread(self._log, f"[red]analysis failed:[/red] {type(exc).__name__}: {exc}")
                self.call_from_thread(self.query_one("#prog", ProgressBar).update, total=100, progress=100)
                return
            self.call_from_thread(self._show_results, out, label)
            self.call_from_thread(self.query_one("#prog", ProgressBar).update, total=100, progress=100)

        def _show_results(self, out, label) -> None:
            table = self.query_one("#results", DataTable)
            table.clear()
            hist_text = []
            for name, res in out.items():
                mean = res["objects"] / res["events"] if res["events"] else 0.0
                table.add_row(name, f"{res['events']:,}", f"{res['objects']:,}", f"{mean:.2f}")
                hist_text.append(f"[b]{label}/event — {name}[/b]\n" + hist_bar_lines(res["hist"]))
            self.query_one("#hist", Static).update("\n\n".join(hist_text))
            self._log("[green]results updated[/green]")

    return PhysliteTUI()


def run_tui(local, n_files, workers, max_files):
    make_tui_app(local, n_files, workers, max_files).run()


# --- entry point -----------------------------------------------------------


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rich", action="store_true", help="non-interactive rich report instead of the TUI")
    p.add_argument("--local", action="store_true", help="use the bundled local ROOT file (offline)")
    p.add_argument("--workers", type=int, default=0, help="use FuturesExecutor with N workers (default: IterativeExecutor)")
    p.add_argument("--files", type=int, default=2, help="number of remote PHYSLITE files to read")
    p.add_argument("--max-chunks", type=int, default=None, help="cap total chunks (handy for a quick demo)")
    args = p.parse_args(argv)

    if args.local and not LOCAL_FILE.exists():
        raise SystemExit(f"--local requested but {LOCAL_FILE} not found")

    if args.rich:
        rich_report(args.local, args.files, args.workers, args.max_chunks)
    else:
        run_tui(args.local, args.files, args.workers, args.max_chunks)


if __name__ == "__main__":
    main()
