---
title: FLUX Image Studio
emoji: ⚡
colorFrom: purple
colorTo: pink
sdk: gradio
sdk_version: 5.0.0
app_file: app.py
pinned: true
license: apache-2.0
tags:
  - image-generation
  - flux
  - zerogpu
  - text-to-image
  - nexflow
---

# ⚡ FLUX Image Studio — Nexflow Studio

> High-quality AI image generation. Free. Open source. Production-ready.

## Features

| Feature | Detail |
|---|---|
| 🖼️ Image Model | FLUX.1-schnell (Apache 2.0, Black Forest Labs) |
| 🧠 Prompt AI | Qwen2.5-7B-Instruct (free HF API) |
| ⚡ GPU | ZeroGPU H200 (free on HuggingFace Spaces) |
| 🎨 Styles | 16 presets (Photorealistic, Cinematic, Anime, Cyberpunk...) |
| 📐 Ratios | 7 aspect ratios (Square, Portrait, Widescreen, Ultrawide...) |
| 🖼️ Batch | 1–4 images per generation |
| 📥 Export | ZIP download of all images |
| 🔁 Consistency | Seed-controlled for reproducible results |
| 💰 Cost | $0 — completely free |

## Setup on HuggingFace Spaces

### 1. Add HF_TOKEN secret
- Space Settings → Variables and Secrets → New Secret
- Name: `HF_TOKEN`
- Value: your free token from huggingface.co/settings/tokens

### 2. Connect GitHub repo
- Space Settings → Repository → Link GitHub repo

### 3. Auto-deploy
Every `git push` to main automatically updates your Space.

## Local Dev

```bash
git clone https://github.com/YOUR_USERNAME/flux-image-studio
cd flux-image-studio
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

> Note: Local runs use SDXL-Turbo fallback (CPU-compatible).
> Full FLUX quality only on HuggingFace Spaces ZeroGPU.

## Stack

- **FLUX.1-schnell** — 12B parameter image model, Apache 2.0
- **Qwen2.5-7B-Instruct** — prompt enhancement LLM
- **Gradio 5** — UI framework
- **HuggingFace Spaces ZeroGPU** — free H200 inference

## License

Apache 2.0 — free for personal and commercial use.

Built with ❤️ by **Nexflow Studio**
