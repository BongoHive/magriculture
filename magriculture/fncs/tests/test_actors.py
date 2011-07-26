from django.test import TestCase
from django.contrib.auth.models import User
from magriculture.fncs.models.actors import (Actor, FarmerGroup, Farmer, Agent)
from magriculture.fncs.models.geo import (Province, RPIArea, District, Ward,
        Village, Zone, Market)

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

def create_farmer(name="farmer", farmergroup_name="farmer group",
        rpiarea_name="rpi area", zone_name="zone", district_name="district",
        village_name="village"):
    rpiarea = create_rpiarea(rpiarea_name)
    zone = create_zone(zone_name, rpiarea)
    district = create_district(district_name, rpiarea)
    village = create_village(village_name, district)
    farmergroup = create_farmer_group(farmergroup_name, zone, district,
            village)
    user, _ = User.objects.get_or_create(username=name, first_name=name)
    farmer, _ = Farmer.objects.get_or_create(farmergroup=farmergroup,
            actor=user.get_profile())
    return farmer

def create_agent(name="agent"):
    user, _ = User.objects.get_or_create(username=name, first_name=name)
    agent, _ = Agent.objects.get_or_create(actor=user.get_profile())
    return agent

class ActorTestCase(TestCase):
    
    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def test_actor_creation(self):
        user = User.objects.create_user('username','email@domain.com')
        actor = user.get_profile()
        self.assertTrue(isinstance(actor, Actor))
    
    def test_farmer_creation(self):
        farmer = create_farmer() 
        self.assertEquals(farmer.actor.user.first_name, "farmer")
        self.assertEquals(farmer.farmergroup.name, "farmer group")
        self.assertEquals(farmer.agents.count(), 0)
    
    def test_agent_creation(self):
        agent = create_agent()
        self.assertEquals(agent.farmers.count(), 0)
        self.assertEquals(agent.markets.count(), 0)

    def test_farmer_agent_link(self):
        farmer = create_farmer()
        market = create_market("market", farmer.farmergroup.district)
        agent = create_agent()

        farmer.sells_at(market, agent)
        self.assertTrue(agent.sells_for(farmer, market))
        self.assertIn(market, agent.markets.all())
        self.assertIn(farmer, agent.farmers.all())
        self.assertIn(market, farmer.markets.all())
    
