import streamlit as st

from code_trainer.api_client import load_random_dataset_problems


def load_tasks_uzdevumi() -> None:
    with st.spinner("ielade uzdevumus"):
        st.session_state.problems = load_random_dataset_problems(
            difficulty=st.session_state.difficulty,
            limit=st.session_state.problems_limit,
        )
