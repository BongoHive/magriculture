from magriculture.fncs.utils import ImportCommand
from magriculture.fncs.models.props import Crop

class Command(ImportCommand):
    help = "Import crops from an excel file"
    
    def handle_row(self, row):
        crop, _ = Crop.objects.get_or_create(name=row['CropName'])
        crop.description = row['CropDescription']
        crop.save()
