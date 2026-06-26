# Persian Language Webapp — Design Document (MVP)

**Project:** A Duolingo-style web app that teaches an English speaker to read, write, and speak Persian (Farsi), from the alphabet through CEFR **A2 (elementary)**.
**Owner:** Ashkon · **Target host:** `https://persian.ashkon.net` (homelab Ubuntu, Postgres + Apache, VPN at 192.168.1.10)
**Status:** Design phase — for review before coding begins.
**Last updated:** 2026-06-24

---

## 1. MVP Scope

### 1.1 Who it's for
A motivated English-speaking adult beginner with no prior Persian. Single learner persona for the MVP (no kids' mode, no teacher/classroom features). Heritage learners who can speak some Persian but can't read are a strong secondary fit because the script track stands on its own.

### 1.2 Learning outcomes (what "done" means)
By completing the MVP a learner can:

- **Read & write** the full Persian alphabet (32 letters) including the four positional forms, and read short vowelled and unvowelled words.
- **Understand and produce** ~600–800 high-frequency words.
- **Handle A1–A2 conversation:** greetings & introductions, family, numbers/time/dates, food & ordering, shopping & prices, directions, daily routine, weather, simple past and present narration, polite requests.
- **Grammar through A2:** present tense, present continuous, simple past, the *ezāfe* construction, plurals, possessives, the object marker *rā*, comparatives, common prepositions, basic subordinate clauses.
- **Speak** by repeating and recording target phrases and getting pronunciation feedback (see §1.4 stretch).

This maps to roughly **CEFR A1 → A2**. We standardize on CEFR so scope, content sourcing, and "milestones" all share one yardstick.

### 1.3 Core feature set (must-have for MVP)
1. **Skill path / learning map** — a linear-with-branches track of units → lessons, Duolingo-style, with locked/unlocked nodes.
2. **Alphabet track** — dedicated early units teaching letterforms, sounds, joining behavior, and handwriting/tracing.
3. **Exercise engine** with these item types:
   - Multiple choice (image ↔ word ↔ audio).
   - Listening (hear Persian, pick/transcribe).
   - Translate (Persian→English and English→Persian) via word-bank tiles and free text.
   - Match pairs (word ↔ image, word ↔ audio, Persian ↔ English).
   - Letter/script drills (identify letter, pick the right positional form, build a word).
   - Tap-to-arrange sentence building.
   - Speaking prompt (record & compare) — see §1.4.
4. **Audio everywhere** — every word/sentence has natural-sounding TTS playback (normal + slow).
5. **Spaced repetition review** — a "Practice" mode that resurfaces weak/old items (SM-2-style scheduling).
6. **Progress & habit tools** (see §1.5): daily streaks, a simple daily goal, and spaced-repetition review — deliberately light-touch, with no points, competition, or rankings.
7. **Accounts & progress** — email/password signup, progress persistence, resume where you left off.
8. **Responsive web UI** — works on phone and desktop browser; RTL-aware rendering for Persian text.

### 1.4 Speaking / pronunciation
- **MVP baseline:** "listen and repeat" with self-grading (hear native TTS, record yourself, play both back, mark if you got it). No automated scoring required to ship.
- **Stretch (post-MVP):** automatic pronunciation scoring via the browser's Web Speech API (`fa-IR` recognition) or a cloud speech-to-text comparison. Treated as a fast-follow, not a launch blocker.

### 1.5 Progress & habit layer (light-touch, not gamified)
Per direction, the app keeps motivation tools minimal and avoids points and competition. **No XP, leaderboards, leagues, or crowns.**
- **Streak** — consecutive days the learner meets a small daily goal; a visible flame counter; an optional streak-freeze so a single missed day doesn't reset everything.
- **Daily goal** — a learner-chosen target measured in *minutes or lessons per day* (not points). Drives the streak and the reminder.
- **Daily reminder** — optional email nudge (email for MVP).
- **Spaced-repetition review** — surfaces words/skills that are due; this "what to do next" cue is the main motivator in place of game mechanics.
- **Hearts / mistake limit** — *optional and off by default.* Offered as a setting for learners who want a focus constraint, but the default experience lets you make mistakes freely. (Decision flagged in §6.)

### 1.6 Explicitly out of scope for MVP (non-goals)
- Native mobile apps (responsive web only).
- User-generated content, social feed, chat, or messaging.
- Multiple source languages (English→Persian only).
- Beyond-A2 content (B1+).
- Stories/podcast features, live tutoring, AI conversation partner.
- In-app payments / subscriptions (build the data model to allow it later, but no paywall at launch).
- Offline mode.

### 1.7 Success metrics
- **Activation:** % of signups who finish the first lesson.
- **Retention:** D1 / D7 / D30 return rate; streak distribution.
- **Progression:** median lessons completed; % reaching "Alphabet complete" and each unit milestone.
- **Engagement:** daily-goal completion rate; average session length.
- These are the levers the habit layer (streaks, daily goal, reminders) exists to move; instrument them from day one.

---

## 2. Lesson Plan & Milestones

The curriculum is organized as **Sections → Units → Lessons**. Each lesson is ~6–12 exercises and ~3–5 minutes. Finishing all lessons in a unit unlocks a **milestone checkpoint** — a short mixed quiz that confirms the learner is ready to move on.

### Section 0 — The Persian Script (the on-ramp)
Goal: read and write all 32 letters and sound out simple words. This is the make-or-break section, so it's heavily scaffolded with tracing, audio, and tiny wins.

- **Unit 1 — First letters & sounds:** ا ب پ ت — letter names, isolated form, sound, first 2-letter combos. Intro to right-to-left.
- **Unit 2 — Joining letters:** how letters connect; initial/medial/final/isolated forms; ث ج چ ح خ.
- **Unit 3 — More consonants:** د ذ ر ز ژ س ش; non-joining letters (د ذ ر ز ژ و).
- **Unit 4 — Remaining consonants:** ص ض ط ظ ع غ ف ق ک گ ل م ن.
- **Unit 5 — Vowels & finals:** و ه ی; short vowels (zabar/zir/pish), short vs. long vowels, *tashdid*, *tanvin*.
- **Milestone: "Alphabet Complete"** — read & type ~30 simple words; first big badge.

### Section 1 — Survival & Self (A1)
- **Unit 6 — Greetings & courtesy:** salām, khodāhāfez, lotfan, mersi/motشakkeram, bale/na.
- **Unit 7 — Introductions:** name, "I am / you are," nationality, simple questions (esm-e shomā chi-e?).
- **Unit 8 — Numbers 0–20 & beyond:** counting, age, phone numbers; Persian digits ۰۱۲۳.
- **Unit 9 — Family:** mādar, pedar, barādar, khāhar; possessive *ezāfe* (ketāb-e man).
- **Unit 10 — Everyday objects & colors:** house items, colors, "this/that," simple plurals.
- **Milestone: "First Conversations"** — role-play a short intro dialogue.

### Section 2 — Daily Life (A1→A2)
- **Unit 11 — Present tense verbs:** budan (to be), dāshtan (to have), raftan/āmadan; subject endings.
- **Unit 12 — Food & eating:** common foods, "I want / I like," ordering, the object marker *rā*.
- **Unit 13 — Time & routine:** clock, days, present continuous (dāram mi-ravam), daily schedule.
- **Unit 14 — Shopping & money:** prices, "how much?", bargaining basics, comparatives (bozorg-tar).
- **Unit 15 — City & directions:** places, prepositions, "where is…?", giving/following directions.
- **Milestone: "Getting Around"** — listening + sentence-building checkpoint.

### Section 3 — Talking About Life (A2)
- **Unit 16 — Simple past:** regular past stems, "yesterday I went…," common irregulars.
- **Unit 17 — Weather & seasons:** describing weather, future intent (mi-khāham beravam).
- **Unit 18 — Health & body:** body parts, "I have a headache," at the doctor/pharmacy.
- **Unit 19 — Travel & plans:** transport, booking, making plans, polite requests (mi-shavad…?).
- **Unit 20 — Connecting ideas:** because/but/when, simple relative clauses, telling a short story.
- **Milestone: "A2 Capstone"** — a mixed review covering reading, listening, translation, and a short recorded monologue.

### 2.1 Cross-cutting tracks
- **Spaced-repetition Practice** unlocks after Unit 6 and continuously recycles seen vocab/grammar.
- **Pronunciation drills** are sprinkled into every unit (listen-and-repeat items).
- **Culture notes** (optional, skippable cards): script etiquette, tā'ārof, formal vs. informal "you" (shomā/to).

### 2.2 Content volume estimate (for build planning)
~20 units × ~4 lessons = **~80 lessons**, ~700 vocab items, ~1,200 example sentences, each with audio + (where useful) an image. This is the dataset the sourcing plan below must fill.

---

## 3. Sourcing the Training Material

The app needs five asset types: **vocabulary lists, example sentences, audio, images, and grammar reference**. The strategy below favors open licenses and a clear path to commercial use later.

### 3.1 Vocabulary & frequency lists
- **A Frequency Dictionary of Persian (Routledge, Miller/Aghajanian/Stewart)** — the gold standard for "which words to teach first." Commercial book; use it as an *ordering reference* for our own list rather than copying entries verbatim.
- **Tatoeba word/sentence data** — open corpus, license **CC-BY 2.0 FR** (attribution required). Good for both vocab-in-context and example sentences.
- **Lexiteria / Persian Today Corpus frequency lists** — useful to cross-check frequency ranking; confirm license before bulk use.
- **Approach:** build our own curated ~700-word MVP list, ordered by frequency and grouped by the unit themes above. Store as structured data (CSV/JSON → Postgres) so it's editable.

### 3.2 Example sentences
- **Tatoeba (CC-BY 2.0 FR)** — primary source; filter for short, A1/A2-appropriate Persian sentences with existing English translations. Attribution baked into the app's credits page.
- **Author original sentences** for grammar points Tatoeba covers thinly (the alphabet section, specific verb drills). Cleanest from a licensing standpoint.
- Avoid the literary corpora (Najwai Sukhan, Anjuman-e-Katib) for teaching content — they're **CC-BY-NC** (non-commercial) and the register is too advanced; fine only for optional "real text" extension material.

### 3.3 Audio (natural-sounding Persian) — **Fully local / self-hosted** (decided)
Decision: generate all audio with an **open-source TTS model running on the homelab server** — no cloud dependency, no per-use cost, full privacy. Because every clip is pre-generated once and cached as a static file, naturalness only has to be judged once, at build time.

**Engine: [Piper](https://github.com/rhasspy/piper)** — MIT-licensed (commercial-OK), runs in real time **on CPU with no GPU**, which suits the existing Ubuntu box. Persian (fa_IR) voices available:

| Voice | Source | Notes |
|---|---|---|
| **fa_IR-amir-medium** | rhasspy/piper-voices | Official Persian male voice; clear, solid baseline |
| **fa_IR-gyro-medium** ✅ **(chosen)** | rhasspy/piper-voices | Official Persian voice; clean and intelligible — **selected voice** |
| **Mana-Persian-Piper** ❌ | MahtaFetrat (fine-tuned on ManaTTS) | Most natural in theory, but its `training_dir` ONNX export produced unintelligible/noisy audio on this piper+onnxruntime build — not used |

Supporting data if we ever want to fine-tune our own voice: **ManaTTS** — largest open Persian speech dataset, 114+ hrs, **CC0** license.

**Quality expectation:** clear and intelligible, a noticeable step below premium cloud neural voices in expressiveness — acceptable for a learning app where clarity matters most. **Voice decided: fa_IR-gyro-medium** (official rhasspy voice). The Mana fine-tuned export was tried first but came out unintelligible on this stack.

**Pipeline:**
1. Install Piper on the server (CPU); download the **gyro** fa_IR voice.
2. A build script walks every `Word`/`Sentence` row and renders **normal + slow** speed clips (Piper exposes a length/speed parameter), output as OGG/MP3 keyed by content ID.
3. Files are written to a media directory served statically by **Apache**; the DB stores the relative path on each `MediaAsset`.
4. The script is idempotent/re-runnable so new content or a voice swap just regenerates what changed.

No external API keys, no network calls at runtime. Estimated one-time render: ~2,000 short clips, minutes-to-low-hours on CPU.

### 3.4 Images
- **Unsplash, Pexels, Pixabay, Openverse** — free, commercial-OK, mostly no attribution required (verify per-asset). Best for concrete nouns (food, objects, places).
- **Wikimedia Commons** — good for cultural/specific items; check each file's license.
- **Approach:** curate one image per teachable concrete noun (~300–400 images), normalize size/crop, store on the server. Keep a license/attribution field per image in the DB.

### 3.5 Grammar & pedagogy reference
- Use established open grammar references (e.g., Wikipedia's Persian grammar, public university Persian course outlines) to *inform* our own concise in-app "grammar tip" cards. Write the tips ourselves to avoid copyright issues.

### 3.6 Licensing hygiene
Every content row in the DB carries `source` and `license` fields. Maintain a public **Credits/Attributions** page (satisfies CC-BY). Keep teaching content on permissive (CC-BY / CC0 / original) sources; quarantine NC-licensed material to optional extras only.

---

## 4. UI Wireframe

A clickable HTML wireframe accompanies this document: **`wireframe.html`** (open it in a browser). It is low-fidelity (grayscale, boxes) and covers the key screens:

1. **Home / Learning Path** — vertical unit path with locked/unlocked lesson nodes; a minimal top bar showing the streak 🔥 (and the optional hearts indicator if enabled).
2. **Lesson — multiple choice** — image + "which word?" with audio button and answer tiles; progress bar and hearts.
3. **Lesson — translate (word bank)** — Persian sentence, tap-to-build English answer from tiles.
4. **Lesson — script drill** — show a letter, pick its correct positional form / matching sound.
5. **Lesson — listening** — play audio, transcribe or choose.
6. **Lesson complete** — words learned this lesson, streak bump, and a simple "continue" CTA.
7. **Profile / Stats** — streak calendar and progress through the units (no points or rankings).
8. **Practice (SRS) entry** — "strengthen weak skills" screen.

RTL handling, the audio-first layout, and a minimal top bar (streak, plus the optional hearts indicator) are shown consistently across screens so the build can lift spacing and component structure directly.

---

## 5. Proposed Architecture (for the build phase)

Chosen stack: **Django + server-rendered templates + HTMX**, Postgres, behind Apache.

- **Backend:** Django (Python). Django ORM over your existing **Postgres**; Django admin gives us a free CMS for editing lessons/words/sentences — a big win for content management.
- **Frontend:** Django templates + **HTMX** for the snappy, no-full-reload exercise flow, with a sprinkle of vanilla JS / Alpine.js for the interactive bits (drag tiles, audio, recording). Keeps the JS footprint small.
- **Auth:** Django's built-in auth (email/password) for MVP.
- **Media:** pre-generated TTS audio + images served as static files by **Apache**; Apache reverse-proxies the dynamic app (gunicorn/uWSGI running Django) and terminates TLS for `persian.ashkon.net`.
- **Data model (sketch):** `User`, `Profile(streak, last_active, daily_goal, hearts_enabled)`, `Section`, `Unit`, `Lesson`, `Exercise`, `Word`, `Sentence`, `MediaAsset(audio/image + source + license)`, `UserLessonProgress`, `SRSItem(ease, interval, due_at)`. (No XP, leaderboard, or crown tables.)
- **Deploy target:** `https://persian.ashkon.net`, reachable via VPN at `192.168.1.10`. Apache vhost + Let's Encrypt (or your existing cert), gunicorn as a systemd service, Postgres on the same host.

This is a sketch for review — we'll firm it up before writing code.

---

## 6. Open Questions / Decisions for Ashkon
1. **Persian variety & register:** standard Tehrani Persian, neutral/polite register (shomā) as default? (Recommended.)
2. **Transliteration:** show Latin transliteration as a training-wheel that fades out, or script-only from early on?
3. **Hearts:** keep the optional, default-off mistake limiter as a setting, or drop it entirely?
4. **TTS voice:** ✅ Decided — fully-local Piper, **fa_IR-gyro-medium** voice (the Mana export was unintelligible on this stack; §3.3).
5. **Auth:** plain email/password for MVP, or add Google sign-in?

---

## 7. Next Steps
1. Review & sign off on scope (§1) and curriculum (§2).
2. Decide the open questions in §6.
3. Lock the data model and lesson JSON schema.
4. Build a thin vertical slice: one unit (Section 0, Unit 1) end-to-end — content → DB → Django/HTMX UI → deploy to the server — to validate the whole pipeline before scaling content.

---

### Sources consulted for this plan
- TTS: [ElevenLabs Persian TTS](https://elevenlabs.io/text-to-speech/persian), [Google Cloud TTS voices](https://docs.cloud.google.com/text-to-speech/docs/list-voices-and-types), [Azure / TTS API comparisons 2026](https://www.speechmatics.com/company/articles-and-news/best-tts-apis-in-2025-top-12-text-to-speech-services-for-developers)
- Text/vocab: [Tatoeba corpus & licensing](https://en.wiki.tatoeba.org/articles/show/using-the-tatoeba-corpus), [A Frequency Dictionary of Persian (Routledge)](https://www.routledge.com/A-Frequency-Dictionary-of-Persian-Core-vocabulary-for-learners/Miller-Aghajanian-Stewart/p/book/9781138833241), [Lexiteria Persian frequency list](https://lexiteria.com/word_frequency/persian_word_frequency_list.html)
- Images: [Unsplash](https://unsplash.com/s/photos/language-learning), [Pixabay](https://pixabay.com/images/search/language%20learning/), [CC0/public-domain image sources](https://www.wpbeginner.com/showcase/16-sources-for-free-public-domain-and-cc0-licensed-images/)
