"""State sesi (st.session_state) dan fungsi callback tombol.

Streamlit menjalankan ulang seluruh skrip pada setiap interaksi, jadi semua yang
harus diingat antar-interaksi disimpan di st.session_state.
"""
import streamlit as st

DEFAULTS = {
    "page": "classification",
    "image": None,
    "result": None,
    "pending": None,
    "reset_key": 0,
    "input_mode": "upload",
    "user": None,           # username yang sedang login (None = belum login)
    "auth_mode": "login",   # "login" atau "register"
    "fails": 0,             # jumlah salah password berturut-turut
    "locked_until": 0.0,    # waktu (epoch) sampai login dikunci
}


def init_state():
    for k, v in DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v


def go(page):
    st.session_state.page = page


def set_mode(mode):
    st.session_state.input_mode = mode


def set_auth_mode(mode):
    st.session_state.auth_mode = mode


def logout():
    for k in ("user", "image", "result", "pending"):
        st.session_state[k] = None
    st.session_state.reset_key += 1
    st.session_state.page = "classification"
    st.session_state.auth_mode = "login"
