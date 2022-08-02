from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render

from .forms import OccurrenceForm, SiteForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Occurrence, Site
from django.db.models import ProtectedError
from django.core.management import execute_from_command_line

# Create your views here.

@login_required
def list_sites(request):
    sites_list = Site.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(sites_list, 15)
    try:
        sites = paginator.page(page)
    except PageNotAnInteger:
        sites = paginator.page(1)
    except EmptyPage:
        sites = paginator.page(paginator.num_pages)
    context = {'sites': sites}
    return render(request, "archaeology/list_sites.html", context=context)

@login_required
def create_site(request):
    formSite = SiteForm(request.POST or None)
    formOccurrence = OccurrenceForm(request.POST or None)
    context = {
            'site': formSite,
            'occurrence': formOccurrence,
        }
    if all([formSite.is_valid(), formOccurrence.is_valid()]):
        site = formSite.save(commit=False)
        occurrence = formOccurrence.save(commit=False)
        site.added_by = request.user
        site.save()
        formSite.save_m2m()
        occurrence.added_by = request.user
        occurrence.site = site
        occurrence.save()
        formOccurrence.save_m2m()
        messages.success(request, "Site and Occurrence created successfully.")
        execute_from_command_line(["../manage_dev.sh", "updatelayers", "-s", "archaeology"])
        return redirect(site.get_absolute_url())
    return render(request, "archaeology/create_site.html", context=context)

@login_required
def update_site(request, pk):
    try:
        site = Site.objects.get(id=pk)
    except Site.DoesNotExist:
        raise Http404("Site does not exist")
    form = SiteForm(request.POST or None, instance=site)
    occurrences_list = site.occurrence_set.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(occurrences_list, 5)
    try:
        occurrences = paginator.page(page)
    except PageNotAnInteger:
        occurrences = paginator.page(1)
    except EmptyPage:
        occurrences = paginator.page(paginator.num_pages)
    if form.is_valid():
        form.save()
        messages.success(request, "Changes saved successfully.")
        execute_from_command_line(["../manage_dev.sh", "updatelayers", "-s", "archaeology"])
        return redirect(site.get_absolute_url())
    context = {
        'form': form,
        'site': site,
        'occurrences': occurrences,
    }
    return render(request, "archaeology/site_form.html", context=context)

@login_required
def delete_site(request, pk):
    try:
        site = Site.objects.get(id=pk)
    except Site.DoesNotExist:
        raise Http404("Site does not exist")
    context = {'item': site,}  
    if request.method == "POST":
        try:
            msg = "Site " + site.name + " successfully deleted."
            site.delete()
            messages.success(request, msg)
            execute_from_command_line(["../manage_dev.sh", "updatelayers", "-s", "archaeology"])
            return redirect(list_sites)
        except ProtectedError:
            context['error']= "Cannot delete the site, as there are still " + str(site.occurrence_set.count()) + " associated occurrence(s). Delete the associated occurrences first to be able to delete the site."
    return render(request, "archaeology/delete.html", context=context)

@login_required
def create_occurrence(request, pk):
    try:
        site = Site.objects.get(id=pk)
    except Site.DoesNotExist:
        raise Http404("Site does not exist")
    form = OccurrenceForm(request.POST or None, initial={'site':site})
    if form.is_valid():
        occurrence = form.save(commit=False)
        occurrence.added_by = request.user
        occurrence.site = site
        occurrence.save()
        messages.success(request, "Occurrence created successfully.")
        execute_from_command_line(["../manage_dev.sh", "updatelayers", "-s", "archaeology"])
        return redirect(occurrence.get_absolute_url())
    context = {
        'form': form,
        'site':site,
    }
    return render(request, "archaeology/occurrence_form.html", context=context)

@login_required
def update_occurrence(request, pk):
    try:
        occurrence = Occurrence.objects.get(id=pk)
    except Occurrence.DoesNotExist:
        raise Http404("Occurrence does not exist")
    form = OccurrenceForm(request.POST or None, instance=occurrence)
    if form.is_valid():
        form.save()
        messages.success(request, "Changes saved successfully.")
        execute_from_command_line(["../manage_dev.sh", "updatelayers", "-s", "archaeology"])
        return redirect(occurrence.get_absolute_url())
    context = {
        'form': form,
        'occurrence': occurrence,
    }
    return render(request, "archaeology/occurrence_form.html", context=context)

@login_required
def delete_occurrence(request, pk):
    try:
        occurrence = Occurrence.objects.get(id=pk)
    except Occurrence.DoesNotExist:
        raise Http404("Occurrence does not exist")
    
    if request.method == "POST":
        site = occurrence.site
        msg = "Occurrence " + occurrence.designation + " successfully deleted."
        occurrence.delete()
        messages.success(request, msg)
        execute_from_command_line(["../manage_dev.sh", "updatelayers", "-s", "archaeology"])
        return redirect(site.get_absolute_url())
    context = {'item': occurrence}    
    return render(request, "archaeology/delete.html", context=context)
