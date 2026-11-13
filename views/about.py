"""Halaman informasi aplikasi dan model."""
import streamlit as st

import settings
from ui import hero


def render():
    hero("About Do or Donut", "Sedikit cerita tentang aplikasi dan model di baliknya.")

    c1, c2 = st.columns(2, gap="large")
    with c1:
        with st.container(border=True, key="card_about_app"):
            st.markdown(
                """
                <div class="about-title">Tentang Aplikasi</div>
                <div class="about-text">
                <b>Do or Donut</b> adalah aplikasi klasifikasi citra donat berbasis
                <b>Vision Transformer (ViT)</b>.
                Nama Do or Donut mencerminkan fungsi sistem dalam mengambil keputusan
                terhadap produk: menentukan apakah sebuah donat lolos standar kualitas
                produksi atau harus dikategorikan sebagai produk cacat berdasarkan
                jenis ketidaksempurnaannya.
                </div>
                """,
                unsafe_allow_html=True,
            )
    with c2:
        with st.container(border=True, key="card_about_model"):
            st.markdown(
                f"""
                <div class="about-title">Tentang Model</div>
                <div class="about-text">
                Model dilatih dengan arsitektur ViT-B/16 yang di-host di Hugging Face:
                <a href="https://huggingface.co/{settings.HF_MODEL_ID}" target="_blank">
                {settings.HF_MODEL_ID}</a>
                <br><br>
                Dataset terdiri dari foto donat yang dikumpulkan secara pribadi, dengan
                label kelas yang ditentukan berdasarkan jenis cacat atau kualitas donat.
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    with st.container(border=True, key="card_about_developer"):
        st.markdown(
            """
            <div class="about-title">Tentang Pengembang</div>
            <div class="about-text">
            Aplikasi ini dikembangkan oleh <b>Paquita Melawi</b> (NIM 535230062)
            sebagai proyek skripsi.
            </div>
            """,
            unsafe_allow_html=True,
        )
