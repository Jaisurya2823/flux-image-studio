# ⚡ FLUX Image Studio — Nexflow Studio

> High-quality AI image generation. Free. Open source. Production-ready.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://flux-image-studio.streamlit.app)

## Features

| Feature | Detail |
|---|---|
| 🖼️ Image Model | FLUX.1-schnell (Apache 2.0, Black Forest Labs) |
| 🧠 Prompt AI | Qwen2.5-7B-Instruct (free HF API) |
| 🎨 Styles | 16 presets (Photorealistic, Cinematic, Anime, Cyberpunk...) |
| 📐 Ratios | 7 aspect ratios |
| 🖼️ Batch | 1–4 images per generation |
| 📥 Export | ZIP download |
| 🔁 Consistency | Seed-controlled |
| 💰 Cost | $0 — completely free |

## Deploy to Streamlit Cloud (Free)

1. Fork this repo on GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repo → `app.py`
5. Add secret: `HF_TOKEN = "hf_your_token"`
6. Deploy ✅

## Local Setup

```bash
git clone https://github.com/Jaisurya2823/flux-image-studio
cd flux-image-studio
pip install -r requirements.txt
streamlit run app.py
```

Add your token to `.streamlit/secrets.toml`:
```toml
HF_TOKEN = "hf_your_token_here"
```

## Stack

- **Streamlit** — UI framework
- **FLUX.1-schnell** — 12B image model (Apache 2.0)
- **Qwen2.5-7B-Instruct** — prompt enhancer
- **HuggingFace Inference API** — free inference

## License

Apache 2.0 — free for personal and commercial use.

Built with ❤️ by **Nexflow Studio**
