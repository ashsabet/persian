"""Staff-only admin console for managing learners.

A single place to see every learner's progress and to perform the common
account chores — send a password-reset email, change a username or email, and
unlock units — without dropping into Django's raw /admin. Gated on is_staff.
"""
from __future__ import annotations

from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.validators import validate_email
from django.shortcuts import get_object_or_404, redirect, render

from .models import Section, Unit, UserLessonProgress


def staff_required(view):
    """Allow only authenticated staff; send anonymous users to log in."""
    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper


def _course():
    """Return (sections, total_lessons) where each section carries its lesson ids."""
    sections = []
    total = 0
    for section in Section.objects.prefetch_related("units__lessons").all():
        lesson_ids = [l.id for u in section.units.all() for l in u.lessons.all()]
        total += len(lesson_ids)
        sections.append({"obj": section, "lesson_ids": lesson_ids})
    return sections, total


def _social_by_user():
    """Map user_id -> [provider, ...] if allauth is present, else empty."""
    try:
        from allauth.socialaccount.models import SocialAccount
    except Exception:
        return {}
    out = {}
    for sa in SocialAccount.objects.all():
        out.setdefault(sa.user_id, []).append(sa.provider)
    return out


@staff_required
def manage_users(request):
    sections, total_lessons = _course()

    # completed lessons per user, in one query
    done_by_user: dict[int, set[int]] = {}
    for uid, lid in UserLessonProgress.objects.filter(completed=True).values_list("user_id", "lesson_id"):
        done_by_user.setdefault(uid, set()).add(lid)
    social = _social_by_user()

    rows = []
    for user in User.objects.select_related("profile").order_by("username"):
        done = done_by_user.get(user.id, set())
        sections_completed = sum(
            1 for s in sections if s["lesson_ids"] and set(s["lesson_ids"]) <= done
        )
        profile = getattr(user, "profile", None)
        rows.append({
            "user": user,
            "streak": profile.current_streak if profile else 0,
            "lessons_done": len(done),
            "sections_completed": sections_completed,
            "providers": social.get(user.id, []),
        })

    return render(request, "learn/manage_users.html", {
        "rows": rows,
        "total_lessons": total_lessons,
        "total_sections": sum(1 for s in sections if s["lesson_ids"]),
    })


def _do_reset_password(request, user):
    if not user.email:
        messages.error(request, f"{user.username} has no email address on file — set one first.")
        return
    form = PasswordResetForm({"email": user.email})
    if not form.is_valid():
        messages.error(request, "That email address is not valid.")
        return
    form.save(
        request=request,
        use_https=request.is_secure(),
        token_generator=default_token_generator,
        from_email=settings.DEFAULT_FROM_EMAIL,
        email_template_name="registration/password_reset_email.html",
        subject_template_name="registration/password_reset_subject.txt",
    )
    messages.success(request, f"Password-reset email sent to {user.email}.")


def _do_set_username(request, user):
    new = (request.POST.get("username") or "").strip()
    if not new:
        messages.error(request, "Username cannot be blank.")
        return
    if new == user.username:
        messages.info(request, "Username unchanged.")
        return
    try:
        UnicodeUsernameValidator()(new)
    except ValidationError:
        messages.error(request, "Invalid username — letters, digits and @/./+/-/_ only.")
        return
    if User.objects.filter(username__iexact=new).exclude(pk=user.pk).exists():
        messages.error(request, f"Username “{new}” is already taken.")
        return
    old = user.username
    user.username = new
    user.save(update_fields=["username"])
    messages.success(request, f"Username changed from “{old}” to “{new}”.")


def _do_set_email(request, user):
    new = (request.POST.get("email") or "").strip()
    if new:
        try:
            validate_email(new)
        except ValidationError:
            messages.error(request, "That is not a valid email address.")
            return
    if new.lower() == (user.email or "").lower():
        messages.info(request, "Email unchanged.")
        return
    if new and User.objects.filter(email__iexact=new).exclude(pk=user.pk).exists():
        messages.error(request, f"Another account already uses {new}.")
        return
    user.email = new
    user.save(update_fields=["email"])
    messages.success(request, f"Email updated to {new or '(cleared)'}.")


def _do_unlock_units(request, user):
    ids = request.POST.getlist("units")
    valid = list(Unit.objects.filter(id__in=ids).values_list("id", flat=True))
    user.profile.unlocked_units.set(valid)
    messages.success(request, f"Saved unlocked units ({len(valid)} selected).")


_ACTIONS = {
    "reset_password": _do_reset_password,
    "set_username": _do_set_username,
    "set_email": _do_set_email,
    "unlock_units": _do_unlock_units,
}


@staff_required
def manage_user(request, user_id):
    user = get_object_or_404(User.objects.select_related("profile"), pk=user_id)

    if request.method == "POST":
        handler = _ACTIONS.get(request.POST.get("action"))
        if handler:
            handler(request, user)
        else:
            messages.error(request, "Unknown action.")
        return redirect("manage_user", user_id=user.id)

    sections, total_lessons = _course()
    done = set(
        UserLessonProgress.objects.filter(user=user, completed=True).values_list("lesson_id", flat=True)
    )
    unlocked_unit_ids = set(user.profile.unlocked_units.values_list("id", flat=True))

    # Build the section/unit tree with per-unit completion + unlock state.
    tree = []
    for section in Section.objects.prefetch_related("units__lessons").all():
        units = []
        for unit in section.units.all():
            lids = [l.id for l in unit.lessons.all()]
            done_ct = sum(1 for lid in lids if lid in done)
            units.append({
                "obj": unit,
                "lessons_total": len(lids),
                "lessons_done": done_ct,
                "complete": bool(lids) and done_ct == len(lids),
                "unlocked": unit.id in unlocked_unit_ids,
            })
        tree.append({"obj": section, "units": units})

    sections_completed = sum(
        1 for s in sections if s["lesson_ids"] and set(s["lesson_ids"]) <= done
    )
    return render(request, "learn/manage_user.html", {
        "u": user,
        "profile": user.profile,
        "streak": user.profile.current_streak,
        "lessons_done": len(done),
        "total_lessons": total_lessons,
        "sections_completed": sections_completed,
        "providers": _social_by_user().get(user.id, []),
        "tree": tree,
    })
