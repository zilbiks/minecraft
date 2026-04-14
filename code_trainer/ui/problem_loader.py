import random

import requests
import streamlit as st

from code_trainer.api_client import fetch_leetcode_problems
from code_trainer.config import DIFFICULTY_TO_API


def load_tasks_uzdevumi() -> None:
    with st.spinner("ielade uzdevumus"):
        try:
            st.session_state.problems = fetch_leetcode_problems(
                difficulty=DIFFICULTY_TO_API[st.session_state.difficulty],
                limit=st.session_state.problems_limit,
                skip=random.randint(0, 50),
            )
        except requests.HTTPError as e:
            resp = getattr(e, "response", None)
            if resp is not None and getattr(resp, "status_code", None) == 429:
                st.warning("API limits (429 Too Many Requests)")
            else:
                st.warning("Neizdevas ieladet uzdevumus no API")

