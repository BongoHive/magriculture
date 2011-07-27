from django.conf.urls.defaults import patterns, include, url
from magriculture.fncs import views

urlpatterns = patterns('',
    # Examples:
    url(r'^$', views.home, name='home'),
    url(r'^todo/.*', views.todo, name='todo'),
)
