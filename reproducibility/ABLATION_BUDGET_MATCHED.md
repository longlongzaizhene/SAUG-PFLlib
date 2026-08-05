# Upload-Budget-Matched State-Factor Ablation

## Reference operating point

The matching target is the training-wide average upload ratio of Full
SAUG with:

```text
tau = 0.5
average upload ratio = 0.7070
```

## Matching protocol

For an ablated variant, the removed state factor is disabled and the
remaining enabled weights are renormalized to sum to one.

The threshold search used the same controlled client-state
trajectories as the main experiments:

- five seeds: `0`, `1`, `2`, `3`, and `4`;
- 20 clients;
- 50 rounds;
- full client participation.

The search objective was the absolute difference between the
training-wide average upload ratio of the ablated variant and the Full
SAUG reference. Model accuracy and communication cost were not used
during threshold selection.

The archived protocol used three progressively refined stages:

1. coarse search over `[0, 1]` with step `0.005`;
2. refinement within `±0.015` of the current best threshold with step
   `0.0001`;
3. final refinement within `±0.001` with step `0.00001`.

Ties were resolved in favor of the candidate closest to the reference
threshold `0.5`.

## Selected thresholds

| Variant | `ld_use_speed` | `ld_use_link` | `ld_use_stale` | Matched tau | Realized upload ratio |
|---|---:|---:|---:|---:|---:|
| `wolink` | 1 | 0 | 1 | 0.52165 | 0.7072 |
| `wospeed` | 0 | 1 | 1 | 0.41964 | 0.7054 |
| `wostale` | 1 | 1 | 0 | 0.55940 | 0.7066 |

The maximum absolute deviation from the Full SAUG upload ratio is
`0.0016`.

## Running the final matched-threshold experiments

From the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\reproducibility\commands\ablation_budget_matched.ps1
```

The script reads:

```text
reproducibility/configs/budget_matched_thresholds.csv
```

and runs:

```text
2 datasets x 3 ablated variants x 5 seeds = 30 runs
```

Full SAUG with `tau = 0.5` is already included in the main experiments
and is therefore not rerun by this script.

## Output safety

The script creates a timestamped directory under:

```text
system/reproducibility_runs/
```

and writes:

- method-specific output directories;
- one console log per run;
- `run_manifest.csv`;
- a copy of the threshold configuration.

Run the script only in a disposable clone or test copy because the
upstream PFLlib workflow may also write model or result files outside
the directory controlled by `-sfn`.
