from django.core.management.base import BaseCommand
from magriculture.fncs.models.actors import Agent, MarketMonitor
from magriculture.fncs.models.geo import Market
from magriculture.fncs.models.props import Crop
from optparse import make_option
import random

class Command(BaseCommand):
    help = "Generate sample offers"
    option_list = BaseCommand.option_list + (
        make_option('--total', dest='total', type='int', default=10, 
                        help='How many offers to create per market monitor'),
        make_option('--agent', dest='marketmonitor', default=None, type='str', 
                        help='Which marketmonitor to write offers for'),
    )
    def handle(self, *args, **options):
        total = options['total']
        marketmonitors = MarketMonitor.objects.all()
        username = options['marketmonitor']
        if username:
            agent = Agent.objects.get(actor__user__username=username)
            marketmonitors = marketmonitors.filter(actor=agent.actor)
        
        for marketmonitor in marketmonitors.iterator():
            print marketmonitor
            for i in range(total):
                crop = Crop.objects.all().order_by('?')[0]
                unit = crop.units.order_by('?')[0]
                market = Market.objects.all().order_by('?')[0]
                price_floor = random.randint(200,400)
                price_ceiling = price_floor + random.randint(10,50)
                amount = random.randint(10,50)
                print marketmonitor.register_offer(market, crop, unit, price_floor,
                        price_ceiling)