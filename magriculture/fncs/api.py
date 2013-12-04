"""FNCS HTTP API functions."""
# Python
import json
import hashlib
import random

# Django
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

# Project
from magriculture.fncs.models.actors import Actor, Farmer, Agent
from magriculture.fncs.models.props import Transaction, Crop, CropReceipt, CropUnit
from magriculture.fncs.models.geo import Market, Ward, District

# Thirdparty
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS, ALL
from tastypie.authorization import Authorization
from tastypie import fields


def get_highest_markets(request):
    crop_pk = request.GET.get('crop')
    limit = int(request.GET.get('limit', '10'))
    crop = get_object_or_404(Crop, pk=crop_pk)
    highest_markets = [(market.pk, market.name) for market
                       in Market.highest_markets_for(crop)[:limit]]
    return HttpResponse(json.dumps(highest_markets))


class CropUnitResource(ModelResource):
    """
    Get the Crop Unit
    ::

         url: <base_url>/api/v1/cropunit/
         url: <base_url>/api/v1/cropunit/?name=TheName
         method: GET
    """
    class Meta:
        queryset = CropUnit.objects.all()
        resource_name = "cropunit"
        list_allowed_methods = ['get']
        authorization = Authorization()
        include_resource_uri = True
        always_return_data = True
        filtering = {"name": ALL,
                     "id": ALL}
        excludes = ["created_at"]


class CropReceiptResource(ModelResource):
    """
    Get the Crop reciept
    ::

         url: <base_url>/api/v1/cropreceipt/
         url: <base_url>/api/v1/cropreceipt/?crop=TheCrop
         url: <base_url>/api/v1/cropreceipt/?unit=TheUnit
         url: <base_url>/api/v1/cropreceipt/?market=TheMarket
         url: <base_url>/api/v1/cropreceipt/?market=TheMarket&unit=TheUnit&crop=TheCrop
         method: GET
    """

    crop = fields.ForeignKey('magriculture.fncs.api.CropResource',
                             'crop',
                             full=True)

    unit = fields.ForeignKey('magriculture.fncs.api.CropUnitResource',
                             'unit',
                             full=True)

    market = fields.ForeignKey('magriculture.fncs.api.MarketResource',
                               'market',
                                full=True)

    class Meta:
        queryset = CropReceipt.objects.all()
        resource_name = "cropreceipt"
        list_allowed_methods = ['get', 'put']
        authorization = Authorization()
        include_resource_uri = True
        always_return_data = True
        filtering = {"crop": ALL_WITH_RELATIONS,
                     "unit": ALL_WITH_RELATIONS,
                     "market": ALL_WITH_RELATIONS}
        excludes = ["created_at"]


class TransactionResource(ModelResource):
    """
    Get Price History
    ::

         url: <base_url>/api/v1/transaction/
         url: <base_url>/api/v1/transaction/?crop_receipt__crop=<id>
         url: <base_url>/api/v1/transaction/?crop_receipt__crop=<id>
         url: <base_url>/api/v1/transaction/?crop_receipt__crop=<id>&crop_receipt__crop=<id>
         method: GET
    """
    crop_receipt = fields.ForeignKey(
        'magriculture.fncs.api.CropReceiptResource', 'crop_receipt', full=True)

    class Meta:
        queryset = Transaction.objects.all()
        resource_name = "transaction"
        list_allowed_methods = ['get', 'put']
        authorization = Authorization()
        include_resource_uri = True
        always_return_data = True
        filtering = {"crop_receipt": ALL_WITH_RELATIONS}
        excludes = ["created_at"]


# ==========================================================
# Tastypie APIs
# ==========================================================
class UserResource(ModelResource):
    """
    Creating the basic user profile before creating the Farmer and actor

     Step 1 - Create a User
    ================================
    "url": "<base_url>/api/v1/user/",,
    "method": "POST",
    "content_type": "application/json",
    "body": {
                "username": "27721231234",
                "first_name": "test_first_name",
                "last_name": "test_last_name"
            }


    :return: json_item_user
    """
    class Meta:
        queryset = User.objects.all()
        resource_name = "user"
        list_allowed_methods = ['post', 'get', 'put']
        authorization = Authorization()
        include_resource_uri = True
        always_return_data = True
        excludes = ['is_active', 'is_staff', 'is_superuser',
                    'date_joined', 'last_login']
        filtering = {"id": ALL,
                     "username": ALL}

    def get_object_list(self, request):
        """
        Remove super user and staff from object list for security purposes
        """
        query = super(UserResource, self).get_object_list(request)
        query = query.filter(is_staff=False).filter(is_superuser=False)
        return query

    def hydrate(self, bundle):
        """
        - Hashing the password to a random value to prevent user login
        - Setting is_staff and is_superuser to False for extra security
        """
        if "is_superuser" in bundle.data:
            bundle.data["is_superuser"] = False

        if "is_staff" in bundle.data:
            bundle.data["is_staff"] = False

        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        password_hash = hashlib.sha1(salt+bundle.data["first_name"] +
                                     bundle.data["last_name"]).hexdigest()
        bundle.data["password"] = password_hash
        return bundle

    def dehydrate(self, bundle):
        if "password" in bundle.data:
            del bundle.data["password"]

        if "is_staff" in bundle.data:
            del bundle.data["is_staff"]

        if "is_superuser" in bundle.data:
            del bundle.data["is_superuser"]

        return bundle


class FarmerResource(ModelResource):
    """
    Creating a new farmer requires 3 steps:

    Step 1 - Create a User
    ================================
    "url": "<base_url>/api/v1/user/",,
    "method": "POST",
    "content_type": "application/json",
    "body": {
                "username": "27721231234",
                "first_name": "test_first_name",
                "last_name": "test_last_name"
            }


    :return: json_item_user



    step 2 - Get post data for foriegn key associations
    ================================
    Get a Crop
    ---------------------------------
    "url": "<base_url>/api/v1/crop/?name=Crop",
    "method": "GET",

    :return: json_item_crop

    Get a ward
    ---------------------------------
    "url": "<base_url>/api/v1/ward/?name=Ward",
    "method": "GET",

    :return: json_item_ward

    Get a district
    ---------------------------------
    "url": "<base_url>/api/v1/district/?name=District",
    "method": "GET",

    :return: json_item_district

    Get a actor
    ---------------------------------
    "url": "<base_url>/api/v1/actor/?user__username=27721231234,
    "method": "GET",

    :return: json_item_actor



    step 3 - Create Farmer
    =============================================
    "url": "<base_url>/api/v1/farmer/",,
    "method": "POST",
    "content_type": "application/json",
    "body": {
                "actor": "/api/v1/actor/%s/" % json_item_actor["objects"][0]["id"],
                "agents": "",
                "crops": ["/api/v1/crop/%s/" % json_item_crop["objects"][0]["id"]],
                "districts": ["/api/v1/district/%s/" % json_item_district["objects"][0]["id"]],
                "hh_id": "",
                "id_number": "123456789",
                "markets": "",
                "participant_type": "",
                "resource_uri": "",
                "wards": ["/api/v1/ward/%s/" % json_item_ward["objects"][0]["id"]]
            }

    """
    agents = fields.ManyToManyField('magriculture.fncs.api.AgentsResource',
                                    'agents',
                                    full=True)
    actor = fields.ForeignKey('magriculture.fncs.api.ActorResource',
                              'actor',
                              full=True)

    markets = fields.ManyToManyField('magriculture.fncs.api.MarketResource',
                                     'markets',
                                     full=True)

    wards = fields.ManyToManyField('magriculture.fncs.api.WardResource',
                                   'wards',
                                   full=True)

    districts = fields.ManyToManyField(
        'magriculture.fncs.api.DistrictResource', 'districts', full=True)

    crops = fields.ManyToManyField('magriculture.fncs.api.CropResource',
                                   'crops',
                                   full=True)

    class Meta:
        queryset = Farmer.objects.all()
        resource_name = "farmer"
        list_allowed_methods = ['post', 'get', 'put']
        authorization = Authorization()
        include_resource_uri = True
        always_return_data = True


class AgentsResource(ModelResource):
    """
    Returns the agents in the system

    Get an agent
    ---------------------------------
    "url": "<base_url>/api/v1/agent/",
    "method": "GET",

    :return: json_item_agent
    """
    class Meta:
        queryset = Agent.objects.all()
        resource_name = "agent"
        authorization = Authorization()
        list_allowed_methods = ['get']
        include_resource_uri = True
        always_return_data = True


class ActorResource(ModelResource):
    """
    Returns the agents in the system

    Get an actor
    ---------------------------------
    "url": "<base_url>/api/v1/actor/",
    "url": "<base_url>/api/v1/actor/?user__username=123456789",
    "url": "<base_url>/api/v1/actor/?user__id=1",
    "method": "GET",

    :return: json_item_actor

    """
    user = fields.ToOneField("magriculture.fncs.api.UserResource",
                             'user',
                             full=True)

    class Meta:
        queryset = Actor.objects.all()
        resource_name = "actor"
        authorization = Authorization()
        list_allowed_methods = ['get']
        include_resource_uri = True
        always_return_data = True
        filtering = {"user": ALL_WITH_RELATIONS}


class MarketResource(ModelResource):
    """
    Returns the market in the system

    Get a market
    ---------------------------------
    "url": "<base_url>/api/v1/market/",
    "url": "<base_url>/api/v1/market/?name=TheName",

    "method": "GET",

    :return: json_item_market

    """
    class Meta:
        queryset = Market.objects.all()
        resource_name = "market"
        authorization = Authorization()
        list_allowed_methods = ['get']
        include_resource_uri = True
        always_return_data = True
        filtering = {"name": ALL}


class WardResource(ModelResource):
    """
    Returns the ward in the system

    Get a ward
    ---------------------------------
    "url": "<base_url>/api/v1/ward/",
    "url": "<base_url>/api/v1/ward/?name=TheName",

    "method": "GET",

    :return: json_item_ward

    """
    class Meta:
        queryset = Ward.objects.all()
        resource_name = "ward"
        authorization = Authorization()
        list_allowed_methods = ['get']
        include_resource_uri = True
        always_return_data = True
        filtering = {"name": ALL}


class DistrictResource(ModelResource):
    """
    Returns the district in the system

    Get a district
    ---------------------------------
    "url": "<base_url>/api/v1/district/",
    "url": "<base_url>/api/v1/district/?name=TheName",

    "method": "GET",`

    :return: json_item_district

    """
    class Meta:
        queryset = District.objects.all()
        resource_name = "district"
        authorization = Authorization()
        list_allowed_methods = ['get']
        include_resource_uri = True
        always_return_data = True
        filtering = {"name": ALL}


class CropResource(ModelResource):
    """
    Returns the Crop in the system

    Get a ward
    ---------------------------------
    "url": "<base_url>/api/v1/crop/",
    "url": "<base_url>/api/v1/crop/?name=TheName",

    "method": "GET",

    :return: json_item_crop

    """
    class Meta:
        queryset = Crop.objects.all()
        resource_name = "crop"
        authorization = Authorization()
        list_allowed_methods = ['get']
        include_resource_uri = True
        always_return_data = True
        filtering = {"name": ALL,
                     "id": ALL}
