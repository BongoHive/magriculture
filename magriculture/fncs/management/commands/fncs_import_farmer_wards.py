from magriculture.fncs.utils import ImportCommand
from magriculture.fncs.models.actors import Farmer
from magriculture.fncs.models.geo import Ward

class Command(ImportCommand):
    help = "Import wards for farmers from an excel file"
    
    def handle_row(self, row):
        try:
            farmer = Farmer.objects.get(actor__user__username=row['HH id'])
            ward = Ward.objects.get(code=row['WardCode'])
            farmer.wards.add(ward)
        except Ward.DoesNotExist:
            print 'Ward with code %(WardCode)s does not exist' % row