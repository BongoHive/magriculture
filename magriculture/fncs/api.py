"""FNCS HTTP API functions."""

import json
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from magriculture.fncs.models.actors import Farmer
from magriculture.fncs.models.props import Transaction, Crop
from magriculture.fncs.models.geo import Market


def get_farmer(request):
    msisdn = request.GET.get('msisdn')
    farmer = get_object_or_404(Farmer, actor__user__username=msisdn)
    crops = [(crop.pk, crop.name) for crop in farmer.crops.all()]
    markets = [(market.pk, market.name) for market in farmer.markets.all()]
    farmer_data = {
        "farmer_name": farmer.actor.name,
        "crops": crops,
        "markets": markets,
        }
    return HttpResponse(json.dumps(farmer_data))


def get_price_history(request):
    market_pk = request.GET.get('market')
    crop_pk = request.GET.get('crop')
    limit = int(request.GET.get('limit', '10'))
    market = get_object_or_404(Market, pk=market_pk)
    crop = get_object_or_404(Crop, pk=crop_pk)
    prices = {}
    for unit in crop.units.all():
        unit_prices = Transaction.price_history_for(market, crop, unit)[:limit]
        unit_prices = list(unit_prices)
        if unit_prices:
            prices[unit.pk] = {
                "unit_name": unit.name,
                "prices": unit_prices,
                }
    return HttpResponse(json.dumps(prices))
