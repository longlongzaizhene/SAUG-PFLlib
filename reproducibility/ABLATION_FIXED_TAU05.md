# Fixed-Threshold State-Factor Ablation Configuration

## Scope

This file documents the reconstructed historical state-factor ablation
configuration with a common SAUG threshold of `tau = 0.5`.

The reconstruction is based on:

- the current command-line interface in `system/main.py`;
- the state-factor switches implemented in `clientala.py`;
- the archived ablation-result summaries;
- the surviving command screenshot showing the common experiment
  prefix for the state-factor ablations.

## Common settings

| Item | Setting |
|---|---|
| Algorithm | FedALA |
| Model | CNN / FedAvgCNN |
| Datasets | Cifar10, Cifar100 |
| Number of classes | 10, 100 |
| Global rounds | 50 |
| Number of clients | 20 |
| Participation ratio | 1.0 |
| Local epochs | 1 |
| Batch size | 10 |
| Local learning rate | 0.005 |
| Evaluation gap | 1 |
| Seeds | 0, 1, 2, 3, 4 |
| SAUG threshold | 0.5 |
| Weights | alpha=0.5, beta=0.3, gamma=0.2 |
| Speed upper bound | 120.0 |
| Staleness upper bound | 5.0 |
| Base communication cost | 1.0 |
| Link penalty scale | 5.0 |

## State-factor switches

| Variant | `ld_use_speed` | `ld_use_link` | `ld_use_stale` |
|---|---:|---:|---:|
| Full SAUG | 1 | 1 | 1 |
| SAUG w/o link quality | 1 | 0 | 1 |
| SAUG w/o speed | 0 | 1 | 1 |
| SAUG w/o staleness | 1 | 1 | 0 |

The client code renormalizes the weights of the remaining enabled
state factors to sum to one.

## Important manuscript note

This script reproduces the reconstructed fixed-threshold (`tau=0.5`)
ablation configuration. It must not be described as a threshold-searched
or upload-budget-matched ablation unless the archived logs supporting
that separate protocol are provided and verified.
