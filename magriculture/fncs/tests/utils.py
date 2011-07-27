from django.contrib.auth.models import User
from magriculture.fncs.models.actors import (Actor, FarmerGroup, Farmer, 
        Agent, MarketMonitor)
from magriculture.fncs.models.geo import (Province, RPIArea, District, Ward,
        Village, Zone, Market)
from magriculture.fncs.models.props import (Crop, CropUnit, Transaction, Offer)
import random

NAMES = ['Aaliyah', 'Abayomi', 'Abebe', 'Abebi', 'Abena', 'Abeo', 'Ada', 
            'Adah', 'Adana', 'Adanna', 'Adanya', 'Akili', 'Alika', 'Ama', 
            'Amadi', 'Amai', 'Amare', 'Amari', 'Abayomi', 'Abiola', 'Abu', 
            'Ade', 'Adeben', 'Adiel', 'Amarey', 'Amari', 'Aren', 'Azibo', 
            'Bobo', 'Chiamaka', 'Chibale', 'Chidi', 'Chike', 'Dakarai', 
            'Davu', 'Deion', 'Dembe', 'Diallo']
SURNAMES = ['Azikiwe','Awolowo','Bello','Balewa','Akintola','Okotie-Eboh',
            'Nzeogwu','Onwuatuegwu','Okafor','Okereke','Okeke','Okonkwo',
            'Okoye','Okorie','Obasanjo','Babangida','Buhari','Dimka','Okar',
            'Diya','Odili','Ibori','Igbinedion','Alamieyeseigha','Yar\'Adua',
            'Asari-Dokubo','Jomo-Gbomo','Anikulapo-Kuti','Iwu','Anenih',
            'Bamgboshe','Biobaku','Tinibu','Akinjide','Akinyemi','Akiloye',
            'Adeyemi','Adesida','Omehia','Sekibo','Amaechi','Bankole','Nnamani',
            'Ayim','Okadigbo','Ironsi','Ojukwu','Danjuma','Effiong','Akpabio',
            'Attah','Chukwumereije','Akunyili','Iweala','Okonjo','Ezekwesili',
            'Achebe','Soyinka','Solarin','Gbadamosi','Olanrewaju','Magoro',
            'Madaki','Jang','Oyinlola','Oyenusi','Onyejekwe','Onwudiwe',
            'Jakande','Kalejaiye','Igwe','Eze','Obi','Ngige','Uba','Kalu',
            'Orji','Ohakim','Egwu','Adesina','Adeoye','Falana','Fagbure',
            'Jaja','Okilo','Okiro','Balogun','Alakija','Akenzua','Akerele',
            'Ademola','Onobanjo','Aguda','Okpara','Mbanefo','Mbadinuju','Boro',
            'Ekwensi','Gowon', 'Saro-Wiwa']

def random_name():
    return random.choice(NAMES)

def random_surname():
    return random.choice(SURNAMES)

def random_full_name():
    return '%s %s' % (random_name(), random_surname())

def create_province(name):
    province, _ = Province.objects.get_or_create(name=name)
    return province

def create_rpiarea(name):
    rpiarea, _ = RPIArea.objects.get_or_create(name=name)
    rpiarea.provinces.add(create_province("province in %s" % name))
    return rpiarea

def create_district(name, rpiarea):
    district, _ = District.objects.get_or_create(rpiarea=rpiarea, name=name)
    return district

def create_village(name, district):
    ward, _ = Ward.objects.get_or_create(name="Ward in %s" %
            district.name, district=district)
    village, _ = Village.objects.get_or_create(name=name, ward=ward)
    return village

def create_zone(name, rpiarea):
    zone, _ = Zone.objects.get_or_create(rpiarea=rpiarea, name=name)
    return zone

def create_market(name, district):
    market, _ = Market.objects.get_or_create(name=name, district=district)
    return market

def create_farmer_group(name, zone, district, village):
    fg, _ = FarmerGroup.objects.get_or_create(name=name, district=district, zone=zone)
    fg.villages.add(village)
    return fg

def create_crop(name, units=["boxes","bunches","kilos"]):
    crop, _ = Crop.objects.get_or_create(name=name)
    for unitname in units:
        crop.units.add(create_crop_unit(unitname))
    return crop

def create_crop_unit(name):
    unit, _ = CropUnit.objects.get_or_create(name=name)
    return unit

def create_farmer(msisdn='27761234567', name="name", surname="surname", 
        farmergroup_name="farmer group", rpiarea_name="rpi area", 
        zone_name="zone", district_name="district", village_name="village"):
    rpiarea = create_rpiarea(rpiarea_name)
    zone = create_zone(zone_name, rpiarea)
    district = create_district(district_name, rpiarea)
    village = create_village(village_name, district)
    farmergroup = create_farmer_group(farmergroup_name, zone, district,
            village)
    user, _ = User.objects.get_or_create(username=msisdn, first_name=name,
            last_name=surname)
    farmer, _ = Farmer.objects.get_or_create(farmergroup=farmergroup,
            actor=user.get_profile())
    return farmer

def create_agent(name="agent"):
    user, _ = User.objects.get_or_create(username=name, first_name=name)
    agent, _ = Agent.objects.get_or_create(actor=user.get_profile())
    return agent

def create_market_monitor(name="market monitor"):
    user, _ = User.objects.get_or_create(username=name, first_name=name)
    market_monitor, _ = MarketMonitor.objects.get_or_create(actor=user.get_profile())
    return market_monitor
