from magriculture.fncs.utils import ImportCommand
from magriculture.fncs.models.props import Crop, CropUnit

class Command(ImportCommand):
    help = "Import crop units from an excel file"
    
    def handle_row(self, row):
        try:
            crop = Crop.objects.get(name=row['CropType'])
            unit, _ = CropUnit.objects.get_or_create(name=row['Unit'])
            unit.description = row['UnitDescription']
            unit.save()
            crop.units.add(unit)
        except Crop.DoesNotExist:
            print 'Crop does not exist for %s' % row['CropType']