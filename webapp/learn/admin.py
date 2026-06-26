from django.contrib import admin

from .models import (
    Exercise,
    Lesson,
    Profile,
    Section,
    Sentence,
    Unit,
    UserLessonProgress,
    Word,
)


class UnitInline(admin.TabularInline):
    model = Unit
    extra = 0


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0


class ExerciseInline(admin.TabularInline):
    model = Exercise
    extra = 0


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("order", "title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [UnitInline]


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("__str__", "order")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "unit", "order", "show_transliteration", "exercise_count")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ExerciseInline]


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ("persian", "transliteration", "english", "audio_key")
    search_fields = ("persian", "english", "transliteration")


@admin.register(Sentence)
class SentenceAdmin(admin.ModelAdmin):
    list_display = ("persian", "english", "audio_key")
    search_fields = ("persian", "english")


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("__str__", "lesson", "kind", "order")
    list_filter = ("kind", "lesson")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "streak_count", "last_active_date", "words_learned", "hearts_enabled")


@admin.register(UserLessonProgress)
class UserLessonProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "completed", "completed_at")
    list_filter = ("completed",)
