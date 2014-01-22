from magriculture.fncs.utils import ImportCommand


class Command(ImportCommand):
    help = ("If a farmer doesn't have a district, the farmers markets"
            " districts are assumed to be his market")


    def handle(self, *args, **options):
        pass
