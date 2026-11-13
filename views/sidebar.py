"""Navigasi halaman dan kontrol akun."""
from html import escape

import streamlit as st

from state import go, logout
from ui import nav_button


def render():
    with st.sidebar:
        st.button(
            "🍩 DO OR DONUT",
            key="nav_home",
            on_click=go,
            args=("classification",),
        )
        nav_button("CLASSIFICATION", "classification", "nav_cls")
        nav_button("TUTORIAL", "tutorial", "nav_tut")
        nav_button("ABOUT", "about", "nav_about")
        st.markdown(
            f'<div class="user-chip">Signed in as <b>{escape(st.session_state.user)}</b></div>',
            unsafe_allow_html=True,
        )
        st.button("LOG OUT", key="logout", on_click=logout, use_container_width=True)
