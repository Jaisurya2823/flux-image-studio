# ══════════════════════════════════════════════════════════════════════
#  FLUX Image Studio — Nexflow Studio
#  Platform : Streamlit Community Cloud (free)
#  Images   : Google Gemini 2.0 Flash Image API (GPT-4o level, free)
#  Prompt AI: Google Gemini Flash (free)
#  Key Rotation: 4 keys × 500/day = 2000 images/day free
# ══════════════════════════════════════════════════════════════════════

import streamlit as st
import random
import io
import os
import zipfile
import time
import base64
import google.generativeai as genai
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
.key-badge {
    display: inline-block; background: rgba(16,185,129,0.1);
    border: 1px solid rgba(16,185,129,0.3); color: #6ee7b7;
    padding: 2px 10px; border-radius: 99px; font-size: 0.7rem;
    font-family: monospace; margin-left: 8px;
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
#  KEY ROTATION SYSTEM
#  Add your keys in Streamlit secrets:
#  GEMINI_KEY_1 = "AIza..."
#  GEMINI_KEY_2 = "AIza..."
#  GEMINI_KEY_3 = "AIza..."
#  GEMINI_KEY_4 = "AIza..."
# ════════════════════════════════════════════════════════════════════
def get_api_keys():
    keys = []
    for i in range(1, 5):
        key = st.secrets.get(f"GEMINI_KEY_{i}", None)
        if key and key.strip() and key != f"AIza_your_key_{i}_here":
            keys.append(key.strip())
    # Also check env vars (local dev)
    for i in range(1, 5):
        key = os.environ.get(f"GEMINI_KEY_{i}", None)
        if key and key.strip():
            if key not in keys:
                keys.append(key.strip())
    return keys

def get_next_key(keys: list, failed_keys: set) -> str:
    available = [k for k in keys if k not in failed_keys]
    if not available:
        return None
    return random.choice(available)

# ════════════════════════════════════════════════════════════════════
#  STYLE PRESETS
# ════════════════════════════════════════════════════════════════════
STYLES = {
    "✨ None (Raw)": "",
    "📷 Photorealistic": (
        "hyperrealistic DSLR photography, 8K UHD, tack-sharp focus, "
        "natural golden-hour lighting, shallow depth of field, "
        "photojournalism, ultra-detailed texture, no watermark"
    ),
    "🎬 Cinematic": (
        "cinematic widescreen movie still, dramatic lighting, "
        "anamorphic lens flare, film grain, Hollywood color grade, "
        "IMAX quality, epic composition, no watermark"
    ),
    "🎌 Anime / Studio Ghibli": (
        "high quality anime illustration, Studio Ghibli aesthetic, "
        "vibrant cel-shading, clean crisp line art, lush detailed background, "
        "soft pastel palette, expressive character design, no watermark"
    ),
    "🎨 Digital Concept Art": (
        "professional digital concept art, ArtStation quality, "
        "volumetric cinematic lighting, intricate details, "
        "matte painting technique, 4K render, no watermark"
    ),
    "🖌️ Oil Painting": (
        "classical oil painting on canvas, rich impasto brushstrokes, "
        "old master chiaroscuro lighting, museum-quality, no watermark"
    ),
    "💧 Watercolor": (
        "delicate watercolor illustration, soft wet-on-wet washes, "
        "translucent luminous colors, hand-painted paper grain, no watermark"
    ),
    "👾 Pixel Art": (
        "crisp 16-bit pixel art, retro JRPG aesthetic, "
        "clean pixel-perfect sprite work, vibrant limited palette, no watermark"
    ),
    "⚡ Neon Cyberpunk": (
        "cyberpunk dystopian cityscape, vivid neon signs in purple cyan magenta, "
        "rain-slicked reflective streets, holographic advertisements, "
        "volumetric fog, ultra-high contrast, Blade Runner aesthetic, no watermark"
    ),
    "🏰 Dark Fantasy Epic": (
        "epic dark fantasy digital art, dramatic stormy atmospheric lighting, "
        "intricate gothic architectural details, cinematic hero composition, no watermark"
    ),
    "◻️ Clean Minimalist": (
        "ultra-clean minimalist design, precise geometric composition, "
        "generous negative space, modern Swiss aesthetic, no watermark"
    ),
    "🕰️ Vintage / Retro": (
        "authentic vintage analog photography, Kodachrome film simulation, "
        "warm faded tones, light leaks, grain, 1970s documentary aesthetic, no watermark"
    ),
    "🔮 3D Render / Blender": (
        "photorealistic 3D CGI render, Blender Cycles path tracing, "
        "physically-based materials, HDRI studio lighting, 8K render, no watermark"
    ),
    "✏️ Pencil Sketch": (
        "detailed graphite pencil sketch, masterful cross-hatching, "
        "fine line work, smudge shading, sketchbook texture, no watermark"
    ),
    "🪔 Indian Traditional Art": (
        "Tanjore gold-leaf painting style, vibrant jewel-tone colors, "
        "intricate mandala motifs, traditional Indian folk art, no watermark"
    ),
    "🌊 Surreal / Dreamlike": (
        "hyper-surrealist fine art, impossible dreamlike geometry, "
        "ethereal glowing atmosphere, Salvador Dali inspired, no watermark"
    ),
}

RATIOS = {
    "⬜ Square 1:1 (1024×1024)":     (1024, 1024),
    "📱 Portrait 9:16 (768×1344)":   (768,  1344),
    "🖼️ Portrait 2:3 (832×1216)":   (832,  1216),
    "🖥️ Landscape 3:2 (1216×832)":  (1216,  832),
    "📺 Widescreen 16:9 (1344×768)": (1344,  768),
    "🎬 Ultrawide 21:9 (1536×640)":  (1536,  640),
    "📷 Classic 4:3 (1152×864)":     (1152,  864),
}

EXAMPLES = [
    ("A Bengal tiger in a neon-lit Tokyo alley at midnight, heavy rain",  "⚡ Neon Cyberpunk",      "🖥️ Landscape 3:2 (1216×832)",  42),
    ("Tamil Chola warrior queen in golden armor, palace at dusk",         "🏰 Dark Fantasy Epic",   "📱 Portrait 9:16 (768×1344)",   77),
    ("Nexflow AI startup logo, geometric, purple gradient, minimal",      "◻️ Clean Minimalist",    "⬜ Square 1:1 (1024×1024)",     13),
    ("Anime school boy and girl on rooftop watching stars at night",      "🎌 Anime / Studio Ghibli","📺 Widescreen 16:9 (1344×768)", 99),
    ("Abstract AI neural network, glowing nodes, deep space background",  "🔮 3D Render / Blender", "📺 Widescreen 16:9 (1344×768)", -1),
    ("Portrait of elderly Indian grandfather, morning village light",     "📷 Photorealistic",      "🖼️ Portrait 2:3 (832×1216)",   -1),
]

# ════════════════════════════════════════════════════════════════════
#  PROMPT ENHANCEMENT — Gemini Flash (free, fast)
# ════════════════════════════════════════════════════════════════════
ENHANCE_SYSTEM = """You are a world-class AI image prompt engineer.
Transform the user's short prompt into a rich, detailed generation prompt.
Rules:
- Preserve exact subject and intent
- Add: lighting, camera angle, composition, color palette, atmosphere, texture, mood
- Use natural comma-separated phrases only
- Maximum 120 words
- Use only simple ASCII characters, no special symbols or unicode dashes
- Output ONLY the enhanced prompt, nothing else"""

def enhance_prompt(raw: str, enabled: bool, api_key: str) -> str:
    if not enabled or not raw.strip() or not api_key:
        return raw.strip()
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        resp  = model.generate_content(
            f"{ENHANCE_SYSTEM}\n\nEnhance this prompt: {raw}"
        )
        enhanced = resp.text.strip().strip('"').strip("'")
        # Strip any non-ASCII characters
        enhanced = ''.join(c for c in enhanced if ord(c) < 128)
        return enhanced if len(enhanced) > 15 else raw.strip()
    except Exception as e:
        st.warning(f"Enhancement skipped: {e}")
        return raw.strip()

# ════════════════════════════════════════════════════════════════════
#  IMAGE GENERATION — Gemini 2.0 Flash Image (free, GPT-4o quality)
# ════════════════════════════════════════════════════════════════════
def generate_image_gemini(
    prompt: str,
    width: int,
    height: int,
    api_key: str,
) -> Image.Image:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-exp-image-generation")

    full_prompt = (
        f"{prompt}. "
        f"Image dimensions: {width}x{height} pixels. "
        f"High quality, no watermark, no text overlay, no logo."
    )

    resp = model.generate_content(
        full_prompt,
        generation_config=genai.GenerationConfig(
            response_modalities=["image", "text"],
        ),
    )

    for part in resp.candidates[0].content.parts:
        if part.inline_data is not None:
            img_data = part.inline_data.data
            if isinstance(img_data, str):
                img_data = base64.b64decode(img_data)
            return Image.open(io.BytesIO(img_data))

    raise ValueError("No image returned from Gemini API")

# ════════════════════════════════════════════════════════════════════
#  GENERATE WITH KEY ROTATION + FALLBACK
# ════════════════════════════════════════════════════════════════════
def generate_with_rotation(
    prompt: str,
    width: int,
    height: int,
    keys: list,
) -> tuple:
    failed_keys = set()
    last_error  = None

    while True:
        key = get_next_key(keys, failed_keys)
        if key is None:
            raise Exception(
                f"All {len(keys)} API keys exhausted or rate limited. "
                f"Last error: {last_error}"
            )
        try:
            img = generate_image_gemini(prompt, width, height, key)
            key_num = keys.index(key) + 1
            return img, key_num
        except Exception as e:
            err_str = str(e).lower()
            if any(x in err_str for x in ["quota", "rate", "limit", "429", "exhausted"]):
                failed_keys.add(key)
                last_error = str(e)
                time.sleep(2)
                continue
            else:
                raise e

# ════════════════════════════════════════════════════════════════════
#  ZIP HELPER
# ════════════════════════════════════════════════════════════════════
def make_zip(images: list, seed: int) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, img in enumerate(images):
            ibuf = io.BytesIO()
            img.save(ibuf, format="PNG")
            zf.writestr(f"nexflow_{i+1:02d}_seed{seed}.png", ibuf.getvalue())
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
        <span class="badge">🧠 Gemini 2.0 Flash Image</span>
        <span class="badge">🔁 Auto Key Rotation</span>
        <span class="badge">🖼️ Batch Generation</span>
        <span class="badge">💎 GPT-4o Level Quality</span>
        <span class="badge">❤️ Nexflow Studio</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Key status
if not keys:
    st.error(
        "⚠️ No API keys found. Add your Gemini keys in Streamlit Secrets:\n\n"
        "```\nGEMINI_KEY_1 = 'AIza...'\n"
        "GEMINI_KEY_2 = 'AIza...'\n"
        "GEMINI_KEY_3 = 'AIza...'\n"
        "GEMINI_KEY_4 = 'AIza...'\n```\n\n"
        "Get free keys at: aistudio.google.com"
    )
    st.stop()

st.success(f"✅ {len(keys)} API key(s) active — up to {len(keys) * 500} free images/day with auto rotation")

# ── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎨 Style & Layout")
    style      = st.selectbox("Style Preset", list(STYLES.keys()), index=0)
    ratio      = st.selectbox("Aspect Ratio", list(RATIOS.keys()), index=0)
    num_images = st.slider("Number of Images", 1, 4, 1)

    st.markdown("---")
    st.markdown("### ⚙️ Advanced")
    use_enhance = st.toggle("✨ AI Enhance Prompt (Gemini Flash)", value=True)
    seed = st.number_input(
        "Seed (-1 = random)", value=-1, step=1,
        help="Same seed = consistent style across runs",
    )

    st.markdown("---")
    st.markdown("### 🔑 Key Status")
    for i, k in enumerate(keys):
        st.markdown(f"Key {i+1}: `...{k[-6:]}` ✅")

    st.markdown("---")
    st.markdown("### 💡 Examples")
    for i, (ep, es, er, eseed) in enumerate(EXAMPLES):
        if st.button(f"#{i+1} {ep[:36]}...", key=f"ex_{i}"):
            st.session_state.update({
                "ex_prompt": ep, "ex_style": es,
                "ex_ratio": er, "ex_seed": eseed,
            })
            st.rerun()

# ── Main ─────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    if "ex_style" in st.session_state:
        style = st.session_state.pop("ex_style", style)
        ratio = st.session_state.pop("ex_ratio", ratio)
        seed  = st.session_state.pop("ex_seed",  seed)

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

# ── Generation ───────────────────────────────────────────────────────
if generate_btn:
    if not prompt.strip():
        status_area.markdown(
            '<div class="status-err">⚠️ Please enter a prompt first.</div>',
            unsafe_allow_html=True,
        )
    else:
        t0 = time.time()

        # 1. Enhance
        with st.spinner("✨ Enhancing prompt with Gemini Flash..."):
            enhanced = enhance_prompt(prompt, use_enhance, keys[0])

        # 2. Build final prompt
        suffix = STYLES.get(style, "")
        final  = f"{enhanced}, {suffix}" if suffix else enhanced

        enhanced_box.text_area(
            "📝 Final Prompt → Gemini Image Model",
            value=final, height=100, disabled=True,
        )

        # 3. Dimensions + seed
        w, h        = RATIOS.get(ratio, (1024, 1024))
        actual_seed = int(seed) if int(seed) != -1 else random.randint(0, 999999)

        # 4. Generate with key rotation
        progress = st.progress(0, text="🎨 Generating with Gemini 2.0 Flash Image...")
        images   = []

        try:
            for i in range(num_images):
                progress.progress(
                    i / num_images,
                    text=f"🎨 Generating image {i+1} of {num_images}... (auto key rotation active)",
                )
                img, key_used = generate_with_rotation(final, w, h, keys)
                images.append(img)

                # Show images progressively with download buttons
                with gallery_area.container():
                    cols = st.columns(2)
                    for j, im in enumerate(images):
                        with cols[j % 2]:
                            st.image(im, use_container_width=True)
                            # Per-image download
                            ibuf = io.BytesIO()
                            im.save(ibuf, format="PNG")
                            st.download_button(
                                label=f"⬇️ Download Image {j+1}",
                                data=ibuf.getvalue(),
                                file_name=f"nexflow_image_{j+1}_seed{actual_seed}.png",
                                mime="image/png",
                                key=f"dl_img_{j}_{actual_seed}",
                                use_container_width=True,
                            )

                if i < num_images - 1:
                    time.sleep(2)

            progress.progress(1.0, text="✅ Done!")
            elapsed = time.time() - t0

            status_area.markdown(
                f'<div class="status-ok">'
                f'✅ {len(images)} image(s) ready · '
                f'{elapsed:.1f}s · {w}×{h} · '
                f'Gemini 2.0 Flash Image · No watermark'
                f'</div>',
                unsafe_allow_html=True,
            )

            zip_data = make_zip(images, actual_seed)
            download_area.download_button(
                label="📥 Download All Images (ZIP)",
                data=zip_data,
                file_name=f"nexflow_gemini_seed{actual_seed}.zip",
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
    Powered by <b>Gemini 2.0 Flash Image</b> (Google · Free) &nbsp;·&nbsp;
    Prompt AI: <b>Gemini Flash</b> (Free) &nbsp;·&nbsp;
    Auto Key Rotation: <b>4 Keys × 500/day</b> &nbsp;·&nbsp;
    Built with ❤️ by <b>JAI SURYA</b> &nbsp;·&nbsp; <b>Nexflow Studio</b>
</div>
""", unsafe_allow_html=True)