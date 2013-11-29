# Django
from django.conf.urls.defaults import patterns, url, include

# Project
from magriculture.fncs import views
from magriculture.fncs import api

# Third Party
from tastypie.api import Api

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^farmers/$', views.farmers, name='farmers'),
    url(r'^farmers/new/$', views.farmer_new, name='farmer_new'),
    url(r'^farmers/(?P<farmer_pk>\d+)/$', views.farmer, name='farmer'),
    url(r'^farmers/(?P<farmer_pk>\d+)/profile/', views.farmer_profile, name='farmer_profile'),
    url(r'^farmers/(?P<farmer_pk>\d+)/location/$', views.farmer_location_search, name='farmer_location_search'),
    url(r'^farmers/(?P<farmer_pk>\d+)/location/save/$', views.farmer_location_save, name='farmer_location_save'),
    url(r'^farmers/(?P<farmer_pk>\d+)/edit/', views.farmer_edit, name='farmer_edit'),
    url(r'^farmers/(?P<farmer_pk>\d+)/crops/', views.farmer_crops, name='farmer_crops'),
    url(r'^farmers/(?P<farmer_pk>\d+)/sales/$', views.farmer_sales, name='farmer_sales'),
    url(r'^farmers/(?P<farmer_pk>\d+)/sales/new/$', views.farmer_new_sale, name='farmer_new_sale'),
    url(r'^farmers/(?P<farmer_pk>\d+)/sales/detail/$', views.farmer_new_sale_detail, name='farmer_new_sale_detail'),
    url(r'^farmers/(?P<farmer_pk>\d+)/sales/(?P<sale_pk>\d+)/$', views.farmer_sale, name='farmer_sale'),
    url(r'^farmers/(?P<farmer_pk>\d+)/messages/$', views.farmer_messages, name='farmer_messages'),
    url(r'^farmers/(?P<farmer_pk>\d+)/messages/new/$', views.farmer_new_message, name='farmer_new_message'),
    url(r'^farmers/(?P<farmer_pk>\d+)/notes/$', views.farmer_notes, name='farmer_notes'),
    url(r'^farmers/(?P<farmer_pk>\d+)/notes/new/$', views.farmer_new_note, name='farmer_new_note'),
    url(r'^messages/$', views.group_messages, name='messages'),
    url(r'^messages/new/$', views.group_message_new, name='group_message_new'),
    url(r'^messages/write/$', views.group_message_write, name='group_message_write'),
    url(r'^sales/$', views.sales, name='sales'),
    url(r'^sales/crops/$', views.sales_crops, name='sales_crops'),
    url(r'^sales/agents/$', views.sales_agents, name='sales_agents'),
    url(r'^sales/agents/breakdown/$', views.sales_agent_breakdown, name='sales_agent_breakdown'),
    url(r'^market-prices/$', views.market_prices, name='market_prices'),
    url(r'^market-prices/offers/$', views.market_offers, name='market_offers'),
    url(r'^market-prices/offers/new/$', views.market_new_offer, name='market_new_offer'),
    url(r'^market-prices/offers/new/(?P<market_pk>\d+)/$', views.market_register_offer, name='market_register_offer'),
    url(r'^market-prices/offers/(?P<market_pk>\d+)/$', views.market_offer, name='market_offer'),
    url(r'^market-prices/offers/(?P<market_pk>\d+)/crops/(?P<crop_pk>\d+)/$', views.offer, name='offer'),
    url(r'^market-prices/offers/(?P<market_pk>\d+)/crops/(?P<crop_pk>\d+)/unit/(?P<unit_pk>\d+)/$', views.offer_unit, name='offer_unit'),
    url(r'^market-prices/sales/$', views.market_sales, name='market_sales'),
    url(r'^market-prices/sales/(?P<market_pk>\d+)/$', views.market_sale, name='market_sale'),
    url(r'^market-prices/sales/(?P<market_pk>\d+)/crops/(?P<crop_pk>\d+)/$', views.crop, name='crop'),
    url(r'^market-prices/sales/(?P<market_pk>\d+)/crops/(?P<crop_pk>\d+)/unit/(?P<unit_pk>\d+)/$', views.crop_unit, name='crop_unit'),
    url(r'^inventory/$', views.inventory, name='inventory'),
    url(r'^inventory/sale/$', views.inventory_sale, name='inventory_sale'),
    url(r'^inventory/sale/details/$', views.inventory_sale_details, name='inventory_sale_details'),
    url(r'^inventory/intake/$', views.inventory_intake, name='inventory_intake'),
    url(r'^inventory/intake/details/$', views.inventory_intake_details, name='inventory_intake_details'),
    url(r'^inventory/(?P<receipt_pk>\d+)/directsale/$', views.inventory_direct_sale, name='inventory_direct_sale'),
    url(r'^agents/$', views.agents, name='agents'),
    url(r'^agents/new/$', views.agent_new, name='agent_new'),
    url(r'^agents/(?P<agent_pk>\d+)/$', views.agent, name='agent'),
    url(r'^todo/.*', views.todo, name='todo'),


    url(r'^api/v1/highest_markets', api.get_highest_markets, name='api_get_highest_markets'),
)

# ==========================================================
#   API
# ==========================================================
api_resources = Api(api_name='v1')
api_resources.register(api.FarmerResource())
api_resources.register(api.AgentsResource())
api_resources.register(api.ActorResource())
api_resources.register(api.MarketResource())
api_resources.register(api.WardResource())
api_resources.register(api.DistrictResource())
api_resources.register(api.CropResource())
api_resources.register(api.UserResource())

api_resources.register(api.CropUnitResource())
api_resources.register(api.CropReceiptResource())
api_resources.register(api.TransactionResource())

# for HAProxy
urlpatterns += patterns('',
    url(r'^health/$', views.health, name='health'),
    url(r'^api/', include(api_resources.urls)),
)

