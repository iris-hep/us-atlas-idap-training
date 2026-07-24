# US ATLAS / IRIS-HEP Analysis Software Training Event

## [2026 training event](https://indico.cern.ch/event/1633749/)

* Indico: https://indico.cern.ch/event/1633749/
* Location: University of Arizona
* Date: July 30&ndash;31, 2026

## Training contributions

* Columnar analysis and uproot
* Distributed analysis and Dask
* Data Visualization techniques and libraries
* Using the UChicago Analysis Facility
* ServiceX
* Statistical tools

## Instructor team

* [Matthew Feickert](https://github.com/matthewfeickert), University of Wisconsin-Madison
* [Fengping Hu](https://github.com/fengpinghu), University of Chicago
* [Nick Manganelli](https://github.com/NJManganelli), Northeastern University
* [Roger Janusiak](https://github.com/RogerJanusiak), University of Washington
* [Gordon Watts](https://github.com/gordonwatts), University of Washington

## Opening in VS Code

Each lesson directory is a standalone [Pixi](https://pixi.sh/) workspace.
To mirror the experience of a US ATLAS Analysis Facility, the assumption is that users will interact with the lessons through Jupyter Lab (via `pixi run start`).
However, the notebook material can be run fully through VS Code as well.

1. [Install Pixi](https://pixi.sh/latest/#installation)
1. Install environment for the lesson(s) you want to work on

   ```
   pixi install --manifest-path <directory>/pixi.toml
   ```

1. Open the multi-root workspace with VS Code

   ```
   code us-atlas-idap-training.code-workspace
   ```

   (or open a single lesson directly, e.g. `code <directory>`)
1. In a notebook, open the kernel picker, choose **Python Environments**, and select the lesson's `default` Pixi environment (`<lesson>/.pixi/envs/default/bin/python`)
