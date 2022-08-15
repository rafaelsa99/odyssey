from ast import And
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.db.models import Q
from .forms import MetricForm, OccurrenceForm, SiteForm, MetricFormSetHelper
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Metric, Occurrence, Site
from django.db.models import ProtectedError
from django.core.management import execute_from_command_line
from django.forms import modelformset_factory
from django.contrib.gis.geos import Polygon
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def list_sites(request):
    if 'searchBy' in request.GET and request.GET['searchBy'] == "extent":
        bbox_coordinates = request.GET['coordinates'].split(",")
        bbox = Polygon.from_bbox((bbox_coordinates[0],bbox_coordinates[1],bbox_coordinates[2],bbox_coordinates[3]))
        sites_list = Site.objects.filter(Q(location__intersects=bbox) | Q(surrounding_polygon__intersects=bbox))
    elif 'text' in request.GET and request.GET['text'] != "":
        text = request.GET['text']
        search_by = request.GET['searchBy']
        if not search_by or search_by == "name":
            sites_list = Site.objects.filter(name__icontains=text)
        elif search_by == "national_site_code":
            try:
                code = int(text)
                sites_list = Site.objects.filter(national_site_code__exact=code)
            except ValueError:
                sites_list = Site.objects.none()
        elif search_by == "parish":
            sites_list = Site.objects.filter(parish__icontains=text)
        elif search_by == "attributes":
            sites_list = Site.objects.filter(attribute_site__value__icontains=text)
    else:
        sites_list = Site.objects.all()
    if 'orderBy' in request.GET:
        orderBy = request.GET['orderBy']
        if orderBy == "recent":
            sites_list = sites_list.order_by('-id')
        elif orderBy == "older":
            sites_list = sites_list.order_by('id')
        elif orderBy == "name_asc":
            sites_list = sites_list.order_by('name')
        elif orderBy == "name_desc":
            sites_list = sites_list.order_by('-name')
        elif orderBy == "code_asc":
            sites_list = sites_list.order_by('national_site_code')
        elif orderBy == "code_desc":
            sites_list = sites_list.order_by('-national_site_code')
    page = request.GET.get('page', 1)
    paginator = Paginator(sites_list, 10)
    try:
        sites = paginator.page(page)
    except PageNotAnInteger:
        sites = paginator.page(1)
    except EmptyPage:
        sites = paginator.page(paginator.num_pages)
    path = ''
    path += "%s" % "&".join(["%s=%s" % (key, value) for (key, value) in request.GET.items() if not key=='page' ])
    context = {
        'sites': sites,
        'values': request.GET,
        'count': sites_list.count(),
        'path': path,
        }
    return render(request, "archaeology/list_sites.html", context=context)

@login_required
def view_site(request, pk):
    try:
        site = Site.objects.get(id=pk)
    except Site.DoesNotExist:
        raise Http404("Site does not exist")
    occurrences = site.occurrence_set.all()
    context = {
        'site': site,
        'occurrences': occurrences,
    }
    return render(request, "archaeology/site_detail.html", context=context)

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
def list_occurrences(request):
    if 'searchBy' in request.GET and request.GET['searchBy'] == "extent":
        bbox_coordinates = request.GET['coordinates'].split(",")
        bbox = Polygon.from_bbox((bbox_coordinates[0],bbox_coordinates[1],bbox_coordinates[2],bbox_coordinates[3]))
        occurrences_list = Occurrence.objects.filter(Q(position__intersects=bbox) | Q(bounding_polygon__intersects=bbox))
    elif 'text' in request.GET and request.GET['text'] != "":
        text = request.GET['text']
        search_by = request.GET['searchBy']
        if not search_by or search_by == "designation":
            occurrences_list = Occurrence.objects.filter(Q(designation__icontains=text) | Q(acronym__icontains=text) | Q(toponym__icontains=text))
        elif search_by == "site":
            try:
                code = int(text)
                occurrences_list = Occurrence.objects.filter(site__national_site_code__exact=code)
            except ValueError:
                occurrences_list = Occurrence.objects.filter(site__name__icontains=text)
        elif search_by == "owner":
            occurrences_list = Occurrence.objects.filter(owner__icontains=text)
        elif search_by == "attributes":
            occurrences_list = Occurrence.objects.filter(attribute_occurrence__value__icontains=text)
    elif 'searchBy' in request.GET and request.GET['searchBy'] == "altitude" and request.GET['min_alt'] != "" and request.GET['max_alt'] != "":
        try:
            min_alt = int(request.GET['min_alt'])
            max_alt = int(request.GET['max_alt'])
            occurrences_list = Occurrence.objects.filter(Q(altitude__gte=min_alt) & Q(altitude__lte=max_alt))
        except ValueError:
            occurrences_list = Occurrence.objects.none()
    else:
        occurrences_list = Occurrence.objects.all()
    if 'orderBy' in request.GET:
        orderBy = request.GET['orderBy']
        if orderBy == "recent":
            occurrences_list = occurrences_list.order_by('-id')
        elif orderBy == "older":
            occurrences_list = occurrences_list.order_by('id')
        elif orderBy == "name_asc":
            occurrences_list = occurrences_list.order_by('designation')
        elif orderBy == "name_desc":
            occurrences_list = occurrences_list.order_by('-designation')
        elif orderBy == "site_asc":
            occurrences_list = occurrences_list.order_by('site__name')
        elif orderBy == "site_desc":
            occurrences_list = occurrences_list.order_by('-site__name')
    page = request.GET.get('page', 1)
    paginator = Paginator(occurrences_list, 10)
    try:
        occurrences = paginator.page(page)
    except PageNotAnInteger:
        occurrences = paginator.page(1)
    except EmptyPage:
        occurrences = paginator.page(paginator.num_pages)
    path = ''
    path += "%s" % "&".join(["%s=%s" % (key, value) for (key, value) in request.GET.items() if not key=='page' ])
    context = {
        'occurrences': occurrences,
        'values': request.GET,
        'count': occurrences_list.count(),
        'path': path,
        }
    return render(request, "archaeology/list_occurrences.html", context=context)


@login_required
def view_occurrence(request, pk):
    try:
        occurrence_instance = Occurrence.objects.get(id=pk)
    except Occurrence.DoesNotExist:
        raise Http404("Occurrence does not exist")
    metrics = occurrence_instance.metric_set.all()
    context = {
        'occurrence': occurrence_instance,
        'metrics': metrics,
    }
    return render(request, "archaeology/occurrence_detail.html", context=context)

@login_required
def create_occurrence(request, pk):
    try:
        site = Site.objects.get(id=pk)
    except Site.DoesNotExist:
        raise Http404("Site does not exist")
    form = OccurrenceForm(request.POST or None, initial={'site':site})
    MetricFormset = modelformset_factory(Metric, form=MetricForm, extra=3)
    formset = MetricFormset(queryset=Metric.objects.none())
    helper = MetricFormSetHelper()
    if form.is_valid():
        occurrence = form.save(commit=False)
        occurrence.added_by = request.user
        occurrence.site = site
        occurrence.save()
        form.save_m2m()
        metric_formset  = MetricFormset(request.POST)
        if metric_formset.is_valid():
            for metric_form in metric_formset.forms:
                if all([metric_form.is_valid(), metric_form.cleaned_data != {}]):
                    metric = metric_form.save(commit=False)
                    metric.occurrence = occurrence
                    metric.save()
        messages.success(request, "Occurrence created successfully.")
        execute_from_command_line(["../manage_dev.sh", "updatelayers", "-s", "archaeology"])
        return redirect(occurrence.get_absolute_url())
    context = {
        'form': form,
        'site':site,
        'formset':formset,
        'helper': helper,
    }
    return render(request, "archaeology/occurrence_form.html", context=context)

@login_required
def update_occurrence(request, pk):
    try:
        occurrence_instance = Occurrence.objects.get(id=pk)
    except Occurrence.DoesNotExist:
        raise Http404("Occurrence does not exist")
    form = OccurrenceForm(request.POST or None, instance=occurrence_instance)
    MetricFormset = modelformset_factory(Metric, form=MetricForm, extra=1, can_delete=True)
    formset = MetricFormset(queryset=Metric.objects.filter(occurrence=occurrence_instance))
    helper = MetricFormSetHelper()
    if form.is_valid():
        form.save()
        metric_formset  = MetricFormset(request.POST)
        if metric_formset.is_valid():
            for metric_form in metric_formset.forms:
                if all([metric_form.is_valid(), metric_form.cleaned_data != {}]):
                    if metric_form.cleaned_data.get("DELETE") == True:
                        if metric_form.cleaned_data.get("id") != None:
                            metric_object = Metric.objects.get(id=int(metric_form.cleaned_data["id"].id))
                            metric_object.delete()
                    else:
                        metric = metric_form.save(commit=False)
                        metric.occurrence = occurrence_instance
                        metric.save()
        messages.success(request, "Changes saved successfully.")
        execute_from_command_line(["../manage_dev.sh", "updatelayers", "-s", "archaeology"])
        return redirect(occurrence_instance.get_absolute_url())
    context = {
        'form': form,
        'occurrence': occurrence_instance,
        'formset':formset,
        'helper': helper,
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
