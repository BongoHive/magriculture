from django.contrib.auth.models import User
from magriculture.fncs.models.props import CropReceipt
from django.core.management.base import BaseCommand
from optparse import make_option

# Example usage:
# python manage.py fncs_users_internationalise --total 30


class Command(BaseCommand):
    help = "Change users from 09 numbers to +260 numbers"
    option_list = BaseCommand.option_list + (
        make_option('--total', dest='total', type='int', default=15000,
                        help='How many users to delete'),
    )

    def handle(self, *args, **options):
        total = options['total']

        problems_numbers = []
        duplicates_numbers = []

        users = User.objects.filter(username__startswith='09')[0:total]

        if len(users) == 0:
            self.stdout.write('No users starting with 09\n')

        # search for same number but starting with +2609
        for user in users:
            international_username = '+26' + user.username

            try:
                duplicate_user = User.objects.get(
                                            username=international_username)
                self.stdout.write('Duplicate found... ' + user.username +
                                    '\n')
                duplicates_numbers.append(international_username)

                # see if the duplicate has any crop_receipts, delete if not
                receipts = CropReceipt.objects.filter(
                        farmer__actor__user__username=international_username)

                if len(receipts) == 0:
                    self.stdout.write('Duplicate has no transactions...' +
                                        'deleting duplicate\n')
                    duplicate_user.delete()
                    self.stdout.write(
                        'Updating number... %s is now saved as %s\n'
                        %(user, international_username)
                    )
                    user.username = international_username
                    user.save()

                else:
                    self.stdout.write('Warning! Problem with duplication!')
                    problems_numbers.append(user.username)


            except:
                self.stdout.write('No duplicates found...')
                self.stdout.write(
                    'Updating number... %s is now saved as %s\n'
                    %(user, international_username)
                )
                user.username = international_username
                user.save()

        self.stdout.write('\nTransfer complete.\n')

        if len(problems_numbers) == 0:
            self.stdout.write('\nNo fatal problems encountered - OK.\n')
            self.stdout.write('\nDuplicates removed:\n')
            for num in duplicates_numbers:
                self.stdout.write(num + '\n')
        else:
            self.stdout.write('\nThere were problems with the following ' +
                                'users:\n')
            for number in problems_numbers:
                self.stdout.write(number)
