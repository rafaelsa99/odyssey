from django.shortcuts import render
from archaeology.models import Occurrence, Site

def index(request):
    num_sites = Site.objects.all().count()
    num_occurrences = Occurrence.objects.all().count()
    context = {
        'num_sites': num_sites,
        'num_occurrences': num_occurrences,
    }
    return render(request, "site_index.html", context=context)