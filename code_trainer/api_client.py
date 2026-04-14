import random
import time
import requests

from typing import Any, Dict, List, Optional
from .config import LEETCODE_API_BASE


def get_json_with_retries(url: str, *, timeout: int, max_attempts: int = 5) -> Any:
    last_exc: Optional[Exception] = None
    for attempt in range(1, max_attempts + 1):
        try:
            resp = requests.get(url, timeout=timeout)

            if resp.status_code == 429 or 500 <= resp.status_code <= 599:
                retry_after = resp.headers.get("megini pectam")
                if retry_after is not None:
                    try:
                        wait_s = float(retry_after)
                    except Exception:
                        wait_s = 0.0
                else:
                    wait_s = min(12.0, float(2 ** (attempt - 1)))
                    wait_s += random.random() * 0.5

                if attempt < max_attempts:
                    time.sleep(max(0.5, wait_s))
                    continue

            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, ValueError) as exc:
            last_exc = exc
            if attempt < max_attempts:
                time.sleep(min(12.0, float(2 ** (attempt - 1))) + random.random() * 0.5)
                continue
            raise

    if last_exc is not None:
        raise last_exc
    raise RuntimeError("error while fetching JSON")


def fetch_leetcode_problems(difficulty: str, limit: int = 15, skip: int = 0) -> List[Dict[str, Any]]:
    url = f"{LEETCODE_API_BASE}/problems?limit={limit}&skip={skip}&difficulty={difficulty}"
    data = get_json_with_retries(url, timeout=12, max_attempts=2)

    items = data.get("problemsetQuestionList", []) or []
    problems: List[Dict[str, Any]] = []
    for item in items:
        problems.append(
            {
                "id": str(item.get("questionFrontendId", "")),
                "title": item.get("title", "Unknown"),
                "titleSlug": item.get("titleSlug"),
                "difficulty": item.get("difficulty"),
            }
        )
    return problems


def fetch_leetcode_problem_raw(title_slug: str) -> Dict[str, Any]:
    url = f"{LEETCODE_API_BASE}/select/raw?titleSlug={title_slug}"
    data = get_json_with_retries(url, timeout=25)

    if "question" in data:
        return data["question"]
    return data


def fetch_leetcode_problem_select(title_slug: str) -> Dict[str, Any]:
    url = f"{LEETCODE_API_BASE}/select?titleSlug={title_slug}"
    return get_json_with_retries(url, timeout=25)
