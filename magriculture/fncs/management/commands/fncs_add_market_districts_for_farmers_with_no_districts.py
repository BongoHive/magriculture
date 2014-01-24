# Django
from django.core.management.base import BaseCommand

# Project
from magriculture.fncs.models.actors import Farmer


class Command(BaseCommand):
    help = ("If a farmer doesn't have a district, the farmers markets"
            " districts are assumed to be his market")


    def handle(self, *args, **options):
        # Getting farmers with no districts
        farmers_no_distr = Farmer.objects.filter(districts=None).all()
        for farmer in farmers_no_distr:
            # Getting the markets for the farmer
            for market in farmer.markets.all():
                farmer.districts.add(market.district)
