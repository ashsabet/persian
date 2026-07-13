"""Seed the spoken/vocabulary curriculum (Sections 1+) from learn/data/curriculum.py.

Non-destructive: Sections, Units, Lessons, Words and Sentences are upserted by
their stable slug/key, so re-running updates content **without** deleting user
progress (UserLessonProgress is keyed to the lesson, which survives). Only each
lesson's Exercises are rebuilt. Section 0 (the alphabet) is never touched.

Audio: every Word/Sentence becomes a `<key>.wav` when you run `generate_audio`
(local Piper gyro voice) on the server. Run order on deploy:

    python manage.py seed_curriculum
    python manage.py generate_audio     # renders the new TTS clips
"""
import random

from django.core.management.base import BaseCommand
from django.db import transaction

from learn.data.curriculum import SECTIONS
from learn.models import Exercise, Lesson, Section, Sentence, Unit, Word

VOICE = "gyro"  # Piper TTS voice for these units (alphabet uses recorded "Shahrzad")


def _opts_fa(correct, pool, rng):
    """4 Persian options (1 correct + up to 3 distinct distractors), shuffled."""
    others = [x for x in pool if x != correct]
    opts = [correct] + rng.sample(others, min(3, len(others)))
    rng.shuffle(opts)
    return [{"text": o, "correct": o == correct} for o in opts]


def _en_tokens(correct, pool, rng):
    others = [x for x in pool if x != correct]
    toks = [correct] + rng.sample(others, min(3, len(others)))
    rng.shuffle(toks)
    return toks


def _build_exercises(lesson_items, words, phrases, vocab_fa, vocab_en, rng):
    """Turn a lesson's item keys into a varied, self-contained exercise set."""
    exs = []
    word_keys = [k for k in lesson_items if k in words]
    introduced = False
    for k in lesson_items:
        if k in words:
            w = words[k]
            if not introduced:
                exs.append(("speak", {
                    "instruction": f"New word: “{w['tr']}” — {w['en']}. Listen and repeat.",
                    "prompt_fa": w["fa"], "translit": w["tr"], "english": w["en"], "audio": w["key"]}))
                introduced = True
            exs.append(("listen", {
                "instruction": "Tap the word you hear.",
                "audio": w["key"], "options": _opts_fa(w["fa"], vocab_fa, rng)}))
        else:
            p = phrases[k]
            exs.append(("speak", {
                "instruction": "Listen and repeat.",
                "prompt_fa": p["fa"], "translit": p["tr"], "english": p["en"], "audio": p["key"]}))

    # A reading-recognition item (English -> pick the Persian) and a translate-back.
    if word_keys:
        rk = rng.choice(word_keys)
        rw = words[rk]
        exs.insert(min(2, len(exs)), ("mc", {
            "instruction": f"Which word means “{rw['en']}”?",
            "options": _opts_fa(rw["fa"], vocab_fa, rng)}))
        tw = words[word_keys[0]]
        exs.append(("translate", {
            "instruction": "What does this mean?", "direction": "fa_en",
            "prompt_fa": tw["fa"], "translit": tw["tr"], "audio": tw["key"],
            "answer": tw["en"], "tokens": _en_tokens(tw["en"], vocab_en, rng)}))
    return exs


class Command(BaseCommand):
    help = "Seed/refresh the vocabulary curriculum (Sections 1+) without wiping progress."

    @transaction.atomic
    def handle(self, *args, **options):
        rng = random.Random(7)
        n_words = n_phrases = n_lessons = n_ex = 0

        for sdata in SECTIONS:
            section, _ = Section.objects.update_or_create(
                slug=sdata["slug"],
                defaults={"order": sdata["order"], "title": sdata["title"],
                          "description": sdata.get("description", "")})

            for udata in sdata["units"]:
                unit, _ = Unit.objects.update_or_create(
                    slug=udata["slug"],
                    defaults={"section": section, "order": udata["order"], "title": udata["title"]})

                words = {}
                for w in udata["words"]:
                    Word.objects.update_or_create(
                        audio_key=w["key"],
                        defaults={"persian": w["fa"], "transliteration": w["tr"],
                                  "english": w["en"], "source": "original", "license": "original"})
                    words[w["key"]] = w
                    n_words += 1

                phrases = {}
                for p in udata["phrases"]:
                    Sentence.objects.update_or_create(
                        audio_key=p["key"],
                        defaults={"persian": p["fa"], "transliteration": p["tr"],
                                  "english": p["en"], "source": "original", "license": "original"})
                    phrases[p["key"]] = p
                    n_phrases += 1

                vocab_fa = [w["fa"] for w in udata["words"]]
                vocab_en = [w["en"] for w in udata["words"]]

                for li, ldata in enumerate(udata["lessons"], start=1):
                    lesson, _ = Lesson.objects.update_or_create(
                        slug=ldata["slug"],
                        defaults={"unit": unit, "order": li, "title": ldata["title"],
                                  "show_transliteration": True})
                    # Rebuild only the exercises; the lesson row (and any progress
                    # pointing at it) is preserved.
                    lesson.exercises.all().delete()
                    exs = _build_exercises(ldata["items"], words, phrases, vocab_fa, vocab_en, rng)
                    for i, (kind, payload) in enumerate(exs, 1):
                        payload["voice"] = VOICE
                        Exercise.objects.create(lesson=lesson, order=i, kind=kind, payload=payload)
                        n_ex += 1
                    n_lessons += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seeded curriculum: {n_lessons} lessons, {n_words} words, "
            f"{n_phrases} phrases, {n_ex} exercises (voice: {VOICE}). Run generate_audio next."))
