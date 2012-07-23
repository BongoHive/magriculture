from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from magriculture.fncs.models.actors import (FarmerGroup, Farmer,
        Agent, MarketMonitor, FarmerBusinessAdvisor, Actor, Identity)
from magriculture.fncs.models.geo import (Province, RPIArea, District, Ward,
        Zone, Market)
from magriculture.fncs.models.props import (Crop, CropUnit)
import random


NAMES = ['Aaliyah', 'Abayomi', 'Abebe', 'Abebi', 'Abena', 'Abeo', 'Ada',
            'Adah', 'Adana', 'Adanna', 'Adanya', 'Akili', 'Alika', 'Ama',
            'Amadi', 'Amai', 'Amare', 'Amari', 'Abayomi', 'Abiola', 'Abu',
            'Ade', 'Adeben', 'Adiel', 'Amarey', 'Amari', 'Aren', 'Azibo',
            'Bobo', 'Chiamaka', 'Chibale', 'Chidi', 'Chike', 'Dakarai',
            'Davu', 'Deion', 'Dembe', 'Diallo']

SURNAMES = ['Azikiwe', 'Awolowo', 'Bello', 'Balewa', 'Akintola', 'Okotie-Eboh',
            'Nzeogwu', 'Onwuatuegwu', 'Okafor', 'Okereke', 'Okeke', 'Okonkwo',
            'Okoye', 'Okorie', 'Obasanjo', 'Babangida', 'Buhari', 'Dimka',
            'Okar', 'Diya', 'Odili', 'Ibori', 'Igbinedion', 'Alamieyeseigha',
            'Yar\'Adua', 'Asari-Dokubo', 'Jomo-Gbomo', 'Anikulapo-Kuti', 'Iwu',
            'Anenih', 'Bamgboshe', 'Biobaku', 'Tinibu', 'Akinjide', 'Akinyemi',
            'Akiloye', 'Adeyemi', 'Adesida', 'Omehia', 'Sekibo', 'Amaechi',
            'Bankole', 'Nnamani', 'Ayim', 'Okadigbo', 'Ironsi', 'Ojukwu',
            'Danjuma', 'Effiong', 'Akpabio', 'Attah', 'Chukwumereije',
            'Akunyili', 'Iweala', 'Okonjo', 'Ezekwesili', 'Achebe', 'Soyinka',
            'Solarin', 'Gbadamosi', 'Olanrewaju', 'Magoro', 'Madaki', 'Jang',
            'Oyinlola', 'Oyenusi', 'Onyejekwe', 'Onwudiwe', 'Jakande',
            'Kalejaiye', 'Igwe', 'Eze', 'Obi', 'Ngige', 'Uba', 'Kalu',
            'Orji', 'Ohakim', 'Egwu', 'Adesina', 'Adeoye', 'Falana', 'Fagbure',
            'Jaja', 'Okilo', 'Okiro', 'Balogun', 'Alakija', 'Akenzua',
            'Akerele', 'Ademola', 'Onobanjo', 'Aguda', 'Okpara', 'Mbanefo',
            'Mbadinuju', 'Boro', 'Ekwensi', 'Gowon', 'Saro-Wiwa']

DISTRICT_NAMES = ['Chibombo', 'Kabwe', 'Kapiri Mposhi', 'Mkushi', 'Mumbwa',
    'Serenje', 'Chililabombwe', 'Chingola', 'Kalulushi', 'Kitwe', 'Luanshya',
    'Lufwanyama', 'Masaiti', 'Mpongwe', 'Mufulira', 'Ndola', 'Chadiza',
    'Chama', 'Chipata', 'Katete', 'Lundazi', 'Mambwe', 'Nyimba', 'Petauke',
    'Chiengi', 'Kawambwa', 'Mansa', 'Milenge', 'Mwense', 'Nchelenge', 'Samfya',
    'Chongwe', 'Kafue', 'Luangwa', 'Lusaka', 'Chavuma', 'Kabompo', 'Kasempa',
    'Mufumbwe', 'Mwinilunga', 'Solwezi', 'Zambezi', 'Chilubi', 'Chinsali',
    'Isoka', 'Kaputa', 'Kasama', 'Luwingu', 'Mbala', 'Mpika', 'Mporokoso',
    'Mpulungu', 'Mungwi', 'Nakonde', 'Choma', 'Gwembe', 'Itezhi Tezhi\'Kalomo',
    'Kazungula', 'Livingstone', 'Mazabuka', 'Monze', 'Namwala\'Siavonga',
    'Sinazongwe', 'Kalabo', 'Kaoma', 'Lukulu', 'Mongu', 'Senanga', 'Sesheke',
    'Shangombo']

CROP_NAMES = [
    'Maize', 'Sorghum', 'Rice', 'Millet', 'Wheat', 'Cassava', 'Soybean',
    'Sunflowers', 'Sugarcane', 'Tobacco', 'Coffee'
]

CROP_UNIT_NAMES = [
    'Boxes', 'Kilos', 'Bunches'
]

AGRICULTURE_QUOTES = [
    """Advances in technology will continue to reach far into every sector of our economy. Future job and economic growth in industry, defense, transportation, agriculture, health care, and life sciences is directly related to scientific advancement. - Christopher Bond """,
    """After the First World War the economic problem was no longer one of production. It was the problem of finding markets to get the output of industry and agriculture dispersed and consumed. - John Boyd Orr """,
    """Agriculture not only gives riches to a nation, but the only riches she can call her own. - Samuel Johnson """,
    """Agriculture was the first manufacturing industry in America and represents the best of all of us. - Zack Wamp """,
    """America was indebted to immigration for her settlement and prosperity. That part of America which had encouraged them most had advanced most rapidly in population, agriculture and the arts. - James Madison """,
    """As an integral part of the Department of Agriculture, the Animal and Plant Health Inspection Service monitors our Nation's agriculture to protect against agricultural pests and diseases. - Mike Rogers """,
    """As the first Member of Congress from western Washington to serve on the House Agriculture Committee in over 50 years, I am proud to represent the needs of our agriculture community. - Rick Larsen """,
    """As the tension eases, we must look in the direction of agriculture, industry and education as our final goals, and toward democracy under Mr Mubarak. - Naguib Mahfouz """,
    """Because of technological limits, there is a certain amount of food that we can produce per acre. If we were to have intensive greenhouse agriculture, we could have much higher production. - Ralph Merkle """,
    """Before the discovery of agriculture mankind was everywhere so divided, the size of each group being determined by the natural fertility of its locality. - Arthur Keith """,
    """Bring diversity back to agriculture. That's what made it work in the first place. - David R. Brower """,
    """By increasing the use of renewable fuels such as ethanol and bio-diesel, and providing the Department of Energy with a budget to create more energy efficiency options, agriculture can be the backbone of our energy supply as well. - John Salazar """,
    """Consequently the student who is devoid of talent will derive no more profit from this work than barren soil from a treatise on agriculture.- Quintilian """,
    """Contrasting sharply, in the developing countries represented by India, Pakistan, and most of the countries in Asia and Africa, seventy to eighty percent of the population is engaged in agriculture, mostly at the subsistence level. - Norman Borlaug """,
    """Every major food company now has an organic division. There's more capital going into organic agriculture than ever before. - Michael Pollan """,
    """High tech companies that focus on research, development and production will learn that they can be the perfect complement to our world-renowned agriculture heritage. - Alan Autry """,
    """I have always said there is only one thing that can bring our nation down - our dependence on foreign countries for food and energy. Agriculture is the backbone of our economy. - John Salazar """,
    """If we win, we'll make history, and I'll serve you on the Agriculture Committee. - George Nethercutt""",
]

def reload_record(record):
    return record.__class__.objects.get(pk=record.pk)

def random_quote():
    return random.choice(AGRICULTURE_QUOTES)

def random_name():
    return random.choice(NAMES)

def random_surname():
    return random.choice(SURNAMES)

def random_full_name():
    return '%s %s' % (random_name(), random_surname())

def random_district_name():
    return random.choice(DISTRICT_NAMES)

def random_crop_name():
    return random.choice(CROP_NAMES)

def random_district():
    return create_district(random_district_name(), create_province("province"))

def random_crop():
    return create_crop(random_crop_name())

def random_message_text():
    messages = [
        'I need more %s, please bring if you have',
        'There are too many %s being sold. Don\'t bring any more',
        'Increasing demand for %s this year, please prepare for demand 3 months from now.',
        'Hi, haven\'t been able to get a hold of you lately. Where are is %s?',
    ]
    crop_name = random_crop_name().lower()
    return random.choice(messages) % crop_name

def create_province(name):
    province, _ = Province.objects.get_or_create(name=name)
    return province

def create_rpiarea(name):
    rpiarea, _ = RPIArea.objects.get_or_create(name=name)
    rpiarea.provinces.add(create_province("province in %s" % name))
    return rpiarea

def create_district(name, province):
    district, _ = District.objects.get_or_create(province=province, name=name)
    return district

def create_ward(name, district):
    ward, _ = Ward.objects.get_or_create(name="Ward in %s" %
            district.name, district=district)
    return ward

def create_zone(name, rpiarea):
    zone, _ = Zone.objects.get_or_create(rpiarea=rpiarea, name=name)
    return zone

def create_market(name, district):
    market, _ = Market.objects.get_or_create(name=name, district=district)
    return market

def create_farmergroup(name, zone, district, ward):
    fg, _ = FarmerGroup.objects.get_or_create(name=name, district=district, zone=zone)
    fg.wards.add(ward)
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
        farmergroup_name="farmer group", province_name="province",
        zone_name="zone", district_name="district", ward_name="ward",
        rpiarea_name="rpiarea"):
    rpiarea = create_rpiarea(rpiarea_name)
    province = create_province(province_name)
    zone = create_zone(zone_name, rpiarea)
    district = create_district(district_name, province)
    ward = create_ward(ward_name, district)
    farmergroup = create_farmergroup(farmergroup_name, zone, district,
            ward)
    user, _ = User.objects.get_or_create(username=msisdn)
    user.first_name = name
    user.last_name = surname
    user.save()
    farmer, _ = Farmer.objects.get_or_create(farmergroup=farmergroup,
            actor=user.get_profile())
    return farmer

def create_agent(msisdn="27761234568", name="name", surname="surname"):
    user, _ = User.objects.get_or_create(username=msisdn)
    user.first_name = name
    user.last_name = surname
    user.save()
    agent, _ = Agent.objects.get_or_create(actor=user.get_profile())
    return agent

def create_market_monitor(name="market monitor"):
    user, _ = User.objects.get_or_create(username=name, first_name=name)
    market_monitor, _ = MarketMonitor.objects.get_or_create(actor=user.get_profile())
    return market_monitor

def create_fba(msisdn='27761234568', name='name', surname='surname'):
    user, _ = User.objects.get_or_create(username=msisdn)
    user.first_name = name
    user.last_name = surname
    user.save()
    fba, _ = FarmerBusinessAdvisor.objects.get_or_create(
                actor=user.get_profile())
    return fba

def is_farmer(msisdn):
    try:
        return Actor.find(msisdn).as_farmer()
    except Identity.DoesNotExist:
        return False

def farmer_url(pk, suffix='', **kwargs):
    if suffix:
        suffix = '_%s' % suffix
    defaults = {
        'farmer_pk': pk
    }
    defaults.update(kwargs)
    return reverse('fncs:farmer%s' % suffix, kwargs=defaults)

def take_in(market, agent, farmer, amount, unit_name, crop_name):
    crop = create_crop(crop_name, units=[unit_name])
    unit = create_crop_unit(unit_name)
    return agent.take_in_crop(market, farmer, amount, unit, crop)

def sell(receipt, amount, price):
    return receipt.agent.register_sale(receipt, amount, price)

