from django.core.management.base import BaseCommand
from magriculture.fncs.tests import utils
from optparse import make_option

class Command(BaseCommand):
    help = "Generate sample farmer data"
    option_list = BaseCommand.option_list + (
        make_option('--total', dest='total', type='int', default=500, 
                        help='How many farmers to create'),
    )
    def handle(self, *args, **options):
        total = options['total']
        for i in range(total):
            msisdn = 2776123456 + i
            
            # create the farmer
            farmer = utils.create_farmer(msisdn=str(msisdn), name=utils.random_name(),
                        surname=utils.random_surname())
            
            # cultivates two types of crops
            farmer.grows_crop(utils.random_crop())
            farmer.grows_crop(utils.random_crop())
            
            # create the agent with msisdn offset of the total generated to
            # avoid collissions on usernames
            msisdn = msisdn + total + 1
            agent = utils.create_agent(msisdn=str(msisdn), name=utils.random_name(),
                        surname=utils.random_surname())
            
            # create a district
            district = utils.random_district()
            
            # create a market in the district
            market_name = '%s Market' % district.name
            market = utils.create_market(market_name, district)
            
            # have the farmer sells crops at that market through the agent
            farmer.sells_at(market, agent)
