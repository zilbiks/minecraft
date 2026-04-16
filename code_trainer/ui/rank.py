from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable


@dataclass(frozen=True)
class RankTier:
    name: str
    min_solved: int


RANK_TIERS: tuple[RankTier, ...] = (
    RankTier(name="8 kyu", min_solved=0),
    RankTier(name="7 kyu", min_solved=5),
    RankTier(name="6 kyu", min_solved=15),
    RankTier(name="5 kyu", min_solved=35),
    RankTier(name="4 kyu", min_solved=60),
    RankTier(name="3 kyu", min_solved=100),
    RankTier(name="2 kyu", min_solved=150),
    RankTier(name="1 kyu", min_solved=220),
)


def get_rank_progress(solved_count: int) -> dict[str, int | float | str | None]:
    solved = max(0, int(solved_count))
    current_idx = 0
    for idx, tier in enumerate(RANK_TIERS):
        if solved >= tier.min_solved:
            current_idx = idx
        else:
            break

    current = RANK_TIERS[current_idx]
    next_tier = RANK_TIERS[current_idx + 1] if current_idx + 1 < len(RANK_TIERS) else None

    if next_tier is None:
        return {
            "rank_name": current.name,
            "current_solved": solved,
            "next_rank_name": None,
            "remaining_to_next": 0,
            "progress_pct": 100,
        }

    span = max(1, next_tier.min_solved - current.min_solved)
    progress = min(100, int(((solved - current.min_solved) / span) * 100))
    return {
        "rank_name": current.name,
        "current_solved": solved,
        "next_rank_name": next_tier.name,
        "remaining_to_next": max(0, next_tier.min_solved - solved),
        "progress_pct": progress,
    }


def get_daily_streak(activity_dates: Iterable[date], today: date | None = None) -> int:
    today = today or date.today()
    activity = set(activity_dates)
    streak = 0
    cursor = today
    while cursor in activity:
        streak += 1
        cursor -= timedelta(days=1)
    return streak
