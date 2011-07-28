from django.conf.urls.defaults import patterns, url
from magriculture.fncs import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^farmers/$', views.farmers, name='farmers'),
    url(r'^farmers/new/$', views.farmer_new, name='farmer_new'),
    url(r'^farmers/(?P<farmer_pk>\d+)/$', views.farmer, name='farmer'),
    url(r'^farmers/(?P<farmer_pk>\d+)/profile/', views.farmer_profile, name='farmer_profile'),
    url(r'^farmers/(?P<farmer_pk>\d+)/sales/$', views.farmer_sales, name='farmer_sales'),
    url(r'^farmers/(?P<farmer_pk>\d+)/sales/new/$', views.farmer_new_sale, name='farmer_new_sale'),
    url(r'^farmers/(?P<farmer_pk>\d+)/sales/detail/$', views.farmer_new_sale_detail, name='farmer_new_sale_detail'),
    url(r'^farmers/(?P<farmer_pk>\d+)/sales/(?P<sale_pk>\d+)/$', views.farmer_sale, name='farmer_sale'),
    url(r'^farmers/(?P<farmer_pk>\d+)/messages/$', views.farmer_messages, name='farmer_messages'),
    url(r'^farmers/(?P<farmer_pk>\d+)/messages/new/$', views.farmer_new_message, name='farmer_new_message'),
    url(r'^farmers/(?P<farmer_pk>\d+)/notes/$', views.farmer_notes, name='farmer_notes'),
    url(r'^farmers/(?P<farmer_pk>\d+)/notes/new/$', views.farmer_new_note, name='farmer_new_note'),
    url(r'^farmers/add/$', views.farmer_add, name='farmer_add'),
    url(r'^farmers/add/$', views.farmer_add, name='farmer_add'),
    url(r'^messages/$', views.list_messages, name='messages'),
    url(r'^sales/$', views.sales, name='sales'),
    url(r'^sales/crops/$', views.sales_crops, name='sales_crops'),
    url(r'^sales/agents/$', views.sales_agents, name='sales_agents'),
    url(r'^sales/agents/breakdown/$', views.sales_agent_breakdown, name='sales_agent_breakdown'),
    url(r'^todo/.*', views.todo, name='todo'),
)

