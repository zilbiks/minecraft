import streamlit as st

from code_trainer.config import DEFAULT_DIFFICULTY, DEFAULT_EXAMPLES_TO_TEST, DEFAULT_PROBLEMS_LIMIT


def init_session_state() -> None:
    if "solved" not in st.session_state:
        st.session_state.solved = set()

    if "problems" not in st.session_state:
        st.session_state.problems = []
    if "difficulty" not in st.session_state:
        st.session_state.difficulty = DEFAULT_DIFFICULTY
    if "problems_limit" not in st.session_state:
        st.session_state.problems_limit = DEFAULT_PROBLEMS_LIMIT

    if "selected_title_slug" not in st.session_state:
        st.session_state.selected_title_slug = None
    if "selected_problem_meta" not in st.session_state:
        st.session_state.selected_problem_meta = {}
    if "last_loaded_title_slug" not in st.session_state:
        st.session_state.last_loaded_title_slug = None

    if "question_html" not in st.session_state:
        st.session_state.question_html = ""
    if "question_en" not in st.session_state:
        st.session_state.question_en = ""
    if "question_lv" not in st.session_state:
        st.session_state.question_lv = ""
    if "method_name" not in st.session_state:
        st.session_state.method_name = ""
    if "param_names" not in st.session_state:
        st.session_state.param_names = []

    if "unordered_output" not in st.session_state:
        st.session_state.unordered_output = False

    if "all_examples" not in st.session_state:
        st.session_state.all_examples = []
    if "tests_to_run" not in st.session_state:
        st.session_state.tests_to_run = DEFAULT_EXAMPLES_TO_TEST
    if "tests" not in st.session_state:
        st.session_state.tests = []

    if "editor_code" not in st.session_state:
        st.session_state.editor_code = ""

