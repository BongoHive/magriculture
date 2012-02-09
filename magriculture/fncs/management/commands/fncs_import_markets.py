from magriculture.fncs.utils import ImportCommand
from magriculture.fncs.models.geo import District, Market

class Command(ImportCommand):
    help = "Import markets from an excel file"

    def handle_row(self, row):
        try:
            district = District.objects.get(name=row['District'])
            market, _ = Market.objects.get_or_create(name=row['MarketName'],
                district=district)
            market.volume = row['MarketVolume'].split(' ')[0].lower()
            market.save()
        except District.DoesNotExist:
            print 'District with name %(District)s does not exist' % row