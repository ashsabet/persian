# Deploying to persian.ashkon.net

Target: your homelab Ubuntu server (Postgres + Apache already running), reachable
via VPN at 192.168.1.10 and published at https://persian.ashkon.net. The app runs
under Gunicorn; Apache reverse-proxies it and serves static/media. All Persian
audio is generated **locally** with the gyro Piper voice — no cloud, no runtime
network calls.

## Quick path (scripted)

```bash
# On the server, as a sudo-capable user:
sudo mkdir -p /opt/persian && sudo chown "$USER" /opt/persian
# copy the webapp/ folder to /opt/persian/webapp  (git clone, rsync, or scp)
cd /opt/persian/webapp
nano .env                 # if it exists; otherwise setup.sh creates it from .env.example
bash deploy/setup.sh
```

`setup.sh` creates the virtualenv, installs deps, downloads the gyro voice, ensures
the Postgres role/db, runs migrations, collects static, seeds Unit 1, and generates
all audio. Then follow the printed steps to install the systemd + Apache units.

## Manual steps (what the script does)

1. **Code** → `/opt/persian/webapp`.
2. **Env**: `cp .env.example .env` and set a real `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`,
   the `POSTGRES_*` values, and `PIPER_MODEL=/opt/piper/voices/fa_IR-gyro-medium.onnx`.
3. **Virtualenv**: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.
4. **Piper voice** (MIT license):
   ```bash
   sudo mkdir -p /opt/piper/voices
   B=https://huggingface.co/rhasspy/piper-voices/resolve/main/fa/fa_IR/gyro/medium
   sudo curl -L -o /opt/piper/voices/fa_IR-gyro-medium.onnx       $B/fa_IR-gyro-medium.onnx
   sudo curl -L -o /opt/piper/voices/fa_IR-gyro-medium.onnx.json  $B/fa_IR-gyro-medium.onnx.json
   ```
5. **Postgres**:
   ```bash
   sudo -u postgres psql -c "CREATE ROLE persian LOGIN PASSWORD 'yourpassword';"
   sudo -u postgres psql -c "CREATE DATABASE persian OWNER persian;"
   ```
6. **Django**:
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py seed_content
   python manage.py generate_audio          # renders gyro audio (CPU, a few minutes)
   python manage.py createsuperuser         # your admin login for /admin
   ```
7. **Gunicorn service**:
   ```bash
   sudo cp deploy/gunicorn.service /etc/systemd/system/persian.service
   sudo systemctl daemon-reload && sudo systemctl enable --now persian
   ```
8. **Apache vhost**:
   ```bash
   sudo a2enmod proxy proxy_http headers ssl rewrite
   sudo cp deploy/apache-persian.conf /etc/apache2/sites-available/persian.conf
   sudo a2ensite persian && sudo systemctl reload apache2
   ```
   (TLS cert via `sudo certbot --apache -d persian.ashkon.net`, or point the
   `SSLCertificate*` lines at your existing cert.)

## Verify

- Visit https://persian.ashkon.net → log in as **demo / persian123**.
- Play a lesson; the 🔊 buttons should speak Persian (gyro voice).
- `/admin` is your content CMS for adding the rest of the curriculum.

## Updating later

```bash
cd /opt/persian/webapp && git pull        # or re-sync files
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py generate_audio           # renders only new/missing clips
sudo systemctl restart persian
```

## Notes
- Paths above assume `/opt/persian/webapp`; adjust the systemd unit and Apache
  `Alias`/`Directory` lines if you put it elsewhere.
- The web process never calls Piper or any network service at request time — audio
  is pre-rendered files served by Apache.
- `generate_audio` is idempotent; use `--force` to re-render after a voice change.

## Social login (Google / Microsoft) — optional

Users can register with a username+password as before; these add one-click
"Continue with Google/Microsoft" buttons. A button only appears once that
provider's client id is set in `.env`, so you can enable one, both, or neither.

Callback (redirect) URLs to register with each provider:

- Google:    `https://persian.ashkon.net/accounts/google/login/callback/`
- Microsoft: `https://persian.ashkon.net/accounts/microsoft/login/callback/`

### Google

1. Google Cloud Console → **APIs & Services → Credentials**.
2. Configure the **OAuth consent screen** (External; app name, support email;
   add your email as a test user while unpublished).
3. **Create credentials → OAuth client ID → Web application**.
   - Authorized JavaScript origin: `https://persian.ashkon.net`
   - Authorized redirect URI: `https://persian.ashkon.net/accounts/google/login/callback/`
4. Copy the **Client ID** and **Client secret** into `.env` as
   `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`.

### Microsoft

1. Azure Portal → **Microsoft Entra ID → App registrations → New registration**.
2. Supported account types: **Accounts in any org directory and personal
   Microsoft accounts** (this matches `MICROSOFT_TENANT=common`).
3. Redirect URI (platform **Web**):
   `https://persian.ashkon.net/accounts/microsoft/login/callback/`
4. **Certificates & secrets → New client secret**; copy the secret **Value**.
5. Put the **Application (client) ID** and secret into `.env` as
   `MICROSOFT_CLIENT_ID` / `MICROSOFT_CLIENT_SECRET`. Set `MICROSOFT_TENANT` to a
   specific tenant id if you want to restrict sign-in to one organization.

### Apply on the server

```bash
cd /opt/persian/webapp && git pull
source .venv/bin/activate
pip install -r requirements.txt          # installs django-allauth
nano .env                                # add the GOOGLE_/MICROSOFT_ values
python manage.py migrate                 # creates allauth + sites tables
python manage.py collectstatic --noinput # ships the new CSS/icons
sudo systemctl restart persian
```

Sign-in with a matching **verified email** links to an existing local account
rather than creating a duplicate. No secrets live in the database or git — the
client id/secret are read from `.env` at startup.
