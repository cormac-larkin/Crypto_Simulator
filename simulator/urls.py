from django.urls import path

from . import views

urlpatterns = [
path("", views.index, name="index"),
path("landing", views.landing, name="landing"),
path("login", views.login_view, name="login"),
path("register", views.register, name="register"),
path("logout", views.logout_view, name="logout"),
path("browse", views.browse, name="browse"),
path("<str:coin_id>", views.coin_info, name="coin_info")
]