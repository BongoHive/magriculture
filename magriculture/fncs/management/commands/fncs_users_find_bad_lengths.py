from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from optparse import make_option

# Example usage:
# python manage.py fncs_users_find_bad_lengths --total 30


class Command(BaseCommand):
    help = "Search for too long and too short numbers"
    option_list = BaseCommand.option_list + (
        make_option('--total', dest='total', type='int', default=15000,
                        help='How many users to delete'),
    )

    def handle(self, *args, **options):
        total = options['total']


        users = User.objects.filter(username__startswith='+260')[0:total]
        total = len(users)
        expected_length = 13

        if total == 0:
            self.stdout.write('No users starting with +260\n')

        print ('Short usernames:')

        for user in users:
            stripped = user.username.replace(' ', '')
            length = len(stripped)
            if length < expected_length:
                print user.username

        print ('Long usernames:')

        for user in users:
            stripped = user.username.replace(' ', '')
            length = len(stripped)
            if length > expected_length:
                print user.username
