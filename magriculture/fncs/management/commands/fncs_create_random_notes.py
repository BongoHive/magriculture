from django.core.management.base import BaseCommand
from magriculture.fncs.models.actors import Agent
from magriculture.fncs.models.props import Note
from magriculture.fncs.tests import utils
from optparse import make_option

class Command(BaseCommand):
    help = "Add random quotes as notes to agents' farmers"
    option_list = BaseCommand.option_list + (
        make_option('--total', dest='total', default=10, type='int', 
                        help='How many notes to write per farmer'),
        make_option('--agent', dest='agent', default=None, type='str', 
                        help='Which agent to write notes for'),
    )
    def handle(self, *args, **options):
        agents = Agent.objects.all()
        username = options['agent']
        if username:
            agents = agents.filter(actor__user__username=username)
        
        for agent in Agent.objects.all():
            for farmer in agent.farmers.all():
                for i in range(options['total']):
                    agent.write_note(farmer, utils.random_quote())