from magriculture.fncs.utils import ImportCommand
from magriculture.fncs.models.geo import District, Province

class Command(ImportCommand):
    help = "Import districts from an excel file"
    
    def handle_row(self, row):
        try:
            province = Province.objects.get(code=row['ProvinceCode'])
            district, _ = District.objects.get_or_create(code=row['DistrictCode'],
                province=province)
            district.name = row['DistrictName']
            district.save()
        except Province.DoesNotExist:
            print 'Province with code %(ProvinceCode)s does not exist' % row