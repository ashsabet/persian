"""Normalize leading/trailing silence on the recorded alphabet WAV clips.

The Shahrzad recordings have a tight, uniform head (~80 ms) but an inconsistent
tail (0.16 s .. 0.93 s). This command detects where speech starts/ends via a
short-window RMS envelope and rewrites each clip with an *exact*, uniform amount
of digital silence before and after the speech, so every clip is evenly spaced.

A small guard band of real audio is kept around the detected speech so soft
consonant onsets and breathy fricative tails are never clipped; the fixed pad is
then added outside that guard. Input is 16-bit mono PCM WAV and we only slice and
pad samples (never re-encode), so it stays lossless. Run --dry-run first.

    python manage.py normalize_audio --dry-run
    python manage.py normalize_audio            # rewrites in place
"""
from __future__ import annotations

import array
import glob
import os
import wave
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

WIN_MS = 10          # RMS analysis window
REL_THRESH = 0.05    # speech = window RMS >= this fraction of the clip's peak
ABS_FLOOR = 60.0     # absolute RMS floor (16-bit range 0..32767)
GUARD_MS = 25        # real audio kept around detected speech, before the fixed pad


def _speech_bounds(samples, rate):
    """Return (start_sample, end_sample) of the speech region, or None if silent."""
    win = max(1, int(rate * WIN_MS / 1000))
    env = []
    for i in range(0, len(samples), win):
        chunk = samples[i:i + win]
        if not chunk:
            break
        s = sum(v * v for v in chunk)
        env.append((s / len(chunk)) ** 0.5)
    if not env:
        return None
    peak = max(env)
    thr = max(peak * REL_THRESH, ABS_FLOOR)
    speech_idx = [i for i, r in enumerate(env) if r >= thr]
    if not speech_idx:
        return None
    start = speech_idx[0] * win
    end = min(len(samples), (speech_idx[-1] + 1) * win)
    return start, end


class Command(BaseCommand):
    help = "Normalize leading/trailing silence on recorded alphabet WAV clips."

    def add_arguments(self, parser):
        parser.add_argument("--dir", default=None,
                            help="Audio directory (default: learn/audio).")
        parser.add_argument("--lead", type=int, default=80,
                            help="Exact silence to place before speech, ms (default 80).")
        parser.add_argument("--trail", type=int, default=150,
                            help="Exact silence to place after speech, ms (default 150).")
        parser.add_argument("--dry-run", action="store_true",
                            help="Report changes without writing files.")

    def handle(self, *args, **opts):
        audio_dir = Path(opts["dir"]) if opts["dir"] else Path(settings.BASE_DIR) / "learn" / "audio"
        lead_ms, trail_ms, dry = opts["lead"], opts["trail"], opts["dry_run"]

        files = sorted(glob.glob(str(audio_dir / "*.wav")))
        if not files:
            self.stderr.write(f"No .wav files in {audio_dir}")
            return

        changed = skipped = 0
        total_trimmed_ms = 0.0
        for path in files:
            with wave.open(path, "rb") as w:
                if w.getsampwidth() != 2 or w.getnchannels() != 1:
                    self.stderr.write(f"SKIP (not 16-bit mono): {os.path.basename(path)}")
                    skipped += 1
                    continue
                rate, n = w.getframerate(), w.getnframes()
                params = w.getparams()
                samples = array.array("h")
                samples.frombytes(w.readframes(n))

            bounds = _speech_bounds(samples, rate)
            if bounds is None:
                self.stderr.write(f"SKIP (no speech detected): {os.path.basename(path)}")
                skipped += 1
                continue

            speech_start, speech_end = bounds
            lead = int(rate * lead_ms / 1000)
            trail = int(rate * trail_ms / 1000)
            guard = int(rate * GUARD_MS / 1000)

            # Keep a guard band of the original audio around the detected speech,
            # then bookend it with exactly `lead`/`trail` ms of digital silence.
            keep_start = max(0, speech_start - guard)
            keep_end = min(n, speech_end + guard)
            core = samples[keep_start:keep_end]
            new_samples = array.array("h", bytes(lead * 2)) + core + array.array("h", bytes(trail * 2))

            old_dur = n / rate
            new_dur = len(new_samples) / rate
            delta_ms = (old_dur - new_dur) * 1000
            total_trimmed_ms += max(0.0, delta_ms)

            name = os.path.basename(path)
            self.stdout.write(
                f"{name:<28} {old_dur:5.3f}s -> {new_dur:5.3f}s  "
                f"({'-' if delta_ms >= 0 else '+'}{abs(delta_ms):4.0f} ms; "
                f"speech {(speech_end-speech_start)/rate*1000:4.0f}ms)"
            )
            changed += 1

            if not dry:
                with wave.open(path, "wb") as out:
                    out.setparams(params)
                    out.writeframes(new_samples.tobytes())

        verb = "would normalize" if dry else "normalized"
        self.stdout.write(self.style.SUCCESS(
            f"\n{verb} {changed} clip(s) to {lead_ms}ms head / {trail_ms}ms tail, "
            f"skipped {skipped}, net reclaimed ~{total_trimmed_ms/1000:.1f}s."
            + ("  (dry run — no files written)" if dry else "")
        ))
