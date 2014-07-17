from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from optparse import make_option
from magriculture.fncs.models.actors import Farmer, FarmerBusinessAdvisor
from magriculture.fncs.models.props import CropReceipt, Message, Crop
from magriculture.fncs.models.geo import Market, Ward, District

# [' 0979338243', ' 0979899912', '  0965050280']


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

        merge_delete_all = args

        # merge ' 097...' into '+26097...' (all fields), then delete ' 097...'
        self.stdout.write('Merging and deleting...\n')

        for username_origin in merge_delete_all:
            username_target = '+26' + username_origin.strip(' ')

            # get the user & farmers
            try:
                user_origin = User.objects.get(username=username_origin)
                farmer_origin = Farmer.objects.get(
                                    actor__user__username=username_origin)
                farmer_target = Farmer.objects.get(
                                    actor__user__username=username_target)

                self.print_verbose('\n' + str(user_origin))
                self.print_verbose('----------------')
                
                # merge crop receipts and messages
                self.merge_crop_receipts(username_origin, farmer_target)
                self.merge_messages(username_origin, farmer_target)

                # move farmer fields data across
                move_fields = ['id_number', 'hh_id', 'participant_type', 'gender',
                                        'number_of_males', 'number_of_females']

                for field in move_fields:
                    farmer_origin_field = getattr(farmer_origin, field)
                    if not (farmer_origin_field == None or farmer_origin_field == ""):
                        farmer_target_field = getattr(farmer_target, field)
                        if (farmer_target_field == None or farmer_target_field == 'U'):
                            farmer_target_field = farmer_origin_field
                            farmer_target.save()
                            self.stdout.write('field updated - OK\n')
                        elif (farmer_target_field == farmer_origin_field):
                            self.stdout.write('field value is the same\n')
                        else:
                            self.stdout.write('Different field values! Fix manually\n')
                    else:
                        self.stdout.write('field value is empty - OK\n')

                # many-to-many's
                    # markets
                self.print_verbose("\nFarmer's Markets:")
                try:
                    markets_origin = farmer_origin.markets.all()
                    markets_target = farmer_target.markets.all()

                    for market in markets_origin:
                        self.print_verbose(str(market))
                        if not (market in markets_target):
                            market_obj = Market.objects.get(name=market.name)
                            farmer_target.markets.add(market_obj)
                            farmer_target.save()
                except:
                    self.print_verbose('Markets not found - evaluate')

                self.print_verbose('Markets updated')

                    # fbas
                self.print_verbose("\nFarmer's FBAs:")
                try:
                    fbas_origin = farmer_origin.fbas.all()
                    fbas_target = farmer_target.fbas.all()

                    for fba in fbas_origin:
                        self.print_verbose(str(fba))
                        if not (fba in fbas_target):
                            fba_obj = FarmerBusinessAdvisor.objects.get(name=fba.name)
                            farmer_target.fbas.add(fba_obj)
                            farmer_target.save()
                except:
                    self.print_verbose('FBAs not found - evaluate')

                self.print_verbose('FBAs updated')

                    # wards
                self.print_verbose("\nFarmer's Wards:")
                try:
                    wards_origin = farmer_origin.wards.all()
                    wards_target = farmer_target.wards.all()

                    for ward in wards_origin:
                        self.print_verbose(str(ward))
                        if not (ward in wards_target):
                            ward_obj = Ward.objects.get(name=ward.name)
                            farmer_target.wards.add(ward_obj)
                            farmer_target.save()
                except:
                    self.print_verbose('Wards not found - evaluate')

                self.print_verbose('Wards updated')

                    # districts
                self.print_verbose("\nFarmer's Districts:")
                try:
                    districts_origin = farmer_origin.districts.all()
                    districts_target = farmer_target.districts.all()

                    for district in districts_origin:
                        self.print_verbose(str(district))
                        if not (district in districts_target):
                            district_obj = District.objects.get(name=district.name)
                            farmer_target.districts.add(district_obj)
                            farmer_target.save()
                except:
                    self.print_verbose('Districts not found - evaluate')

                self.print_verbose('Districts updated')

                # crops
                self.print_verbose("\nFarmer's Crops:")
                try:
                    crops_origin = farmer_origin.crops.all()
                    crops_target = farmer_target.crops.all()

                    for crop in crops_origin:
                        self.print_verbose(str(crop))
                        if not (crop in crops_target):
                            crop_obj = Crop.objects.get(name=crop.name)
                            farmer_target.crops.add(crop_obj)
                            farmer_target.save()
                except:
                    self.print_verbose('Crops not found - evaluate')

                self.print_verbose('Crops updated')


                self.print_verbose('Deleting origin user')
                user_origin.delete()
                self.print_verbose('Deleted.')


            except:
                self.print_verbose('User not found - OK')


        self.stdout.write('Done.\n')
