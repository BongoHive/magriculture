from magriculture.fncs.utils import ImportCommand
from magriculture.fncs.models.actors import Farmer, FarmerGroup

class Command(ImportCommand):
    help = "Import farmer groups from an excel file"
    
    def handle_row(self, row):
        try:
            farmer = Farmer.objects.get(hh_id=row["HH id"])
            farmergroup, _ = FarmerGroup.objects.get_or_create(
                name=row["Farm grp Name"])
            farmer.farmergroup = farmergroup
            farmer.save()

        except Farmer.DoesNotExist:
            print 'Farmer with HH id %(HH id)s does not exist' % row