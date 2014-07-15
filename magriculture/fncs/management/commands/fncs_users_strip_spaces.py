from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from optparse import make_option
from magriculture.fncs.models.actors import Farmer, FarmerBusinessAdvisor
from magriculture.fncs.models.props import CropReceipt, Message, Crop
from magriculture.fncs.models.geo import Market, Ward, District


def merge_crop_receipts(username_origin, farmer_target):
    print 'Crop Receipts:'
    crop_receipts_origin = CropReceipt.objects.filter(
                farmer__actor__user__username=username_origin)
    print 'Moving to ', farmer_target
    if len(crop_receipts_origin) != 0:
        for crop_receipt in crop_receipts_origin:
            print crop_receipt
            crop_receipt.farmer = farmer_target
            crop_receipt.save()
        print 'Crop receipts merged.'
    else:
        print 'No crop receipts for farmer.'

def merge_messages(username_origin, farmer_target):
    print '\nMessages:'
    messages_origin = Message.objects.filter(
                recipient__user__username=username_origin)
    print 'Moving to ', farmer_target
    if len(messages_origin) != 0:
        for message in messages_origin:
            print message
            message.farmer = farmer_target
            message.save()
        print 'Messages merged.'
    else:
        print 'No messages for farmer.'


class Command(BaseCommand):
    help = "Delete users that have '.0' in username"
    option_list = BaseCommand.option_list + (
        make_option('--total', dest='total', type='int', default=15000,
                        help='How many users to delete'),
    )

    def handle(self, *args, **options):
        total = options['total']
        users = User.objects.filter(username__contains=' ')[0:total]
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
            in_non_spaced = len(User.objects.filter(username__contains=username))

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
        print 'Updating non-duplicated users...'
        for user in users:
            stripped = user.username.replace(' ', '')
            if stripped in non_duplicated:
                if stripped[0:3] == '+26':
                    user.username = stripped
                    user.save()
                    print user.username, ' saved'
                elif stripped[0:2] == '09':
                    user.username = '+26' + stripped
                    user.save()
                    print user.username, ' saved'

        print 'Done.'


        # for username in duplicated:
        #     print username

        print '\nHandling duplication..........\n'




        # print '-----------------------------------------------------'

        # # strip space and save users
        # users_strip_space = ['+260978 342416']

        # for username in users_strip_space:
        #     print 'Cleaning ', username
        #     try:
        #         user = User.objects.get(username=username)
        #         user.username = username.replace(' ','')
        #         user.save()
        #         print 'Spaces removed.'
        #     except:
        #         print 'User not found - OK\n'

        # print '-----------------------------------------------------'





        # print '-----------------------------------------------------'

        # # delete these users
        # users_delete = ['  0968535703', ' 0976727879', ' 0977244702',
        #     ' 0965178414', ' 0972178866', ' 0979519388', '+260977 496544']

        # for username in users_delete:
        #     print 'Deleting user ', username 
        #     try:
        #         user = User.objects.get(username=username)
        #         user.delete()
        #         print 'Deleted.\n'
        #     except:
        #         print 'User not found - OK\n'

        # print '-----------------------------------------------------'





        # print '-----------------------------------------------------'

        # # delete '+2609' user, then rename ' 09' to '+2609...'
        # # delete the first user, then rename the second user to that one
        # users_delete_rename = [' 0979535304', ' 0977521089', ' 0966270705',
        #                         ' 0965476912', ' 0965225080']

        # for username in users_delete_rename:
        #     plus_username = '+26' + username.strip(' ')
        #     print 'Deleting user ', plus_username
        #     try:
        #         user_target = User.objects.get(username=plus_username)
        #         user_origin = User.objects.get(username=username)

        #         user_target.delete()
        #         print 'Deleted.'

        #         print 'Renaming user ', username
        #         user_origin.username = plus_username
        #         user_origin.save()
        #         print 'Renamed'

        #     except:
        #         print 'User not found - OK'

        # print '-----------------------------------------------------'





        # print '-----------------------------------------------------'

        # # merge ' 097...' into '+26097...' (receipts and messages only), then
        # # delete ' 097...'
        # merge_delete = ['  0976712188', ' 0964541673', ' 0979572717',
        #                 ' 0978444239', ' 0977982058']

        # for username_origin in merge_delete:
        #     username_target = '+26' + username_origin.strip(' ')

        #     # get the users
        #     try:
        #         user_origin = User.objects.get(username=username_origin)
        #         farmer_target = Farmer.objects.get(
        #                             actor__user__username=username_target)

        #         print '\n', user_origin
        #         print '----------------'
                
        #         merge_crop_receipts(username_origin, farmer_target)
        #         merge_messages(username_origin, farmer_target)

        #         print 'Deleting origin user'
        #         user_origin.delete()
        #         print 'Deleted.'


        #     except:
        #         print 'User not found - OK'

        # print '-----------------------------------------------------'





        # print '-----------------------------------------------------'

        # # Merge '+2609...' into ' 09...' (receipts and messages only),
        # # then delete '+2609...', then rename ' 09...' to '+2609...'
        # merge_delete_rename = [' 0963460484', ' 0978909306',
        #                         ' 0977409931', ' 0979157826']

        # for username_target in merge_delete_rename:
        #     username_origin = '+26' + username_target.strip(' ')

        #     # get the users
        #     try:
        #         user_origin = User.objects.get(username=username_origin)
        #         user_target = User.objects.get(username=username_target)
        #         farmer_target = Farmer.objects.get(
        #                             actor__user__username=username_target)

        #         print '\n', user_origin
        #         print '----------------'

        #         merge_crop_receipts(username_origin, farmer_target)
        #         merge_messages(username_origin, farmer_target)

        #         print 'Deleting origin user'
        #         user_origin.delete()
        #         print 'Deleted.'

        #         print 'Renaming target user'
        #         user_target.username = username_origin
        #         user_target.save()
        #         print 'Renamed.'

        #     except:
        #         print 'User not found - OK'

        # print '-----------------------------------------------------'





        # print '-----------------------------------------------------'

        # # merge user2 into user1 (receipts and messages only)
        # # merge user3 into user1 (receipts and messages only)
        # # delete user2 and user 3
        # # rename user1 to '+2609...'
        # double_user_merge_delete_rename = [
        # (' 0979339243', '   0979339243', '+260979339243'),
        # ('     0969179963', '   0969179963', '+260969179963')]

        # for user_tuple in double_user_merge_delete_rename:
        #     username_target = user_tuple[0]
        #     username_origin1 = user_tuple[1]
        #     username_origin2 = user_tuple[2]

        #     try:
        #         user_target = User.objects.get(username=username_target)
        #         user_origin1 = User.objects.get(username=username_origin1)
        #         user_origin2 = User.objects.get(username=username_origin2)
        #         farmer_target = Farmer.objects.get(
        #                             actor__user__username=username_target)

        #         print '\n', user_origin1
        #         print '----------------'
        #         merge_crop_receipts(username_origin1, farmer_target)
        #         merge_messages(username_origin1, farmer_target)

        #         print '\n', user_origin2
        #         print '----------------'
        #         merge_crop_receipts(username_origin2, farmer_target)
        #         merge_messages(username_origin2, farmer_target)


        #         print '\nDeleting origin users'
        #         user_origin1.delete()
        #         user_origin2.delete()
        #         print 'Deleted.'

        #         print 'Renaming target user'
        #         user_target.username = username_origin2
        #         user_target.save()
        #         print 'Renamed.'

        #     except:
        #         print 'User not found - OK'

        # print '-----------------------------------------------------'




        print '-----------------------------------------------------'

        # merge ' 097...' into '+26097...' (all fields), then delete ' 097...'
        merge_delete_all = [' 0979338243', ' 0979899912', '  0965050280']

        for username_origin in merge_delete_all:
            username_target = '+26' + username_origin.strip(' ')

            # get the user & farmers
            try:
                user_origin = User.objects.get(username=username_origin)
                farmer_origin = Farmer.objects.get(
                                    actor__user__username=username_origin)
                farmer_target = Farmer.objects.get(
                                    actor__user__username=username_target)

                print '\n', user_origin
                print '----------------'
                
                # merge crop receipts and messages
                merge_crop_receipts(username_origin, farmer_target)
                merge_messages(username_origin, farmer_target)

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
                print "\nFarmer's Markets:"
                try:
                    markets_origin = farmer_origin.markets.all()
                    markets_target = farmer_target.markets.all()

                    for market in markets_origin:
                        print market
                        if not (market in markets_target):
                            market_obj = Market.objects.get(name=market.name)
                            farmer_target.markets.add(market_obj)
                            farmer_target.save()
                except:
                    print 'Markets not found - evaluate'

                print 'Markets updated'

                    # fbas
                print "\nFarmer's FBAs:"
                try:
                    fbas_origin = farmer_origin.fbas.all()
                    fbas_target = farmer_target.fbas.all()

                    for fba in fbas_origin:
                        print fba
                        if not (fba in fbas_target):
                            fba_obj = FarmerBusinessAdvisor.objects.get(name=fba.name)
                            farmer_target.fbas.add(fba_obj)
                            farmer_target.save()
                except:
                    print 'FBAs not found - evaluate'

                print 'FBAs updated'

                    # wards
                print "\nFarmer's Wards:"
                try:
                    wards_origin = farmer_origin.wards.all()
                    wards_target = farmer_target.wards.all()

                    for ward in wards_origin:
                        print ward
                        if not (ward in wards_target):
                            ward_obj = Ward.objects.get(name=ward.name)
                            farmer_target.wards.add(ward_obj)
                            farmer_target.save()
                except:
                    print 'Wards not found - evaluate'

                print 'Wards updated'

                    # districts
                print "\nFarmer's Districts:"
                try:
                    districts_origin = farmer_origin.districts.all()
                    districts_target = farmer_target.districts.all()

                    for district in districts_origin:
                        print district
                        if not (district in districts_target):
                            district_obj = District.objects.get(name=district.name)
                            farmer_target.districts.add(district_obj)
                            farmer_target.save()
                except:
                    print 'Districts not found - evaluate'

                print 'Districts updated'

                # crops
                print "\nFarmer's Crops:"
                try:
                    crops_origin = farmer_origin.crops.all()
                    crops_target = farmer_target.crops.all()

                    for crop in crops_origin:
                        print crop
                        if not (crop in crops_target):
                            crop_obj = Crop.objects.get(name=crop.name)
                            farmer_target.crops.add(crop_obj)
                            farmer_target.save()
                except:
                    print 'Crops not found - evaluate'

                print 'Crops updated'




                print 'Deleting origin user'
                user_origin.delete()
                print 'Deleted.'


            except:
                print 'User not found - OK'




