"""Halaman input gambar dan hasil klasifikasi donat."""
from html import escape

import streamlit as st
from PIL import Image

import classifier
import settings
from state import set_mode
from ui import hero


def _result_html(label, score, ranked):
    level = classifier.confidence_level(score)
    debug_html = (
        f'<div style="font-size:.75rem;color:var(--ink-soft);">'
        f'label model: <code>{escape(str(label))}</code></div>'
        if settings.DEBUG_LABEL
        else ""
    )
    rows = "".join(
        f"""
        <div class="row">
            <div class="name">{escape(classifier.prettify(name))}</div>
            <div class="track"><div style="width:{probability * 100:.1f}%"></div></div>
            <div class="val">{probability:.6f}</div>
        </div>"""
        for name, probability in ranked
    )
    return f"""
        <span class="pill">HASIL KLASIFIKASI</span>
        <div class="result-label">{escape(classifier.prettify(label))}</div>
        {debug_html}
        <div class="big-pct">{score * 100:.0f}%<small></small></div>
        <div class="meter"><div style="width:{score * 100:.0f}%"></div></div>
        <span style="font-weight:700;letter-spacing:.08em;font-size:.85rem;color:var(--ink);">CONFIDENCE</span>&nbsp;
        <span class="badge {level}">{level}</span>
        <div class="conf-text" style="margin:10px 0 0;">{classifier.CONF_TEXT[level]}</div>
        <div class="breakdown">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h4 style="margin: 0;">DETAIL SEMUA KELAS</h4>
                <span style="font-size: 0.75rem; font-weight: bold; color: var(--ink-soft); letter-spacing: .05em;">PROBABILITAS</span>
            </div>
            {rows}
        </div>
        """


def render():
    hero(
        "Classification",
        "Unggah foto donat atau ambil gambar langsung dari kamera untuk mulai klasifikasi.",
    )
    slot = st.empty()

    if st.session_state.result is not None:
        label, score, ranked = st.session_state.result
        with slot.container(border=True, key="card_result"):
            c1, c2 = st.columns([1, 1.1], gap="large")
            with c1:
                st.image(st.session_state.image, use_container_width=True)
            with c2:
                st.markdown(_result_html(label, score, ranked), unsafe_allow_html=True)
                st.write("")
                if st.button("TRY ANOTHER IMAGE", use_container_width=True):
                    st.session_state.image = None
                    st.session_state.result = None
                    st.session_state.reset_key += 1
                    st.rerun()
        return

    if st.session_state.pending is not None:
        image = st.session_state.pending
        with slot.container(border=True, key="card_analyzing"):
            c1, c2 = st.columns([1, 1.1], gap="large")
            with c1:
                st.image(image, use_container_width=True)
            with c2:
                st.markdown(
                    """
                    <span class="pill">SEDANG DIANALISIS</span>
                    <div class="result-label">Menganalisis foto...</div>
                    <div class="about-text">Model Vision Transformer sedang memeriksa donatmu.
                    Mohon tunggu sebentar.</div>
                    """,
                    unsafe_allow_html=True,
                )
                with st.spinner("Model ViT sedang bekerja..."):
                    label, score, ranked = classifier.predict(image)
        st.session_state.image = image
        st.session_state.result = (label, score, ranked)
        st.session_state.pending = None
        st.rerun()
        return

    key = st.session_state.reset_key
    picked = None
    mode = st.session_state.input_mode
    with slot.container(border=True, key="card_input"):
        with st.container(key="tabbar"):
            b1, b2 = st.columns(2)
            with b1:
                st.button(
                    "UPLOAD",
                    key="tab_upload",
                    on_click=set_mode,
                    args=("upload",),
                    type="primary" if mode == "upload" else "secondary",
                )
            with b2:
                st.button(
                    "CAMERA",
                    key="tab_camera",
                    on_click=set_mode,
                    args=("camera",),
                    type="primary" if mode == "camera" else "secondary",
                )

        if mode == "upload":
            uploaded = st.file_uploader(
                "Upload gambar donat",
                type=["jpg", "jpeg", "png", "webp"],
                key=f"uploader_{key}",
                label_visibility="collapsed",
            )
            if uploaded is not None:
                picked = classifier.shrink(Image.open(uploaded))
        else:
            captured = st.camera_input(
                "Ambil foto donat",
                key=f"camera_{key}",
                label_visibility="collapsed",
            )
            if captured is not None:
                picked = classifier.shrink(Image.open(captured))

    if picked is not None:
        st.session_state.pending = picked
        st.rerun()
