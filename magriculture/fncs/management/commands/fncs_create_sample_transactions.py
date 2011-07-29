from django.core.management.base import BaseCommand
from magriculture.fncs.models.actors import Farmer, Agent
from optparse import make_option
import random

class Command(BaseCommand):
    help = "Generate sample transactions for farmers"
    option_list = BaseCommand.option_list + (
        make_option('--total', dest='total', type='int', default=10, 
                        help='How many transactions to create per farmer'),
        make_option('--agent', dest='agent', default=None, type='str', 
                        help='Which agent to write notes for'),
    )
    def handle(self, *args, **options):
        total = options['total']
        
        farmers = Farmer.objects.all()
        username = options['agent']
        if username:
            agent = Agent.objects.get(actor__user__username=username)
            farmers = farmers.filter(agent=agent)
        
        for farmer in farmers.iterator():
            for i in range(total):
                crop = farmer.crops.order_by('?')[0]
                unit = crop.units.order_by('?')[0]
                agent = farmer.agents.order_by('?')[0]
                market = farmer.markets.order_by('?')[0]
                price = random.randint(200,400)
                amount = random.randint(10,50)
                agent.register_sale(market, farmer, crop, unit, price, amount)