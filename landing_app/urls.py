from django.urls import path
from . import views

#TEMPLATE TAGGING


urlpatterns = [
    path('', views.index, name='index'),
    path('', views.login_user, name= 'login'),
    path('info/', views.info, name= 'info'),

    ]
