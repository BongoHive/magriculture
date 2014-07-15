from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from optparse import make_option
from magriculture.fncs.models.actors import (Actor, Farmer, Agent, Identity,
                            )
from magriculture.fncs.models.geo import Market
from magriculture.fncs.models.props import (Message, GroupMessage, Note,
                                            Transaction, CropReceipt)


# Example usage:
# Add '+' to 30 users:
# python manage.py fncs_users_add_plus --total 30


# def has_child(parent, child):
#     try:


class Command(BaseCommand):
    help = "Search for '260' numbers, change to '+260'"
    option_list = BaseCommand.option_list + (
        make_option('--total', dest='total', type='int', default=15000,
                        help='How many users to delete'),
    )

    def handle(self, *args, **options):
        total = options['total']
        counter = 0
        users = User.objects.filter(username__startswith='260')[0:total]
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
                    problems_numbers.append(user.username)








            
                self.stdout.write('Merging into existing user %s (%s/%s users updated)\n' %(duplicate_user, counter, total))

                # Move data across
                try:
                    actor_from = Actor.objects.get(user__username=user)
                    actor_to = Actor.objects.get(user__username=duplicate_user)
                    self.stdout.write('\nActors:\n')
                except:
                    self.stdout.write('User has no actor! What?!')

                # Deal with Actor > Farmer
                # check if actor_from has a farmer
                try:
                    farmer_from = Farmer.objects.get(actor__user__username=user)
                    self.stdout.write('%s has a farmer\n' %(user))

                    try:
                        # check if farmer_to has an existing farmer element
                        farmer_to = Farmer.objects.get(actor__user__username=duplicate_user)
                        self.stdout.write('%s has a farmer\n' %(duplicate_user))

                        print '~~~~~~~'

                        # move farmer data across (remember to delete later)

                        move_fields = ['id_number', 'hh_id', 'participant_type', 'gender',
                                        'number_of_males', 'number_of_females']

                        # id_number

                        for field in move_fields:
                            farmer_from_field = getattr(farmer_from, field)
                            if not (farmer_from_field == None or farmer_from_field == ""):
                                farmer_to_field = getattr(farmer_to, field)
                                if (farmer_to_field == None or farmer_to_field == 'U'):
                                    farmer_to_field = farmer_from_field
                                    # farmer_to_save()
                                    self.stdout.write('field updated - OK\n')
                                elif (farmer_to_field == farmer_from_field):
                                    self.stdout.write('field value is the same\n')
                                else:
                                    self.stdout.write('Different field values! Fix manually\n')
                            else:
                                self.stdout.write('field value is empty - OK\n')




                    except:
                        # if farmer_to doesn't have an existing actor, change the farmer's actor
                        farmer_from.actor = actor_to
                        # farmer_from.save()


                        print "\nFarmer's Markets:"
                        markets_from = farmer_from.markets.all()
                        markets_to = farmer_to.markets.all()
                        print markets_from
                        print markets_to

                        for market in markets_from:
                            print 'From markets:'
                            print market
                            if not (market in markets_to):
                                market_obj = Market.objects.get(name=market.name)
                                print market_obj

                                farmer_to.markets.add(market_obj)
                                # farmer_to.save()

                        markets_to = farmer_to.markets.all()
                        print 'To markets:'
                        for market in markets_to:
                            print market

                        

                    print '\nCrop Receipts (farmer):'
                    crop_receipts_farmer = CropReceipt.objects.filter(farmer__actor__user__username=user)
                    if len(crop_receipts_farmer) != 0:
                        for crop_receipt in crop_receipts_farmer:
                            print crop_receipt
                            print crop_receipt.farmer, ' > ', farmer_to
                            crop_receipt.farmer = farmer_to
                            # crop_receipt.save()
                    else:
                        print 'No crop receipts for farmers'

                except:
                    self.stdout.write('Actor does not have a farmer\n')






                print '\nMessages:'
                messages = Message.objects.filter(recipient__user__username=user)
                if len(messages) != 0:
                    for message in messages:
                        print message
                        print message.recipient, ' > ', actor_to
                        message.recipient = actor_to
                        # message.save()
                else:
                    print 'No messages for actor'


                print '\nAgents:'
                try:
                    agent_from = Agent.objects.get(actor__user__username=user)
                    try:
                        agent_to = Agent.objects.get(actor__user__username=duplicate_user)
                    except:
                        agent_from.actor = actor_to
                        # agent_from.save()
                    print agent_from.actor
                except:
                    print 'No agent found in original'

                # print agent_from.actor


                self.stdout.write('\n\n')

            

            except:
                self.stdout.write('no duplicate found.\n')
                self.stdout.write('Updating %s to +%s (%s/%s users updated)\n' %(user, user, counter, total))
                user.username = '+' + user.username
                user.save()

        self.stdout.write('Done.\n')

