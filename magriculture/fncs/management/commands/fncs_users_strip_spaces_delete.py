from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from optparse import make_option


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

        # delete these users
        users_delete = args

        self.stdout.write('Deleting users...\n')

        for username in users_delete:
            try:
                user = User.objects.get(username=username)
                self.print_verbose('Deleting user ' + username)
                user.delete()
                self.print_verbose('Deleted.')
            except:
                self.print_verbose('User not found - OK')

        self.stdout.write('Done.\n')
