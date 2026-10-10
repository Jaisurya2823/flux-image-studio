#!/bin/bash
echo "================================================"
echo "  FLUX Image Studio -- Nexflow Studio"
echo "  Setup (Mac / Linux)"
echo "================================================"

command -v python3 &>/dev/null || { echo "[ERROR] Python3 not found."; exit 1; }

echo "[1/3] Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "[2/3] Installing dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo "[3/3] Setting up .env..."
[ ! -f .env ] && cp .env.example .env && echo "[!] Open .env and paste your HF_TOKEN"

echo ""
echo "================================================"
echo "  Done! Run: bash start.sh"
echo "================================================"
