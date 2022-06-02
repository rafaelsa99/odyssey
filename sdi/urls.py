from django.urls import path
from . import views

urlpatterns = [
    path('addsite/', views.add_site, name='addsite'),
    path('search/', views.search, name='search'),
    ]
 