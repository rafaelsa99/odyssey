from django.urls import path
from . import views

#TEMPLATE TAGGING


urlpatterns = [
    path('', views.index, name='index'),
    path('', views.login_user, name= 'login'),
    path('', views.logout_user, name= 'logout'),
    path('landing_app', views.info, name= 'info'),

    ]
