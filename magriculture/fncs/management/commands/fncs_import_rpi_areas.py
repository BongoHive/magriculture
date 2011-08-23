from magriculture.fncs.utils import ImportCommand
from magriculture.fncs.models.geo import RPIArea, Province

class Command(ImportCommand):
    help = "Import RPI Areas from an excel file"
    
    def handle_row(self, row):
        try:
            rpiarea, _ = RPIArea.objects.get_or_create(name=row['RPI AREA'])
            province = Province.objects.get(name=row['PROVINCE'])
            rpiarea.provinces.add(province)
        except Province.DoesNotExist:
            print 'Province %s does not exist' % row['PROVINCE']