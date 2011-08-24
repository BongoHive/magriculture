from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from magriculture.fncs.models.geo import District
from magriculture.fncs.models.props import Message, GroupMessage, Note
from datetime import datetime

def create_actor(sender, instance, created, **kwargs):
    if created:
        Actor.objects.create(user=instance)
    else:
        actor = instance.get_profile()
        actor.name = '%s %s' % (instance.first_name.strip(), 
                                    instance.last_name.strip())
        actor.save()

post_save.connect(create_actor, sender=User)


class Actor(models.Model):
    """A person with access to FNCS and who is able to interact with the
    data avaible."""
    user = models.OneToOneField('auth.User')
    # TODO: do we need a name here, it's duplicated from the Django User model
    name = models.CharField(blank=False, max_length=255)
    gender = models.CharField(blank=True, max_length=100, choices=(
        ('M', 'Male'),
        ('F', 'Female'),
    ))
    
    def as_agent(self):
        agents = self.agent_set.all()
        if agents.count() > 1:
            raise Exception, 'More than one agent for an actor'
        return agents[0]
    
    def as_marketmonitor(self):
        marketmonitors = self.marketmonitor_set.all()
        if marketmonitors.count() > 1:
            raise Exception, 'More than one marketmonitor for an actor'
        return marketmonitors[0]
    
    def send_message(self, recipient, message, group):
        return Message.objects.create(sender=self, recipient=recipient, 
            content=message, group=group)
    
    class Meta:
        ordering = ['-name']
        get_latest_by = 'pk'
        app_label = 'fncs'
    
    def __unicode__(self): # pragma: no cover
        return u"%s (Actor)" % self.name
    

class Farmer(models.Model):
    """A farmer is an actor that provides goods to be sold in a market"""
    actor = models.ForeignKey('fncs.Actor')
    farmergroup = models.ForeignKey('fncs.FarmerGroup', null=True)
    agents = models.ManyToManyField('fncs.Agent')
    markets = models.ManyToManyField('fncs.Market')
    wards = models.ManyToManyField('fncs.Ward')
    crops = models.ManyToManyField('fncs.Crop')
    hh_id = models.CharField(blank=True, max_length=100)
    participant_type = models.CharField(blank=True, max_length=100, choices=(
        ('Y', 'Y'),
        ('N', 'N'),
    ))
    number_of_males = models.IntegerField(blank=True, null=True)
    number_of_females = models.IntegerField(blank=True, null=True)
    
    class Meta:
        app_label = 'fncs'
        get_latest_by = 'actor__pk'
    
    def grows_crop(self, crop):
        self.crops.add(crop)
    
    def is_growing_crop(self, crop):
        return self.crops.filter(pk=crop.pk).exists()
    
    def grows_crops_exclusively(self, crops):
        """Warning this is a destructive method!"""
        self.crops.clear()
        for crop in crops:
            self.grows_crop(crop)
    
    def districts(self):
        return District.objects.filter(market__in=self.markets.all())
    
    def transactions(self):
        return self.transaction_set.all()
    
    def sells_at(self, market, agent):
        # the farmer and the agent need to sell at the given market
        self.markets.add(market)
        agent.markets.add(market)
        # the farmer has the agent registered as an agent
        self.agents.add(agent)
        # the agent has the farmer registered as a farmer
        agent.farmers.add(self)
    
    def sells_at_markets_exclusively(self, markets):
        """Warning this is a destructive method!"""
        self.markets.clear()
        for market in markets:
            self.markets.add(market)
    
    @classmethod
    def create(cls, msisdn, name, surname, farmergroup):
        user = User.objects.create(username=msisdn)
        user.first_name = name
        user.last_name = surname
        user.save()
        
        actor = user.get_profile()
        
        farmer = cls(actor=actor, farmergroup=farmergroup)
        farmer.save()
        
        return farmer

    def __unicode__(self): # pragma: no cover
        return self.actor.name


class FarmerGroup(models.Model):
    """A collection of farmers in a geographic area"""
    name = models.CharField(blank=False, max_length=255)
    zone = models.ForeignKey('fncs.Zone', null=True)
    district = models.ForeignKey('fncs.District', null=True)
    wards = models.ManyToManyField('fncs.Ward')
    extensionofficer = models.ForeignKey('fncs.ExtensionOfficer', null=True)
    
    def members(self):
        return self.farmer_set.all()
    
    class Meta:
        ordering = ['-name']
        get_latest_by = 'pk'
        app_label = 'fncs'
    
    def __unicode__(self): # pragma: no cover
        return self.name


class ExtensionOfficer(models.Model):
    """A extension officer is an actor that is linked to a geographic zone and
    communicates with farmer groups"""
    actor = models.ForeignKey('fncs.Actor')
    
    class Meta:
        app_label = 'fncs'
    
    def __unicode__(self): # pragma: no cover
        return u"%s (ExtensionOfficer)" % (self.actor,)

class MarketMonitor(models.Model):
    """A market monitor is an actor that is linked to a market and provides
    input on opening prices of goods availabe in that market"""
    actor = models.ForeignKey('fncs.Actor')
    markets = models.ManyToManyField('fncs.Market')
    rpiareas = models.ManyToManyField('fncs.RPIArea')
    
    def register_offer(self, market, crop, unit, price_floor, price_ceiling):
        offer = self.offer_set.create(crop=crop, unit=unit, 
                    price_floor=price_floor, price_ceiling=price_ceiling, 
                    market=market)
        self.markets.add(market)
        for rpiarea in market.rpiareas():
            self.rpiareas.add(rpiarea)
        return offer
    
    def is_monitoring(self, market):
        return self.markets.filter(pk=market.pk).exists()
    
    class Meta:
        app_label = 'fncs'
    
    def __unicode__(self): # pragma: no cover
        return u"%s (MarketMonitor)" % (self.actor,)

class Agent(models.Model):
    """An agent is an actor that is linked to a market and does a financial
    transaction on behalf of a Farmer"""
    actor = models.ForeignKey('fncs.Actor')
    farmers = models.ManyToManyField('fncs.Farmer')
    markets = models.ManyToManyField('fncs.Market')
    
    class Meta:
        app_label = 'fncs'
    
    def is_selling_for(self, farmer, market):
        return (self.farmers.filter(pk=farmer.pk).exists() and
                self.markets.filter(pk=market.pk).exists() and
                farmer.markets.filter(pk=market.pk).exists())
    
    def register_sale(self, market, farmer, crop, unit, price, amount):
        transaction = self.transaction_set.create(market=market, 
                    farmer=farmer, crop=crop, unit=unit, price=price, 
                    amount=amount, created_at=datetime.now())
        self.markets.add(market)
        self.farmers.add(farmer)
        farmer.markets.add(market)
        farmer.crops.add(crop)
        return transaction
    
    def sales_for(self, farmer):
        return self.transaction_set.filter(farmer=farmer)
    
    def send_message_to_farmer(self, farmer, message, group=None):
        return self.actor.send_message(farmer.actor, message, group)
    
    def send_message_to_farmergroups(self, farmergroups, message):
        groupmessage = GroupMessage.objects.create(sender=self.actor, 
                        content=message)
        for farmergroup in farmergroups:
            groupmessage.farmergroups.add(farmergroup)
            for farmer in farmergroup.members():
                self.send_message_to_farmer(farmer, message, groupmessage)
        return groupmessage
    
    def write_note(self, farmer, note):
        return Note.objects.create(owner=self.actor, about_actor=farmer.actor,
            content=note)
    
    def notes_for(self, farmer):
        return self.actor.note_set.filter(about_actor=farmer.actor)
    
    def __unicode__(self): # pragma: no cover
        return self.actor.name

