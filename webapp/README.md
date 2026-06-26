# Persian Webapp — Vertical Slice

A Django + HTMX/vanilla-JS web app that teaches an English speaker to read, write,
and speak Persian. This is the **first vertical slice**: Section 0 / Unit 1 (the
alphabet on-ramp) wired end-to-end — content → DB → exercise player → streak
tracking → fully-local Piper audio. See `../DESIGN.md` for the full plan.

Light-touch by design: **streaks only**, no XP / leaderboards / leagues / crowns.

## What's here

```
webapp/
  config/            Django project (settings, urls, wsgi)
  learn/             the app
    models.py        Section→Unit→Lesson→Exercise, Word/Sentence, Profile (streak), progress
    views.py         path, lesson player, answer checking, completion, profile, auth
    management/commands/
      seed_content.py    loads Section 0 Unit 1 (2 lessons, 10 exercises) + demo user
      generate_audio.py  renders Piper (gyro) audio for every word — normal + slow
  templates/         base, learn pages, login/register
  static/learn/      app.css (RTL-aware) + lesson.js (the exercise engine)
  deploy/            gunicorn.service, apache-persian.conf, setup.sh
```

Exercise types implemented: multiple choice, listening, script drill (positional
forms), translate (word bank, both directions), and speak (listen & repeat).
Transliteration shows on early lessons and is controlled per-lesson
(`Lesson.show_transliteration`) so it can fade out later.

## Local development (SQLite, no audio)

```bash
cd webapp
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # piper-tts optional locally
python manage.py migrate
python manage.py seed_content            # creates demo / persian123
python manage.py runserver
# open http://127.0.0.1:8000  — log in as demo / persian123
```

Leave the `POSTGRES_*` env vars unset to use SQLite automatically. Audio buttons
are silent until you run `generate_audio` with the Piper model present (that's
expected on a dev box without the voice).

## Production

See **DEPLOY.md** — Postgres + Gunicorn + Apache on the Ubuntu server, with the
gyro Persian voice generating all audio locally.
