# ══════════════════════════════════════════════════════════════════════
#  FLUX Image Studio — Nexflow Studio
#  Platform : Streamlit Community Cloud (free)
#  Images   : gemini-2.5-flash-image via new google-genai SDK
#  Prompt AI: gemini-3.8-flash (free)
#  Key Rotation: 4 keys x 500/day = 2000 free images/day
#  Built by  : JAI SURYA | Nexflow Studio
# ══════════════════════════════════════════════════════════════════════

import streamlit as st
import random
import io
import os
import zipfile
import time
import base64
from google import genai
from google.genai import types
from PIL import Image

# ─── Page config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="FLUX Image Studio — Nexflow",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.hero {
    text-align: center; padding: 2rem 0 1.5rem;
    background: linear-gradient(135deg, #0f0a1e 0%, #1a1035 100%);
    border-radius: 20px; margin-bottom: 1.5rem;
    border: 1px solid rgba(168,85,247,0.2);
}
.hero h1 {
    font-size: 2.8rem; font-weight: 900;
    background: linear-gradient(90deg, #7c3aed, #a855f7, #ec4899);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0 0 0.5rem 0;
}
.hero p { color: #9ca3af; font-size: 1rem; margin: 0 0 1rem 0; }
.badges { display: flex; flex-wrap: wrap; justify-content: center; gap: 6px; }
.badge {
    background: rgba(30,27,75,0.9); color: #c4b5fd;
    padding: 4px 14px; border-radius: 99px;
    font-size: 0.72rem; font-weight: 600;
    border: 1px solid rgba(139,92,246,0.3);
}
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #5b21b6, #7c3aed, #a855f7, #ec4899) !important;
    color: white !important; font-size: 1.1rem !important;
    font-weight: 800 !important; border: none !important;
    border-radius: 14px !important; padding: 0.75rem 1.5rem !important;
    box-shadow: 0 4px 24px rgba(139,92,246,0.4) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(139,92,246,0.6) !important;
}
.status-ok {
    background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3);
    border-radius: 10px; padding: 10px 16px;
    color: #6ee7b7; font-size: 0.85rem; font-family: monospace;
}
.status-err {
    background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3);
    border-radius: 10px; padding: 10px 16px; color: #fca5a5; font-size: 0.85rem;
}
section[data-testid="stSidebar"] {
    background: #130d28 !important;
    border-right: 1px solid rgba(168,85,247,0.15);
}
.footer {
    text-align: center; color: #4b5563; font-size: 0.78rem;
    margin-top: 2rem; padding-top: 1rem;
    border-top: 1px solid rgba(168,85,247,0.1);
}
.footer b { color: #7c3aed; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
#  KEY ROTATION
# ════════════════════════════════════════════════════════════════════
def get_api_keys():
    keys = []
    for i in range(1, 5):
        k = st.secrets.get(f"GEMINI_KEY_{i}", "")
        if k and k.strip() and not k.startswith("AIza_your"):
            keys.append(k.strip())
    for i in range(1, 5):
        k = os.environ.get(f"GEMINI_KEY_{i}", "")
        if k and k.strip() and k not in keys:
            keys.append(k.strip())
    return keys

def get_next_key(keys, failed):
    available = [k for k in keys if k not in failed]
    return random.choice(available) if available else None

# ════════════════════════════════════════════════════════════════════
#  STYLES & RATIOS
# ════════════════════════════════════════════════════════════════════
STYLES = {
    "✨ None (Raw)": "",
    "📷 Photorealistic": "hyperrealistic DSLR photography, 8K UHD, tack-sharp focus, natural golden-hour lighting, shallow depth of field, ultra-detailed texture",
    "🎬 Cinematic": "cinematic widescreen movie still, dramatic lighting, anamorphic lens flare, film grain, Hollywood blockbuster color grade, IMAX quality",
    "🎌 Anime / Studio Ghibli": "high quality anime illustration, Studio Ghibli aesthetic, vibrant cel-shading, clean crisp line art, lush detailed background, soft pastel palette",
    "🎨 Digital Concept Art": "professional digital concept art, ArtStation quality, volumetric cinematic lighting, intricate details, 4K render",
    "🖌️ Oil Painting": "classical oil painting on canvas, rich impasto brushstrokes, old master chiaroscuro lighting, museum-quality",
    "💧 Watercolor": "delicate watercolor illustration, soft wet-on-wet washes, translucent luminous colors, hand-painted paper grain",
    "👾 Pixel Art": "crisp 16-bit pixel art, retro JRPG aesthetic, clean pixel-perfect sprite work, vibrant limited palette",
    "⚡ Neon Cyberpunk": "cyberpunk dystopian cityscape, vivid neon signs in purple cyan magenta, rain-slicked reflective streets, holographic advertisements, Blade Runner aesthetic",
    "🏰 Dark Fantasy Epic": "epic dark fantasy digital art, dramatic stormy atmospheric lighting, intricate gothic architectural details, cinematic hero composition",
    "◻️ Clean Minimalist": "ultra-clean minimalist design, precise geometric composition, generous negative space, modern Swiss aesthetic",
    "🕰️ Vintage / Retro": "authentic vintage analog photography, Kodachrome film simulation, warm faded tones, light leaks, grain, 1970s documentary aesthetic",
    "🔮 3D Render / Blender": "photorealistic 3D CGI render, Blender Cycles path tracing, physically-based materials, HDRI studio lighting, 8K render",
    "✏️ Pencil Sketch": "detailed graphite pencil sketch, masterful cross-hatching, fine line work, smudge shading, sketchbook texture",
    "🪔 Indian Traditional Art": "Tanjore gold-leaf painting style, vibrant jewel-tone colors, intricate mandala motifs, traditional Indian folk art",
    "🌊 Surreal / Dreamlike": "hyper-surrealist fine art, impossible dreamlike geometry, ethereal glowing atmosphere, Salvador Dali inspired",
}

RATIOS = {
    "⬜ Square 1:1 (1024×1024)":     ("1:1",   1024, 1024),
    "📱 Portrait 9:16 (768×1344)":   ("9:16",  768,  1344),
    "🖼️ Portrait 2:3 (832×1216)":   ("3:4",   832,  1216),
    "🖥️ Landscape 3:2 (1216×832)":  ("4:3",   1216,  832),
    "📺 Widescreen 16:9 (1344×768)": ("16:9",  1344,  768),
    "🎬 Ultrawide 21:9 (1536×640)":  ("16:9",  1536,  640),
    "📷 Classic 4:3 (1152×864)":     ("4:3",   1152,  864),
}

EXAMPLES = [
    ("A Bengal tiger in a neon-lit Tokyo alley at midnight, heavy rain",  "⚡ Neon Cyberpunk",      "🖥️ Landscape 3:2 (1216×832)"),
    ("Tamil Chola warrior queen in golden armor, palace at dusk",         "🏰 Dark Fantasy Epic",   "📱 Portrait 9:16 (768×1344)"),
    ("Nexflow AI startup logo, geometric, purple gradient, minimal",      "◻️ Clean Minimalist",    "⬜ Square 1:1 (1024×1024)"),
    ("Anime school boy and girl on rooftop watching stars at night",      "🎌 Anime / Studio Ghibli","📺 Widescreen 16:9 (1344×768)"),
    ("Abstract AI neural network, glowing nodes, deep space background",  "🔮 3D Render / Blender", "📺 Widescreen 16:9 (1344×768)"),
    ("Portrait of elderly Indian grandfather, morning village light",     "📷 Photorealistic",      "🖼️ Portrait 2:3 (832×1216)"),
]

# ════════════════════════════════════════════════════════════════════
#  PROMPT ENHANCEMENT
# ════════════════════════════════════════════════════════════════════
ENHANCE_SYSTEM = """You are a world-class AI image prompt engineer.
Transform the short prompt into a rich, detailed generation prompt.
Rules:
- Preserve exact subject and intent
- Add: lighting, camera angle, composition, color palette, atmosphere, texture, mood
- Use natural comma-separated phrases only
- Maximum 100 words
- Use only simple ASCII characters, no special unicode symbols
- Output ONLY the enhanced prompt, nothing else, no explanation"""

def enhance_prompt(raw: str, enabled: bool, api_key: str) -> str:
    if not enabled or not raw.strip() or not api_key:
        return raw.strip()
    try:
        client = genai.Client(api_key=api_key)
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{ENHANCE_SYSTEM}\n\nEnhance this prompt: {raw}",
        )
        enhanced = resp.text.strip().strip('"').strip("'")
        enhanced = ''.join(c for c in enhanced if ord(c) < 128)
        return enhanced if len(enhanced) > 15 else raw.strip()
    except Exception as e:
        st.warning(f"Enhancement skipped: {e}")
        return raw.strip()

# ════════════════════════════════════════════════════════════════════
#  IMAGE GENERATION — gemini-2.5-flash-image (correct current model)
# ════════════════════════════════════════════════════════════════════
def generate_image(prompt: str, aspect_ratio: str, api_key: str) -> Image.Image:
    client = genai.Client(api_key=api_key)

    full_prompt = f"{prompt}. High quality, no watermark, no text overlay, no logo, no signature."

    resp = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=full_prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
            ),
        ),
    )

    for part in resp.candidates[0].content.parts:
        if part.inline_data is not None:
            img_data = part.inline_data.data
            if isinstance(img_data, str):
                img_data = base64.b64decode(img_data)
            return Image.open(io.BytesIO(img_data))

    raise ValueError("No image in response. Check your API key permissions at aistudio.google.com")

# ════════════════════════════════════════════════════════════════════
#  KEY ROTATION WRAPPER
# ════════════════════════════════════════════════════════════════════
def generate_with_rotation(prompt: str, aspect_ratio: str, keys: list) -> tuple:
    failed = set()
    last_err = None
    while True:
        key = get_next_key(keys, failed)
        if key is None:
            raise Exception(f"All keys exhausted. Last error: {last_err}")
        try:
            img = generate_image(prompt, aspect_ratio, key)
            return img, keys.index(key) + 1
        except Exception as e:
            err = str(e).lower()
            if any(x in err for x in ["quota", "rate", "limit", "429", "exhausted", "resource"]):
                failed.add(key)
                last_err = str(e)
                time.sleep(3)
                continue
            raise e

# ════════════════════════════════════════════════════════════════════
#  ZIP HELPER
# ════════════════════════════════════════════════════════════════════
def make_zip(images: list, run_id: int) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, img in enumerate(images):
            ibuf = io.BytesIO()
            img.save(ibuf, format="PNG")
            zf.writestr(f"nexflow_image_{i+1:02d}_{run_id}.png", ibuf.getvalue())
    return buf.getvalue()

def img_to_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# ════════════════════════════════════════════════════════════════════
#  UI
# ════════════════════════════════════════════════════════════════════
keys = get_api_keys()

st.markdown("""
<div class="hero">
    <h1>⚡ FLUX Image Studio</h1>
    <p>High-quality AI image generation — free, open source, production-ready</p>
    <div class="badges">
        <span class="badge">🆓 100% Free</span>
        <span class="badge">🔓 Open Source</span>
        <span class="badge">🧠 Gemini 2.5 Flash Image</span>
        <span class="badge">🔁 Auto Key Rotation</span>
        <span class="badge">🖼️ Batch Generation</span>
        <span class="badge">💎 GPT-4o Level Quality</span>
        <span class="badge">❤️ JAI SURYA</span>
    </div>
</div>
""", unsafe_allow_html=True)

if not keys:
    st.error(
        "⚠️ No API keys found!\n\n"
        "Go to: Manage app → Settings → Secrets → add:\n\n"
        "```\nGEMINI_KEY_1 = 'AIza...'\n"
        "GEMINI_KEY_2 = 'AIza...'\n"
        "GEMINI_KEY_3 = 'AIza...'\n"
        "GEMINI_KEY_4 = 'AIza...'\n```\n\n"
        "Get free keys at: aistudio.google.com"
    )
    st.stop()

st.success(f"✅ {len(keys)} key(s) active — up to {len(keys) * 500} free images/day with auto rotation")

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎨 Style & Layout")
    style      = st.selectbox("Style Preset", list(STYLES.keys()), index=0)
    ratio_key  = st.selectbox("Aspect Ratio", list(RATIOS.keys()), index=0)
    num_images = st.slider("Number of Images", 1, 4, 1)

    st.markdown("---")
    st.markdown("### ⚙️ Advanced")
    use_enhance = st.toggle("✨ AI Enhance Prompt (Gemini Flash)", value=True)

    st.markdown("---")
    st.markdown("### 🔑 Key Status")
    for i, k in enumerate(keys):
        st.markdown(f"Key {i+1}: `...{k[-6:]}` ✅")

    st.markdown("---")
    st.markdown("### 💡 Examples")
    for i, (ep, es, er) in enumerate(EXAMPLES):
        if st.button(f"#{i+1} {ep[:36]}...", key=f"ex_{i}"):
            st.session_state.update({"ex_prompt": ep, "ex_style": es, "ex_ratio": er})
            st.rerun()

# ── Main ──────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    if "ex_style" in st.session_state:
        style     = st.session_state.pop("ex_style", style)
        ratio_key = st.session_state.pop("ex_ratio", ratio_key)

    prompt = st.text_area(
        "✏️ Your Prompt",
        value=st.session_state.pop("ex_prompt", ""),
        placeholder=(
            "Describe what you want to see...\n\n"
            "e.g. Tamil Chola warrior queen in golden armor standing on "
            "a temple rooftop at sunset, dramatic lighting"
        ),
        height=160,
    )

    enhanced_box  = st.empty()
    generate_btn  = st.button("🚀  Generate Images", type="primary")
    status_area   = st.empty()
    download_area = st.empty()

with col_right:
    gallery_area = st.empty()
    gallery_area.markdown(
        "<div style='text-align:center;color:#4b5563;padding:80px 0;'>"
        "🖼️ Generated images appear here</div>",
        unsafe_allow_html=True,
    )

# ── Generation ────────────────────────────────────────────────────
if generate_btn:
    if not prompt.strip():
        status_area.markdown(
            '<div class="status-err">⚠️ Please enter a prompt.</div>',
            unsafe_allow_html=True,
        )
    else:
        t0     = time.time()
        run_id = random.randint(1000, 9999)

        # 1. Enhance
        with st.spinner("✨ Enhancing prompt..."):
            enhanced = enhance_prompt(prompt, use_enhance, keys[0])

        # 2. Build final prompt
        suffix = STYLES.get(style, "")
        final  = f"{enhanced}, {suffix}" if suffix else enhanced
        enhanced_box.text_area("📝 Final Prompt → Gemini", value=final, height=90, disabled=True)

        # 3. Aspect ratio
        aspect_ratio, w, h = RATIOS.get(ratio_key, ("1:1", 1024, 1024))

        # 4. Generate
        progress = st.progress(0, text="🎨 Generating with Gemini 2.5 Flash Image...")
        images   = []

        try:
            for i in range(num_images):
                progress.progress(
                    i / num_images,
                    text=f"🎨 Image {i+1} of {num_images} — auto key rotation active...",
                )
                img, key_num = generate_with_rotation(final, aspect_ratio, keys)
                images.append(img)

                # Show gallery progressively with per-image download
                with gallery_area.container():
                    cols = st.columns(2)
                    for j, im in enumerate(images):
                        with cols[j % 2]:
                            st.image(im, use_container_width=True)
                            st.download_button(
                                label=f"⬇️ Download Image {j+1}",
                                data=img_to_bytes(im),
                                file_name=f"nexflow_{j+1}_{run_id}.png",
                                mime="image/png",
                                key=f"dl_{j}_{run_id}_{i}",
                                use_container_width=True,
                            )

                if i < num_images - 1:
                    time.sleep(2)

            progress.progress(1.0, text="✅ Done!")
            elapsed = time.time() - t0

            status_area.markdown(
                f'<div class="status-ok">'
                f'✅ {len(images)} image(s) · {elapsed:.1f}s · '
                f'Gemini 2.5 Flash Image · No watermark · {w}x{h}'
                f'</div>',
                unsafe_allow_html=True,
            )

            zip_data = make_zip(images, run_id)
            download_area.download_button(
                label="📥 Download All as ZIP",
                data=zip_data,
                file_name=f"nexflow_all_{run_id}.zip",
                mime="application/zip",
                use_container_width=True,
            )

        except Exception as e:
            progress.empty()
            status_area.markdown(
                f'<div class="status-err">❌ {str(e)}</div>',
                unsafe_allow_html=True,
            )

# Footer
st.markdown("""
<div class="footer">
    Powered by <b>Gemini 2.5 Flash Image</b> (Google · Free) &nbsp;·&nbsp;
    Prompt AI: <b>Gemini 2.5 Flash</b> (Free) &nbsp;·&nbsp;
    Auto Key Rotation: <b>4 Keys x 500/day</b> &nbsp;·&nbsp;
    Built with ❤️ by <b>JAI SURYA</b> &nbsp;·&nbsp; <b>Nexflow Studio</b>
</div>
""", unsafe_allow_html=True)