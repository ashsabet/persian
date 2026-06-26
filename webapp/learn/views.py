import json

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Exercise, Lesson, Section, UserLessonProgress


def _ordered_lessons():
    return list(
        Lesson.objects.select_related("unit", "unit__section").order_by(
            "unit__section__order", "unit__order", "order"
        )
    )


@login_required
def home(request):
    """The learning path: sections -> units -> lessons, with lock/complete state."""
    lessons = _ordered_lessons()
    completed_ids = set(
        UserLessonProgress.objects.filter(user=request.user, completed=True).values_list(
            "lesson_id", flat=True
        )
    )

    # Sequential unlock: lesson is open if it's the first or the previous is done.
    unlocked_ids = set()
    prev_done = True
    current_id = None
    for lesson in lessons:
        is_open = prev_done
        if is_open:
            unlocked_ids.add(lesson.id)
        if is_open and lesson.id not in completed_ids and current_id is None:
            current_id = lesson.id
        prev_done = lesson.id in completed_ids

    sections = []
    for section in Section.objects.prefetch_related("units__lessons").all():
        units = []
        for unit in section.units.all():
            unit_lessons = []
            for lesson in unit.lessons.all():
                unit_lessons.append(
                    {
                        "obj": lesson,
                        "done": lesson.id in completed_ids,
                        "open": lesson.id in unlocked_ids,
                        "current": lesson.id == current_id,
                    }
                )
            units.append({"obj": unit, "lessons": unit_lessons})
        sections.append({"obj": section, "units": units})

    return render(request, "learn/home.html", {"sections": sections})


@login_required
def lesson(request, slug):
    lesson_obj = get_object_or_404(Lesson, slug=slug)
    exercises = [
        {"id": ex.id, "kind": ex.kind, **(ex.payload or {})}
        for ex in lesson_obj.exercises.all()
    ]
    context = {
        "lesson": lesson_obj,
        "exercises_json": json.dumps(exercises),
        "show_translit": lesson_obj.show_transliteration,
    }
    return render(request, "learn/lesson.html", context)


@login_required
@require_POST
def check(request, exercise_id):
    ex = get_object_or_404(Exercise, id=exercise_id)
    submitted = request.POST.get("answer", "")
    correct = ex.check_answer(submitted)
    p = ex.payload or {}
    # Provide the correct answer for feedback display.
    correct_answer = p.get("answer")
    if ex.kind in {ex.Kind.MULTIPLE_CHOICE, ex.Kind.LISTEN, ex.Kind.SCRIPT}:
        opts = p.get("options", [])
        correct_answer = next((o["text"] for o in opts if o.get("correct")), None)
    return JsonResponse({"correct": correct, "correct_answer": correct_answer})


@login_required
@require_POST
def complete_lesson(request, slug):
    lesson_obj = get_object_or_404(Lesson, slug=slug)
    progress, _ = UserLessonProgress.objects.get_or_create(
        user=request.user, lesson=lesson_obj
    )
    first_time = not progress.completed
    if first_time:
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()

    profile = request.user.profile
    profile.register_activity()  # updates streak

    words_added = 0
    if first_time:
        keys = set()
        for ex in lesson_obj.exercises.all():
            if ex.kind in {Exercise.Kind.TRANSLATE, Exercise.Kind.LISTEN, Exercise.Kind.SPEAK}:
                key = (ex.payload or {}).get("audio")
                if key:
                    keys.add(key)
        words_added = len(keys)
        if words_added:
            profile.words_learned += words_added
            profile.save(update_fields=["words_learned"])

    return redirect("lesson_complete", slug=slug)


@login_required
def lesson_complete(request, slug):
    lesson_obj = get_object_or_404(Lesson, slug=slug)
    # Find the next lesson in global order, if any.
    lessons = _ordered_lessons()
    next_slug = None
    for i, l in enumerate(lessons):
        if l.id == lesson_obj.id and i + 1 < len(lessons):
            next_slug = lessons[i + 1].slug
            break
    return render(
        request,
        "learn/complete.html",
        {"lesson": lesson_obj, "next_slug": next_slug, "profile": request.user.profile},
    )


@login_required
def profile_view(request):
    profile = request.user.profile
    lessons = _ordered_lessons()
    total = len(lessons)
    done = UserLessonProgress.objects.filter(user=request.user, completed=True).count()

    section_progress = []
    for section in Section.objects.prefetch_related("units__lessons").all():
        sec_lessons = [l for u in section.units.all() for l in u.lessons.all()]
        sec_ids = {l.id for l in sec_lessons}
        sec_done = UserLessonProgress.objects.filter(
            user=request.user, completed=True, lesson_id__in=sec_ids
        ).count()
        pct = round(100 * sec_done / len(sec_lessons)) if sec_lessons else 0
        section_progress.append({"title": section.title, "pct": pct})

    return render(
        request,
        "learn/profile.html",
        {
            "profile": profile,
            "lessons_done": done,
            "lessons_total": total,
            "section_progress": section_progress,
        },
    )


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})
