# TTS Pipeline — local Piper audio for vocabulary

How non-alphabet vocabulary gets its audio. The pipeline lives in
`learn/management/commands/generate_audio.py`; this doc captures the reasoning and
the dead-ends, which aren't visible in the code. (The **alphabet** deliberately
uses native recordings instead — see the bottom section.)

## Engine + voice
- **Engine: Piper** (rhasspy/piper) — MIT license, runs on CPU, no cloud. Chosen
  because the app is fully local/self-hosted; audio is pre-generated once and served
  as static WAVs (the web request path never calls Piper).
- **Voice: `fa_IR-gyro-medium`** — the official rhasspy Persian voice. Model + config
  come from HuggingFace and are pointed at via `PIPER_MODEL` in `.env`.

## Voices/engines tried and rejected
- **Mana (fine-tuned Piper export):** tried first. Phonemes were correct, but on the
  piper 1.4.2 + onnxruntime build the export produced an unintelligible, noisy hiss
  (normalization amplified a noisy export). Dropped.
- **Tacotron2:** muffled output. Rejected.
- **Cloud TTS:** rejected on principle — the project is deliberately fully local.
- Of all candidates, **gyro sounded clearly the best** in the A/B.

## The pipeline (per item: render → post-process)

1. **Render with Piper, normalization OFF.**
   `piper --model $PIPER_MODEL --length-scale 1.0 --no-normalize --output_file out.wav`
   - `--no-normalize` is the key flag: it stops Piper from slamming levels to full
     scale — the main source of harsh, clipped-sounding output. We normalize ourselves
     afterward with headroom.

2. **Post-process in numpy/scipy** (`_postprocess`), in this order:
   - **Silence trim** — drop leading/trailing dead air below **−45 dB**, keep a 10 ms pad.
   - **High-shelf EQ** — RBJ biquad, corner **3000 Hz**, gain **+5 dB**, slope **0.7**.
     Adds consonant clarity/brightness (Persian consonant contrasts were getting lost).
   - **Fades** — **10 ms** in/out to remove clicks at the boundaries.
   - **Padding** — add **30 ms** of silence head and tail.
   - **Peak-normalize** to **−2.0 dBFS** (headroom; avoids clipping harshness).
   - Clip to [−1, 1] and write back as 16-bit PCM mono.

   Tunables (top of `generate_audio.py`): `TARGET_PEAK_DB=-2.0`, `SHELF_FREQ=3000`,
   `SHELF_GAIN_DB=5.0`, `SHELF_SLOPE=0.7`, `FADE_MS=10`, `PAD_MS=30`, `SILENCE_DB=-45`.

## Command ergonomics
- `python manage.py generate_audio` — renders only missing files (normal speed).
- `--force` re-renders everything (use after a voice or parameter change).
- `--slow` also renders a `-slow` clip per item (`--length-scale 1.5`). Off by default:
  the player does "slow" in the browser with `playbackRate = 0.6` + `preservesPitch`
  (same clip, slower, natural pitch), so separate `-slow` files aren't needed. Kept as
  an opt-in for anyone who wants pre-rendered slow files.
- `--no-postprocess` — raw Piper output, for A/B comparison/debugging.
- Idempotent and re-runnable; runs on the server, never at request time.

## Why the alphabet uses recorded voice instead
Even fully tuned, TTS wasn't good enough **for teaching the alphabet**: bare consonant
glyphs came out muffled/unintelligible and prosody was breathy. The alphabet is where
pronunciation precision matters most, so we recorded a native speaker ("Shahrzad") and
spliced 128 clips. Methodology lesson that drove this: **never teach a bare consonant** —
present each letter as name → sound triad (e.g. "ba be bo") → two example words.

## If reviving/extending TTS for new vocabulary
- Keep `--no-normalize` + custom headroom normalization; it's the highest-leverage bit.
- Re-tune the high-shelf gain per voice; +5 dB @ 3 kHz suited gyro.
- A/B against `--no-postprocess` to confirm the pass is helping, not smearing.
- Consider matching loudness (e.g. LUFS) across TTS and recorded clips so mixed lessons
  don't jump in volume. (Not yet done — peak-normalization only.)
