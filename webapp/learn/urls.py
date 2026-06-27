from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("profile/", views.profile_view, name="profile"),
    path("lesson/<slug:slug>/", views.lesson, name="lesson"),
    path("lesson/<slug:slug>/complete/", views.lesson_complete, name="lesson_complete"),
    path("lesson/<slug:slug>/finish/", views.complete_lesson, name="complete_lesson"),
    path("exercise/<int:exercise_id>/check/", views.check, name="check"),
    # Auth
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", views.register, name="register"),
    # Password change (logged in) and reset (forgot) — Django's built-in views.
    path("password_change/", auth_views.PasswordChangeView.as_view(), name="password_change"),
    path("password_change/done/", auth_views.PasswordChangeDoneView.as_view(), name="password_change_done"),
    path("password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
]
