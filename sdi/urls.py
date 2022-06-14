from django.urls import path
from . import views

urlpatterns = [
    path('addsite/', views.create_site, name='addsite'),
    path('search/', views.search, name='search'),
    path('sites/', views.list_sites, name='list_sites'),
    path('site/<int:pk>/', views.update_site, name='update_site'),
    path('delete_site/<int:pk>/', views.delete_site, name='delete_site'),
    path('create_occurrence/<int:pk>/', views.create_occurrence, name='create_occurrence'),
    path('update_occurrence/<int:pk>/', views.update_occurrence, name='update_occurrence'),
    path('delete_occurrence/<int:pk>/', views.delete_occurrence, name='delete_occurrence'),
    ]
 