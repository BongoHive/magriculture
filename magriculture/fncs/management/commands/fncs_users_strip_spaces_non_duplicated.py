from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from optparse import make_option

# sample usage:
# python manage.py fncs_users_strip_spaces_non_duplicated --verbose True
# python manage.py fncs_users_strip_spaces_non_duplicated


class Command(BaseCommand):
    help = "Delete users that have ' ' in username and are not duplicated"
    option_list = BaseCommand.option_list + (
        make_option('--verbose', dest='verbose', type='str', default='False',
                    help='Show detailed on-going activity and duplicates'),
    )

    def print_verbose(self, s):
        if self.verbose == 'True':
            self.stdout.write(s + '\n')


    def handle(self, *args, **options):
        self.verbose = options['verbose']
        users = User.objects.filter(username__contains=' ')
        stripped_list = []
        non_duplicated = []
        duplicated = []
        space_in_middle = []

        for user in users:
            strp = user.username.strip(' ')
            stripped = user.username.replace(' ', '')
            stripped_list.append(stripped)

            if len(strp) != len(stripped):
                space_in_middle.append(user.username)


        for username in stripped_list:
            count = stripped_list.count(username)
            in_non_spaced = len(User.objects.filter(
                                    username__contains=username))

            # check for duplication among stripped users
            if count != 1:
                duplicated.append(username)
            # check for duplication among other users
            elif in_non_spaced != 1:
                duplicated.append(username)
            # one number with space in middle problem
            elif username == '+260977496544':
                duplicated.append(username)
            else:
                non_duplicated.append(username)

        # adjust non-duplicated users
        self.stdout.write('Updating non-duplicated users...\n')
        for user in users:
            stripped = user.username.replace(' ', '')
            if stripped in non_duplicated:
                if stripped[0:3] == '+26':
                    user.username = stripped
                    user.save()
                    self.print_verbose(str(user) + ' saved')
                elif stripped[0:2] == '09':
                    user.username = '+26' + stripped
                    user.save()
                    self.print_verbose(str(user) + ' saved')

        self.stdout.write('Done.\n')

        # print list of duplicates if verbose
        self.print_verbose('\nDuplicates:')
        for username in duplicated:
            self.print_verbose(str(username))
