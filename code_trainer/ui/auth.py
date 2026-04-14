import streamlit as st

from database import authenticate_user, create_user, get_solved


def render_auth() -> None:
    st.markdown("## CodeTrainer")
    st.caption("login vai register lai saglabatu atrisinatos uzdevumus")

    kolonna_login, kolonna_register = st.columns(2)
    with kolonna_login:
        st.subheader("login")
        with st.form("login_form"):
            lietotajvards_username = st.text_input("lietotajvards", key="login_username")
            parole_password = st.text_input("Parole", type="password", key="login_password")
            ok_poga_login = st.form_submit_button("ielogoties")
        if ok_poga_login:
            user_id = authenticate_user(lietotajvards_username, parole_password)
            if user_id is None:
                st.error("nepareizs lietotajvards vai parole")
            else:
                st.session_state.user_id = user_id
                st.session_state.username = (lietotajvards_username or "").strip()
                st.session_state.solved = get_solved(user_id)
                st.rerun()

    with kolonna_register:
        st.subheader("registracija")
        with st.form("register_form"):
            registret_username = st.text_input("lietotajvards", key="reg_username")
            registret_password = st.text_input("parole", type="password", key="reg_password")
            ok_poga_register = st.form_submit_button("izveidot kontu")
        if ok_poga_register:
            izveide_ok, izveide_msg = create_user(registret_username, registret_password)
            if izveide_ok:
                st.success(izveide_msg)
            else:
                st.error(izveide_msg)

