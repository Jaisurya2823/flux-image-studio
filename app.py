# ══════════════════════════════════════════════════════════════════════
#  FLUX Image Studio — Nexflow Studio
#  Production build — GitHub + HuggingFace Spaces (CPU Basic, free)
#
#  Image Model : FLUX.1-schnell via HF Inference API (real images, free)
#  Prompt AI   : Qwen2.5-7B-Instruct via HF Inference API (free)
#  Hardware    : CPU Basic (free) — no GPU, no card needed
#  Speed       : ~15-30s per image via HF API
# ══════════════════════════════════════════════════════════════════════

import gradio as gr
import random
import io
import os
import zipfile
import time
import base64
from huggingface_hub import InferenceClient
from PIL import Image

# ─── Config ─────────────────────────────────────────────────────────
HF_TOKEN  = os.environ.get("HF_TOKEN", None)
IMG_MODEL = "black-forest-labs/FLUX.1-schnell"
LLM_MODEL = "Qwen/Qwen2.5-7B-Instruct"
MAX_IMGS  = 4

# ─── HF Inference Client ────────────────────────────────────────────
client = InferenceClient(token=HF_TOKEN)

# ════════════════════════════════════════════════════════════════════
#  STYLE PRESETS
# ════════════════════════════════════════════════════════════════════
STYLES = {
    "✨ None (Raw)": "",
    "📷 Photorealistic": (
        "hyperrealistic DSLR photography, 8K UHD resolution, tack-sharp focus, "
        "natural golden-hour lighting, shallow depth of field, Nikon Z9 quality, "
        "photojournalism, ultra-detailed skin and texture"
    ),
    "🎬 Cinematic": (
        "cinematic widescreen movie still, dramatic three-point lighting, "
        "anamorphic lens flare, shallow depth of field, film grain, "
        "Hollywood blockbuster color grade, IMAX quality, epic composition"
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
        "classical oil painting on linen canvas, rich impasto brushstrokes, "
        "old master chiaroscuro lighting, museum-quality pigments, "
        "Rembrandt-inspired depth, gallery-worthy composition"
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
        "1970s documentary aesthetic, nostalgic emotional quality"
    ),
    "🔮 3D Render / Blender": (
        "photorealistic 3D CGI render, Blender Cycles path tracing, "
        "physically-based materials, HDRI studio lighting, "
        "subsurface scattering, 8K render, award-winning 3D art"
    ),
    "✏️ Pencil Sketch": (
        "detailed graphite pencil sketch, masterful cross-hatching technique, "
        "fine line work with gestural strokes, smudge shading, "
        "sketchbook texture, classical academic drawing style"
    ),
    "🪔 Indian Traditional Art": (
        "Tanjore gold-leaf painting style, vibrant jewel-tone colors, "
        "intricate mandala and floral motifs, divine iconography, "
        "traditional Indian folk art aesthetic, rich decorative borders"
    ),
    "🌊 Surreal / Dreamlike": (
        "hyper-surrealist fine art, impossible dreamlike geometry, "
        "ethereal glowing atmosphere, Salvador Dali and Magritte influence, "
        "photorealistic impossible scenes, otherworldly beauty"
    ),
}

# ════════════════════════════════════════════════════════════════════
#  ASPECT RATIOS
# ════════════════════════════════════════════════════════════════════
RATIOS = {
    "⬜ Square 1:1 (1024×1024)":     (1024, 1024),
    "📱 Portrait 9:16 (768×1344)":   (768,  1344),
    "🖼️ Portrait 2:3 (832×1216)":   (832,  1216),
    "🖥️ Landscape 3:2 (1216×832)":  (1216, 832),
    "📺 Widescreen 16:9 (1344×768)": (1344, 768),
    "🎬 Ultrawide 21:9 (1536×640)":  (1536, 640),
    "📷 Classic 4:3 (1152×864)":     (1152, 864),
}

NEG_DEFAULT = (
    "blurry, low quality, distorted, deformed, ugly, bad anatomy, "
    "watermark, text overlay, signature, extra limbs, missing limbs, "
    "out of frame, cropped, grainy, noisy, oversaturated, washed out"
)

# ════════════════════════════════════════════════════════════════════
#  PROMPT ENHANCEMENT
# ════════════════════════════════════════════════════════════════════
ENHANCE_SYSTEM = """You are a world-class AI image prompt engineer specializing in FLUX.1 diffusion models.

Transform any short user prompt into a rich, detailed, photographic generation prompt.

RULES:
1. Preserve the EXACT subject, setting, and intent of the original
2. Add specific details: lighting quality, camera lens, composition, color palette, atmosphere, texture, mood
3. Use natural comma-separated phrases — never bullet points or numbered lists
4. Maximum 130 words
5. Output ONLY the enhanced prompt — zero preamble, zero explanation, no quotes
"""

def enhance_prompt(raw: str, enabled: bool) -> str:
    if not enabled or not raw.strip():
        return raw.strip()
    if not HF_TOKEN:
        return raw.strip()
    try:
        resp = client.chat_completion(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": ENHANCE_SYSTEM},
                {"role": "user",   "content": f"Enhance this prompt: {raw}"},
            ],
            max_tokens=200,
            temperature=0.65,
        )
        enhanced = resp.choices[0].message.content.strip().strip('"').strip("'")
        return enhanced if len(enhanced) > 15 else raw.strip()
    except Exception as e:
        print(f"⚠️ Enhancement failed: {e}")
        return raw.strip()

# ════════════════════════════════════════════════════════════════════
#  IMAGE GENERATION via HF Inference API
# ════════════════════════════════════════════════════════════════════
def generate_images(
    prompt: str,
    num_images: int,
    width: int,
    height: int,
    seed: int,
) -> tuple:
    if not HF_TOKEN:
        raise ValueError(
            "HF_TOKEN not set. Add it in Space Settings → Variables and Secrets."
        )

    actual_seed = seed if seed != -1 else random.randint(0, 2**32 - 1)
    images = []

    for i in range(num_images):
        img_bytes = client.text_to_image(
            prompt,
            model=IMG_MODEL,
            width=width,
            height=height,
            num_inference_steps=4,
            guidance_scale=0.0,
            seed=actual_seed + i,
        )
        # HF API returns PIL Image directly
        if isinstance(img_bytes, Image.Image):
            images.append(img_bytes)
        else:
            images.append(Image.open(io.BytesIO(img_bytes)))

    return images, actual_seed

# ════════════════════════════════════════════════════════════════════
#  ZIP helper
# ════════════════════════════════════════════════════════════════════
def make_zip(images: list, seed: int) -> str:
    path = f"/tmp/nexflow_{seed}.zip"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, img in enumerate(images):
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            zf.writestr(f"nexflow_image_{i+1:02d}_seed{seed}.png", buf.getvalue())
    return path

# ════════════════════════════════════════════════════════════════════
#  FULL PIPELINE
# ════════════════════════════════════════════════════════════════════
def pipeline(
    raw_prompt, style, num_images, aspect_ratio,
    steps, guidance, seed, use_enhance, neg_prompt,
):
    if not raw_prompt.strip():
        return [], "⚠️ Please enter a prompt first.", "", None, gr.update(visible=False)

    if not HF_TOKEN:
        return [], (
            "❌ HF_TOKEN not set.\n"
            "Go to: Space Settings → Variables and Secrets → Add HF_TOKEN"
        ), "", None, gr.update(visible=False)

    t0 = time.time()

    # 1. Enhance prompt
    enhanced = enhance_prompt(raw_prompt, use_enhance)

    # 2. Apply style
    suffix = STYLES.get(style, "")
    final  = f"{enhanced}, {suffix}" if suffix else enhanced

    # 3. Dimensions
    w, h = RATIOS.get(aspect_ratio, (1024, 1024))

    # 4. Generate
    try:
        images, actual_seed = generate_images(final, int(num_images), w, h, int(seed))
        elapsed = time.time() - t0
        status  = (
            f"✅ {len(images)} image(s) ready · "
            f"{elapsed:.1f}s · "
            f"Seed {actual_seed} · "
            f"{w}×{h} · "
            f"FLUX.1-schnell via HF API"
        )
        zip_path = make_zip(images, actual_seed)
        return images, status, final, zip_path, gr.update(visible=True)

    except Exception as e:
        err = str(e)
        print(f"❌ Generation error: {err}")
        return [], f"❌ Error: {err}", final, None, gr.update(visible=False)

# ════════════════════════════════════════════════════════════════════
#  GRADIO UI
# ════════════════════════════════════════════════════════════════════
CSS = """
* { box-sizing: border-box; }
.generate-btn {
    background: linear-gradient(135deg,#5b21b6,#7c3aed,#a855f7,#ec4899) !important;
    color: #fff !important;
    font-size: 1.15rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.02em !important;
    border: none !important;
    border-radius: 16px !important;
    padding: 16px !important;
    box-shadow: 0 4px 24px rgba(139,92,246,0.4) !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
}
.generate-btn:hover {
    transform: translateY(-2px) scale(1.01) !important;
    box-shadow: 0 8px 32px rgba(139,92,246,0.55) !important;
}
#hero { text-align:center; padding:16px 0 28px; }
#hero h1 {
    font-size:2.4rem; font-weight:900; letter-spacing:-0.02em;
    background:linear-gradient(90deg,#7c3aed,#a855f7,#ec4899);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    margin-bottom:10px;
}
.badge {
    display:inline-block; padding:4px 14px; border-radius:99px;
    font-size:0.72rem; font-weight:600; letter-spacing:0.03em;
    margin:3px; border:1px solid rgba(139,92,246,0.3);
    background:rgba(30,27,75,0.8); color:#c4b5fd;
}
.status-out textarea {
    font-family: monospace !important;
    font-size: 0.82rem !important;
}
#footer { text-align:center; color:#4b5563; font-size:0.78rem; margin-top:24px; }
#footer b { color:#7c3aed; }
"""

EXAMPLES = [
    ["A Bengal tiger in a neon-lit Tokyo alley at midnight, heavy rain",  "⚡ Neon Cyberpunk",     2, "🖥️ Landscape 3:2 (1216×832)",  4, 0.0, 42,  True],
    ["Tamil Chola warrior queen in golden armor, palace at dusk",         "🏰 Dark Fantasy Epic",  2, "📱 Portrait 9:16 (768×1344)",   4, 0.0, 77,  True],
    ["Nexflow AI startup logo, geometric, purple gradient, minimal",      "◻️ Clean Minimalist",   1, "⬜ Square 1:1 (1024×1024)",     4, 0.0, 13,  False],
    ["Cozy mountain coffee shop interior, misty morning, warm lights",    "📷 Photorealistic",     2, "🖥️ Landscape 3:2 (1216×832)",  4, 0.0, -1,  True],
    ["Abstract AI neural network, glowing nodes, deep space background",  "🔮 3D Render / Blender",2, "📺 Widescreen 16:9 (1344×768)", 4, 0.0, -1,  True],
    ["Portrait of elderly Indian grandfather, morning village light",     "📷 Photorealistic",     2, "🖼️ Portrait 2:3 (832×1216)",   4, 0.0, -1,  True],
]

with gr.Blocks(css=CSS, title="⚡ FLUX Image Studio — Nexflow Studio") as demo:

    gr.HTML("""
    <div id="hero">
        <h1>⚡ FLUX Image Studio</h1>
        <div>
            <span class="badge">🆓 100% Free</span>
            <span class="badge">🔓 Apache 2.0</span>
            <span class="badge">🖼️ Batch Generation</span>
            <span class="badge">🧠 AI Prompt Engine</span>
            <span class="badge">⚡ FLUX.1-schnell</span>
            <span class="badge">🎯 HF Inference API</span>
            <span class="badge">🔁 High Consistency</span>
        </div>
    </div>
    """)

    with gr.Row(equal_height=False):
        with gr.Column(scale=1, min_width=420):

            prompt_in = gr.Textbox(
                label="✏️ Your Prompt",
                placeholder=(
                    "Describe what you want to see...\n"
                    "e.g. A lone samurai standing in a bamboo forest, misty dawn"
                ),
                lines=4, max_lines=8,
            )
            with gr.Row():
                enhance_chk = gr.Checkbox(
                    label="✨ AI Enhance Prompt (Qwen2.5-7B)",
                    value=True, scale=3,
                )
                num_slider = gr.Slider(
                    1, MAX_IMGS, value=2, step=1,
                    label="🖼️ Images", scale=1,
                )
            enhanced_out = gr.Textbox(
                label="📝 Final Prompt → Model",
                interactive=False, lines=3,
                placeholder="Enhanced prompt appears here after generation...",
            )
            with gr.Row():
                style_dd = gr.Dropdown(
                    choices=list(STYLES.keys()),
                    value="✨ None (Raw)",
                    label="🎨 Style Preset", scale=2,
                )
                ratio_dd = gr.Dropdown(
                    choices=list(RATIOS.keys()),
                    value="⬜ Square 1:1 (1024×1024)",
                    label="📐 Aspect Ratio", scale=2,
                )
            with gr.Accordion("⚙️ Advanced", open=False):
                with gr.Row():
                    steps_sl = gr.Slider(
                        1, 8, value=4, step=1,
                        label="Steps (4 = optimal)",
                    )
                    guidance_sl = gr.Slider(
                        0.0, 7.5, value=0.0, step=0.5,
                        label="Guidance Scale (0 = optimal)",
                    )
                seed_num = gr.Number(
                    label="🎲 Seed  (−1 = random | fixed seed = consistent style)",
                    value=-1, precision=0,
                )
                neg_in = gr.Textbox(
                    label="🚫 Negative Prompt",
                    value=NEG_DEFAULT, lines=2,
                )

            gen_btn = gr.Button(
                "🚀  Generate Images",
                variant="primary",
                elem_classes="generate-btn",
                size="lg",
            )
            status_out = gr.Textbox(
                label="📊 Status",
                interactive=False,
                lines=2,
                elem_classes="status-out",
            )
            dl_btn = gr.File(
                label="📥 Download All as ZIP",
                visible=False,
            )

        with gr.Column(scale=1):
            gallery_out = gr.Gallery(
                label="🖼️ Generated Images",
                columns=2, rows=2,
                height=700,
                object_fit="contain",
                show_download_button=True,
                show_share_button=True,
                preview=True,
            )

    gr.Examples(
        examples=EXAMPLES,
        inputs=[
            prompt_in, style_dd, num_slider, ratio_dd,
            steps_sl, guidance_sl, seed_num, enhance_chk,
        ],
        label="💡 Example Prompts — click any to load",
        examples_per_page=6,
    )

    gr.HTML("""
    <div id="footer">
        Powered by <b>FLUX.1-schnell</b> (Black Forest Labs · Apache 2.0) &nbsp;·&nbsp;
        Prompt AI: <b>Qwen2.5-7B-Instruct</b> &nbsp;·&nbsp;
        Inference: <b>HuggingFace API</b> (Free) &nbsp;·&nbsp;
        Built with ❤️ by <b>Nexflow Studio</b>
    </div>
    """)

    _inputs  = [prompt_in, style_dd, num_slider, ratio_dd,
                steps_sl, guidance_sl, seed_num, enhance_chk, neg_in]
    _outputs = [gallery_out, status_out, enhanced_out, dl_btn, dl_btn]

    gen_btn.click(fn=pipeline, inputs=_inputs, outputs=_outputs)
    prompt_in.submit(fn=pipeline, inputs=_inputs, outputs=_outputs)

demo.launch()
