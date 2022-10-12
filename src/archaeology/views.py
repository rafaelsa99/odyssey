from unicodedata import name
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.db.models import Q
from .forms import MetricForm, OccurrenceForm, SiteForm, MetricFormSetHelper
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import AlgorithmExecution, AttributeChoice, Metric, Occurrence, Site
from django.core.management import execute_from_command_line
from django.forms import modelformset_factory
from django.contrib.gis.geos import Polygon
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy
import pandas
from django.db import connection
from osgeo import gdal
from geonode.layers.models import LayerFile
from django.conf import settings
from pyproj import Proj, transform
import os, json, threading, uuid, requests
from pathlib import Path
import base64
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

def updateLayers(filter):
    if filter == "store":
        #execute_from_command_line(["../manage_dev.sh", "updatelayers", "-s", "archaeology"])
        execute_from_command_line(["../manage.py", "updatelayers", "-s", "archaeology"])
    elif filter == "site":
        #execute_from_command_line(["../manage_dev.sh", "updatelayers", "-f", "site"])
        execute_from_command_line(["../manage.py", "updatelayers", "-f", "site"])
    elif filter == "occurrence":
        #execute_from_command_line(["../manage_dev.sh", "updatelayers", "-f", "occurrence"])
        execute_from_command_line(["../manage.py", "updatelayers", "-f", "occurrence"])

@login_required
def view_site(request, pk):
    try:
        site = Site.objects.get(id=pk)
    except Site.DoesNotExist:
        raise Http404(ugettext_lazy('Site does not exist'))
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
        messages.success(request, ugettext_lazy('Site and Occurrence created successfully.'))
        threading.Thread(target=updateLayers, args=("store",)).start()
        return redirect(site.get_absolute_url())
    return render(request, "archaeology/create_site.html", context=context)

@login_required
def update_site(request, pk):
    try:
        site = Site.objects.get(id=pk)
    except Site.DoesNotExist:
        raise Http404(ugettext_lazy('Site does not exist'))
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
        messages.success(request, ugettext_lazy('Changes saved successfully.'))
        threading.Thread(target=updateLayers, args=("site",)).start()
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
        raise Http404(ugettext_lazy('Site does not exist'))
    occurrences = site.occurrence_set.all()
    context = {'item': site, 'occurrences': occurrences, }  
    if request.method == "POST":
        msg = str(ugettext_lazy('Site ')) + site.name + str(ugettext_lazy(' successfully deleted.'))
        site.delete()
        messages.success(request, msg)
        threading.Thread(target=updateLayers, args=("store",)).start()
        return redirect(list_sites)
    return render(request, "archaeology/delete.html", context=context)

@login_required
def import_occurrences(request, pk):
    try:
        site_to_import = Site.objects.get(id=pk)
    except Site.DoesNotExist:
        raise Http404(ugettext_lazy('Site does not exist'))
    context = {'site': site_to_import, }  
    if request.method == "POST":
        csv_file = request.FILES["csv_file"]
        if not csv_file.name.endswith('.csv'):
            messages.error(request,'File is not CSV type')
        else:
            counter = 0
            # Reads small chunks to avoid memory errors
            for chunk in pandas.read_csv(csv_file, chunksize=50):
                for row in chunk.itertuples():
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT ST_Transform(ST_SetSRID(geom, 3763), 4326) FROM ST_Dump(%s);", [row.WKT])
                        rows = cursor.fetchall()
                        for item in rows: #Iterate over all polygons inside the Multipolygon
                            cursor.execute("SELECT ST_GeometryType(%s);", [item[0]])
                            type = cursor.fetchone()
                            name = row.Id + " " + str(row.Index)
                            if type[0] == "ST_Point":
                                new_occurrence = Occurrence(designation=name, position=item[0], site=site_to_import, added_by=request.user)
                                new_occurrence.save()
                                try:
                                    attribute = AttributeChoice.objects.get(value__icontains=row.Id)
                                    new_occurrence.attribute_occurrence.add(attribute)
                                except AttributeChoice.DoesNotExist:
                                    pass
                                counter += 1
                            elif type[0] == "ST_Polygon":
                                new_occurrence = Occurrence(designation=name, bounding_polygon=item[0], site=site_to_import, added_by=request.user)
                                new_occurrence.save()
                                try:
                                    attribute = AttributeChoice.objects.get(value__icontains=row.Id)
                                    new_occurrence.attribute_occurrence.add(attribute)
                                except AttributeChoice.DoesNotExist:
                                    pass
                                counter += 1
            msg = str(ugettext_lazy('A total of ')) + str(counter) + str(ugettext_lazy(' new occurrences were added.'))
            messages.success(request, msg)
            threading.Thread(target=updateLayers, args=("occurrence",)).start()
            return redirect(site_to_import.get_absolute_url())
    return render(request, "archaeology/import_occurrences.html", context=context)

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
        raise Http404(ugettext_lazy('Occurrence does not exist'))
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
        raise Http404(ugettext_lazy('Site does not exist'))
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
        messages.success(request, ugettext_lazy('Occurrence created successfully.'))
        threading.Thread(target=updateLayers, args=("occurrence",)).start()
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
        raise Http404(ugettext_lazy('Occurrence does not exist'))
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
        messages.success(request, ugettext_lazy('Changes saved successfully.'))
        threading.Thread(target=updateLayers, args=("occurrence",)).start()
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
        raise Http404(ugettext_lazy('Occurrence does not exist'))
    
    if request.method == "POST":
        site = occurrence.site
        msg = str(ugettext_lazy('Occurrence ')) + occurrence.designation + str(ugettext_lazy(' successfully deleted.'))
        occurrence.delete()
        messages.success(request, msg)
        threading.Thread(target=updateLayers, args=("occurrence",)).start()
        return redirect(site.get_absolute_url())
    context = {'item': occurrence}    
    return render(request, "archaeology/delete.html", context=context)

@login_required
def identification_aoi(request):
    if request.method == 'GET' and 'bbox' in request.GET:
        bbox_coordinates = request.GET['bbox']
        if bbox_coordinates:
            bbox_coordinates = request.GET['bbox'].split(",")
            request.session['bbox'] = bbox_coordinates
            return redirect(identification_layers)
        else:
            messages.warning(request, ugettext_lazy('It is required to select an area of interest on the map.'))
    return render(request, "archaeology/identification_aoi.html")

@login_required
def identification_layers(request):
    if 'bbox' not in request.session:
        return redirect(identification_aoi)
    bbox_coordinates = request.session.get('bbox')
    bbox_polygon = Polygon.from_bbox((bbox_coordinates[0],bbox_coordinates[1],bbox_coordinates[2],bbox_coordinates[3]))
    #Get only occurrences from the polygons, since the points are not useful for the ML algorithm, and with a type defined and with the information verified
    types_list = AttributeChoice.objects.filter(Q(category__name__icontains="type") | Q(category__name__icontains="tipo"))
    occurrences_list = Occurrence.objects.filter(Q(bounding_polygon__coveredby=bbox_polygon) & Q(attribute_occurrence__in=types_list) & (Q(status_occurrence__icontains="V") | Q(status_occurrence__icontains="T")))
    if not occurrences_list:
        messages.warning(request, ugettext_lazy('The area of interest that has been selected does not intersect any archaeological occurrence that can be used.'))
        return redirect(identification_aoi)
    if request.method == "POST":
        checked_layers = request.POST.getlist("layers")
        if not checked_layers:
            messages.warning(request, ugettext_lazy("No layer is selected. At least one layer must be selected."))
        else:
            #Create json with the occurrences inside the bbox
            #Necessary to aggregate all polygons of a type inside a MULTIPOLYGON and convert to SRID 3763.
            data = {}
            for type in types_list:
                with connection.cursor() as cursor:
                        cursor.execute("SELECT ST_AsText(ST_Transform(ST_Multi(ST_Union(o.bounding_polygon)), 3763)) FROM occurrence o JOIN occurrence_attribute_occurrence ot ON ot.occurrence_id = o.id AND ot.attributechoice_id = %s  WHERE ST_CoveredBy(o.bounding_polygon, ST_PolygonFromText(%s, 4326));", [type.id, bbox_polygon.wkt])
                        rows = cursor.fetchall()
                        for row in rows:
                            if row and row[0]:
                                data[type.value] = row[0]
            #Crop the selected layers with the defined bbox
            gdal.UseExceptions() # For debuging
            inProj = Proj(init='epsg:4326')
            outProj = Proj(init='epsg:3763')
            xmin,ymin = transform(inProj,outProj,bbox_coordinates[0],bbox_coordinates[1])
            xmax,ymax = transform(inProj,outProj,bbox_coordinates[2],bbox_coordinates[3])
            bbox_converted = [xmin, ymin, xmax, ymax]
            folder_path = settings.MEDIA_ROOT + "/"
            temp_folder_path = os.path.join(folder_path, "tmp")
            Path(temp_folder_path).mkdir(parents=True, exist_ok=True)
            layers = {}
            for file in checked_layers:
                file_path = os.path.join(folder_path + file)
                output_file = "{0}_{2}{1}".format(*os.path.splitext(os.path.basename(file)) + ("cropped",))
                output_file_path = os.path.join(temp_folder_path, output_file)
                ds = gdal.Open(file_path)
                #ds = gdal.Translate(output_file_path, ds, projWin = bbox, options = "-projwin_srs EPSG:4326") #Not creating the output file - using gdal.Warp instead
                ds = gdal.Warp(output_file_path, ds, outputBounds = bbox_converted)   
                ds = None # To close the dataset
                layer = base64.b64encode(open(output_file_path,'rb').read()).decode('ascii')    
                layerObj = LayerFile.objects.get(file = file)
                layers[layerObj.name] = layer
                # Delete temporary file after write in the zip file
                os.remove(output_file_path)

            execution = threading.Thread(target=execute_identification, args=(data, layers, request, bbox_polygon))
            execution.start()
            
            messages.success(request, ugettext_lazy('The automatic identification has been started, and the results will be added as soon as the identification process is finished.'))
            return redirect(executions_history)

    #Filter by file extension and geographic bbox (ll_bbox_polygon from resourcebase is already in 4326, despite the GeoTiffs are in 3763)
    files_list = LayerFile.objects.filter(Q(file__icontains=".tif") & Q(upload_session__resource__ll_bbox_polygon__intersects=bbox_polygon))
    if not files_list:
        messages.warning(request, ugettext_lazy('The area of interest that has been selected does not intersect any layer that can be used.'))
        return redirect(identification_aoi)
    context = {
        'layers': files_list,
        'occurrences': occurrences_list,
    }    
    return render(request, "archaeology/identification_layers.html", context=context)


def execute_identification(data, files, request, polygon):
    ml_webservice_url = 'http://192.168.1.65:8080' #TODO: Put the correct URl
    title = request.POST.get("name")
    checked_layers = request.POST.getlist("layers")
    purpose = request.POST.get("purpose")
    execution = AlgorithmExecution(name=title, purpose=purpose, aoi=polygon, executed_by=request.user)
    execution.save()
    for file in checked_layers:
        layer = LayerFile.objects.get(file=file)
        execution.layers_used.add(layer)

    json_data = json.dumps(data)
    files_data = json.dumps(files)
    multipleFiles = [('annotations', json_data), ('geotiff', files_data), ('purpose', purpose)]

    #TODO: Uncomment line to use the POST request.
    #response = requests.post(ml_webservice_url, data=multipleFiles)

    #TODO: Delete the following line when using the POST request. Just for testing.
    response_text = '{"Mamoa": "MULTIPOLYGON (((-29241.2906252581 241680.89583582,-29221.2441570028 241680.969808027,-29221.8359346635 241662.920589377,-29241.2166530505 241662.772644962,-29241.2906252581 241680.89583582)), ((-23757.952793673 238264.267511927,-23731.4707433579 238268.188038928,-23731.3227989427 238242.149821859,-23757.7308770502 238241.927905236,-23757.952793673 238264.267511927)))"}'

    execution.status = 'F'
    execution.save()
    
    if purpose == "inference":
        #response_text = response.text #TODO: Uncomment line when using the POST request.
        detections = json.loads(response_text)
        if detections: #Check if there is any detection
            site = Site(name=title, surrounding_polygon=polygon, added_by=request.user, created_by_execution=execution, status_site='N')
            site.save()
            counter = 0
            for key, value in detections.items():
                with connection.cursor() as cursor:
                    cursor.execute("SELECT ST_Transform(ST_SetSRID(geom, 3763), 4326) FROM ST_Dump(%s);", [value])
                    rows = cursor.fetchall()
                    for item in rows: #Iterate over all polygons inside the Multipolygon
                        cursor.execute("SELECT ST_GeometryType(%s);", [item[0]])
                        type = cursor.fetchone()
                        designation = key + " " + str(counter)
                        counter += 1
                        if type[0] == "ST_Polygon":
                            new_occurrence = Occurrence(designation=designation, bounding_polygon=item[0], site=site, added_by=request.user, algorithm_execution=execution, status_occurrence='N')
                            new_occurrence.save()
                            new_occurrence.attribute_occurrence.add(AttributeChoice.objects.get(value=key))
            threading.Thread(target=updateLayers, args=("store",)).start()

@login_required
def executions_history(request):
    if 'searchBy' in request.GET and request.GET['searchBy'] == "extent":
        bbox_coordinates = request.GET['coordinates'].split(",")
        bbox = Polygon.from_bbox((bbox_coordinates[0],bbox_coordinates[1],bbox_coordinates[2],bbox_coordinates[3]))
        executions_list = AlgorithmExecution.objects.filter(Q(aoi__intersects=bbox))
    elif 'text' in request.GET and request.GET['text'] != "":
        text = request.GET['text']
        search_by = request.GET['searchBy']
        if not search_by or search_by == "name":
            executions_list = AlgorithmExecution.objects.filter(name__icontains=text)
    else:
        executions_list = AlgorithmExecution.objects.all()
    if 'orderBy' in request.GET:
        orderBy = request.GET['orderBy']
        if orderBy == "recent":
            executions_list = executions_list.order_by('-id')
        elif orderBy == "older":
            executions_list = executions_list.order_by('id')
        elif orderBy == "name_asc":
            executions_list = executions_list.order_by('name')
        elif orderBy == "name_desc":
            executions_list = executions_list.order_by('-name')
    page = request.GET.get('page', 1)
    paginator = Paginator(executions_list, 10)
    try:
        executions = paginator.page(page)
    except PageNotAnInteger:
        executions = paginator.page(1)
    except EmptyPage:
        executions = paginator.page(paginator.num_pages)
    path = ''
    path += "%s" % "&".join(["%s=%s" % (key, value) for (key, value) in request.GET.items() if not key=='page' ])
    total_occurrences = Occurrence.objects.filter(algorithm_execution__isnull=False).count()
    not_verified_occurrences = Occurrence.objects.filter(algorithm_execution__isnull=False, status_occurrence__icontains="N").count()
    false_positive_occurrences = Occurrence.objects.filter(algorithm_execution__isnull=False, status_occurrence__icontains="F").count()
    true_positive_occurrences = Occurrence.objects.filter(algorithm_execution__isnull=False, status_occurrence__icontains="T").count()
    context = {
        'executions': executions,
        'values': request.GET,
        'count': executions_list.count(),
        'path': path,
        'total_occurrences': total_occurrences,
        'not_verified_occurrences': not_verified_occurrences,
        'false_positive_occurrences': false_positive_occurrences,
        'true_positive_occurrences': true_positive_occurrences,
        }
    return render(request, "archaeology/executions_history.html", context=context)

@login_required
def view_execution(request, pk):
    try:
        execution = AlgorithmExecution.objects.get(id=pk)
    except AlgorithmExecution.DoesNotExist:
        raise Http404(ugettext_lazy('Execution does not exist'))
    occurrences = execution.occurrence_set.all()
    layers = execution.layers_used.all()
    context = {
        'execution': execution,
        'occurrences': occurrences,
        'total_detections':occurrences.count(),
        'layers': layers,
    }
    return render(request, "archaeology/execution_detail.html", context=context)

@login_required
def delete_execution(request, pk):
    try:
        execution = AlgorithmExecution.objects.get(id=pk)
    except AlgorithmExecution.DoesNotExist:
        raise Http404(ugettext_lazy('Execution does not exist'))
    if request.method == "POST":
        msg = str(ugettext_lazy('Execution log ')) + execution.name + str(ugettext_lazy(' successfully deleted.'))
        execution.delete()
        messages.success(request, msg)
        return redirect(executions_history)
    context = {'item': execution}  
    return render(request, "archaeology/delete_execution.html", context=context)
