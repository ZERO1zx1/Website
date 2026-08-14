#!/usr/bin/env python3
"""Validate the repository's GitHub Actions CI contract without contacting GitHub."""
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
REQUIRED_JOBS = {"verify", "dependency-audit", "compose", "docker-build"}


def main() -> int:
    if not WORKFLOW.is_file():
        print(f"Missing workflow: {WORKFLOW}", file=sys.stderr)
        return 1
    document = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8")) or {}
    jobs = document.get("jobs") or {}
    missing = sorted(REQUIRED_JOBS - set(jobs))
    if missing:
        print(f"Missing workflow jobs: {', '.join(missing)}", file=sys.stderr)
        return 1
    if document.get("permissions", {}).get("contents") != "read":
        print("Workflow must use read-only contents permission.", file=sys.stderr)
        return 1
    if "on" not in document and True not in document:
        print("Workflow triggers are missing.", file=sys.stderr)
        return 1
    if "docker-build" not in jobs.get("docker-build", {}).get("needs", []):
        # The job must depend on verification and Compose, not itself.
        needs = set(jobs["docker-build"].get("needs", []))
        if not {"verify", "compose"}.issubset(needs):
            print("docker-build must depend on verify and compose.", file=sys.stderr)
            return 1
    print(f"workflow_contract=ok jobs={','.join(sorted(jobs))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
