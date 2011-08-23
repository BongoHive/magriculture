from magriculture.fncs.utils import ImportCommand
from magriculture.fncs.models.geo import Province

class Command(ImportCommand):
    help = "Import districts from an excel file"
    
    def handle_row(self, row):
        province, _ = Province.objects.get_or_create(code=row['ProvinceCode'],
            name=row['ProvinceName'], country=row['CountryCode'])
