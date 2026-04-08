import random
from typing import Any, Dict, List, Tuple

TASK_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "sum_two": {
        "signature": "def solution(a, b):",
        "description": "atgriez divu skaitlu summu.",
        "examples": [
            ("solution(2, 3)", 5),
            ("solution(-1, 1)", 0),
        ],
    },
    "is_even": {
        "signature": "def solution(n):",
        "description": "atgriez True, ja skaitlis ir para, citadi False.",
        "examples": [
            ("solution(4)", True),
            ("solution(7)", False),
        ],
    },
    "max_in_list": {
        "signature": "def solution(nums):",
        "description": "atgriez lielako elementu saraksta nums.",
        "examples": [
            ("solution([1, 9, 3])", 9),
            ("solution([-5, -2, -8])", -2),
        ],
    },
}


def generate_random_tests(task_type: str, count: int = 5) -> List[Tuple[Tuple[Any, ...], Any]]:
    tests: List[Tuple[Tuple[Any, ...], Any]] = []

    if task_type == "sum_two":
        for _ in range(count):
            a = random.randint(-100, 100)
            b = random.randint(-100, 100)
            tests.append(((a, b), a + b))

    elif task_type == "is_even":
        for _ in range(count):
            n = random.randint(-1000, 1000)
            tests.append(((n,), n % 2 == 0))

    elif task_type == "max_in_list":
        for _ in range(count):
            size = random.randint(3, 8)
            arr = [random.randint(-99, 99) for _ in range(size)]
            tests.append(((arr,), max(arr)))

    return tests


def default_fallback_tasks() -> List[Dict[str, Any]]:
    return [
        {"id": "local-1", "title": "easy: sum two numbers", "task_type": "sum_two"},
        {"id": "local-2", "title": "medium: check even", "task_type": "is_even"},
        {"id": "local-3", "title": "harder: max in list", "task_type": "max_in_list"},
    ]
