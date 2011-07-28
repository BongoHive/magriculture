from django.core.management.base import BaseCommand
from magriculture.fncs.models.actors import Farmer
from optparse import make_option
import random

class Command(BaseCommand):
    help = "Generate sample transactions for farmers"
    option_list = BaseCommand.option_list + (
        make_option('--total', dest='total', type='int', default=10, 
                        help='How many transactions to create per farmer'),
    )
    def handle(self, *args, **options):
        total = options['total']
        for farmer in Farmer.objects.all():
            for i in range(total):
                crop = farmer.crops.order_by('?')[0]
                unit = crop.units.order_by('?')[0]
                agent = farmer.agents.order_by('?')[0]
                market = farmer.markets.order_by('?')[0]
                price = random.randint(200,400)
                amount = random.randint(10,50)
                agent.register_sale(market, farmer, crop, unit, price, amount)