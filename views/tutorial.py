"""Panduan penggunaan aplikasi."""
import streamlit as st

from ui import hero


def render():
    hero("How to <span>Use?</span>", "Empat langkah mudah untuk mengklasifikasikan donat.")
    left, right = st.columns([1, 1.05], gap="large")
    with left:
        with st.container(border=True, key="card_tutorial"):
            st.markdown(
                """
                <div class="mock-tabs"><div class="on">UPLOAD</div><div>CAMERA</div></div>
                <div class="mock-drop">
                    <div style="font-size:2.2rem;">🖼️</div>
                    <div style="margin:8px 0 14px;font-weight:700;">Drag &amp; drop foto donat di sini</div>
                    <div class="btn">UPLOAD IMAGE</div>
                    <div class="hint">JPG, PNG, atau WEBP</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    with right:
        steps = [
            ("Buka menu Classification", "Pilih CLASSIFICATION di sidebar sebelah kiri."),
            ("Pilih metode input", "Tab UPLOAD untuk mengunggah file, atau CAMERA untuk foto langsung."),
            (
                "Kirim gambar donat",
                "Klik UPLOAD IMAGE untuk pilih foto atau TAKE PHOTO untuk mengambil foto langsung.",
            ),
            ("Baca hasilnya", "Hasil klasifikasi akan muncul otomatis. Klik TRY ANOTHER IMAGE untuk mengulang."),
        ]
        html = "".join(
            f'<div class="step"><div class="num">{number}</div>'
            f"<div><b>{title}</b><span>{description}</span></div></div>"
            for number, (title, description) in enumerate(steps, 1)
        )
        st.markdown(html, unsafe_allow_html=True)
        st.info("💡 Tips: gunakan foto yang terang dan fokus, dengan donat terlihat jelas di tengah gambar.")
