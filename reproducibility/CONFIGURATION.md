# Verified Experimental Configuration

## General training settings

| Item | Setting |
|---|---|
| Underlying PFL method | FedALA |
| Local model | FedAvgCNN (`CNN` in the command line) |
| Datasets | CIFAR-10 and CIFAR-100 |
| Data partition | Dirichlet non-IID, `alpha = 0.1` |
| Number of clients | 20 |
| Participation ratio | 1.0 |
| Global rounds | 50 |
| Local epochs | 1 |
| Batch size | 10 |
| Local learning rate | 0.005 |
| Evaluation gap | 1 round |
| Independent seeds | 0, 1, 2, 3, 4 |
| Device | CUDA, device ID 0 |
| FedALA `eta` | 1.0 |
| FedALA `rand_percent` | 80 |
| FedALA `layer_idx` | 2 |

CIFAR-10 uses `-ncl 10`, and CIFAR-100 uses `-ncl 100`.

## Strategy-to-code mapping

| Paper name | Command-line mode | Additional parameter |
|---|---|---|
| Off | `--ld_mode off` | none |
| Speed | `--ld_mode speed` | `--ld_speed_threshold 100.0` |
| Random-Gate | `--ld_mode random` | `--random_upload_ratio p` |
| SAUG | `--ld_mode score` | `--ld_tau tau` |

## SAUG parameters

| Parameter | Value |
|---|---:|
| Speed weight, `ld_alpha` | 0.5 |
| Link-risk weight, `ld_beta` | 0.3 |
| Staleness weight, `ld_gamma` | 0.2 |
| Speed normalization upper bound, `ld_v_max` | 120.0 |
| Staleness normalization upper bound, `ld_k_max` | 5.0 |
| Main-experiment thresholds | 0.4, 0.5, 0.6, 0.7 |

The score-mode decision is:

```text
score <= tau  -> upload
score >  tau  -> local-only
```

## Random-Gate operating points

| Dataset | Target probability | Matched SAUG operating point |
|---|---:|---|
| CIFAR-10 | 0.5398 | SAUG, `tau = 0.4` |
| CIFAR-100 | 0.9156 | SAUG, `tau = 0.7` |

The target probability is the per-selected-client upload probability.
The realized upload ratio may differ slightly over a finite number of
rounds and random seeds. The probability `p` is used only by
Random-Gate.

## Upload-budget-matched state-factor ablation

Full SAUG with `tau = 0.5` is used as the reference:

```text
target training-wide average upload ratio = 0.7070
```

For each ablated variant, the removed factor is disabled and the
remaining enabled weights are renormalized to sum to one.

| Variant | Speed | Link | Staleness | Matched tau | Realized upload ratio | Difference from Full |
|---|---:|---:|---:|---:|---:|---:|
| SAUG w/o link quality | 1 | 0 | 1 | 0.52165 | 0.7072 | 0.0002 |
| SAUG w/o speed | 0 | 1 | 1 | 0.41964 | 0.7054 | 0.0016 |
| SAUG w/o staleness | 1 | 1 | 0 | 0.55940 | 0.7066 | 0.0004 |

The matched thresholds are shared by CIFAR-10 and CIFAR-100 because
the upload decisions are generated from the controlled client-state
trajectories and gating configuration, while the datasets primarily
affect model accuracy.

The threshold-matching protocol uses the upload ratio only. Accuracy
and communication cost are not used to select the thresholds.

## Synthetic client-state trajectories

For each client, the implementation uses a client-specific random
number generator initialized from the experiment seed and client ID.

The state-generation procedure is:

```text
initial speed ~ Uniform(20, 60)
speed_t = clip(speed_(t-1) + Normal(0, 10^2), 0, 120)
link_t  = clip(1 - 0.8 * speed_t / 120 + Normal(0, 0.05^2), 0, 1)
```

Consecutive non-upload staleness is reset to zero after a successful
upload and is incremented after a local-only round.

## Emulated uplink communication cost

For an uploading client:

```text
cost = 1.0 + 5.0 * (1 - link_quality)
```

For a local-only client:

```text
cost = 0
```

The metric is an emulated comparison proxy. It is not a direct
measurement of latency, energy consumption, spectrum usage, or
real-network traffic.

## Verified command scope

The command files cover:

- Off, Speed, and SAUG on CIFAR-10;
- Off, Speed, and SAUG on CIFAR-100;
- Random-Gate on both datasets;
- upload-budget-matched state-factor ablations on both datasets;
- a short smoke test.
