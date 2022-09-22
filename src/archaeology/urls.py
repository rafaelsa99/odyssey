from django.urls import path
from . import views

urlpatterns = [
    path('site/create', views.create_site, name='addsite'),
    path('site', views.list_sites, name='list_sites'),
    path('site/<int:pk>', views.view_site, name='view_site'),
    path('site/<int:pk>/update', views.update_site, name='update_site'),
    path('site/<int:pk>/import', views.import_occurrences, name='import_occurrences'),
    path('site/<int:pk>/delete', views.delete_site, name='delete_site'),
    path('occurrence', views.list_occurrences, name='list_occurrences'),
    path('occurrence/<int:pk>/create', views.create_occurrence, name='create_occurrence'),
    path('occurrence/<int:pk>', views.view_occurrence, name='view_occurrence'),
    path('occurrence/<int:pk>/update', views.update_occurrence, name='update_occurrence'),
    path('occurrence/<int:pk>/delete', views.delete_occurrence, name='delete_occurrence'),
    path('identification', views.identification_aoi, name='identification_aoi'),
    path('identification/layers', views.identification_layers, name='identification_layers'),
    path('execution', views.executions_history, name='executions_history'),
    path('execution/<int:pk>', views.view_execution, name='view_execution'),
    path('execution/<int:pk>/delete', views.delete_execution, name='delete_execution'),
    ]
 