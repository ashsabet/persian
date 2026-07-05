"""
Copy the committed recorded audio clips (learn/audio/*.wav) into MEDIA_ROOT/audio
so Apache can serve them at /media/audio/. Run after `git pull`. Idempotent.

    python manage.py install_audio
"""
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Install committed recorded audio into MEDIA_ROOT/audio (world-readable for the web server)."

    def handle(self, *args, **options):
        src = Path(settings.BASE_DIR) / "learn" / "audio"
        dst = Path(settings.MEDIA_ROOT) / "audio"
        dst.mkdir(parents=True, exist_ok=True)
        n = 0
        for f in sorted(src.glob("*.wav")):
            target = dst / f.name
            shutil.copyfile(f, target)
            target.chmod(0o644)  # ensure Apache (www-data) can read it
            n += 1
        self.stdout.write(self.style.SUCCESS(f"Installed {n} audio clips into {dst}"))
