from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from optparse import make_option
from magriculture.fncs.models.actors import Farmer
from magriculture.fncs.models.props import CropReceipt, Message

# '  0976712188' ' 0964541673' ' 0979572717' ' 0978444239' ' 0977982058'


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

        # merge ' 097...' into '+26097...' (receipts and messages only), then
        # delete ' 097...'
        merge_delete = args

        self.stdout.write('Merging and deleting...\n')

        for username_origin in merge_delete:
            username_target = '+26' + username_origin.strip(' ')

            try:
                user_origin = User.objects.get(username=username_origin)
                farmer_target = Farmer.objects.get(
                                    actor__user__username=username_target)

                print '3'
                print user_origin.id
                self.print_verbose('\n' + str(user_origin))
                self.print_verbose('----------------')
                
                print '2'
                self.merge_crop_receipts(username_origin, farmer_target)
                self.merge_messages(username_origin, farmer_target)

                print '1'
                self.print_verbose('Deleting origin user')
                user_origin.delete()
                self.print_verbose('Deleted.')


            except:
                self.print_verbose('User not found - OK')

        self.stdout.write('Done.\n')
