from magriculture.fncs.utils import ImportCommand
from magriculture.fncs.models.geo import District, Ward

class Command(ImportCommand):
    help = "Import wards from an excel file"
    
    def handle_row(self, row):
        try:
            district = District.objects.get(code=row['DistrictCode'])
            ward, _ = Ward.objects.get_or_create(code=row['WardCode'], 
                district=district)
            ward.name = row['WardName']
            ward.save()
        except District.DoesNotExist:
            print 'District with code %(DistrictCode)s does not exist' % row