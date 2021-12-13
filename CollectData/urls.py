"""CollectData URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from web import views

urlpatterns = [
    #path('admin/', admin.site.urls),
    #path('login/', views.login),
    url(r'^LogInfo', views.LogInfo, name='LogInfo'),
    url(r'^PhoneBook', views.PhoneBook, name='PhoneBook'),
    url(r'^PhoneCall', views.PhoneCall, name='PhoneCall'),
    url(r'^SmsCall', views.SmsCall, name='SmsCall'),
    url(r'^Gps', views.Gps, name='Gps'),
    url(r'^PowerInfo', views.PowerInfo, name='PowerInfo'),
    url(r'^Question', views.Question, name='Question'),
    url(r'^Morning', views.Morning, name='Morning'),
    url(r'^Night', views.Night, name='Night'),
    url(r'^Behavior', views.Behavior, name='Behavior'),

]
