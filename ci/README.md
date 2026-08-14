# Codehaven CI

The `ci/` directory contains repository-owned, deterministic quality gates. GitHub Actions calls the same canonical checks used locally so that local results and pull-request results do not drift.

## Structure

```text
ci/
├── README.md
├── check.sh                         # Canonical local/CI quality gate
├── validate_frontend_structure.py   # Required Flask frontend layout validator
└── validate_workflow.py             # GitHub Actions contract validator
```

## Local command

From the repository root:

```bash
bash ci/check.sh
```

The canonical check compiles Python, runs the full pytest suite, checks all browser JavaScript modules, validates the frontend folder structure, GitHub Actions workflow contract, Compose topology, and repository hygiene for whitespace, committed `.env` files, and known insecure secret patterns.

## GitHub Actions jobs

The workflow in `.github/workflows/ci.yml` runs on every push and pull request. It contains four gates: the main Python/frontend/repository verification job, a Python dependency audit using `pip-audit`, Docker Compose interpolation and topology validation, and a Docker image build that depends on the verification and Compose jobs.

No real credentials are stored in the repository or workflow. Compose validation uses short-lived CI-only placeholder values created inside the runner. Production values must be supplied through the deployment environment or GitHub Actions secrets when a deployment workflow is added.

## Adding a new gate

Add deterministic logic to `ci/check.sh` or a dedicated validator under `ci/`, then call it from `ci/check.sh` first. Keep the check runnable on a clean Ubuntu runner without private credentials. If a check requires an external service, split it into a separate workflow job and use explicit, documented environment variables.
