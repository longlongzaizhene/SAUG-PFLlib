# Reproducibility Guide

## Scope of this package

This directory documents the verified main experiments, the
upload-budget-matched Random-Gate baselines, and the
upload-budget-matched state-factor ablations used in the manuscript.

The experiment groups covered here are:

1. `Off`: always-upload FedALA;
2. `Speed`: mobility-only upload gating;
3. `Random-Gate`: state-agnostic random upload gating;
4. `SAUG`: state-aware upload gating with thresholds
   `0.4`, `0.5`, `0.6`, and `0.7`;
5. state-factor ablations matched to the training-wide average upload
   ratio of Full SAUG with `tau = 0.5`.

## Included files

- `CONFIGURATION.md`: verified experiment parameters and method definitions;
- `experiment_manifest.csv`: machine-readable experiment index;
- `ABLATION_BUDGET_MATCHED.md`: matched-ablation protocol and thresholds;
- `configs/budget_matched_thresholds.csv`: selected ablation thresholds;
- `commands/cifar10_main.ps1`: CIFAR-10 Off, Speed, and SAUG runs;
- `commands/cifar100_main.ps1`: CIFAR-100 Off, Speed, and SAUG runs;
- `commands/random_gate.ps1`: matched Random-Gate runs;
- `commands/ablation_budget_matched.ps1`: final matched-threshold ablation runs;
- `commands/smoke_test.ps1`: short two-round execution check.

## Important safety note

The scripts create timestamped output directories under:

```text
system/reproducibility_runs/
```

This prevents newly generated round-log directories from overwriting
the archived experiment directories. However, the upstream PFLlib
workflow may also save model or result files outside the directory
controlled by `-sfn`.

Run the scripts only in a disposable clone or test copy of the
repository. Do not run them inside the directory containing the
original experimental artifacts.

## Environment

Create the environment from the repository root:

```bash
conda env create -f environment.yml
conda activate pfllib
```

For a more strictly versioned environment:

```bash
conda env create -f environment-lock.yml
conda activate pfllib
```

## Dataset preparation

The manuscript uses CIFAR-10 and CIFAR-100 partitioned among 20 clients
with a Dirichlet non-IID distribution with `alpha = 0.1`.

The original datasets and private client-partition artifacts are not
redistributed in this working repository. Dataset preparation follows
the inherited PFLlib utilities.

Before running the commands, confirm that the expected PFLlib client
data files have already been generated for:

```text
Cifar10
Cifar100
```

## Running the verified main experiments

```powershell
powershell -ExecutionPolicy Bypass -File .\reproducibility\commands\cifar10_main.ps1
```

```powershell
powershell -ExecutionPolicy Bypass -File .\reproducibility\commands\cifar100_main.ps1
```

## Running Random-Gate

```powershell
powershell -ExecutionPolicy Bypass -File .\reproducibility\commands\random_gate.ps1
```

The target upload probabilities are:

- CIFAR-10: `p = 0.5398`, matched to SAUG with `tau = 0.4`;
- CIFAR-100: `p = 0.9156`, matched to SAUG with `tau = 0.7`.

Here, `p` is used only by Random-Gate. It is not a SAUG threshold and
is not an ablation parameter.

## Running the upload-budget-matched ablations

```powershell
powershell -ExecutionPolicy Bypass -File .\reproducibility\commands\ablation_budget_matched.ps1
```

Full SAUG with `tau = 0.5` is the reference operating point and has a
training-wide average upload ratio of `0.7070`.

The ablated variants use:

| Variant | Matched threshold | Realized average upload ratio |
|---|---:|---:|
| SAUG w/o link quality | 0.52165 | 0.7072 |
| SAUG w/o speed | 0.41964 | 0.7054 |
| SAUG w/o staleness | 0.55940 | 0.7066 |

The run script reads these values from:

```text
reproducibility/configs/budget_matched_thresholds.csv
```

It runs the three ablated variants on both datasets and five seeds,
for a total of 30 runs. Full SAUG is not rerun by this script because
the `tau = 0.5` reference is already part of the main experiments.

The final thresholds are used only to match the upload quantity. Model
accuracy and communication cost are not used to select them.

## Smoke test

Run the smoke test only in a disposable clone:

```powershell
powershell -ExecutionPolicy Bypass -File .\reproducibility\commands\smoke_test.ps1
```

The smoke test uses two global rounds and seed `999`. It verifies that
the command interface, SAUG client/server code, and round-log output
can start successfully. It is not intended to reproduce the reported
numerical results.

## Output files

For each run, the modified FedALA server creates a method-specific
directory containing:

```text
round_log.csv
accuracy_curve.png
comm_curve.png
participation_curve.png
```

The round log records:

- round index;
- current evaluation accuracy;
- best accuracy so far;
- round communication cost;
- cumulative communication cost;
- selected, uploading, and dropped client counts;
- runtime;
- gating mode;
- threshold;
- target Random-Gate probability;
- random seed.

The matched-ablation script additionally writes a run manifest and a
separate console log for every experiment.

## Data availability

The working GitHub repository provides source code, environment
specifications, verified commands, and configuration documentation.

Complete raw experimental logs, processed result tables, and private
client-partition artifacts are not included in this working public
repository. They are retained by the authors and may be shared with
editors or reviewers through an appropriate controlled-access channel.
