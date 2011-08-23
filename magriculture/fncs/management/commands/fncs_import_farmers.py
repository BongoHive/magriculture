from magriculture.fncs.utils import ImportCommand
from magriculture.fncs.models.actors import Farmer
from django.contrib.auth.models import User, Group

class Command(ImportCommand):
    help = "Import farmers from an excel file"
    
    def handle_row(self, row):
        user, _ = User.objects.get_or_create(username=row['HH id'])
        group, _ = Group.objects.get_or_create(name="FNCS Farmers")
        
        user.groups.add(group)
        user.first_name = row['F_NAME']
        user.last_name = row['S_NAME']
        user.save()
        
        actor = user.get_profile()
        actor.gender = row['sex']
        actor.save()
        
        farmer, _ = Farmer.objects.get_or_create(actor=actor)
        farmer.participant_type = row['Main participant type']
        farmer.number_of_males = row['Family sze M'] or None
        farmer.number_of_females = row['Family size F'] or None
        farmer.save()
        