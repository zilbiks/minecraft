import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .config import DATASET_PATH


def _to_test_tuple(raw_input: Any) -> Tuple[Any, ...]:
    if isinstance(raw_input, dict):
        return tuple(raw_input.values())
    if isinstance(raw_input, (list, tuple)):
        return tuple(raw_input)
    return (raw_input,)


def _parse_examples(raw_examples: str) -> List[Tuple[Tuple[Any, ...], Any]]:
    if not raw_examples:
        return []
    try:
        items = json.loads(raw_examples)
    except json.JSONDecodeError:
        return []

    parsed: List[Tuple[Tuple[Any, ...], Any]] = []
    for item in items:
        raw_inp = item.get("input")
        expected = item.get("output", item.get("expected_output"))
        parsed.append((_to_test_tuple(raw_inp), expected))
    return parsed


def _parse_constraints(raw_constraints: str) -> List[str]:
    if not raw_constraints:
        return []
    try:
        data = json.loads(raw_constraints)
    except json.JSONDecodeError:
        return []
    return [str(x) for x in data]


def _parse_test_cases(raw_test_cases: str) -> List[Tuple[Tuple[Any, ...], Any]]:
    if not raw_test_cases:
        return []
    try:
        items = json.loads(raw_test_cases)
    except json.JSONDecodeError:
        return []

    parsed: List[Tuple[Tuple[Any, ...], Any]] = []
    for item in items:
        raw_inp = item.get("input")
        expected = item.get("expected_output", item.get("output"))
        parsed.append((_to_test_tuple(raw_inp), expected))
    return parsed


def load_dataset_problems(difficulty: str, limit: int = 15, skip: int = 0) -> List[Dict[str, Any]]:
    csv_path = Path(DATASET_PATH)
    if not csv_path.exists():
        return []

    normalized_diff = difficulty.strip().lower()
    problems: List[Dict[str, Any]] = []

    with csv_path.open("r", encoding="utf-8", newline="") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            level = (row.get("difficulty_level") or "").strip().lower()
            if level != normalized_diff:
                continue
            problems.append(
                {
                    "id": str(row.get("id", "")),
                    "title": row.get("title", "Unknown"),
                    "titleSlug": str(row.get("id", "")),
                    "difficulty": row.get("difficulty_level", ""),
                    "description": row.get("description", ""),
                    "examples": _parse_examples(row.get("examples", "")),
                    "constraints": _parse_constraints(row.get("constraints", "")),
                    "test_cases": _parse_test_cases(row.get("test_cases", "")),
                }
            )

    return problems[skip : skip + limit]
