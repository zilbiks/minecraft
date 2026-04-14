import random

import streamlit as st
from bs4 import BeautifulSoup

from code_trainer.api_client import fetch_leetcode_problem_raw
from code_trainer.evaluator import run_tests
from code_trainer.tasks import (
    build_leetcode_starter_code,
    extract_python_method_signature,
    parse_leetcode_examples_from_html,
)
from code_trainer.ui.auth import render_auth
from code_trainer.ui.lang import strip_garumzimes_accents, strip_number_prefix, translate_to_lv
from code_trainer.ui.problem_loader import load_tasks_uzdevumi
from code_trainer.ui.state import init_session_state
from database import init_db, mark_solved

try:
    from streamlit_ace import st_ace
except Exception:
    st_ace = None


def run_app() -> None:
    st.set_page_config(layout="wide")
    init_db()

    if "user_id" not in st.session_state:
        render_auth()
        st.stop()

    init_session_state()

    if not st.session_state.problems:
        load_tasks_uzdevumi()

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Uzdevumi")

        st.session_state.difficulty = st.selectbox(
            "Grutibas pakape",
            ["Easy", "Medium", "Hard"],
            index=["Easy", "Medium", "Hard"].index(st.session_state.difficulty),
        )
        st.session_state.problems_limit = st.slider(
            "Cik uzdevumus ieladet",
            min_value=5,
            max_value=30,
            value=st.session_state.problems_limit,
            step=5,
        )

        if st.button("Atjauninat uzdevumu sarakstu"):
            load_tasks_uzdevumi()

        if st.session_state.problems:
            labels = []
            for p in st.session_state.problems:
                base_title = strip_number_prefix(p.get("title", "(bez nosaukuma)"))
                lv_title = translate_to_lv(base_title)
                labels.append(lv_title or base_title)
            selected_label = st.selectbox("Izvelies uzdevumu", labels)
            idx = labels.index(selected_label)
            task = st.session_state.problems[idx]

            st.session_state.selected_title_slug = task.get("titleSlug")
            st.session_state.selected_problem_meta = task

            st.write(f"atrisinats: **{len(st.session_state.solved)} / {len(st.session_state.problems)}**")
        else:
            st.warning("neizdevas ieladet uzdevumus")

    with col2:
        st.subheader("koda redaktors")

        if not st.session_state.selected_title_slug:
            st.info("izvelies uzdevumu kreisaja puse")
            st.stop()

        if st.session_state.last_loaded_title_slug != st.session_state.selected_title_slug:
            raw_question = fetch_leetcode_problem_raw(st.session_state.selected_title_slug)
            saturs_html = raw_question.get("content") or ""
            try:
                plain = BeautifulSoup(saturs_html, "html.parser").get_text("\n", strip=True)
            except Exception:
                plain = saturs_html
            st.session_state.question_en = plain
            st.session_state.question_lv = translate_to_lv(plain) or strip_garumzimes_accents(plain)

            code_snippets = raw_question.get("codeSnippets") or []
            method_name, param_names = extract_python_method_signature(code_snippets)
            st.session_state.method_name = method_name
            st.session_state.param_names = param_names

            tests, unordered_output = parse_leetcode_examples_from_html(saturs_html, param_names)
            st.session_state.all_examples = tests
            st.session_state.unordered_output = unordered_output

            if tests:
                k = min(st.session_state.tests_to_run, len(tests))
                st.session_state.tests = random.sample(tests, k=k)
            else:
                st.session_state.tests = []

            st.session_state.editor_code = build_leetcode_starter_code(method_name, param_names)
            st.session_state.last_loaded_title_slug = st.session_state.selected_title_slug

        meta = st.session_state.selected_problem_meta or {}
        if meta:
            pamata_title = strip_number_prefix(meta.get("title", ""))
            st.markdown(f"### {translate_to_lv(pamata_title) or pamata_title}")
            st.caption(f"Grutibas pakape: {meta.get('difficulty', '')}")

        if st.session_state.all_examples:
            max_k = len(st.session_state.all_examples)
            if max_k <= 1:
                st.session_state.tests_to_run = 1
            else:
                st.session_state.tests_to_run = st.slider(
                    "Cik piemerius izmantot testiem (nejausi izveleti)",
                    min_value=1,
                    max_value=max_k,
                    value=min(st.session_state.tests_to_run, max_k),
                    step=1,
                )

        with st.expander("Uzdevuma teksts"):
            en_txt = (st.session_state.question_en or "").strip()
            lv_txt = (st.session_state.question_lv or "").strip()
            if not (en_txt or lv_txt):
                st.markdown("_Nav teksta_")
            else:
                st.markdown(en_txt or "")
                if lv_txt:
                    st.markdown(
                        f"<div style='opacity:0.65; font-size:0.9em; margin-top:0.75rem'>{lv_txt}</div>",
                        unsafe_allow_html=True,
                    )

        with st.expander("Piemeri (Input/Output)"):
            if not st.session_state.all_examples:
                st.write("Neizdevas parset piemerius.")
            else:
                for i, (inp, exp) in enumerate(st.session_state.all_examples, start=1):
                    st.write(f"{i}) Ievade: {inp} | Izvade: {exp}")

        st.caption("Atbildei jabut funkcijai `solution()` (starter koda ta jau ir).")
        if st_ace is not None:
            user_code = st_ace(
                value=st.session_state.editor_code,
                language="python",
                theme="monokai",
                key="editor_code_ace",
                height=360,
                auto_update=True,
                show_gutter=True,
                tab_size=4,
                wrap=False,
            )
            if isinstance(user_code, str):
                st.session_state.editor_code = user_code
            else:
                user_code = st.session_state.editor_code
        else:
            user_code = st.text_area(
                "Python kods",
                key="editor_code",
                height=360,
                placeholder="class Solution:\n    def myMethod(self, ...):\n        pass\n\ndef solution(*args):\n    return Solution().myMethod(*args)\n",
            )
            st.info("Lai Tab/indent stradatu ka ista redaktora: `pip install -r requirements.txt`.")

        with st.expander("Risinajums"):
            st.caption("Atvers LeetCode risinajuma lapu (oficialais raksts).")
            st.markdown(
                f"[Atvert risinajumu]({('https://leetcode.com/problems/' + st.session_state.selected_title_slug + '/solution/')})"
            )

        if st.button("Parbaudit"):
            if st.session_state.all_examples:
                k = min(st.session_state.tests_to_run, len(st.session_state.all_examples))
                st.session_state.tests = random.sample(st.session_state.all_examples, k=k)
            else:
                st.session_state.tests = []

            if not st.session_state.tests:
                st.warning("Sim uzdevumam neizdevas izvilkt testus no piemeriem (Input/Output parsesana).")
            else:
                ok, message, failed = run_tests(
                    user_code=user_code,
                    tests=st.session_state.tests,
                    unordered_output=st.session_state.unordered_output,
                )
                if ok:
                    st.success("Pareizi!")
                    st.write(message)
                    st.session_state.solved.add(st.session_state.selected_title_slug)
                    try:
                        mark_solved(int(st.session_state.user_id), st.session_state.selected_title_slug)
                    except Exception:
                        pass
                else:
                    st.error("Nekorekti.")
                    st.write(message)
                    if failed:
                        st.write("Neizdevas sie testi:")
                        for i, item in enumerate(failed, start=1):
                            st.write(
                                f"{i}) input={item['input']} | expected={item['expected']} | got={item['got']}"
                            )

