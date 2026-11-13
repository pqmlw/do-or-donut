"""Formulir masuk dan pendaftaran akun."""
import streamlit as st

import auth
import settings
from state import set_auth_mode
from ui import hero


def _login():
    with st.form("login_form"):
        username = st.text_input("USERNAME").strip()
        password = st.text_input("PASSWORD", type="password")
        submitted = st.form_submit_button("LOGIN", use_container_width=True)

    if not submitted:
        return
    if auth.locked_seconds() > 0:
        st.error(f"Terlalu banyak percobaan. Coba lagi dalam {auth.locked_seconds()} detik.")
        return
    if auth.verify_user(auth.normalize_username(username), password):
        auth.reset_failed_logins()
        st.session_state.user = auth.normalize_username(username)
        st.session_state.page = "classification"
        st.rerun()
    else:
        auth.register_failed_login()
        remaining = auth.locked_seconds()
        if remaining:
            st.error(f"Terlalu banyak percobaan. Login dikunci selama {remaining} detik.")
        else:
            st.error("Username atau password salah.")


def _register():
    with st.form("register_form"):
        username = st.text_input("USERNAME").strip()
        password = st.text_input("PASSWORD", type="password")
        confirm = st.text_input("KONFIRMASI PASSWORD", type="password")
        submitted = st.form_submit_button("BUAT AKUN", use_container_width=True)

    if not submitted:
        return

    username = auth.normalize_username(username)
    error = auth.validate_new_account(username, password, confirm)
    if error:
        st.error(error)
        return

    if not auth.create_user(username, password):
        st.error("Username sudah digunakan.")
        return

    st.success("Akun berhasil dibuat. Silakan login.")
    set_auth_mode("login")
    st.rerun()


def render():
    # CSS Kustom untuk Container Card DAN Kotak Input Form agar punya border & warna kontras
    st.markdown(
        """
        <style>
        /* Mengatur Container/Card Utama */
        [data-testid="stVerticalBlock"] div[data-testid="stContainer"] {
            background-color: #ffffff;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }
        
        /* Memberikan border dan background pada kotak input teks (USERNAME & PASSWORD) */
        [data-testid="stTextInput"] input {
            background-color: #f9f9f9;
            border: 1.5px solid #cccccc;
            border-radius: 8px;
            color: #000000;
        }
        
        /* Warna border kotak input saat diklik/fokus */
        [data-testid="stTextInput"] input:focus {
            border-color: #ff4b4b;
            box-shadow: 0 0 0 1px #ff4b4b;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    hero("Do or <span>Donut</span>", "Masuk untuk mulai mengklasifikasikan donat.")
    _, center, _ = st.columns([1, 1.1, 1])
    with center:
        with st.container(border=True, key="card_auth"):
            login_col, register_col = st.columns(2)
            with login_col:
                st.button(
                    "LOGIN",
                    key="auth_login",
                    on_click=set_auth_mode,
                    args=("login",),
                    type="primary" if st.session_state.auth_mode == "login" else "secondary",
                    use_container_width=True,
                )
            with register_col:
                st.button(
                    "DAFTAR",
                    key="auth_register",
                    on_click=set_auth_mode,
                    args=("register",),
                    type="primary" if st.session_state.auth_mode == "register" else "secondary",
                    use_container_width=True,
                )

            if st.session_state.auth_mode == "register":
                _register()
            else:
                remaining = auth.locked_seconds()
                if remaining:
                    st.warning(f"Login dikunci. Coba lagi dalam {remaining} detik.")
                _login()