import re
from django.shortcuts import render

from sdi.forms import SiteForm
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required(login_url='login')
def search(request):
    return render(request, "sdi/search_map.html")

@login_required(login_url='login')
def add_site(request):
    if request.method == "GET":
        form = SiteForm()
        context = {
            'form': form
        }
        return render(request, "sdi/add_site.html", context=context)
    else:
        form = SiteForm(request.POST)
        if form.is_valid():
            site = form.save()
            form = SiteForm()
        context = {
            'form': form
        }
        return render(request, "sdi/add_site.html", context=context)