from magriculture.fncs.utils import ImportCommand
from magriculture.fncs.models.actors import Agent
from magriculture.fncs.tests import utils
from django.contrib.auth.models import User
import sys


class Command(ImportCommand):
    help = "Import agents from an excel file"
    
    def handle_row(self, row):
        username = row['Mobile_Number_1']
        password = username[-4:]
        
        if User.objects.filter(username=username).exists():
            print 'User with username %s already exists' % username
            return
        
        user = User.objects.create_user(username, '%s@domain.com' % username,
            password)
        user.first_name = row['Agent_F_Name']
        user.last_name = row['Agent_S_Name']
        user.save()
        
        actor = user.get_profile()
        agent, _ = Agent.objects.get_or_create(actor=actor)
        province = utils.create_province("Unspecified Province")
        district = utils.create_district("Unspecified District", province)
        market = utils.create_market(row['Market1'], district)
        agent.markets.add(market)