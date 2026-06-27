"""
Data model for the Persian learning app (MVP vertical slice).

Content hierarchy:  Section -> Unit -> Lesson -> Exercise
Vocabulary:         Word, Sentence (each carries an audio key for the Piper pipeline)
Per-user state:     Profile (streak), UserLessonProgress

Deliberately light-touch: streaks only. No XP / leaderboards / leagues / crowns.
"""
from __future__ import annotations

from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Section(models.Model):
    """Top-level grouping, e.g. 'The Persian Script'."""
    order = models.PositiveIntegerField(default=0)
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return f"{self.order}. {self.title}"


class Unit(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="units")
    order = models.PositiveIntegerField(default=0)
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=120)

    class Meta:
        ordering = ["section__order", "order"]

    def __str__(self) -> str:
        return f"{self.section.title} / {self.title}"


class Lesson(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="lessons")
    order = models.PositiveIntegerField(default=0)
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=120)
    # Fading training wheels: show Latin transliteration on early lessons, off later.
    show_transliteration = models.BooleanField(default=True)

    class Meta:
        ordering = ["unit__section__order", "unit__order", "order"]

    def __str__(self) -> str:
        return self.title

    @property
    def exercise_count(self) -> int:
        return self.exercises.count()


class Word(models.Model):
    persian = models.CharField(max_length=120)
    transliteration = models.CharField(max_length=120, blank=True)
    english = models.CharField(max_length=120)
    # Key used to locate the generated audio file: media/audio/<audio_key>.ogg
    audio_key = models.SlugField(max_length=80, unique=True)
    image = models.CharField(
        max_length=200, blank=True,
        help_text="Relative path under static/, e.g. learn/img/water.jpg",
    )
    source = models.CharField(max_length=120, blank=True)
    license = models.CharField(max_length=120, blank=True)

    def __str__(self) -> str:
        return f"{self.persian} ({self.english})"


class Sentence(models.Model):
    persian = models.CharField(max_length=300)
    transliteration = models.CharField(max_length=300, blank=True)
    english = models.CharField(max_length=300)
    audio_key = models.SlugField(max_length=80, unique=True)
    source = models.CharField(max_length=120, blank=True)
    license = models.CharField(max_length=120, blank=True)

    def __str__(self) -> str:
        return self.persian


class Exercise(models.Model):
    """
    A generic exercise. `kind` selects the template/checker; `payload` (JSON)
    holds the prompt, options, and correct answer for that kind.
    """
    class Kind(models.TextChoices):
        MULTIPLE_CHOICE = "mc", "Multiple choice"
        TRANSLATE = "translate", "Translate (word bank)"
        LISTEN = "listen", "Listening"
        SCRIPT = "script", "Script drill"
        SPEAK = "speak", "Speak (listen & repeat)"

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="exercises")
    order = models.PositiveIntegerField(default=0)
    kind = models.CharField(max_length=20, choices=Kind.choices)
    payload = models.JSONField(default=dict)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return f"{self.lesson.slug} #{self.order} [{self.kind}]"

    # --- Answer checking -------------------------------------------------
    def check_answer(self, submitted) -> bool:
        """Return True if `submitted` is correct for this exercise."""
        p = self.payload or {}
        if self.kind in {self.Kind.MULTIPLE_CHOICE, self.Kind.LISTEN, self.Kind.SCRIPT}:
            # Options are [{text, correct}]; submitted is the chosen option's TEXT,
            # so checking is independent of display order (options are shuffled).
            correct = next((o.get("text") for o in p.get("options", []) if o.get("correct")), None)
            return correct is not None and _normalize(submitted) == _normalize(correct)
        if self.kind == self.Kind.TRANSLATE:
            return _normalize(submitted) == _normalize(p.get("answer", ""))
        if self.kind == self.Kind.SPEAK:
            # Self-graded: always accepted when the learner confirms.
            return True
        return False


def _normalize(text: str) -> str:
    return " ".join(str(text).strip().lower().split())


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    streak_count = models.PositiveIntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)
    daily_goal_lessons = models.PositiveIntegerField(default=1)
    hearts_enabled = models.BooleanField(default=False)  # optional, off by default
    words_learned = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f"Profile<{self.user.username}>"

    def register_activity(self) -> None:
        """Update the daily streak when the learner completes activity today."""
        today = timezone.localdate()
        if self.last_active_date == today:
            return  # already counted today
        if self.last_active_date == today - timedelta(days=1):
            self.streak_count += 1
        else:
            self.streak_count = 1
        self.last_active_date = today
        self.save(update_fields=["streak_count", "last_active_date"])


class UserLessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="progress")
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "lesson")

    def __str__(self) -> str:
        return f"{self.user.username} · {self.lesson.slug} · {'done' if self.completed else 'open'}"
