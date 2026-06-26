"""
Generate Persian audio for every Word and Sentence using the local Piper
(gyro) voice, then apply a light post-processing pass for clarity:

  * render with Piper --no-normalize (so Piper never slams to full scale)
  * trim leading/trailing silence
  * gentle high-shelf EQ for consonant clarity
  * short fade in/out + small padding (no clicks / abrupt cuts)
  * peak-normalize to TARGET_PEAK_DB (headroom, no clipping)

Produces a normal and a slow ('-slow') WAV per item under MEDIA_ROOT/audio/.
Re-runnable; skips existing files unless --force.

    python manage.py generate_audio
    python manage.py generate_audio --force
    python manage.py generate_audio --no-postprocess   # raw Piper output

Requires the Piper CLI on PATH and PIPER_MODEL set (see .env). Runs on the
server, not the web request path.
"""
import subprocess
import wave
from pathlib import Path

import numpy as np
from scipy import signal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from learn.models import Sentence, Word

NORMAL_LENGTH = "1.0"
SLOW_LENGTH = "1.5"          # higher = slower speech

# --- Post-processing tunables (taste-adjust here) ---
TARGET_PEAK_DB = -2.0       # leave headroom; avoids the clipping harshness
SHELF_FREQ = 3000.0         # Hz: high-shelf corner
SHELF_GAIN_DB = 5.0         # brightness/clarity boost
SHELF_SLOPE = 0.7
FADE_MS = 10                # fade in/out to kill clicks
PAD_MS = 30                 # small silence pad head/tail
SILENCE_DB = -45.0          # threshold for trimming dead air


def _high_shelf(x, sr, f0, gain_db, S):
    """RBJ high-shelf biquad."""
    A = 10 ** (gain_db / 40.0)
    w0 = 2 * np.pi * f0 / sr
    cw, sw = np.cos(w0), np.sin(w0)
    alpha = sw / 2 * np.sqrt((A + 1 / A) * (1 / S - 1) + 2)
    b0 = A * ((A + 1) + (A - 1) * cw + 2 * np.sqrt(A) * alpha)
    b1 = -2 * A * ((A - 1) + (A + 1) * cw)
    b2 = A * ((A + 1) + (A - 1) * cw - 2 * np.sqrt(A) * alpha)
    a0 = (A + 1) - (A - 1) * cw + 2 * np.sqrt(A) * alpha
    a1 = 2 * ((A - 1) - (A + 1) * cw)
    a2 = (A + 1) - (A - 1) * cw - 2 * np.sqrt(A) * alpha
    return signal.lfilter([b0 / a0, b1 / a0, b2 / a0], [1, a1 / a0, a2 / a0], x)


def _postprocess(path):
    with wave.open(str(path), "rb") as w:
        sr, n, ch = w.getframerate(), w.getnframes(), w.getnchannels()
        x = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float64) / 32768.0
    if ch > 1:
        x = x[::ch]
    if x.size == 0:
        return
    # trim silence
    thr = 10 ** (SILENCE_DB / 20.0)
    nz = np.where(np.abs(x) > thr)[0]
    if len(nz):
        pad = int(0.01 * sr)
        x = x[max(0, nz[0] - pad): nz[-1] + pad]
    # EQ
    x = _high_shelf(x, sr, SHELF_FREQ, SHELF_GAIN_DB, SHELF_SLOPE)
    # fades
    fade = int(FADE_MS / 1000 * sr)
    if len(x) > 2 * fade and fade > 0:
        x[:fade] *= np.linspace(0, 1, fade)
        x[-fade:] *= np.linspace(1, 0, fade)
    # pad
    pad = np.zeros(int(PAD_MS / 1000 * sr))
    x = np.concatenate([pad, x, pad])
    # peak-normalize with headroom
    peak = np.max(np.abs(x))
    if peak > 0:
        x = x / peak * (10 ** (TARGET_PEAK_DB / 20.0))
    x = np.clip(x, -1.0, 1.0)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


class Command(BaseCommand):
    help = "Render Piper TTS audio (normal + slow) for all Words and Sentences, with a clarity post-pass."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Re-render existing files.")
        parser.add_argument("--no-postprocess", action="store_true",
                            help="Render raw Piper audio without the EQ/normalize pass.")

    def handle(self, *args, **options):
        model = settings.PIPER_MODEL
        if not model or not Path(model).exists():
            raise CommandError(
                f"Piper model not found at PIPER_MODEL='{model}'. "
                "Set PIPER_MODEL in .env to the fa_IR .onnx path."
            )
        out_dir = Path(settings.MEDIA_ROOT) / "audio"
        out_dir.mkdir(parents=True, exist_ok=True)
        post = not options["no_postprocess"]

        items = [(w.audio_key, w.persian) for w in Word.objects.all()]
        items += [(s.audio_key, s.persian) for s in Sentence.objects.all()]

        made = 0
        for key, text in items:
            for suffix, length in (("", NORMAL_LENGTH), ("-slow", SLOW_LENGTH)):
                target = out_dir / f"{key}{suffix}.wav"
                if target.exists() and not options["force"]:
                    continue
                self._synthesize(model, text, target, length, post)
                made += 1
                self.stdout.write(f"  ✓ {target.name}")

        self.stdout.write(self.style.SUCCESS(
            f"Generated {made} audio file(s) in {out_dir}"
            + ("" if post else " (raw, no post-processing)")))

    def _synthesize(self, model, text, target, length, post):
        cmd = ["piper", "--model", model, "--length-scale", length, "--output_file", str(target)]
        if post:
            cmd.insert(-2, "--no-normalize")  # we normalize ourselves with headroom
        try:
            subprocess.run(cmd, input=text.encode("utf-8"), check=True, capture_output=True)
        except FileNotFoundError as exc:
            raise CommandError("`piper` CLI not found on PATH. Install piper-tts.") from exc
        except subprocess.CalledProcessError as exc:
            raise CommandError(f"Piper failed for '{text}': {exc.stderr.decode(errors='ignore')}") from exc
        if post:
            _postprocess(target)
