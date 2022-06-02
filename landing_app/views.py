from django.shortcuts import render, redirect


#Authentication imports
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages



# Create your views here.

def index(request):

    return render (request, 'registration/landing.html', {})

def login_user(request):

    return render(request, 'registration/login.html', {})

def logout_user (request):

    return render (request, 'account/logged_out.html', {})


def info(request) :
    return render (request, 'registration/info.html', {})
