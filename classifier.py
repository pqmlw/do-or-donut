"""Model klasifikasi: memuat ViT dari Hugging Face, preprocessing gambar, dan prediksi.

Tidak ada tampilan di file ini. Tampilan hasil ada di views/classification.py.
"""
import gc
import re

import streamlit as st
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification

import settings


# ============================================================
# MEMUAT MODEL
# ============================================================
def _get_token():
    return settings.HF_TOKEN or settings.get_secret("HF_TOKEN")


@st.cache_resource(show_spinner="Memuat model dari Hugging Face...")
def load_model():
    token = _get_token()
    processor = AutoImageProcessor.from_pretrained(settings.HF_MODEL_ID, token=token)
    model = AutoModelForImageClassification.from_pretrained(
        settings.HF_MODEL_ID, token=token, low_cpu_mem_usage=True
    )
    model.eval()
    for p in model.parameters():
        p.requires_grad = False
    return processor, model


@st.cache_resource(show_spinner="Memuat model penghapus background...")
def load_rembg_session():
    from rembg import new_session      # diimpor hanya saat dipakai
    return new_session(settings.REMBG_MODEL)


# ============================================================
# PREPROCESSING GAMBAR
# ============================================================
def shrink(img: Image.Image, max_side: int = settings.MAX_SIDE) -> Image.Image:
    img = img.convert("RGB")
    img.thumbnail((max_side, max_side))
    return img


def remove_background(image: Image.Image) -> Image.Image:
    from rembg import remove
    session = load_rembg_session()
    cutout = remove(image, session=session)          # RGBA
    bg = Image.new("RGB", cutout.size, settings.BG_COLOR)
    bg.paste(cutout, mask=cutout.getchannel("A"))
    del cutout
    return bg


# ============================================================
# NAMA KELAS
# ============================================================
# Kunci = label asli dari model (huruf kecil, spasi/"-" dianggap "_")
# Nilai = nama yang ditampilkan di aplikasi
LABEL_NAMES = {
    "cincin_lolos": "Donat Cincin - Lolos",
    "cincin_penyok": "Donat Cincin - Tidak Lolos (Penyok)",
    "cincin_tidaksimetris": "Donat Cincin - Tidak Lolos (Tidak Simetris)",
    "isi_bocor": "Donat Isi - Tidak Lolos (Bocor)",
    "isi_lolos": "Donat Isi - Lolos",
    "isi_penyok": "Donat Isi - Tidak Lolos (Penyok)",
}

# Urutan kelas sesuai id2label (cadangan kalau model mengembalikan "LABEL_0", "LABEL_1", dst.)
CLASS_ORDER = [
    "cincin_lolos",          # 0
    "cincin_penyok",         # 1
    "cincin_tidaksimetris",  # 2
    "isi_bocor",             # 3
    "isi_lolos",             # 4
    "isi_penyok",            # 5
]


def prettify(label: str) -> str:
    key = re.sub(r"[\s\-]+", "_", str(label).strip().lower())
    m = re.fullmatch(r"label_(\d+)", key)
    if m and int(m.group(1)) < len(CLASS_ORDER):
        key = CLASS_ORDER[int(m.group(1))]
    return LABEL_NAMES.get(key, key.replace("_", " ").title())


# ============================================================
# PREDIKSI
# ============================================================
def predict(image: Image.Image):
    """Mengembalikan (label tertinggi, confidence, daftar semua kelas terurut)."""
    processor, model = load_model()
    if settings.USE_REMBG:
        image = remove_background(image)
    inputs = processor(images=image, return_tensors="pt")
    with torch.inference_mode():
        logits = model(**inputs).logits
    probs = torch.softmax(logits, dim=-1)[0].tolist()
    id2label = model.config.id2label
    ranked = sorted(
        ((id2label[i], p) for i, p in enumerate(probs)),
        key=lambda x: x[1],
        reverse=True,
    )
    del inputs, logits
    gc.collect()
    return ranked[0][0], ranked[0][1], ranked


def confidence_level(score: float) -> str:
    if score >= settings.HIGH_THRESHOLD:
        return "HIGH"
    if score >= settings.MEDIUM_THRESHOLD:
        return "MEDIUM"
    return "LOW"


CONF_TEXT = {
    "HIGH": "Model sangat yakin dengan hasil ini",
    "MEDIUM": "Cukup yakin, coba foto lebih jelas bila ragu",
    "LOW": "Kurang yakin, coba foto dengan cahaya lebih baik",
}
