from django.core.management.base import BaseCommand
from magriculture.fncs.models.actors import Agent, Actor
from magriculture.fncs.management.commands import fncs_create_sample_farmers
from django.contrib.auth.models import User
from optparse import make_option
import random, sys

class Command(BaseCommand):
    help = "Promote a given user account to Agent status"
    option_list = BaseCommand.option_list + (
        make_option('--username', dest='username', type='str',
                        help='Username of account to be made a Farmer'),
    )
    def handle(self, *args, **options):
        username = options['username']
        if not username:
            print 'Please provide --username'
            sys.exit(1)

        actor = Actor.objects.get(user__username=username)
        agent = actor.as_agent()

        command = fncs_create_sample_farmers.Command()
        command.generate_farmers([username], agent)