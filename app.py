# ══════════════════════════════════════════════════════════════════════
#  FLUX Image Studio — Nexflow Studio
#  Platform : Streamlit Community Cloud (free)
#  Images   : FLUX.1-schnell via HF Inference API (real, free)
#  Prompt AI: Qwen2.5-7B-Instruct via HF Inference API (free)
#  Deploy   : streamlit.io → connect GitHub → done
# ══════════════════════════════════════════════════════════════════════

import streamlit as st
import random
import io
import os
import zipfile
import time
from huggingface_hub import InferenceClient
from PIL import Image

# ─── Page config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="FLUX Image Studio — Nexflow",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Hero */
.hero {
    text-align: center;
    padding: 2rem 0 1.5rem;
    background: linear-gradient(135deg, #0f0a1e 0%, #1a1035 100%);
    border-radius: 20px;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(168,85,247,0.2);
}
.hero h1 {
    font-size: 2.8rem;
    font-weight: 900;
    background: linear-gradient(90deg, #7c3aed, #a855f7, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.5rem 0;
}
.hero p { color: #9ca3af; font-size: 1rem; margin: 0 0 1rem 0; }

/* Badges */
.badges { display: flex; flex-wrap: wrap; justify-content: center; gap: 6px; }
.badge {
    background: rgba(30,27,75,0.9);
    color: #c4b5fd;
    padding: 4px 14px;
    border-radius: 99px;
    font-size: 0.72rem;
    font-weight: 600;
    border: 1px solid rgba(139,92,246,0.3);
}

/* Generate button */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #5b21b6, #7c3aed, #a855f7, #ec4899) !important;
    color: white !important;
    font-size: 1.1rem !important;
    font-weight: 800 !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.75rem 1.5rem !important;
    box-shadow: 0 4px 24px rgba(139,92,246,0.4) !important;
    transition: all 0.2s !important;
    letter-spacing: 0.02em !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(139,92,246,0.6) !important;
}

/* Image cards */
.img-card {
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid rgba(168,85,247,0.25);
    background: #1a1035;
    margin-bottom: 12px;
}

/* Status */
.status-ok {
    background: rgba(16,185,129,0.1);
    border: 1px solid rgba(16,185,129,0.3);
    border-radius: 10px;
    padding: 10px 16px;
    color: #6ee7b7;
    font-size: 0.85rem;
    font-family: monospace;
}
.status-err {
    background: rgba(239,68,68,0.1);
    border: 1px solid rgba(239,68,68,0.3);
    border-radius: 10px;
    padding: 10px 16px;
    color: #fca5a5;
    font-size: 0.85rem;
}
.status-warn {
    background: rgba(245,158,11,0.1);
    border: 1px solid rgba(245,158,11,0.3);
    border-radius: 10px;
    padding: 10px 16px;
    color: #fcd34d;
    font-size: 0.85rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #130d28 !important;
    border-right: 1px solid rgba(168,85,247,0.15);
}

/* Footer */
.footer {
    text-align: center;
    color: #4b5563;
    font-size: 0.78rem;
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(168,85,247,0.1);
}
.footer b { color: #7c3aed; }

/* Hide Streamlit branding */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── Constants ──────────────────────────────────────────────────────
IMG_MODEL = "black-forest-labs/FLUX.1-schnell"
LLM_MODEL = "Qwen/Qwen2.5-7B-Instruct"

STYLES = {
    "✨ None (Raw)": "",
    "📷 Photorealistic": (
        "hyperrealistic DSLR photography, 8K UHD, tack-sharp focus, "
        "natural golden-hour lighting, shallow depth of field, Nikon Z9 quality, "
        "photojournalism, ultra-detailed texture"
    ),
    "🎬 Cinematic": (
        "cinematic widescreen movie still, dramatic three-point lighting, "
        "anamorphic lens flare, shallow depth of field, film grain, "
        "Hollywood blockbuster color grade, IMAX quality"
    ),
    "🎌 Anime / Studio Ghibli": (
        "anime illustration, Studio Ghibli aesthetic, vibrant cel-shading, "
        "clean crisp line art, lush detailed background, soft pastel palette, "
        "expressive character design, hand-drawn feel"
    ),
    "🎨 Digital Concept Art": (
        "professional digital concept art, ArtStation top-100 quality, "
        "volumetric cinematic lighting, intricate environmental details, "
        "matte painting technique, 4K render, heroic composition"
    ),
    "🖌️ Oil Painting": (
        "classical oil painting on canvas, rich impasto brushstrokes, "
        "old master chiaroscuro lighting, museum-quality pigments, "
        "Rembrandt-inspired depth, gallery-worthy"
    ),
    "💧 Watercolor": (
        "delicate watercolor illustration, soft wet-on-wet washes, "
        "granulation texture, translucent luminous colors, "
        "hand-painted paper grain, editorial illustration quality"
    ),
    "👾 Pixel Art": (
        "crisp 16-bit pixel art, retro JRPG aesthetic, clean pixel-perfect "
        "sprite work, vibrant limited palette, nostalgic game art style"
    ),
    "⚡ Neon Cyberpunk": (
        "cyberpunk dystopian cityscape, vivid neon signs in purple cyan magenta, "
        "rain-slicked reflective streets, holographic advertisements, "
        "volumetric fog, ultra-high contrast, Blade Runner aesthetic"
    ),
    "🏰 Dark Fantasy Epic": (
        "epic dark fantasy digital art, dramatic stormy atmospheric lighting, "
        "intricate gothic architectural details, mysterious ancient magic, "
        "hyper-detailed creature design, cinematic hero composition"
    ),
    "◻️ Clean Minimalist": (
        "ultra-clean minimalist design, precise geometric composition, "
        "generous negative space, modern Swiss typography influence, "
        "soft directional shadows, premium brand aesthetic"
    ),
    "🕰️ Vintage / Retro": (
        "authentic vintage analog photography, Kodachrome film simulation, "
        "warm faded tones, light leaks, grain and halation, "
        "1970s documentary aesthetic, nostalgic quality"
    ),
    "🔮 3D Render / Blender": (
        "photorealistic 3D CGI render, Blender Cycles path tracing, "
        "physically-based materials, HDRI studio lighting, "
        "subsurface scattering, 8K render, award-winning 3D art"
    ),
    "✏️ Pencil Sketch": (
        "detailed graphite pencil sketch, masterful cross-hatching, "
        "fine line work with gestural strokes, smudge shading, "
        "sketchbook texture, classical academic drawing style"
    ),
    "🪔 Indian Traditional Art": (
        "Tanjore gold-leaf painting style, vibrant jewel-tone colors, "
        "intricate mandala and floral motifs, divine iconography, "
        "traditional Indian folk art, rich decorative borders"
    ),
    "🌊 Surreal / Dreamlike": (
        "hyper-surrealist fine art, impossible dreamlike geometry, "
        "ethereal glowing atmosphere, Salvador Dali and Magritte influence, "
        "photorealistic impossible scenes, otherworldly beauty"
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

NEG_DEFAULT = (
    "blurry, low quality, distorted, deformed, ugly, bad anatomy, "
    "watermark, text overlay, signature, extra limbs, out of frame, "
    "cropped, grainy, noisy, oversaturated, washed out"
)

ENHANCE_SYSTEM = """You are a world-class AI image prompt engineer for FLUX.1 diffusion models.

Transform any short user prompt into a rich, detailed generation prompt.

RULES:
1. Preserve the EXACT subject, setting, and intent
2. Add: lighting quality, camera lens, composition, color palette, atmosphere, texture, mood
3. Use natural comma-separated phrases — no bullet points
4. Maximum 130 words
5. Output ONLY the enhanced prompt — no quotes, no explanation, nothing else
"""

EXAMPLES = [
    ("A Bengal tiger in a neon-lit Tokyo alley, midnight rain",          "⚡ Neon Cyberpunk",     "🖥️ Landscape 3:2 (1216×832)",  42),
    ("Tamil Chola warrior queen, golden armor, palace at dusk",          "🏰 Dark Fantasy Epic",  "📱 Portrait 9:16 (768×1344)",   77),
    ("Nexflow AI startup logo, geometric, purple gradient, minimal",     "◻️ Clean Minimalist",   "⬜ Square 1:1 (1024×1024)",     13),
    ("Cozy mountain coffee shop, misty morning, warm lights inside",     "📷 Photorealistic",     "🖥️ Landscape 3:2 (1216×832)",  -1),
    ("Abstract AI neural network, glowing nodes, deep space",           "🔮 3D Render / Blender","📺 Widescreen 16:9 (1344×768)", -1),
    ("Elderly Indian grandfather portrait, morning village light",       "📷 Photorealistic",     "🖼️ Portrait 2:3 (832×1216)",   -1),
]

# ─── HF Token ───────────────────────────────────────────────────────
HF_TOKEN = os.environ.get("HF_TOKEN") or st.secrets.get("HF_TOKEN", None)

# ─── Cached client ──────────────────────────────────────────────────
@st.cache_resource
def get_client():
    return InferenceClient(token=HF_TOKEN)

# ─── Prompt enhancement ─────────────────────────────────────────────
def enhance_prompt(raw: str, enabled: bool) -> str:
    if not enabled or not raw.strip() or not HF_TOKEN:
        return raw.strip()
    try:
        client = get_client()
        resp = client.chat_completion(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": ENHANCE_SYSTEM},
                {"role": "user",   "content": f"Enhance: {raw}"},
            ],
            max_tokens=200,
            temperature=0.65,
        )
        enhanced = resp.choices[0].message.content.strip().strip('"').strip("'")
        return enhanced if len(enhanced) > 15 else raw.strip()
    except Exception as e:
        st.warning(f"Prompt enhancement skipped: {e}")
        return raw.strip()

# ─── Image generation ───────────────────────────────────────────────
def generate_images(prompt, num_images, width, height, seed):
    client   = get_client()
    actual   = seed if seed != -1 else random.randint(0, 2**32 - 1)
    images   = []
    for i in range(num_images):
        img = client.text_to_image(
            prompt,
            model              = IMG_MODEL,
            width              = width,
            height             = height,
            num_inference_steps= 4,
            guidance_scale     = 0.0,
            seed               = actual + i,
        )
        if isinstance(img, Image.Image):
            images.append(img)
        else:
            images.append(Image.open(io.BytesIO(img)))
    return images, actual

# ─── ZIP helper ─────────────────────────────────────────────────────
def make_zip(images, seed):
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

# Hero
st.markdown("""
<div class="hero">
    <h1>⚡ FLUX Image Studio</h1>
    <p>High-quality AI image generation — free, open source, production-ready</p>
    <div class="badges">
        <span class="badge">🆓 100% Free</span>
        <span class="badge">🔓 Apache 2.0</span>
        <span class="badge">⚡ FLUX.1-schnell</span>
        <span class="badge">🧠 AI Prompt Engine</span>
        <span class="badge">🖼️ Batch Generation</span>
        <span class="badge">🔁 Seed Consistency</span>
        <span class="badge">❤️ Nexflow Studio</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Token check
if not HF_TOKEN:
    st.markdown("""
    <div class="status-warn">
    ⚠️ <b>HF_TOKEN not set.</b><br>
    Go to: Streamlit Cloud → App Settings → Secrets → add:<br>
    <code>HF_TOKEN = "hf_your_token_here"</code>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎨 Style & Layout")

    style = st.selectbox(
        "Style Preset",
        options=list(STYLES.keys()),
        index=0,
    )
    ratio = st.selectbox(
        "Aspect Ratio",
        options=list(RATIOS.keys()),
        index=0,
    )
    num_images = st.slider("Number of Images", 1, 4, 2)

    st.markdown("---")
    st.markdown("### ⚙️ Advanced")

    use_enhance = st.toggle("✨ AI Enhance Prompt", value=True)
    seed = st.number_input(
        "Seed (−1 = random)",
        value=-1, step=1,
        help="Same seed = same style every time. Great for consistency.",
    )

    st.markdown("---")
    st.markdown("### 🚫 Negative Prompt")
    neg_prompt = st.text_area(
        label="Negative Prompt",
        value=NEG_DEFAULT,
        height=100,
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("### 💡 Examples")
    for i, (ex_prompt, ex_style, ex_ratio, ex_seed) in enumerate(EXAMPLES):
        if st.button(f"#{i+1} {ex_prompt[:35]}...", key=f"ex_{i}"):
            st.session_state["ex_prompt"] = ex_prompt
            st.session_state["ex_style"]  = ex_style
            st.session_state["ex_ratio"]  = ex_ratio
            st.session_state["ex_seed"]   = ex_seed
            st.rerun()

# ── Main area ────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    # Load example if clicked
    default_prompt = st.session_state.get("ex_prompt", "")
    if st.session_state.get("ex_style"):
        style      = st.session_state.pop("ex_style", style)
        ratio      = st.session_state.pop("ex_ratio", ratio)
        seed       = st.session_state.pop("ex_seed",  seed)

    prompt = st.text_area(
        "✏️ Your Prompt",
        value=default_prompt,
        placeholder=(
            "Describe what you want to see...\n\n"
            "e.g. A lone samurai standing in a misty bamboo forest at dawn, "
            "cinematic lighting, fog drifting through the trees"
        ),
        height=160,
    )

    # Enhanced prompt preview
    enhanced_box = st.empty()

    generate = st.button("🚀  Generate Images", type="primary")

    # Status area
    status_area = st.empty()

    # Download area
    download_area = st.empty()

with col_right:
    gallery_area = st.empty()
    gallery_area.markdown(
        "<div style='text-align:center;color:#4b5563;padding:80px 0;'>"
        "🖼️ Generated images appear here</div>",
        unsafe_allow_html=True
    )

# ── Generation logic ────────────────────────────────────────────────
if generate:
    if not prompt.strip():
        status_area.markdown(
            '<div class="status-warn">⚠️ Please enter a prompt first.</div>',
            unsafe_allow_html=True
        )
    else:
        t0 = time.time()

        # 1. Enhance prompt
        with st.spinner("✨ Enhancing prompt with Qwen2.5-7B..."):
            enhanced = enhance_prompt(prompt, use_enhance)

        # Show enhanced prompt
        suffix = STYLES.get(style, "")
        final  = f"{enhanced}, {suffix}" if suffix else enhanced
        enhanced_box.text_area(
            "📝 Final Prompt → FLUX Model",
            value=final,
            height=100,
            disabled=True,
        )

        # 2. Get dimensions
        w, h = RATIOS.get(ratio, (1024, 1024))

        # 3. Generate
        progress = st.progress(0, text="🎨 Generating images via FLUX.1-schnell...")
        try:
            images = []
            actual_seed = int(seed) if int(seed) != -1 else random.randint(0, 2**32 - 1)
            client = get_client()

            for i in range(num_images):
                progress.progress(
                    (i) / num_images,
                    text=f"🎨 Generating image {i+1} of {num_images}..."
                )
                img = client.text_to_image(
                    final,
                    model               = IMG_MODEL,
                    width               = w,
                    height              = h,
                    num_inference_steps = 4,
                    guidance_scale      = 0.0,
                    seed                = actual_seed + i,
                )
                if isinstance(img, Image.Image):
                    images.append(img)
                else:
                    images.append(Image.open(io.BytesIO(img)))

                # Show images progressively as they generate
                with gallery_area.container():
                    cols = st.columns(2)
                    for j, im in enumerate(images):
                        with cols[j % 2]:
                            st.image(im, use_container_width=True)

            progress.progress(1.0, text="✅ Done!")
            elapsed = time.time() - t0

            # Status
            status_area.markdown(
                f'<div class="status-ok">'
                f'✅ {len(images)} image(s) ready · '
                f'{elapsed:.1f}s · '
                f'Seed {actual_seed} · '
                f'{w}×{h} · '
                f'FLUX.1-schnell'
                f'</div>',
                unsafe_allow_html=True
            )

            # ZIP download
            zip_data = make_zip(images, actual_seed)
            download_area.download_button(
                label="📥 Download All Images (ZIP)",
                data=zip_data,
                file_name=f"nexflow_images_seed{actual_seed}.zip",
                mime="application/zip",
                use_container_width=True,
            )

        except Exception as e:
            progress.empty()
            status_area.markdown(
                f'<div class="status-err">❌ Error: {str(e)}</div>',
                unsafe_allow_html=True
            )

# Footer
st.markdown("""
<div class="footer">
    Powered by <b>FLUX.1-schnell</b> (Black Forest Labs · Apache 2.0) &nbsp;·&nbsp;
    Prompt AI: <b>Qwen2.5-7B-Instruct</b> &nbsp;·&nbsp;
    Inference: <b>HuggingFace API</b> (Free) &nbsp;·&nbsp;
    Built with ❤️ by <b>Nexflow Studio</b>
</div>
""", unsafe_allow_html=True)
