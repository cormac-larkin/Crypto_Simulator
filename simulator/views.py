from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse

import simulator
from .forms import SignUpForm

# Create your views here.

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "simulator/register.html", {
                "message": "Passwords must match.", "form": SignUpForm
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "simulator/register.html", {
                "message": "Username already taken.", "form": SignUpForm
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "simulator/register.html", {
            "form": SignUpForm
        })


def login_view(request):    
    if request.method == "POST":
         # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "simulator/login.html", {
                "message": "Invalid username and/or password.", "form": SignUpForm
            })
    else:
        return render(request, "simulator/login.html", {
            "form": SignUpForm
        })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


@login_required(login_url= "/login")
def index(request):
    return render(request, "simulator/index.html")