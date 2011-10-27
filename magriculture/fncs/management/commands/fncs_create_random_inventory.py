from django.core.management.base import BaseCommand
from magriculture.fncs.models.actors import Farmer, Agent
from magriculture.fncs.tests import utils
from optparse import make_option
import random

class Command(BaseCommand):
    help = "Generate sample inventory for agents"
    option_list = BaseCommand.option_list + (
        make_option('--total', dest='total', type='int', default=10,
                        help='How many crop intakes to create per farmer'),
        make_option('--agent', dest='agent', default=None, type='str',
                        help='Which agent to create inventory for'),
    )
    def handle(self, *args, **options):
        total = options['total']

        farmers = Farmer.objects.all()
        username = options['agent']
        if not username:
            raise Exception, 'please provide --agent'

        agent = Agent.objects.get(actor__user__username=username)
        farmers = farmers.filter(agent=agent)

        for farmer in farmers.iterator():
            for i in range(total):
                crop = utils.random_crop()
                unit = crop.units.order_by('?')[0]
                market = farmer.markets.order_by('?')[0]
                amount = random.randint(10,50)
                receipt = agent.take_in_crop(market, farmer, amount, unit, crop)
                print receipt
