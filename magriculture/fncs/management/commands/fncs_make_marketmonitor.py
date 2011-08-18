from django.core.management.base import BaseCommand
from magriculture.fncs.models.actors import MarketMonitor
from django.contrib.auth.models import User
from optparse import make_option
import random, sys

class Command(BaseCommand):
    help = "Promote a given user account to MarketMonitor status"
    option_list = BaseCommand.option_list + (
        make_option('--username', dest='username', type='str', 
                        help='Username of account to be made an MarketMonitor'),
    )
    def handle(self, *args, **options):
        username = options['username']
        if not username:
            print 'Please provide --username'
            sys.exit(1)
        
        try:
            user = User.objects.get(username=username.strip())
            if not user.first_name:
                user.first_name = raw_input("First name: ")
            if not user.last_name:
                user.last_name = raw_input("Last name: ")
            user.save()
            
            actor = user.get_profile()
            marketmonitor, _ = MarketMonitor.objects.get_or_create(actor=actor)
            print '%s is now MarketMonitor %s with id %s' % (username, marketmonitor, marketmonitor.pk)
        except User.DoesNotExist:
            print 'User %s does not exist' % (username, )