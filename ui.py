"""Komponen tampilan kecil yang dipakai di beberapa halaman."""
import streamlit as st

from state import go


def hero(title_html, sub):
    st.markdown(
        f"""
        <div class="hero">
            <h1>{title_html}</h1>
            <p>{sub}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def nav_button(label, page, key):
    """Tombol navigasi sidebar. Tombol halaman aktif berwarna pink (primary)."""
    active = st.session_state.page == page
    st.button(
        label,
        key=key,
        on_click=go,
        args=(page,),
        type="primary" if active else "secondary",
        use_container_width=True,
    )
