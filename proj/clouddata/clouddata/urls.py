"""qclouddata URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from operation import views as operation_views
from operation.qcloudApi import GetRegion, GetProject, GetInstances


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^q/v1/region/$', GetRegion.as_view()),
    url(r'^q/v1/project/$', GetProject.as_view()),
    url(r'^q/v1/instances/$', GetInstances.as_view()),

    url(r'^$', operation_views.index, name='index'),
    url(r'^login/$', operation_views.login, name='login'),
    url(r'^search/$', operation_views.search, name='search'),
    url(r'^sync/$', operation_views.syncQcloud, name='sync'),
    url(r'^fluxpercentage/$', operation_views.fluxpercentage, name='fluxpercentage'),
    url(r'^platpercentage/$', operation_views.platpercentage, name='platpercentage'),
    url(r'^awscost/$', operation_views.awsCost, name='awscost'),
    url(r'^othercost/$', operation_views.qcloudOtherCost, name='othercost'),
    url(r'^otherplatcost/$', operation_views.otherPlatCost, name='otherplatcost'),
    url(r'^bigdata/$', operation_views.bigData, name='bigdata'),

    url(r'^cost/', include('operation.urls')),
]
