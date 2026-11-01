import re

import streamlit as st
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification
from rembg import remove, new_session
# ============================================================
# KONFIGURASI
# ============================================================
HF_MODEL_ID = "pqmlw/vit_donat_4"
HF_TOKEN = None

HIGH_THRESHOLD = 0.85
MEDIUM_THRESHOLD = 0.60

DEBUG_LABEL = False

st.set_page_config(page_title="Do or Donut", page_icon="🍩", layout="wide")

# ============================================================
# STYLE
# ============================================================
FONT_IMPORT = """
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=DM+Sans:wght@400;500;700&display=swap');
"""

LIGHT_VARS = """
:root {
    color-scheme: light;
    --ink: #3E2218;
    --ink-soft: #8A6A58;
    --line: #F1DFCC;
    --card: #FFFFFF;
    --bg: #FFF8F0;
    --blob1: #FFE1EA;
    --blob2: #FFEFD2;
    --pink: #FF5C8A;
    --pink-hover: #E8467A;
    --pink-soft: #FFE1EA;
    --caramel: #E9A44C;
    --caramel-soft: #FFEFD2;
    --drop: #FFFBF4;
    --drop-hover: #FFF3F7;
    --track: #F6E8DA;
    --bar: #5A3626;
    --side: #3E2218;
    --tab-on: #3E2218;
    --pill-text: #B8741A;
    --chip-text: #9A5F12;
    --shadow: rgba(62,34,24,.08);
    --img-shadow: rgba(62,34,24,.18);
    --alert-bg: #FFF3DF;
    --ok: #2FA66A;
    --warn: #E9A44C;
    --bad: #E5484D;
}
"""

BASE_CSS = """
html, body, [class*="css"], .stApp { font-family: 'DM Sans', sans-serif; color: var(--ink); }
h1, h2, h3, .display { font-family: 'Fredoka', sans-serif !important; color: var(--ink); }

.stApp {
    background:
        radial-gradient(circle at 8% 0%, var(--blob1) 0, transparent 32%),
        radial-gradient(circle at 100% 8%, var(--blob2) 0, transparent 30%),
        radial-gradient(circle at 90% 100%, var(--blob1) 0, transparent 28%),
        var(--bg);
}
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; color: var(--ink); }
header[data-testid="stHeader"] button { color: var(--ink); }
.block-container { padding-top: 2.2rem; max-width: 1150px; }

/* ---------- SIDEBAR ---------- */
[data-testid="stSidebar"] {
    background: var(--side);
    min-width: 290px;
    border-right: 6px solid var(--pink);
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1.2rem; }
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarHeader"] button { color: #FFE9D6 !important; }
[data-testid="stSidebar"] .stButton { margin-bottom: 6px; }
[data-testid="stSidebar"] .stButton > button {
    width: 100%; justify-content: flex-start; height: 58px; padding: 0 22px;
    border: none; border-radius: 18px; background: transparent; color: #FFE9D6;
    letter-spacing: .08em; transition: all .18s ease;
}
[data-testid="stSidebar"] .stButton > button p { font-weight: 700; font-size: 1rem; color: inherit; }
[data-testid="stSidebar"] .stButton > button:hover { background: rgba(255,255,255,.09); color: #fff; transform: translateX(4px); }
[data-testid="stSidebar"] .stButton > button:focus { box-shadow: none; color: #fff; }
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: var(--pink); color: #fff; box-shadow: 0 8px 20px rgba(255,92,138,.35);
}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover { transform: none; }

.st-key-nav_home button {
    height: 96px !important; margin-bottom: 14px;
    border-bottom: 2px dashed rgba(255,233,214,.25) !important; border-radius: 0 !important;
}
.st-key-nav_home button { padding: 0 8px !important; }
.st-key-nav_home button p {
    font-family: 'Fredoka', sans-serif !important; font-size: clamp(1.05rem, 1.35rem, 1.35rem) !important;
    letter-spacing: .02em; white-space: nowrap !important; text-align: center;
}
.st-key-nav_home button:hover { transform: none !important; background: transparent !important; }

/* ---------- HERO ---------- */
.hero { text-align: center; margin: 4px 0 26px; }
.hero .eyebrow {
    display: inline-block; background: var(--pink-soft); color: var(--pink);
    font-weight: 700; font-size: .78rem; letter-spacing: .16em;
    padding: 6px 14px; border-radius: 99px; margin-bottom: 12px;
}
.hero h1 { font-size: 3.1rem; line-height: 1.05; margin: 0 0 8px; font-weight: 700; }
.hero h1 span { color: var(--pink); }
.hero p { color: var(--ink-soft); font-size: 1.05rem; margin: 0; }

/* ---------- CARD (st.container(border=True, key="card_*")) ---------- */
[class*="st-key-card"] {
    background: var(--card); border: 2px solid var(--line) !important; border-radius: 32px !important;
    padding: 34px 38px !important; box-shadow: 0 18px 50px var(--shadow);
}

/* ---------- UPLOADER (disamakan dengan mockup di halaman Tutorial) ---------- */
[data-testid="stFileUploader"] label { display: none; }
/* kotak persegi di tengah kartu */
[data-testid="stFileUploader"] { max-width: 440px; margin: 0 auto; }
[data-testid="stFileUploader"] section {
    display: flex !important; flex-direction: column !important; align-items: center !important;
    justify-content: center !important; flex-wrap: nowrap !important;
    gap: 12px; text-align: center; padding: 20px;
    width: 100%; aspect-ratio: 1 / 1; box-sizing: border-box;
    border: 3px dashed var(--caramel); background: var(--drop); border-radius: 18px;
    transition: all .2s ease;
}
[data-testid="stFileUploader"] section:hover { border-color: var(--pink); background: var(--drop-hover); }

/* ikon di atas */
[data-testid="stFileUploader"] section::before {
    content: "🖼️"; order: -2; width: 100%; text-align: center; font-size: 2.2rem; line-height: 1;
}
/* teks bawaan diganti judul (order -1: tampil sebelum tombol, apa pun posisinya di DOM) */
[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] {
    order: -1; display: block; width: 100%; text-align: center; margin: 0; padding: 0;
    flex: 0 0 auto !important; /* cegah teks bawaan "melar" mengisi tinggi kotak */
}
[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] > * { display: none; }
[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"]::before {
    content: "Drag & drop foto donat di sini";
    display: block; text-align: center; font-weight: 700; font-size: 1rem; line-height: 1.4; color: var(--ink);
}
/* tombol besar UPLOAD IMAGE */
[data-testid="stFileUploader"] section button {
    font-size: 0; padding: 12px 36px; border: none; border-radius: 99px; margin: 0 auto;
    flex: 0 0 auto; background: var(--pink); box-shadow: 0 0 0 6px rgba(255,92,138,.18);
}
[data-testid="stFileUploader"] section button * { display: none; }
[data-testid="stFileUploader"] section button::after {
    content: "UPLOAD IMAGE"; font-size: .95rem; font-weight: 700; letter-spacing: .08em; color: #fff;
}
[data-testid="stFileUploader"] section button:hover { background: var(--pink-hover); }
/* petunjuk format di bawah */
[data-testid="stFileUploader"] section::after {
    content: "JPG, PNG, atau WEBP"; order: 1; width: 100%; text-align: center; font-size: .85rem; color: var(--ink-soft);
}

/* ---------- KAMERA: kotak dashed persegi (sama seperti area upload), video di dalamnya, tombol di bawah ---------- */
[data-testid="stCameraInput"] { max-width: 440px; margin: 0 auto; text-align: center; }
[data-testid="stCameraInput"] label { display: none; }
[data-testid="stCameraInputWebcamComponent"] {
    width: 100% !important; display: flex !important; flex-direction: column !important; align-items: center !important;
}
/* kotak dashed persegi */
[data-testid="stCameraInputWebcamStyledBox"] {
    position: relative; display: flex !important; align-items: center !important; justify-content: center !important;
    width: 100% !important; height: auto !important; aspect-ratio: 1 / 1; box-sizing: border-box; overflow: hidden;
    padding: 18px; border: 3px dashed var(--caramel) !important; border-radius: 18px !important;
    background: var(--drop) !important; color: var(--ink-soft); transition: all .2s ease;
}
[data-testid="stCameraInputWebcamStyledBox"]:hover { border-color: var(--pink) !important; background: var(--drop-hover) !important; }
/* video/foto di dalam kotak, rasio asli kamera (tidak terpotong) */
[data-testid="stCameraInputWebcamStyledBox"] video,
[data-testid="stCameraInputWebcamStyledBox"] img {
    display: block; width: 100% !important; height: auto !important; max-height: 100%;
    object-fit: contain; border: none !important; border-radius: 12px !important;
    background: #1E1412; box-shadow: 0 8px 22px var(--img-shadow);
}
/* tombol TAKE PHOTO di bawah kotak */
[data-testid="stCameraInput"] button:not([data-testid="stCameraInputSwitchButton"]) {
    position: static !important; display: block; width: auto !important; min-width: 230px;
    margin: 20px auto 0 !important; padding: 12px 36px; height: auto;
    background: var(--pink) !important; border: none !important; border-radius: 99px !important;
    box-shadow: 0 0 0 6px rgba(255,92,138,.18) !important; transition: all .18s ease;
}
[data-testid="stCameraInput"] button:not([data-testid="stCameraInputSwitchButton"]):hover { background: var(--pink-hover) !important; }
[data-testid="stCameraInput"] button:not([data-testid="stCameraInputSwitchButton"]),
[data-testid="stCameraInput"] button:not([data-testid="stCameraInputSwitchButton"]) * {
    color: #fff !important; font-weight: 700; font-size: .95rem; letter-spacing: .08em; text-transform: uppercase;
}
[data-testid="stCameraInput"] small, [data-testid="stCameraInput"] p { color: var(--ink-soft); }

/* tombol SWITCH CAMERA: lingkaran kecil di pojok kanan atas kotak.
   Kena dua kemungkinan: (a) elemen ber-data-testid switch, (b) tombol apa pun yang ada di dalam kotak kamera */
[data-testid="stCameraInput"] [data-testid="stCameraInputSwitchButton"],
[data-testid="stCameraInput"] [data-testid="stCameraInputWebcamStyledBox"] button:not([data-testid="stCameraInputSwitchButton"] button) {
    position: absolute !important; top: 12px !important; right: 12px !important; left: auto !important; bottom: auto !important;
    z-index: 5; width: 40px !important; height: 40px !important; min-width: 0 !important;
    margin: 0 !important; padding: 0 !important; border-radius: 50% !important;
    display: inline-flex !important; align-items: center; justify-content: center;
    background: rgba(62,34,24,.62) !important; border: none !important;
    box-shadow: 0 4px 12px var(--img-shadow) !important; transition: background .18s ease;
}
[data-testid="stCameraInput"] [data-testid="stCameraInputSwitchButton"]:hover,
[data-testid="stCameraInput"] [data-testid="stCameraInputWebcamStyledBox"] button:not([data-testid="stCameraInputSwitchButton"] button):hover {
    background: var(--pink) !important;
}
/* kalau data-testid ada di pembungkus, tombol di dalamnya cukup mengisi lingkaran */
[data-testid="stCameraInput"] [data-testid="stCameraInputSwitchButton"] button {
    position: static !important; width: 100% !important; height: 100% !important; min-width: 0 !important;
    margin: 0 !important; padding: 0 !important; border: none !important; border-radius: 50% !important;
    background: transparent !important; box-shadow: none !important;
    display: flex !important; align-items: center; justify-content: center;
}
[data-testid="stCameraInput"] [data-testid="stCameraInputSwitchButton"] svg,
[data-testid="stCameraInput"] [data-testid="stCameraInputWebcamStyledBox"] button svg {
    width: 20px; height: 20px; color: #fff !important; fill: currentColor;
}

/* petunjuk di bawah tombol */
[data-testid="stCameraInput"]::after {
    content: "Izinkan akses kamera di browser, lalu ambil foto";
    display: block; margin-top: 14px; font-size: .85rem; color: var(--ink-soft);
}

/* ---------- SISA ELEMEN LAMA ("stale") SAAT ANALISIS BERJALAN: disembunyikan ---------- */
[data-stale="true"] [data-testid="stFileUploader"],
[data-stale="true"] [data-testid="stCameraInput"],
[data-testid="stFileUploader"][data-stale="true"],
[data-testid="stCameraInput"][data-stale="true"],
[data-stale="true"]:has([data-testid="stFileUploader"]),
[data-stale="true"]:has([data-testid="stCameraInput"]),
[class*="st-key-card_input"][data-stale="true"] {
    display: none !important;
}

/* ---------- BUTTONS (main area) ---------- */
section.main .stButton > button, [data-testid="stMain"] .stButton > button {
    border-radius: 99px; height: 54px; font-weight: 700; letter-spacing: .1em;
    border: none; background: var(--pink); color: #fff;
    box-shadow: 0 10px 24px rgba(255,92,138,.35); transition: all .18s ease;
}
[data-testid="stMain"] .stButton > button p { color: #fff; font-weight: 700; }
[data-testid="stMain"] .stButton > button:hover { transform: translateY(-2px); background: var(--pink-hover); color: #fff; }

/* ---------- TAB PILL: UPLOAD | CAMERA ---------- */
.st-key-tabbar { display: flex; flex-direction: column; align-items: center; margin-bottom: 22px; }
.st-key-tabbar > div { width: 100%; }
.st-key-tabbar [data-testid="stHorizontalBlock"] {
    width: fit-content; margin: 0 auto; gap: 6px; flex-wrap: nowrap;
    background: var(--caramel-soft); padding: 6px; border-radius: 99px;
}
.st-key-tabbar [data-testid="stColumn"], .st-key-tabbar [data-testid="column"] {
    width: auto !important; flex: 0 0 auto !important; min-width: 0 !important;
}
.st-key-tabbar .stButton > button {
    height: 44px; padding: 0 32px; border-radius: 99px; border: none;
    background: transparent; color: var(--ink-soft); box-shadow: none; letter-spacing: .1em;
}
.st-key-tabbar .stButton > button p { color: inherit; }
.st-key-tabbar .stButton > button:hover { background: rgba(255,92,138,.12); color: var(--ink); transform: none; }
.st-key-tabbar .stButton > button[kind="primary"],
.st-key-tabbar .stButton > button[kind="primary"]:hover { background: var(--tab-on); color: #fff; }

/* ---------- ALERT / SPINNER ---------- */
[data-testid="stAlert"] {
    background: var(--alert-bg); border: 2px solid var(--line); border-radius: 18px;
}
[data-testid="stAlert"], [data-testid="stAlert"] * { color: var(--ink); }
[data-testid="stSpinner"], [data-testid="stSpinner"] * { color: var(--ink); }

/* ---------- IMAGE ---------- */
[data-testid="stImage"] img { border-radius: 24px; box-shadow: 0 14px 36px var(--img-shadow); }

/* ---------- RESULT ---------- */
.pill {
    display: inline-block; font-weight: 700; font-size: .75rem; letter-spacing: .16em;
    background: var(--caramel-soft); color: var(--pill-text); padding: 6px 14px; border-radius: 99px;
}
.result-label {
    font-family: 'Fredoka', sans-serif; font-size: 2.3rem; font-weight: 700;
    line-height: 1.12; margin: 14px 0 6px; letter-spacing: .01em; color: var(--ink);
}
.big-pct { font-family: 'Fredoka', sans-serif; font-size: 3.6rem; font-weight: 700; color: var(--pink); line-height: 1; }
.big-pct small { font-size: 1.3rem; color: var(--ink-soft); font-weight: 500; margin-left: 6px; }
.meter { height: 14px; background: var(--track); border-radius: 99px; overflow: hidden; margin: 14px 0 16px; }
.meter > div { height: 100%; border-radius: 99px; background: linear-gradient(90deg, var(--caramel), var(--pink)); }
.badge { display: inline-block; font-weight: 700; letter-spacing: .12em; font-size: .85rem; padding: 7px 16px; border-radius: 99px; color: #fff; }
.badge.HIGH { background: var(--ok); }
.badge.MEDIUM { background: var(--warn); }
.badge.LOW { background: var(--bad); }
.conf-text { color: var(--ink-soft); font-weight: 500; margin-left: 10px; }

.breakdown { margin-top: 22px; padding-top: 18px; border-top: 2px dashed var(--line); }
.breakdown h4 { font-size: .78rem; letter-spacing: .16em; color: var(--ink-soft); margin: 0 0 10px; font-weight: 700; }
.row { display: flex; align-items: center; gap: 12px; margin: 8px 0; font-size: .92rem; color: var(--ink); }
.row .name { width: 44%; font-weight: 500; }
.row .track { flex: 1; height: 8px; background: var(--track); border-radius: 99px; overflow: hidden; }
.row .track > div { height: 100%; background: var(--bar); border-radius: 99px; }
.row .val { width: 52px; text-align: right; font-weight: 700; }

/* ---------- TUTORIAL ---------- */
.step { display: flex; gap: 16px; align-items: flex-start; background: var(--card); border: 2px solid var(--line);
        border-radius: 22px; padding: 16px 20px; margin-bottom: 12px; box-shadow: 0 8px 24px var(--shadow); color: var(--ink); }
.step .num { flex: 0 0 38px; height: 38px; border-radius: 50%; background: var(--pink); color: #fff;
             font-family: 'Fredoka', sans-serif; font-weight: 700; display: grid; place-items: center; }
.step b { display: block; margin-bottom: 2px; }
.step span { color: var(--ink-soft); font-size: .94rem; }

.mock-tabs { display: flex; justify-content: center; gap: 6px; background: var(--caramel-soft); padding: 6px; border-radius: 99px; width: fit-content; margin: 0 auto 16px; }
.mock-tabs div { padding: 8px 22px; border-radius: 99px; font-weight: 700; letter-spacing: .1em; font-size: .85rem; color: var(--ink-soft); }
.mock-tabs div.on { background: var(--tab-on); color: #fff; }
.mock-drop { border: 3px dashed var(--caramel); border-radius: 22px; background: var(--drop); padding: 34px 10px; text-align: center; position: relative; color: var(--ink); }
.mock-drop .btn { display: inline-block; background: var(--pink); color: #fff; font-weight: 700; letter-spacing: .08em;
                  padding: 10px 26px; border-radius: 99px; box-shadow: 0 0 0 6px rgba(255,92,138,.18); }
.mock-drop .hint { margin-top: 10px; color: var(--ink-soft); font-size: .85rem; }
.arrow { text-align: center; font-size: 1.1rem; color: var(--pink); font-weight: 700; margin-top: 12px; }

/* ---------- ABOUT ---------- */
.chip { display: inline-block; background: var(--caramel-soft); color: var(--chip-text); font-weight: 700;
        font-size: .82rem; padding: 6px 14px; border-radius: 99px; margin: 0 6px 8px 0; }
.about-title { font-family: 'Fredoka', sans-serif; font-size: 1.5rem; font-weight: 700; margin: 0 0 10px; color: var(--ink); }
.about-text { color: var(--ink-soft); line-height: 1.7; }
.about-text b { color: var(--ink); }
.about-text a { color: var(--pink); font-weight: 700; text-decoration: none; }
"""

_vars = LIGHT_VARS

st.markdown(
    "<style>" + FONT_IMPORT + _vars + BASE_CSS + "</style>",
    unsafe_allow_html=True,
)


# ============================================================
# MODEL
# ============================================================
def _get_token():
    if HF_TOKEN:
        return HF_TOKEN
    try:
        return st.secrets.get("HF_TOKEN", None)
    except Exception:
        return None


@st.cache_resource(show_spinner="Memuat model dari Hugging Face...")
def load_model():
    token = _get_token()
    processor = AutoImageProcessor.from_pretrained(HF_MODEL_ID, token=token)
    model = AutoModelForImageClassification.from_pretrained(HF_MODEL_ID, token=token)
    model.eval()
    return processor, model

# ============================================================
# REMBG 
# ============================================================
REMBG_MODEL = "u2net"        
BG_COLOR = (255, 255, 255)    


@st.cache_resource(show_spinner="Memuat model penghapus background...")
def load_rembg_session():
    return new_session(REMBG_MODEL)

def remove_background(image: Image.Image) -> Image.Image:
    session = load_rembg_session()
    cutout = remove(image.convert("RGB"), session=session)  # hasil RGBA
    bg = Image.new("RGB", cutout.size, BG_COLOR)
    bg.paste(cutout, mask=cutout.split()[3])
    return bg

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
    "cincin_lolos",        # 0
    "cincin_penyok",       # 1
    "cincin_tidaksimetris",  # 2
    "isi_bocor",           # 3
    "isi_lolos",           # 4
    "isi_penyok",          # 5
]


def prettify(label: str) -> str:
    key = re.sub(r"[\s\-]+", "_", str(label).strip().lower())
    m = re.fullmatch(r"label_(\d+)", key)
    if m and int(m.group(1)) < len(CLASS_ORDER):
        key = CLASS_ORDER[int(m.group(1))]
    return LABEL_NAMES.get(key, key.replace("_", " ").title())


def predict(image: Image.Image):
    processor, model = load_model()
    image = remove_background(image)
    inputs = processor(images=image.convert("RGB"), return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = torch.softmax(logits, dim=-1)[0]
    ranked = sorted(
        [(model.config.id2label[i], float(p)) for i, p in enumerate(probs)],
        key=lambda x: x[1],
        reverse=True,
    )
    return ranked[0][0], ranked[0][1], ranked


def confidence_level(score: float) -> str:
    if score >= HIGH_THRESHOLD:
        return "HIGH"
    if score >= MEDIUM_THRESHOLD:
        return "MEDIUM"
    return "LOW"


CONF_TEXT = {
    "HIGH": "Model sangat yakin dengan hasil ini",
    "MEDIUM": "Cukup yakin, coba foto lebih jelas bila ragu",
    "LOW": "Kurang yakin, coba foto dengan cahaya lebih baik",
}

# ============================================================
# STATE & NAVIGASI
# ============================================================
for k, v in {
    "page": "classification",
    "image": None,
    "result": None,
    "pending": None,
    "reset_key": 0,
    "input_mode": "upload",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


def go(page):
    st.session_state.page = page


def set_mode(mode):
    st.session_state.input_mode = mode


def nav_button(label, page, key):
    active = st.session_state.page == page
    st.button(
        label,
        key=key,
        on_click=go,
        args=(page,),
        type="primary" if active else "secondary",
        use_container_width=True,
    )


with st.sidebar:
    st.button("🍩 DO OR DONUT", key="nav_home", on_click=go, args=("classification",))
    nav_button("CLASSIFICATION", "classification", "nav_cls")
    nav_button("TUTORIAL", "tutorial", "nav_tut")
    nav_button("ABOUT", "about", "nav_about")


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


# ============================================================
# HALAMAN: CLASSIFICATION
# ============================================================
def result_html(label, score, ranked):
    level = confidence_level(score)
    debug_html = (
        f'<div style="font-size:.75rem;color:var(--ink-soft);">label model: <code>{label}</code></div>'
        if DEBUG_LABEL else ""
    )
    rows = "".join(
        f"""
        <div class="row">
            <div class="name">{prettify(n)}</div>
            <div class="track"><div style="width:{p * 100:.1f}%"></div></div>
            <div class="val">{p * 100:.1f}%</div>
        </div>"""
        for n, p in ranked
    )
    return f"""
    <span class="pill">HASIL KLASIFIKASI</span>
    <div class="result-label">{prettify(label)}</div>
    {debug_html}
    <div class="big-pct">{score * 100:.0f}%<small></small></div>
    <div class="meter"><div style="width:{score * 100:.0f}%"></div></div>
    <span style="font-weight:700;letter-spacing:.08em;font-size:.85rem;color:var(--ink);">CONFIDENCE</span>&nbsp;
    <span class="badge {level}">{level}</span>
    <div class="conf-text" style="margin:10px 0 0;">{CONF_TEXT[level]}</div>
    <div class="breakdown"><h4>DETAIL SEMUA KELAS</h4>{rows}</div>
    """


def page_classification():
    hero("Classification", "Unggah foto donat atau ambil gambar langsung dari kamera untuk mulai klasifikasi.")

    slot = st.empty()

    # ---------- Hasil ----------
    if st.session_state.result is not None:
        label, score, ranked = st.session_state.result
        with slot.container(border=True, key="card_result"):
            c1, c2 = st.columns([1, 1.1], gap="large")
            with c1:
                st.image(st.session_state.image, use_container_width=True)
            with c2:
                st.markdown(result_html(label, score, ranked), unsafe_allow_html=True)
                st.write("")
                if st.button("TRY ANOTHER IMAGE", use_container_width=True):
                    st.session_state.image = None
                    st.session_state.result = None
                    st.session_state.reset_key += 1
                    st.rerun()
        return

    # ---------- Sedang dianalisis ----------
    if st.session_state.pending is not None:
        img = st.session_state.pending
        with slot.container(border=True, key="card_analyzing"):
            c1, c2 = st.columns([1, 1.1], gap="large")
            with c1:
                st.image(img, use_container_width=True)
            with c2:
                st.markdown(
                    """
                    <span class="pill">SEDANG DIANALISIS</span>
                    <div class="result-label">Menganalisis foto…</div>
                    <div class="about-text">Model Vision Transformer sedang memeriksa donatmu.
                    Mohon tunggu sebentar.</div>
                    """,
                    unsafe_allow_html=True,
                )
                with st.spinner("Model ViT sedang bekerja..."):
                    label, score, ranked = predict(img)
        st.session_state.image = img
        st.session_state.result = (label, score, ranked)
        st.session_state.pending = None
        st.rerun()
        return

    # ---------- Input ----------
    key = st.session_state.reset_key
    picked = None
    mode = st.session_state.input_mode
    with slot.container(border=True, key="card_input"):
        with st.container(key="tabbar"):
            b1, b2 = st.columns(2)
            with b1:
                st.button(
                    "UPLOAD", key="tab_upload", on_click=set_mode, args=("upload",),
                    type="primary" if mode == "upload" else "secondary",
                )
            with b2:
                st.button(
                    "CAMERA", key="tab_camera", on_click=set_mode, args=("camera",),
                    type="primary" if mode == "camera" else "secondary",
                )

        if mode == "upload":
            f = st.file_uploader(
                "Upload gambar donat",
                type=["jpg", "jpeg", "png", "webp"],
                key=f"uploader_{key}",
                label_visibility="collapsed",
            )
            if f is not None:
                picked = Image.open(f).convert("RGB")
        else:
            c = st.camera_input("Ambil foto donat", key=f"camera_{key}", label_visibility="collapsed")
            if c is not None:
                picked = Image.open(c).convert("RGB")

    if picked is not None:
        st.session_state.pending = picked
        st.rerun()


# ============================================================
# HALAMAN: TUTORIAL
# ============================================================
def page_tutorial():
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
            ("Kirim gambar donat", "Klik UPLOAD IMAGE untuk pilih foto atau TAKE PHOTO untuk mengambil foto langsung."),
            ("Baca hasilnya", "Hasil klasifikasi akan muncul otomatis. Klik TRY ANOTHER IMAGE untuk mengulang."),
        ]
        html = "".join(
            f'<div class="step"><div class="num">{i}</div><div><b>{t}</b><span>{d}</span></div></div>'
            for i, (t, d) in enumerate(steps, 1)
        )
        st.markdown(html, unsafe_allow_html=True)
        st.info("💡 Tips: gunakan foto yang terang dan fokus, dengan donat terlihat jelas di tengah gambar.")


# ============================================================
# HALAMAN: ABOUT
# ============================================================
def page_about():
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
                <a href="https://huggingface.co/{HF_MODEL_ID}" target="_blank">{HF_MODEL_ID}</a>
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


# ============================================================
# ROUTER
# ============================================================
page = st.session_state.page
if page == "classification":
    page_classification()
elif page == "tutorial":
    page_tutorial()
else:
    page_about()