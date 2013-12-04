"""FNCS HTTP API functions."""
# Python
import json
import hashlib
import random

# Django
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

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
    Creating a user
    ::

         url: <base_url>/api/v1/user/
         method: POST
         content_type: "application/json"
         body: {
                    "username": "27721231234",
                    "first_name": "test_first_name",
                    "last_name": "test_last_name"
         }
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
        - Setting password to None on make_password so as to prevent user login
        - Setting is_staff and is_superuser to False for extra security
        """
        if "is_superuser" in bundle.data:
            bundle.data["is_superuser"] = False

        if "is_staff" in bundle.data:
            bundle.data["is_staff"] = False

        bundle.data["password"] = make_password(None)
        return bundle

    def dehydrate(self, bundle):
        """
        - Removing password from here and not exclude inorder to manually create
        a random password
        - removing is_staff and is_superuser as tasypie returns the result status
        of the original post item so if included returns their status.
        """
        if "password" in bundle.data:
            del bundle.data["password"]

        if "is_staff" in bundle.data:
            del bundle.data["is_staff"]

        if "is_superuser" in bundle.data:
            del bundle.data["is_superuser"]

        return bundle


class FarmerResource(ModelResource):
    """
    Creating a new farmer requires several:

    1. Create a User
    2. On created user filter for Actor based on user.id or msisdn
    3. Get crop data (as crop), can filter by name based on user input
    4. Get ward (as ward), can filter by name
    5. Get district (as district), can filter by name
    6. Create the farmer using above responses
    ::

        url: <base_url>/api/v1/farmer/
        method: POST
        content_type: application/json
        body: {
                    "actor": "/api/v1/actor/%s/" % actor["objects"][0]["id"],
                    "agents": "",
                    "crops": ["/api/v1/crop/%s/" % crop["objects"][0]["id"]],
                    "districts": ["/api/v1/district/%s/" % district["objects"][0]["id"]],
                    "hh_id": "",
                    "id_number": "123456789",
                    "markets": "",
                    "participant_type": "",
                    "resource_uri": "",
                    "wards": ["/api/v1/ward/%s/" % ward["objects"][0]["id"]]
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

    **Get specific Farmer based on msisdn**
    ::

        url: <base_url>/api/v1/farmer/?actor__user__username=123456789
        method: GET
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
        filtering = {"actor" : ALL_WITH_RELATIONS}


class AgentsResource(ModelResource):
    """
    Get the agents in the system
    ::

        url: <base_url>/api/v1/agent/
        method: GET
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
    Returns the actors in the system and can filter on id or msisdn as username
    ::

        url: <base_url>/api/v1/actor/
        url: <base_url>/api/v1/actor/?user__username=123456789
        url: <base_url>/api/v1/actor/?user__id=1
        method": GET

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
    Returns the market in the system and can filter by name
    ::

        url: <base_url>/api/v1/market/
        url: <base_url>/api/v1/market/?name=TheName
        method: GET
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
    Returns the ward in the system and can filter by name
    ::

        url: <base_url>/api/v1/ward/
        url: <base_url>/api/v1/ward/?name=TheName

        method: GET
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
    Returns the districts in the system and can filter by name
    ::

        url: <base_url>/api/v1/district/
        url: <base_url>/api/v1/district/?name=TheName
        method: GET

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
    Returns the Crops in the system and can filter by name
    ::

        url: <base_url>/api/v1/crop/
        url: <base_url>/api/v1/crop/?name=TheName
        method: GET
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
