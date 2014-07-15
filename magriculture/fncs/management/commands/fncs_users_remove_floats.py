from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from optparse import make_option

# Example usage:
# Delete 30 '.0'-containing users:
# python manage.py fncs_users_remove_floats --total 30


class Command(BaseCommand):
    help = "Delete users that have '.0' in username"
    option_list = BaseCommand.option_list + (
        make_option('--total', dest='total', type='int', default=15000,
                        help='How many users to delete'),
    )

    def handle(self, *args, **options):
        total = options['total']

        counter = 0

        users = User.objects.filter(username__contains='.0')[0:total]
        total = len(users)

        if total == 0:
            self.stdout.write('No users to delete\n')

        for user in users:
            counter += 1
            self.stdout.write('Deleting %s (%s/%s users deleted)\n' %(user, counter, total))
            user.delete()

        self.stdout.write('Done.\n')
