# ══════════════════════════════════════════════════════════════════════
#  FLUX Image Studio — Nexflow Studio
#  Platform : Streamlit Community Cloud (free)
#  Images   : Pollinations.ai FLUX API (real, 100% free, no key needed)
#  Prompt AI: Pollinations.ai text API (free, no key needed)
#  Deploy   : streamlit.io → connect GitHub → done
# ══════════════════════════════════════════════════════════════════════

import streamlit as st
import random
import io
import os
import zipfile
import time
import requests
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
    color: white !important;
    font-size: 1.1rem !important;
    font-weight: 800 !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.75rem 1.5rem !important;
    box-shadow: 0 4px 24px rgba(139,92,246,0.4) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(139,92,246,0.6) !important;
}
.status-ok {
    background: rgba(16,185,129,0.1);
    border: 1px solid rgba(16,185,129,0.3);
    border-radius: 10px; padding: 10px 16px;
    color: #6ee7b7; font-size: 0.85rem; font-family: monospace;
}
.status-err {
    background: rgba(239,68,68,0.1);
    border: 1px solid rgba(239,68,68,0.3);
    border-radius: 10px; padding: 10px 16px;
    color: #fca5a5; font-size: 0.85rem;
}
section[data-testid="stSidebar"] {
    background: #130d28 !important;
    border-right: 1px solid rgba(168,85,247,0.15);
}
.footer {
    text-align: center; color: #4b5563;
    font-size: 0.78rem; margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(168,85,247,0.1);
}
.footer b { color: #7c3aed; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ════════════════════════════════════════════════════════════════════
STYLES = {
    "✨ None (Raw)": "",
    "📷 Photorealistic": (
        "hyperrealistic DSLR photography, 8K UHD, tack-sharp focus, "
        "natural golden-hour lighting, shallow depth of field, "
        "photojournalism, ultra-detailed texture"
    ),
    "🎬 Cinematic": (
        "cinematic widescreen movie still, dramatic three-point lighting, "
        "anamorphic lens flare, film grain, "
        "Hollywood blockbuster color grade, IMAX quality"
    ),
    "🎌 Anime / Studio Ghibli": (
        "anime illustration, Studio Ghibli aesthetic, vibrant cel-shading, "
        "clean crisp line art, lush detailed background, soft pastel palette"
    ),
    "🎨 Digital Concept Art": (
        "professional digital concept art, ArtStation top-100 quality, "
        "volumetric cinematic lighting, matte painting technique, 4K render"
    ),
    "🖌️ Oil Painting": (
        "classical oil painting on canvas, rich impasto brushstrokes, "
        "old master chiaroscuro lighting, museum-quality pigments"
    ),
    "💧 Watercolor": (
        "delicate watercolor illustration, soft wet-on-wet washes, "
        "translucent luminous colors, hand-painted paper grain"
    ),
    "👾 Pixel Art": (
        "crisp 16-bit pixel art, retro JRPG aesthetic, "
        "clean pixel-perfect sprite work, vibrant limited palette"
    ),
    "⚡ Neon Cyberpunk": (
        "cyberpunk dystopian cityscape, vivid neon signs in purple cyan magenta, "
        "rain-slicked reflective streets, holographic advertisements, "
        "volumetric fog, ultra-high contrast, Blade Runner aesthetic"
    ),
    "🏰 Dark Fantasy Epic": (
        "epic dark fantasy digital art, dramatic stormy atmospheric lighting, "
        "intricate gothic architectural details, cinematic hero composition"
    ),
    "◻️ Clean Minimalist": (
        "ultra-clean minimalist design, precise geometric composition, "
        "generous negative space, modern Swiss typography influence"
    ),
    "🕰️ Vintage / Retro": (
        "authentic vintage analog photography, Kodachrome film simulation, "
        "warm faded tones, light leaks, grain, 1970s documentary aesthetic"
    ),
    "🔮 3D Render / Blender": (
        "photorealistic 3D CGI render, Blender Cycles path tracing, "
        "physically-based materials, HDRI studio lighting, 8K render"
    ),
    "✏️ Pencil Sketch": (
        "detailed graphite pencil sketch, masterful cross-hatching, "
        "fine line work, smudge shading, sketchbook texture"
    ),
    "🪔 Indian Traditional Art": (
        "Tanjore gold-leaf painting style, vibrant jewel-tone colors, "
        "intricate mandala motifs, traditional Indian folk art"
    ),
    "🌊 Surreal / Dreamlike": (
        "hyper-surrealist fine art, impossible dreamlike geometry, "
        "ethereal glowing atmosphere, Salvador Dali inspired"
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

EXAMPLES = [
    ("A Bengal tiger in a neon-lit Tokyo alley at midnight, heavy rain",  "⚡ Neon Cyberpunk",      "🖥️ Landscape 3:2 (1216×832)",  42),
    ("Tamil Chola warrior queen in golden armor, palace at dusk",         "🏰 Dark Fantasy Epic",   "📱 Portrait 9:16 (768×1344)",   77),
    ("Nexflow AI startup logo, geometric, purple gradient, minimal",      "◻️ Clean Minimalist",    "⬜ Square 1:1 (1024×1024)",     13),
    ("Cozy mountain coffee shop interior, misty morning, warm lights",    "📷 Photorealistic",      "🖥️ Landscape 3:2 (1216×832)",  -1),
    ("Abstract AI neural network, glowing nodes, deep space background",  "🔮 3D Render / Blender", "📺 Widescreen 16:9 (1344×768)", -1),
    ("Portrait of elderly Indian grandfather, morning village light",     "📷 Photorealistic",      "🖼️ Portrait 2:3 (832×1216)",   -1),
]

# ════════════════════════════════════════════════════════════════════
#  PROMPT ENHANCEMENT — Pollinations text API (free, no key)
# ════════════════════════════════════════════════════════════════════
ENHANCE_SYSTEM = (
    "You are a world-class AI image prompt engineer for FLUX.1 diffusion models. "
    "Transform the user's short prompt into a rich, detailed generation prompt. "
    "Rules: preserve exact subject and intent, add lighting, camera angle, "
    "composition, color palette, atmosphere, texture, mood. "
    "Use natural comma-separated phrases. Max 130 words. "
    "Output ONLY the enhanced prompt — no quotes, no explanation."
)

def clean_ascii(text: str) -> str:
    """Remove special unicode chars that break URLs"""
    replacements = {
        '\u2011': '-', '\u2012': '-', '\u2013': '-', '\u2014': '-',
        '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"',
        '\u2026': '...', '\u00e2': '', '\u0080': '', '\u0091': "'",
        '\u0092': "'", '\u0093': '"', '\u0094': '"',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    # Keep only ASCII printable chars
    return ''.join(c for c in text if ord(c) < 128)

def enhance_prompt(raw: str, enabled: bool) -> str:
    if not enabled or not raw.strip():
        return raw.strip()
    try:
        payload = {
            "model": "openai",
            "messages": [
                {"role": "system", "content": ENHANCE_SYSTEM},
                {"role": "user",   "content": f"Enhance this prompt: {raw}"},
            ],
            "seed": 42,
            "private": True,
        }
        resp = requests.post(
            "https://text.pollinations.ai/openai",
            json=payload,
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        enhanced = data["choices"][0]["message"]["content"].strip().strip('"').strip("'")
        enhanced = clean_ascii(enhanced)
        return enhanced if len(enhanced) > 15 else raw.strip()
    except Exception as e:
        st.warning(f"Prompt enhancement skipped: {e}")
        return raw.strip()

# ════════════════════════════════════════════════════════════════════
#  IMAGE GENERATION — Pollinations FLUX API (free, no key)
# ════════════════════════════════════════════════════════════════════
def generate_image(prompt: str, neg: str, width: int, height: int, seed: int) -> Image.Image:
    import urllib.parse
    # Clean prompt — remove special unicode chars that break URLs
    clean = clean_ascii(prompt)
    encoded = urllib.parse.quote(clean)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?model=flux"
        f"&width={width}"
        f"&height={height}"
        f"&seed={seed}"
        f"&nologo=true"
        f"&nofeed=true"
        f"&enhance=false"
        f"&private=true"
    )
    for attempt in range(4):
        try:
            time.sleep(attempt * 4)  # Back off: 0s, 4s, 8s, 12s
            resp = requests.get(url, timeout=120)
            resp.raise_for_status()
            img = Image.open(io.BytesIO(resp.content))
            return img
        except Exception as e:
            if attempt < 3:
                continue
            raise e

# ════════════════════════════════════════════════════════════════════
#  ZIP helper
# ════════════════════════════════════════════════════════════════════
def make_zip(images: list, seed: int) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, img in enumerate(images):
            ibuf = io.BytesIO()
            img.save(ibuf, format="PNG")
            zf.writestr(f"nexflow_{i+1:02d}_seed{seed+i}.png", ibuf.getvalue())
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
        <span class="badge">⚡ FLUX Model</span>
        <span class="badge">🧠 AI Prompt Engine</span>
        <span class="badge">🖼️ Batch Generation</span>
        <span class="badge">🔁 Seed Consistency</span>
        <span class="badge">❤️ Nexflow Studio</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎨 Style & Layout")
    style = st.selectbox("Style Preset", list(STYLES.keys()), index=0)
    ratio = st.selectbox("Aspect Ratio", list(RATIOS.keys()), index=0)
    num_images = st.slider("Number of Images", 1, 4, 2)

    st.markdown("---")
    st.markdown("### ⚙️ Advanced")
    use_enhance = st.toggle("✨ AI Enhance Prompt", value=True)
    seed = st.number_input(
        "Seed (−1 = random)", value=-1, step=1,
        help="Same seed = same style every time.",
    )

    st.markdown("---")
    st.markdown("### 🚫 Negative Prompt")
    neg_prompt = st.text_area(
        "Negative Prompt", value=NEG_DEFAULT, height=100,
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("### 💡 Examples")
    for i, (ep, es, er, eseed) in enumerate(EXAMPLES):
        if st.button(f"#{i+1} {ep[:38]}...", key=f"ex_{i}"):
            st.session_state.update({
                "ex_prompt": ep, "ex_style": es,
                "ex_ratio": er, "ex_seed": eseed,
            })
            st.rerun()

# ── Main ─────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    # Load example values if set
    if "ex_style" in st.session_state:
        style = st.session_state.pop("ex_style", style)
        ratio = st.session_state.pop("ex_ratio", ratio)
        seed  = st.session_state.pop("ex_seed",  seed)

    prompt = st.text_area(
        "✏️ Your Prompt",
        value=st.session_state.pop("ex_prompt", ""),
        placeholder=(
            "Describe what you want to see...\n\n"
            "e.g. A lone samurai standing in a misty bamboo forest at dawn, "
            "cinematic lighting, fog drifting through the trees"
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
            '<div class="status-warn">⚠️ Please enter a prompt first.</div>',
            unsafe_allow_html=True,
        )
    else:
        t0 = time.time()

        # 1. Enhance
        with st.spinner("✨ Enhancing prompt..."):
            enhanced = enhance_prompt(prompt, use_enhance)

        # 2. Build final prompt
        suffix = STYLES.get(style, "")
        final  = f"{enhanced}, {suffix}" if suffix else enhanced

        enhanced_box.text_area(
            "📝 Final Prompt → FLUX Model",
            value=final, height=100, disabled=True,
        )

        # 3. Dimensions + seed
        w, h        = RATIOS.get(ratio, (1024, 1024))
        actual_seed = int(seed) if int(seed) != -1 else random.randint(0, 999999)

        # 4. Generate images one by one (show progressively)
        progress = st.progress(0, text="🎨 Connecting to FLUX...")
        images   = []

        try:
            for i in range(num_images):
                progress.progress(
                    i / num_images,
                    text=f"🎨 Generating image {i+1} of {num_images}... (may take 15–30s each)",
                )
                img = generate_image(final, neg_prompt, w, h, actual_seed + i)
                images.append(img)
                if i < num_images - 1:
                    time.sleep(8)  # Prevent rate limiting between images

                # Show images as they arrive
                with gallery_area.container():
                    cols = st.columns(2)
                    for j, im in enumerate(images):
                        with cols[j % 2]:
                            st.image(im, use_container_width=True)

            progress.progress(1.0, text="✅ Done!")
            elapsed = time.time() - t0

            status_area.markdown(
                f'<div class="status-ok">'
                f'✅ {len(images)} image(s) ready · '
                f'{elapsed:.1f}s · Seed {actual_seed} · {w}×{h} · FLUX'
                f'</div>',
                unsafe_allow_html=True,
            )

            zip_data = make_zip(images, actual_seed)
            download_area.download_button(
                label="📥 Download All Images (ZIP)",
                data=zip_data,
                file_name=f"nexflow_seed{actual_seed}.zip",
                mime="application/zip",
                use_container_width=True,
            )

        except Exception as e:
            progress.empty()
            status_area.markdown(
                f'<div class="status-err">❌ Error: {str(e)}</div>',
                unsafe_allow_html=True,
            )

# Footer
st.markdown("""
<div class="footer">
    Powered by <b>FLUX</b> (Pollinations.ai · Free) &nbsp;·&nbsp;
    Prompt AI: <b>GPT-4o mini</b> (Pollinations.ai · Free) &nbsp;·&nbsp;
    Built with ❤️ by <b>Nexflow Studio</b>
</div>
""", unsafe_allow_html=True)