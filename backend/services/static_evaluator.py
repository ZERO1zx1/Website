"""Deterministic checks for HTML/CSS learning challenges.

HTML and CSS are authored as document/style source, so these challenges use
server-side source assertions rather than executing in the Python/JavaScript
sandbox. Admins can define expected_output as a required source token.
"""

import re
from typing import Dict, List


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip().lower()


def evaluate_static(code: str, language: str, test_cases: List[Dict]) -> Dict:
    normalized = _normalize(code)
    results = []
    for index, case in enumerate(test_cases, start=1):
        expected = str(case.get("expected_output", "")).strip()
        requirement = _normalize(expected)
        passed = bool(requirement) and requirement in normalized
        # Optional semantic shortcuts make admin authoring clearer while the
        # raw expected token remains the source of truth for normal tests.
        if language == "html" and requirement == "required":
            passed = bool(re.search(r"\brequired(?:\s*=|\s|>)", code, re.I))
        result = {
            "test_number": index,
            "status": "passed" if passed else "failed",
            "passed": passed,
            "actual_output": "source requirement found" if passed else "source requirement missing",
            "expected_output": expected,
            "is_hidden": bool(case.get("is_hidden", False)),
        }
        if not passed:
            result["error"] = f"Required {language} token was not found."
        results.append(result)
    passed_count = sum(1 for item in results if item["passed"])
    failed_count = len(results) - passed_count
    status = "accepted" if results and failed_count == 0 else "partial_accepted" if passed_count else "wrong_answer"
    return {
        "status": status,
        "mode": "static",
        "total_tests": len(results),
        "passed_tests": passed_count,
        "failed_tests": failed_count,
        "test_results": results,
    }
