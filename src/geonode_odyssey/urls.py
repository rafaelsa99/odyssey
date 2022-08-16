# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2017 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

from django.conf.urls import url, include
from django.views.generic import TemplateView
from django.urls import include, path
from geonode.urls import urlpatterns
from geonode.base import register_url_event
from . import views

urlpatterns += [
    url(r'^archaeology/', include('archaeology.urls')),
    path("select2/", include("django_select2.urls")),
    path('about/project', TemplateView.as_view(template_name='about_project.html'), name="about_project"),
]

urlpatterns = [
    url(r'^/?$',
        views.index,
        name='home'),
 ] + urlpatterns
