"""
Seed the database with Section 0, Unit 1 of the Persian course (the vertical slice).
Idempotent: safe to run repeatedly. Also creates a demo learner account.

    python manage.py seed_content
"""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from learn.models import Exercise, Lesson, Section, Unit, Word

# Vocabulary + letters (audio_key -> text to synthesize). Letters are stored as
# Words so the audio pipeline can render them generically.
WORDS = [
    # letters
    ("letter-a", "آ", "ā", "letter alef"),
    ("letter-be", "ب", "be", "letter be"),
    ("letter-pe", "پ", "pe", "letter pe"),
    ("letter-te", "ت", "te", "letter te"),
    # words
    ("word-ab", "آب", "āb", "water"),
    ("word-baba", "بابا", "bābā", "dad"),
    ("word-pa", "پا", "pā", "foot"),
    ("word-tab", "تب", "tab", "fever"),
]

LESSON_1 = [
    {
        "kind": "script",
        "instruction": "Tap the initial (joining) form of this letter.",
        "prompt_fa": "ب", "audio": "letter-be",
        "options": [{"text": "بـ", "correct": True}, {"text": "ـبـ"}, {"text": "ـب"}, {"text": "ب"}],
    },
    {
        "kind": "mc",
        "instruction": "Which letter makes the “p” sound?",
        "audio": "letter-pe",
        "options": [{"text": "پ", "correct": True}, {"text": "ب"}, {"text": "ت"}, {"text": "آ"}],
    },
    {
        "kind": "mc",
        "instruction": "Which letter is “t”?",
        "audio": "letter-te",
        "options": [{"text": "ت", "correct": True}, {"text": "ب"}, {"text": "پ"}, {"text": "آ"}],
    },
    {
        "kind": "listen",
        "instruction": "Tap what you hear.",
        "audio": "word-ab",
        "options": [{"text": "آب", "correct": True}, {"text": "بابا"}, {"text": "پا"}, {"text": "تب"}],
    },
    {
        "kind": "translate", "direction": "fa_en",
        "instruction": "Translate this word.",
        "prompt_fa": "آب", "translit": "āb", "audio": "word-ab",
        "answer": "water", "tokens": ["water", "father", "foot", "fever"],
    },
]

LESSON_2 = [
    {
        "kind": "mc",
        "instruction": "Which word means “water”?",
        "audio": "word-ab",
        "options": [{"text": "آب", "correct": True}, {"text": "بابا"}, {"text": "پا"}, {"text": "تب"}],
    },
    {
        "kind": "translate", "direction": "en_fa",
        "instruction": "Say “dad” in Persian.",
        "prompt_en": "dad",
        "answer": "بابا", "tokens": ["بابا", "آب", "پا", "تب"],
    },
    {
        "kind": "listen",
        "instruction": "Tap what you hear.",
        "audio": "word-baba",
        "options": [{"text": "بابا", "correct": True}, {"text": "پا"}, {"text": "تب"}, {"text": "آب"}],
    },
    {
        "kind": "speak",
        "instruction": "Listen, then say it aloud.",
        "prompt_fa": "بابا", "translit": "bābā", "english": "dad", "audio": "word-baba",
    },
    {
        "kind": "translate", "direction": "fa_en",
        "instruction": "Translate this word.",
        "prompt_fa": "پا", "translit": "pā", "audio": "word-pa",
        "answer": "foot", "tokens": ["foot", "water", "fever", "father"],
    },
]


class Command(BaseCommand):
    help = "Seed Section 0 / Unit 1 content and a demo account."

    @transaction.atomic
    def handle(self, *args, **options):
        for key, persian, translit, english in WORDS:
            Word.objects.update_or_create(
                audio_key=key,
                defaults={
                    "persian": persian, "transliteration": translit, "english": english,
                    "source": "original", "license": "project-original",
                },
            )

        section, _ = Section.objects.update_or_create(
            slug="script", defaults={"order": 0, "title": "The Persian Script",
                                     "description": "Read and write the alphabet."}
        )
        unit, _ = Unit.objects.update_or_create(
            slug="u1-first-letters", defaults={"section": section, "order": 1,
                                               "title": "Unit 1 · First letters & sounds"}
        )

        for l_order, (slug, title, payloads) in enumerate(
            [
                ("l1-letters", "Letters: ا ب پ ت", LESSON_1),
                ("l2-first-words", "First words", LESSON_2),
            ],
            start=1,
        ):
            lesson, _ = Lesson.objects.update_or_create(
                slug=slug,
                defaults={"unit": unit, "order": l_order, "title": title,
                          "show_transliteration": True},
            )
            lesson.exercises.all().delete()
            for e_order, payload in enumerate(payloads, start=1):
                kind = payload.pop("kind")
                Exercise.objects.create(lesson=lesson, order=e_order, kind=kind, payload=payload)

        demo, created = User.objects.get_or_create(
            username="demo", defaults={"email": "demo@example.com"}
        )
        if created:
            demo.set_password("persian123")
            demo.save()
            self.stdout.write(self.style.SUCCESS("Created demo account: demo / persian123"))

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {Word.objects.count()} words, "
            f"{Lesson.objects.count()} lessons, {Exercise.objects.count()} exercises."
        ))
