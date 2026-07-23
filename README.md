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

## Opening in VS Code

Each lesson directory is a standalone [Pixi](https://pixi.sh/) workspace (see the lesson READMEs for the JupyterLab workflow via `pixi run start`).
To work on the notebooks in VS Code instead:

1. [Install Pixi](https://pixi.sh/latest/#installation).
2. Create the environment for the lesson(s) you want, e.g.

   ```
   pixi install --manifest-path mplhep/pixi.toml
   ```

3. Open the multi-root workspace

   ```
   code us-atlas-idap-training.code-workspace
   ```

   (or open a single lesson directly, e.g. `code mplhep`) and install the recommended extensions when prompted.
4. In a notebook, open the kernel picker, choose **Python Environments**, and select the lesson's `default` Pixi environment (`<lesson>/.pixi/envs/default/bin/python`).

## Instructor team

* [Matthew Feickert](https://github.com/matthewfeickert), University of Wisconsin-Madison
* [Fengping Hu](https://github.com/fengpinghu), University of Chicago
* [Nick Manganelli](https://github.com/NJManganelli), Northeastern University
* [Roger Janusiak](https://github.com/RogerJanusiak), University of Washington
* [Gordon Watts](https://github.com/gordonwatts), University of Washington
