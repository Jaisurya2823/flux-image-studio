#!/bin/bash
echo "================================================"
echo "  FLUX Image Studio -- Nexflow Studio"
echo "================================================"

[ ! -f venv/bin/activate ] && echo "[ERROR] Run setup.sh first!" && exit 1

source venv/bin/activate
[ -f .env ] && export $(grep -v '^#' .env | xargs)

echo "[INFO] Open http://127.0.0.1:7860 in your browser"
echo "[INFO] Press Ctrl+C to stop"
echo ""
python app.py
