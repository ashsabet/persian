#!/usr/bin/env bash
# One-shot setup for the Persian webapp on the Ubuntu server.
# Run from the webapp/ directory:  bash deploy/setup.sh
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$APP_DIR"
echo ">> App dir: $APP_DIR"

# 1) Python virtualenv + dependencies (includes piper-tts for audio)
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 2) Environment file
if [ ! -f .env ]; then
    cp .env.example .env
    echo ">> Created .env from template — EDIT IT (secret key, Postgres password) before going live."
fi
# shellcheck disable=SC1091
set -a; source .env; set +a

# 3) Download the Mana Persian Piper voice (MIT license)
MODEL_PATH="${PIPER_MODEL:-/opt/piper/voices/fa_IR-mana-medium.onnx}"
MODEL_DIR="$(dirname "$MODEL_PATH")"
BASE="https://huggingface.co/MahtaFetrat/Mana-Persian-Piper/resolve/main"
if [ ! -f "$MODEL_PATH" ]; then
    sudo mkdir -p "$MODEL_DIR"
    echo ">> Downloading Mana voice to $MODEL_DIR ..."
    sudo curl -L -o "$MODEL_PATH"        "$BASE/fa_IR-mana-medium.onnx"
    sudo curl -L -o "$MODEL_PATH.json"   "$BASE/fa_IR-mana-medium.onnx.json"
fi

# 4) Postgres (create role + db if missing). Requires local postgres superuser access.
if [ -n "${POSTGRES_DB:-}" ]; then
    echo ">> Ensuring Postgres role/db exist (ignore 'already exists' notices)..."
    sudo -u postgres psql -c "CREATE ROLE ${POSTGRES_USER} LOGIN PASSWORD '${POSTGRES_PASSWORD}';" || true
    sudo -u postgres psql -c "CREATE DATABASE ${POSTGRES_DB} OWNER ${POSTGRES_USER};" || true
fi

# 5) Django: migrate, static, seed content, generate audio
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py seed_content
python manage.py generate_audio

echo
echo ">> Done. Next:"
echo "   - Create your admin user:  python manage.py createsuperuser"
echo "   - Install services:        sudo cp deploy/gunicorn.service /etc/systemd/system/persian.service"
echo "                              sudo systemctl daemon-reload && sudo systemctl enable --now persian"
echo "   - Install Apache vhost:    sudo a2enmod proxy proxy_http headers ssl rewrite"
echo "                              sudo cp deploy/apache-persian.conf /etc/apache2/sites-available/persian.conf"
echo "                              sudo a2ensite persian && sudo systemctl reload apache2"
echo "   - Visit https://persian.ashkon.net  (demo login: demo / persian123)"
