import streamlit as st

from code_trainer.api_client import fetch_tasks_from_api
from code_trainer.config import APP_TITLE, DEFAULT_RANDOM_TESTS
from code_trainer.evaluator import get_starter_code, run_tests
from code_trainer.tasks import TASK_TEMPLATES, generate_random_tests


st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)
st.write("vienkarss codewars stila prototips: izvelies uzdevumu, uzraksti `solution`, parbaudi.")

if "solved" not in st.session_state:
    st.session_state.solved = set()
if "tasks" not in st.session_state:
    st.session_state.tasks = fetch_tasks_from_api()
if "last_task_id" not in st.session_state:
    st.session_state.last_task_id = None
if "cached_tests" not in st.session_state:
    st.session_state.cached_tests = []
if "editor_code" not in st.session_state:
    st.session_state.editor_code = ""

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("uzdevumi (no api)")
    labels = [f"#{t['id']} - {t['title']}" for t in st.session_state.tasks]
    selected_label = st.selectbox("izvelies uzdevumu", labels)
    idx = labels.index(selected_label)
    task = st.session_state.tasks[idx]

    template = TASK_TEMPLATES[task["task_type"]]
    st.write(f"**tips:** `{task['task_type']}`")
    st.write(f"**apraksts:** {template['description']}")

    st.write("**piemeri:**")
    for ex_call, ex_result in template["examples"]:
        st.write(f"- `{ex_call}` -> `{ex_result}`")

    st.write("---")
    st.write(f"atrisinati: **{len(st.session_state.solved)} / {len(st.session_state.tasks)}**")

with col2:
    st.subheader("koda redaktors")

    if st.session_state.last_task_id != task["id"]:
        st.session_state.editor_code = get_starter_code(template["signature"])
        st.session_state.last_task_id = task["id"]
        st.session_state.cached_tests = generate_random_tests(task["task_type"], count=DEFAULT_RANDOM_TESTS)

    st.caption("raksti funkciju ar nosaukumu `solution`.")
    user_code = st.text_area(
        "python kods",
        key="editor_code",
        height=360,
        placeholder="def solution(...):\n    pass",
    )

    a, b = st.columns(2)
    with a:
        regen = st.button("jauni random testi")
    with b:
        check = st.button("parbaudit")

    if regen:
        st.session_state.cached_tests = generate_random_tests(task["task_type"], count=DEFAULT_RANDOM_TESTS)
        st.info("izveidoti jauni random testi")

    if check:
        ok, message, failed = run_tests(
            user_code=user_code,
            tests=st.session_state.cached_tests,
        )

        if ok:
            st.success("✅ verno!")
            st.write(message)
            st.session_state.solved.add(task["id"])
        else:
            st.error("❌ kluda")
            st.write(message)
            if failed:
                st.write("neizgajusie testi:")
                for i, item in enumerate(failed, start=1):
                    st.write(f"{i}) input={item['input']} | expected={item['expected']} | got={item['got']}")

st.write("---")
st.caption("palaist: `streamlit run app.py`")
