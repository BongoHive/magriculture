from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
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
            utils.create_farmer(msisdn=str(msisdn), name=utils.random_name(),
                    surname=utils.random_surname())
