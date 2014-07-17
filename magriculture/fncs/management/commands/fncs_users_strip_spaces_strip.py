from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from optparse import make_option

# ['+260978 342416']


class Command(BaseCommand):
    help = "Delete users that have ' ' in username"
    option_list = BaseCommand.option_list + (
        make_option('--verbose', dest='verbose', type='str', default='False',
                    help='Show detailed on-going activity and duplicates'),
    )

    def print_verbose(self, s):
        if self.verbose == 'True':
            self.stdout.write(s + '\n')


    def handle(self, *args, **options):
        self.verbose = options['verbose']

        # remove spaces from these users
        users_strip_space = args

        self.stdout.write('Cleaning spaces from usernames...\n')

        for username in users_strip_space:
            try:
                user = User.objects.get(username=username)
                self.print_verbose('Cleaning ' + str(username))
                user.username = username.replace(' ','')
                user.save()
                self.print_verbose('Spaces removed.')
            except:
                self.print_verbose('User not found - OK')

        self.stdout.write('Done.\n')
