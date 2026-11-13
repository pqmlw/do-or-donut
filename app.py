"""Do or Donut: titik masuk aplikasi.

Jalankan dengan:  streamlit run app.py
"""
import streamlit as st

# Harus menjadi perintah Streamlit pertama
st.set_page_config(page_title="Do or Donut", page_icon="🍩", layout="wide")

from state import init_state            # noqa: E402
from styles import inject_styles        # noqa: E402
from views import about, classification, login, sidebar, tutorial   # noqa: E402

inject_styles()
init_state()

# ---------- Gerbang login: halaman lain tidak dijalankan sebelum login ----------
if st.session_state.user is None:
    login.render()
    st.stop()

sidebar.render()

# ---------- Router ----------
PAGES = {
    "classification": classification.render,
    "tutorial": tutorial.render,
    "about": about.render,
}
PAGES.get(st.session_state.page, about.render)()
