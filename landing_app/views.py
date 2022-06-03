from django.shortcuts import render, redirect


#Authentication imports
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages



# Create your views here.

def index(request):

    return render (request, 'landing/index.html', {})

def login_user(request):

    return render(request, 'registration/login.html', {})

def info(request) :
    return render (request, 'landing/info.html', {})

