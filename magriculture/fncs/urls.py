from django.conf.urls.defaults import patterns, include, url
from magriculture.fncs import views

urlpatterns = patterns('',
    # Examples:
    url(r'^$', views.home, name='home'),
    url(r'^farmers/$', views.farmers, name='farmers'),
    url(r'^farmers/(?P<farmer_pk>\d+)/$', views.farmer, name='farmer'),
    url(r'^farmers/(?P<farmer_pk>\d+)/sales/$', views.farmer_sales, name='farmer_sales'),
    url(r'^farmers/(?P<farmer_pk>\d+)/sales/new/$', views.farmer_new_sale, name='farmer_new_sale'),
    url(r'^farmers/(?P<farmer_pk>\d+)/sales/detail/$', views.farmer_new_sale_detail, name='farmer_new_sale_detail'),
    url(r'^farmers/(?P<farmer_pk>\d+)/sales/(?P<sale_pk>\d+)/$', views.farmer_sale, name='farmer_sale'),
    url(r'^farmers/add/$', views.farmer_add, name='farmer_add'),
    url(r'^farmers/add/$', views.farmer_add, name='farmer_add'),
    url(r'^todo/.*', views.todo, name='todo'),
)
