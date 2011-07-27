from django.conf.urls.defaults import patterns, include, url
from magriculture.fncs import views

urlpatterns = patterns('',
    # Examples:
    url(r'^$', views.home, name='home'),
    url(r'^farmers/$', views.farmers, name='farmers'),
    url(r'^farmers/(?P<pk>\d+)/$', views.farmer, name='farmer'),
    url(r'^farmers/add/$', views.farmer_add, name='farmer_add'),
    url(r'^todo/.*', views.todo, name='todo'),
)
