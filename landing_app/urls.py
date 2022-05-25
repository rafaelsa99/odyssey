from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('', views.login_user, name= 'login'),
    path('', views.logout_user, name= 'logout'),

    ]