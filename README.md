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
├─ environment.yml             Concise Conda environment specification
├─ environment-lock.yml        More complete Conda environment specification
├─ requirements-lock.txt       Pip package-version snapshot
├─ environment-info.txt        Python, PyTorch, CUDA, OS, and GPU information
├─ nvidia-smi.txt              NVIDIA driver and GPU information
├─ README.md                   SAUG project documentation
├─ UPSTREAM.md                 Upstream attribution and modification summary
└─ LICENSE                     Apache License 2.0
```

Additional reproducibility materials will be organized under:

```text
reproducibility/
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

The original datasets are not redistributed in this repository. Dataset preparation follows the utilities provided by PFLlib.

The reported experiments use:

- 20 clients;
- a Dirichlet non-IID partition with `alpha = 0.1`; and
- five random seeds: `0`, `1`, `2`, `3`, and `4`.

Detailed dataset-generation commands and client-partition information will be added under:

```text
reproducibility/
```

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

Exact commands, configurations, and random-seed settings will be organized under:

```text
reproducibility/commands/
reproducibility/configs/
```

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

Raw logs and analysis scripts will be organized under:

```text
reproducibility/raw_logs/
reproducibility/scripts/
```

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
- the main experiment argument interface; and
- the Conda, pip, CUDA, and hardware environment specifications.

Experiment commands, selected raw logs, state-generation materials, and analysis scripts are being organized for the submission release.

## License

This repository is based on PFLlib and retains the Apache License 2.0.

See [`LICENSE`](LICENSE) for details.

## Citation

The archived software citation and Zenodo DOI will be added after the submission release is finalized.