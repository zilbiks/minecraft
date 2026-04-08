from typing import Any, Dict, List

import requests

from .config import API_URL
from .tasks import default_fallback_tasks


def fetch_tasks_from_api() -> List[Dict[str, Any]]:
    mapping = ["sum_two", "is_even", "max_in_list"]

    try:
        resp = requests.get(API_URL, timeout=6)
        resp.raise_for_status()
        data = resp.json()

        tasks = []
        for i, item in enumerate(data[:3]):
            tasks.append(
                {
                    "id": str(item.get("id", f"api-{i+1}")),
                    "title": item.get("title", f"api task {i+1}"),
                    "task_type": mapping[i % len(mapping)],
                }
            )

        if len(tasks) < 3:
            return default_fallback_tasks()

        return tasks
    except Exception:
        return default_fallback_tasks()
