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

        # delete '+2609' user, then rename ' 09' to '+2609...'
        # delete the first user, then rename the second user to that one
        users_delete_rename = args

        self.stdout.write('Deleting and renaming users...\n')

        for username in users_delete_rename:
            plus_username = '+26' + username.strip(' ')
            try:
                user_target = User.objects.get(username=plus_username)
                user_origin = User.objects.get(username=username)

                self.print_verbose('Deleting user ' + plus_username)
                user_target.delete()
                self.print_verbose('Deleted.')

                self.print_verbose('Renaming user ' + username)
                user_origin.username = plus_username
                user_origin.save()
                self.print_verbose('Renamed')

            except:
                self.print_verbose('User not found - OK')

        self.stdout.write('Done.\n')
