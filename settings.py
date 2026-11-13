"""Konfigurasi aplikasi Do or Donut.

Semua pengaturan yang mungkin diubah ada di sini, jadi file lain tidak perlu disentuh.
"""
import os

import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------- MODEL ----------
HF_MODEL_ID = "pqmlw/vit_donat_4"
HF_TOKEN = None            # isi lewat st.secrets atau environment variable, jangan ditulis di sini

HIGH_THRESHOLD = 0.85      # confidence >= 0.85  -> HIGH
MEDIUM_THRESHOLD = 0.60    # confidence >= 0.60  -> MEDIUM, selain itu LOW

DEBUG_LABEL = False        # True = tampilkan label mentah model di halaman hasil

# ---------- PREPROCESSING ----------
USE_REMBG = True           # hapus latar belakang sebelum prediksi
REMBG_MODEL = "u2net"
BG_COLOR = (255, 255, 255)
MAX_SIDE = 1024            # sisi terpanjang gambar diperkecil ke ukuran ini sebelum rembg

# ---------- AKUN ----------
DB_PATH = os.environ.get("USERS_DB", os.path.join(BASE_DIR, "users.db"))
PBKDF2_ITER = 200_000      # jumlah iterasi hashing password
MIN_PASSWORD_LEN = 8
MAX_FAILED = 5             # salah password berturut-turut sebelum login dikunci
LOCK_SECONDS = 60          # lama penguncian (detik)


def get_secret(name):
    """Baca nilai rahasia dari environment variable dulu, lalu dari st.secrets."""
    val = os.environ.get(name)
    if val:
        return val
    try:
        return st.secrets.get(name, None)
    except Exception:
        return None
