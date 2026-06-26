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
]
