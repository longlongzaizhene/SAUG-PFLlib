# Reproducibility Guide

## Scope of this package

This directory documents the verified main experiments and the
upload-budget-matched Random-Gate baselines used in the manuscript.

The verified experiment groups included here are:

1. `Off`: always-upload FedALA;
2. `Speed`: mobility-only upload gating;
3. `Random-Gate`: state-agnostic random upload gating;
4. `SAUG`: state-aware upload gating with thresholds
   `0.4`, `0.5`, `0.6`, and `0.7`.

The state-factor ablation commands are intentionally not included in
this verified batch. They should be added only after the final
ablation run configuration is reconciled with the archived logs and
the manuscript.

## Included files

- `CONFIGURATION.md`: experiment parameters and method definitions;
- `experiment_manifest.csv`: machine-readable experiment index;
- `commands/cifar10_main.ps1`: CIFAR-10 Off, Speed, and SAUG runs;
- `commands/cifar100_main.ps1`: CIFAR-100 Off, Speed, and SAUG runs;
- `commands/random_gate.ps1`: matched Random-Gate runs;
- `commands/smoke_test.ps1`: short two-round execution check.

## Important safety note

The scripts create a timestamped output directory under:

```text
system/reproducibility_runs/
```

This prevents the new round logs from overwriting previous round-log
directories. However, the upstream PFLlib workflow may also save model
or result files outside the directory controlled by `-sfn`.

Therefore, run these scripts only in a disposable clone or test copy
of the repository. Do not run them inside the directory that contains
the original experimental artifacts.

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

Open PowerShell in the repository and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\reproducibility\commands\cifar10_main.ps1
```

```powershell
powershell -ExecutionPolicy Bypass -File .\reproducibility\commands\cifar100_main.ps1
```

Each script asks for explicit confirmation before launching the full
set of experiments.

## Running Random-Gate

```powershell
powershell -ExecutionPolicy Bypass -File .\reproducibility\commands\random_gate.ps1
```

The target upload probabilities are:

- CIFAR-10: `p = 0.5398`, matched to SAUG with `tau = 0.4`;
- CIFAR-100: `p = 0.9156`, matched to SAUG with `tau = 0.7`.

Here, `p` is used only by Random-Gate. It is not a SAUG threshold and
is not an ablation parameter.

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

## Data availability

The working GitHub repository provides source code, environment
specifications, verified commands, and configuration documentation.

Complete raw experimental logs and ablation records are not included
in this working public repository. They are retained by the authors
and may be shared with editors or reviewers through an appropriate
controlled-access channel.
