# SAUG-PFLlib

This repository provides the implementation and reproducibility materials for:

**State-Aware Upload Gating for Personalized Federated Learning in Mobile Edge Environments**

## Overview

State-Aware Upload Gating (SAUG) is a post-selection upload-control mechanism for personalized federated learning in mobile edge environments.

After a client has been selected by the server, SAUG determines whether the client should operate in:

- `upload` mode, in which the client performs personalized initialization, local training, and model upload; or
- `local-only` mode, in which the client performs local training without uploading its current-round model update.

The gating decision jointly considers:

- client speed;
- link quality; and
- consecutive non-upload staleness.

The current implementation uses FedALA as the underlying personalized federated learning method.

## Upstream Project

This repository is derived from PFLlib:

- Upstream repository: https://github.com/TsingZ0/PFLlib
- Underlying method: FedALA
- Upstream license: Apache License 2.0

The original PFLlib license and attribution are retained. A detailed description of the modifications is provided in [`UPSTREAM.md`](UPSTREAM.md).

The original PFLlib README is preserved at:

```text
docs/PFLlib_original_README.md
```

## Main Modifications

The main modifications introduced for the SAUG study include:

1. state-aware upload-risk calculation;
2. threshold-based switching between upload and local-only modes;
3. cross-round non-upload staleness tracking;
4. synthetic client-speed and link-quality state handling;
5. emulated uplink communication-cost calculation;
6. mobility-only gating and state-agnostic random gating;
7. upload-budget-matched state-factor ablations; and
8. round-level logging of accuracy, upload behavior, and communication cost.

The principal modified files are:

```text
system/main.py
system/flcore/clients/clientala.py
system/flcore/servers/serverala.py
```

## Repository Structure

```text
SAUG-PFLlib/
├─ system/                     PFLlib framework and SAUG implementation
├─ dataset/                    Dataset preparation utilities inherited from PFLlib
├─ docs/                       Original PFLlib documentation
├─ reproducibility/            Verified configurations and execution commands
│  ├─ README.md
│  ├─ CONFIGURATION.md
│  ├─ ABLATION_BUDGET_MATCHED.md
│  ├─ experiment_manifest.csv
│  ├─ configs/
│  │  └─ budget_matched_thresholds.csv
│  └─ commands/
│     ├─ cifar10_main.ps1
│     ├─ cifar100_main.ps1
│     ├─ random_gate.ps1
│     ├─ ablation_budget_matched.ps1
│     └─ smoke_test.ps1
├─ environment.yml             Concise Conda environment specification
├─ environment-lock.yml        More complete Conda environment specification
├─ requirements-lock.txt       Pip package-version snapshot
├─ environment-info.txt        Python, PyTorch, CUDA, OS, and GPU information
├─ nvidia-smi.txt              NVIDIA driver and GPU information
├─ DATA_AVAILABILITY.md        Public-data scope and access statement
├─ CITATION.cff                Software citation metadata
├─ README.md                   SAUG project documentation
├─ UPSTREAM.md                 Upstream attribution and modification summary
└─ LICENSE                     Apache License 2.0
```

## Environment Setup

The experiments were run using the Conda environment documented in this repository.

### Recommended installation

```bash
conda env create -f environment.yml
conda activate pfllib
```

### More strictly versioned installation

```bash
conda env create -f environment-lock.yml
conda activate pfllib
```

The following files provide additional environment information:

- `requirements-lock.txt`;
- `environment-info.txt`; and
- `nvidia-smi.txt`.

The Conda files are recommended as the primary environment specifications. The pip requirements file is provided as an auxiliary package-version snapshot.

## Datasets

The experiments use:

- CIFAR-10; and
- CIFAR-100.

The original CIFAR-10 and CIFAR-100 benchmark datasets are publicly
available from their original sources and are not duplicated in this
software repository.

The client-partition files used in the reported experiments are archived
separately in the restricted Zenodo supporting-data record:

[https://doi.org/10.5281/zenodo.21815686](https://doi.org/10.5281/zenodo.21815686)

The repository retains sample MNIST artifacts inherited from the
upstream PFLlib project. These artifacts are not used in the reported
CIFAR-10 and CIFAR-100 experiments.

The reported experiments use:

- 20 clients;
- a Dirichlet non-IID partition with `alpha = 0.1`; and
- five random seeds: `0`, `1`, `2`, `3`, and `4`.

The verified dataset settings are documented in
[`reproducibility/CONFIGURATION.md`](reproducibility/CONFIGURATION.md).

## Experimental Strategies

The reported experiments include:

1. `Off`: always-upload FedALA baseline;
2. `Speed`: mobility-only upload gating;
3. `Random-Gate`: state-agnostic random upload gating;
4. `SAUG`: state-aware upload gating with multiple thresholds; and
5. upload-budget-matched state-factor ablations.

The main SAUG thresholds evaluated in the paper are:

```text
0.4, 0.5, 0.6, and 0.7
```

The Random-Gate target upload probabilities are:

```text
CIFAR-10: p = 0.5398
CIFAR-100: p = 0.9156
```

The verified commands and configurations are provided in the [`reproducibility`](reproducibility/) directory.

## Reproducibility Materials

The verified implementation, experiment configurations, and execution commands are documented in the following files:

- [Reproducibility guide](reproducibility/README.md)
- [Verified experimental configuration](reproducibility/CONFIGURATION.md)
- [Experiment manifest](reproducibility/experiment_manifest.csv)
- [Upload-budget-matched ablation configuration](reproducibility/ABLATION_BUDGET_MATCHED.md)
- [Matched ablation thresholds](reproducibility/configs/budget_matched_thresholds.csv)
- [Experiment commands](reproducibility/commands/)
- [Data availability statement](DATA_AVAILABILITY.md)

The archived software release, including the source code, environment
specifications, verified experiment commands, and reproducibility
documentation, is available in Zenodo:

[https://doi.org/10.5281/zenodo.21807089](https://doi.org/10.5281/zenodo.21807089)

Supporting research data, including the client partitions, per-seed
experimental logs, processed summary data, and analysis scripts, are
archived separately in Zenodo:

[https://doi.org/10.5281/zenodo.21815686](https://doi.org/10.5281/zenodo.21815686)

The supporting-data files are restricted during peer review and are
accessible to editors and reviewers through a private access link. They
will be made publicly available upon publication of the associated article.

## Recorded Outputs

The implementation records or derives the following experimental quantities:

- test accuracy;
- selected-client count;
- uploading-client count;
- upload ratio;
- round-level emulated uplink communication cost; and
- cumulative emulated uplink communication cost.

The processed results reported in the paper include:

- best test accuracy;
- late-stage average test accuracy;
- training-wide average upload ratio; and
- total emulated uplink communication cost.

The per-seed raw experimental logs, processed summary data, and analysis
scripts are archived in the separate Zenodo supporting-data record
(https://doi.org/10.5281/zenodo.21815686). The files are restricted during
peer review and will be made publicly available upon publication of the
associated article.

## Reproducibility Scope

The communication-cost metric implemented in this repository is an emulated uplink communication-cost proxy used for controlled comparisons among upload strategies.

It should not be interpreted as directly measured:

- network latency;
- energy consumption;
- spectrum usage; or
- real-world wireless traffic.

Client speed and link-quality trajectories are synthetically generated according to the procedures and parameters described in the manuscript.

## Current Repository Status

The repository currently contains:

- the core SAUG implementation;
- the modified FedALA client and server logic;
- the verified Conda, pip, CUDA, and hardware environment specifications;
- the main-experiment commands for CIFAR-10 and CIFAR-100;
- the upload-budget-matched Random-Gate commands;
- the upload-budget-matched state-factor ablation configuration;
- the matched ablation thresholds and execution script; and
- the experiment manifest and data-availability statement.

The client partitions, per-seed raw experimental logs, processed summary
data, and analysis scripts are archived separately in Zenodo
(https://doi.org/10.5281/zenodo.21815686) and are not duplicated in this
software repository.

## License

This repository is based on PFLlib and retains the Apache License 2.0.

See [`LICENSE`](LICENSE) for details.

## Citation

Software citation metadata are provided in [`CITATION.cff`](CITATION.cff).

Archived software release:

[https://doi.org/10.5281/zenodo.21807089](https://doi.org/10.5281/zenodo.21807089)

Supporting-data record:

[https://doi.org/10.5281/zenodo.21815686](https://doi.org/10.5281/zenodo.21815686)
