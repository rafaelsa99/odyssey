from django.urls import path
from . import views

urlpatterns = [
    path('site/create', views.create_site, name='addsite'),
    path('site', views.list_sites, name='list_sites'),
    path('site/<int:pk>', views.update_site, name='update_site'),
    path('site/<int:pk>/delete', views.delete_site, name='delete_site'),
    path('occurrence', views.list_occurrences, name='list_occurrences'),
    path('occurrence/<int:pk>/create', views.create_occurrence, name='create_occurrence'),
    path('occurrence/<int:pk>', views.update_occurrence, name='update_occurrence'),
    path('occurrence/<int:pk>/delete', views.delete_occurrence, name='delete_occurrence'),
    ]
 