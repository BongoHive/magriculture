from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from magriculture.fncs.models.props import CropReceipt


# Example usage:
# Add '+' to 30 users:
# python manage.py fncs_users_add_plus


class Command(BaseCommand):
    help = "Search for '260' numbers, change to '+260'"

    def handle(self, *args, **options):
        counter = 0
        users = User.objects.filter(username__startswith='260')
        total = len(users)

        if total == 0:
            self.stdout.write('No users starting with "260"\n')

        for user in users:
            counter += 1

            self.stdout.write('Checking %s for duplicate user...' %(user))
            try:
                # Search for duplicate user
                new_username = '+' + user.username
                duplicate_user = User.objects.get(username=new_username)
                self.stdout.write('duplicate user found.\n')

                # see if the duplicate has any crop_receipts, delete if not
                receipts = CropReceipt.objects.filter(farmer__actor__user__username=new_username)

                if len(receipts) == 0:
                    self.stdout.write('Duplicate has no transactions...deleting duplicate\n')
                    duplicate_user.delete()
                    self.stdout.write('Updating number... %s is now saved as %s\n' %(user, new_username))
                    user.username = '+' + user.username
                    user.save()
                else:
                    self.stdout.write('Warning! Problem with duplication!')

            except:
                self.stdout.write('no duplicate found.\n')
                self.stdout.write('Updating %s to +%s (%s/%s users updated)\n' %(user, user, counter, total))
                user.username = '+' + user.username
                user.save()

        self.stdout.write('Done.\n')
