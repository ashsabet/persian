"""
Generate Persian audio for every Word and Sentence using the local Piper
(Mana-Persian) voice. Produces a normal and a slow ('-slow') WAV per item under
MEDIA_ROOT/audio/. Re-runnable; skips files that already exist unless --force.

    python manage.py generate_audio
    python manage.py generate_audio --force

Requires the Piper CLI on PATH and PIPER_MODEL set to the Mana .onnx path
(see .env). This is meant to run on the server, not the web request path.
"""
import subprocess
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from learn.models import Sentence, Word

NORMAL_LENGTH = "1.0"
SLOW_LENGTH = "1.5"  # higher = slower speech


class Command(BaseCommand):
    help = "Render Piper TTS audio (normal + slow) for all Words and Sentences."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Re-render existing files.")

    def handle(self, *args, **options):
        model = settings.PIPER_MODEL
        if not model or not Path(model).exists():
            raise CommandError(
                f"Piper model not found at PIPER_MODEL='{model}'. "
                "Set PIPER_MODEL in .env to the Mana fa_IR .onnx path."
            )

        out_dir = Path(settings.MEDIA_ROOT) / "audio"
        out_dir.mkdir(parents=True, exist_ok=True)

        items = [(w.audio_key, w.persian) for w in Word.objects.all()]
        items += [(s.audio_key, s.persian) for s in Sentence.objects.all()]

        made = 0
        for key, text in items:
            for suffix, length in (("", NORMAL_LENGTH), ("-slow", SLOW_LENGTH)):
                target = out_dir / f"{key}{suffix}.wav"
                if target.exists() and not options["force"]:
                    continue
                self._synthesize(model, text, target, length)
                made += 1
                self.stdout.write(f"  ✓ {target.name}")

        self.stdout.write(self.style.SUCCESS(f"Generated {made} audio file(s) in {out_dir}"))

    def _synthesize(self, model: str, text: str, target: Path, length: str):
        """Call the Piper CLI: pipe text in, write a WAV out."""
        cmd = ["piper", "--model", model, "--length-scale", length, "--output_file", str(target)]
        try:
            subprocess.run(cmd, input=text.encode("utf-8"), check=True,
                           capture_output=True)
        except FileNotFoundError as exc:
            raise CommandError("`piper` CLI not found on PATH. Install piper-tts.") from exc
        except subprocess.CalledProcessError as exc:
            raise CommandError(f"Piper failed for '{text}': {exc.stderr.decode(errors='ignore')}") from exc
