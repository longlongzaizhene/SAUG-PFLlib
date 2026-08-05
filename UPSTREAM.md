# Upstream Project and Modifications

This repository is derived from PFLlib.

- Upstream repository: https://github.com/TsingZ0/PFLlib
- Underlying personalized federated learning method: FedALA
- Upstream license: Apache License 2.0

## Main modifications

The following functionality was added for the SAUG study:

1. State-aware upload-risk calculation.
2. Upload and local-only execution modes.
3. Client mobility and link-quality state handling.
4. Consecutive non-upload staleness tracking.
5. Emulated uplink communication-cost calculation.
6. Mobility-only and state-agnostic random-gating strategies.
7. Upload-budget-matched state-factor ablation settings.
8. Round-level logging of accuracy, uploads, and communication cost.

## Principal modified files

- `system/main.py`
- `system/flcore/clients/clientala.py`
- `system/flcore/servers/serverala.py`

The original PFLlib license and attribution are retained.