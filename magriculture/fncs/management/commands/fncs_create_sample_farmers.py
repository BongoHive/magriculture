from django.core.management.base import BaseCommand
from magriculture.fncs.tests import utils
from magriculture.fncs.models.actors import Actor
from optparse import make_option

class Command(BaseCommand):
    help = "Generate sample farmer data"
    option_list = BaseCommand.option_list + (
        make_option('--total', dest='total', type='int', default=500,
                        help='How many farmers to create'),
        make_option('--agent', dest='agent', type='str', default=None,
                        help='Generate farmers for a specific agent'),
        make_option('--farmer', dest='farmer', type='str', default=None,
                        help='Generate sample data for a specific farmer'
                             ' (misisdn)'),
    )

    def handle(self, *args, **options):
        total = options['total']
        username = options['agent']
        farmer = options['farmer']
        if farmer:
            msisdns = [farmer]
        else:
            msisdns = [str(2776123456 + i) for i in range(total)]
        if username:
            actor = Actor.objects.get(user__username=username)
            agent = actor.as_agent()
            self.generate_farmers(msisdns, agent)
        else:
            self.generate_farmers(msisdns)

    def generate_farmers(self, msisdns, agent=None):
        for msisdn in msisdns:
            # create a district
            district = utils.random_district()
            farmergroup_name = "%s Farmer Group" % (district.name,)

            # create the farmer
            farmer = utils.create_farmer(msisdn=str(msisdn), name=utils.random_name(),
                        surname=utils.random_surname(), farmergroup_name=farmergroup_name)

            # cultivates two types of crops
            farmer.grows_crop(utils.random_crop())
            farmer.grows_crop(utils.random_crop())

            # create the agent with msisdn offset of the total generated to
            # avoid collissions on usernames
            msisdn = msisdn + total + 1
            if not agent:
                agent = utils.create_agent(msisdn=str(msisdn),
                            name=utils.random_name(),
                            surname=utils.random_surname())

            # create a market in the district
            market_name = '%s Market' % district.name
            market = utils.create_market(market_name, district)

            # have the farmer sells crops at that market through the agent
            farmer.operates_at(market, agent)

