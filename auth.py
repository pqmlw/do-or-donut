"""Logika akun: database pengguna, hash password, verifikasi, dan pembatasan login.

File ini tidak berisi tampilan. Tampilan form ada di views/login.py.
"""
import hashlib
import hmac
import os
import re
import sqlite3
import time
from contextlib import closing

import streamlit as st

import settings

USERNAME_RE = re.compile(r"[a-z0-9_.]{3,20}")


# ---------- DATABASE ----------
def _db():
    con = sqlite3.connect(settings.DB_PATH)
    con.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        "username TEXT PRIMARY KEY, salt BLOB NOT NULL, "
        "pw_hash BLOB NOT NULL, created_at TEXT NOT NULL)"
    )
    return con


def _hash_password(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, settings.PBKDF2_ITER)


def user_count() -> int:
    with closing(_db()) as con:
        return con.execute("SELECT COUNT(*) FROM users").fetchone()[0]


def create_user(username: str, password: str) -> bool:
    """Simpan akun baru. Mengembalikan False kalau username sudah dipakai."""
    salt = os.urandom(16)
    try:
        with closing(_db()) as con, con:
            con.execute(
                "INSERT INTO users VALUES (?, ?, ?, datetime('now'))",
                (username, salt, _hash_password(password, salt)),
            )
        return True
    except sqlite3.IntegrityError:
        return False


def verify_user(username: str, password: str) -> bool:
    with closing(_db()) as con:
        row = con.execute(
            "SELECT salt, pw_hash FROM users WHERE username = ?", (username,)
        ).fetchone()
    if row is None:
        # samakan waktu proses agar username yang ada tidak bisa ditebak dari kecepatan respons
        _hash_password(password, b"\x00" * 16)
        return False
    return hmac.compare_digest(_hash_password(password, row[0]), row[1])


# ---------- VALIDASI ----------
def normalize_username(username: str) -> str:
    return username.strip().lower()


def validate_new_account(username: str, password: str, confirm: str):
    """Mengembalikan pesan kesalahan, atau None kalau semuanya valid."""
    if not USERNAME_RE.fullmatch(username):
        return "Username harus 3-20 karakter: huruf, angka, titik, atau garis bawah."
    if len(password) < settings.MIN_PASSWORD_LEN:
        return f"Password minimal {settings.MIN_PASSWORD_LEN} karakter."
    if password != confirm:
        return "Konfirmasi password tidak sama."
    return None


def check_invite_code(code: str, invite: str) -> bool:
    return hmac.compare_digest(code.encode("utf-8"), invite.encode("utf-8"))


# ---------- PEMBATASAN PERCOBAAN LOGIN (per sesi browser) ----------
def locked_seconds() -> int:
    return max(0, int(st.session_state.locked_until - time.time()))


def register_failed_login():
    st.session_state.fails += 1
    if st.session_state.fails >= settings.MAX_FAILED:
        st.session_state.locked_until = time.time() + settings.LOCK_SECONDS
        st.session_state.fails = 0


def reset_failed_logins():
    st.session_state.fails = 0
