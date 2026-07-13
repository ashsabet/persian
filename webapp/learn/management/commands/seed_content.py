"""
Seed Section 0 — the Persian alphabet — from the recorded native-speaker clips
(voice: Shahrzad). Reads learn/data/alphabet.csv and builds one lesson per
letter (name -> sound -> example words), referencing the recorded audio keys.
The audio files (name-*.wav, sound-*.wav, word-*-*.wav) are the human recordings
placed under MEDIA_ROOT/audio (see DEPLOY). Rebuilds all content on each run.

    python manage.py seed_content
"""
import csv
import random
from collections import OrderedDict
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from learn.models import Exercise, Lesson, Section, Unit

DATA = Path(settings.BASE_DIR) / "learn" / "data" / "alphabet.csv"
VOICE = "Shahrzad"
LETTERS_PER_UNIT = 4


def load_letters():
    letters = OrderedDict()
    with open(DATA, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            g = r["letter"]
            L = letters.setdefault(g, {"glyph": g, "name": None, "sound": None, "words": []})
            e = {"key": r["audio_key"], "fa": r["persian"],
                 "tr": r["transliteration"], "en": r["english_or_note"]}
            t = r["type"]
            if t == "name":
                L["name"] = e
            elif t == "sound":
                L["sound"] = e
            else:
                L["words"].append(e)
    return list(letters.values())


class Command(BaseCommand):
    help = "Seed the Persian alphabet (Section 0) from recorded Shahrzad clips."

    @transaction.atomic
    def handle(self, *args, **options):
        letters = load_letters()
        glyphs = [L["glyph"] for L in letters]
        all_word_fa = [w["fa"] for L in letters for w in L["words"]]
        all_word_en = list({w["en"] for L in letters for w in L["words"]})
        rng = random.Random(42)

        def glyph_opts(correct):
            opts = [correct] + rng.sample([g for g in glyphs if g != correct], 3)
            return [{"text": o, "correct": o == correct} for o in opts]

        def word_opts(correct_fa):
            opts = [correct_fa] + rng.sample([w for w in all_word_fa if w != correct_fa], 3)
            return [{"text": o, "correct": o == correct_fa} for o in opts]

        def en_tokens(correct_en):
            pool = [e for e in all_word_en if e != correct_en]
            toks = [correct_en] + rng.sample(pool, min(3, len(pool)))
            rng.shuffle(toks)
            return toks

        # Rebuild only the alphabet section, so seeding it never wipes the
        # vocabulary sections (seed_curriculum) or their learners' progress.
        Section.objects.filter(slug="script").delete()
        sec = Section.objects.create(slug="script", order=0, title="The Persian Script",
                                     description="Learn to read and pronounce all 32 letters.")

        unit = None
        for li, L in enumerate(letters):
            if li % LETTERS_PER_UNIT == 0:
                ui = li // LETTERS_PER_UNIT
                grp = "".join(x["glyph"] for x in letters[li:li + LETTERS_PER_UNIT])
                unit = Unit.objects.create(section=sec, order=ui + 1,
                                           slug=f"u{ui + 1}-script", title=f"Unit {ui + 1} · {grp}")
            g, name, sound, words = L["glyph"], L["name"], L["sound"], L["words"]
            slug = name["key"][len("name-"):]
            lesson = Lesson.objects.create(unit=unit, order=li + 1, slug=f"ltr-{slug}",
                                           title=f"{g} — {name['tr']}", show_transliteration=True)
            exs = []
            exs.append(("speak", {
                "instruction": f"This is the letter {g}. Its name is “{name['tr']}”. Listen and repeat.",
                "prompt_fa": g, "translit": name["tr"], "english": "the letter's name", "audio": name["key"]}))
            exs.append(("listen", {"instruction": "Which letter has this name?",
                                   "audio": name["key"], "options": glyph_opts(g)}))
            exs.append(("listen", {"instruction": "Which letter makes this sound?",
                                   "audio": sound["key"], "options": glyph_opts(g)}))
            for w in words[:2]:
                exs.append(("listen", {"instruction": "Tap the word you hear.",
                                       "audio": w["key"], "options": word_opts(w["fa"])}))
            w0 = words[0]
            exs.append(("translate", {"instruction": "What does this word mean?", "direction": "fa_en",
                                      "prompt_fa": w0["fa"], "translit": w0["tr"], "audio": w0["key"],
                                      "answer": w0["en"], "tokens": en_tokens(w0["en"])}))
            for i, (kind, payload) in enumerate(exs, 1):
                payload["voice"] = VOICE
                Exercise.objects.create(lesson=lesson, order=i, kind=kind, payload=payload)

        demo, created = User.objects.get_or_create(username="demo", defaults={"email": "demo@example.com"})
        if created:
            demo.set_password("persian123")
            demo.save()

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {Section.objects.count()} section, {Unit.objects.count()} units, "
            f"{Lesson.objects.count()} lessons, {Exercise.objects.count()} exercises (voice: {VOICE})."))
