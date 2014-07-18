from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from optparse import make_option
from magriculture.fncs.models.actors import Farmer
from magriculture.fncs.models.props import CropReceipt, Message


class Command(BaseCommand):
    help = "Delete users that have ' ' in username"
    option_list = BaseCommand.option_list + (
        make_option('--verbose', dest='verbose', type='str', default='False',
                    help='Show detailed on-going activity and duplicates'),
    )

    def merge_crop_receipts(self, username_origin, farmer_target):
        self.print_verbose('Crop Receipts:')
        crop_receipts_origin = CropReceipt.objects.filter(
                    farmer__actor__user__username=username_origin)
        self.print_verbose('Moving to ' + str(farmer_target))
        if len(crop_receipts_origin) != 0:
            for crop_receipt in crop_receipts_origin:
                self.print_verbose(str(crop_receipt))
                crop_receipt.farmer = farmer_target
                crop_receipt.save()
            self.print_verbose('Crop receipts merged.')
        else:
            self.print_verbose('No crop receipts for farmer.')

    def merge_messages(self, username_origin, farmer_target):
        self.print_verbose('\nMessages:')
        messages_origin = Message.objects.filter(
                    recipient__user__username=username_origin)
        self.print_verbose('Moving to ' + str(farmer_target))
        if len(messages_origin) != 0:
            for message in messages_origin:
                self.print_verbose(str(message))
                message.farmer = farmer_target
                message.save()
            self.print_verbose('Messages merged.')
        else:
            self.print_verbose('No messages for farmer.')

    def print_verbose(self, s):
        if self.verbose == 'True':
            self.stdout.write(s + '\n')


    def handle(self, *args, **options):
        self.verbose = options['verbose']
        double_user_merge_delete_rename = []
        unique_users_reqd = len(args) / 3
        index = 0
        for i in range(unique_users_reqd):
            double_user_merge_delete_rename.append(
                (args[index], args[index+1], args[index+2]))
            index += 3
            
        # merge user2 into user1 (receipts and messages only)
        # merge user3 into user1 (receipts and messages only)
        # delete user2 and user 3
        # rename user1 to '+2609...'

        self.stdout.write('Merging, deleting and renaming...\n')

        for user_tuple in double_user_merge_delete_rename:
            username_target = user_tuple[0]
            username_origin1 = user_tuple[1]
            username_origin2 = user_tuple[2]

            try:
                user_target = User.objects.get(username=username_target)
                user_origin1 = User.objects.get(username=username_origin1)
                user_origin2 = User.objects.get(username=username_origin2)
                farmer_target = Farmer.objects.get(
                                    actor__user__username=username_target)

                self.print_verbose('\n' + str(user_origin1))
                self.print_verbose('----------------')
                self.merge_crop_receipts(username_origin1, farmer_target)
                self.merge_messages(username_origin1, farmer_target)

                self.print_verbose('\n' + str(user_origin2))
                self.print_verbose('----------------')
                self.merge_crop_receipts(username_origin2, farmer_target)
                self.merge_messages(username_origin2, farmer_target)


                self.print_verbose('\nDeleting origin users')
                user_origin1.delete()
                user_origin2.delete()
                self.print_verbose('Deleted.')

                self.print_verbose('Renaming target user')
                user_target.username = username_origin2
                user_target.save()
                self.print_verbose('Renamed.')

            except:
                self.print_verbose('User not found - OK')


        self.stdout.write('Done.\n')
