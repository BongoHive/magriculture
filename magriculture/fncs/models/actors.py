from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from magriculture.fncs.models.geo import District
from magriculture.fncs.models.props import Transaction

def create_actor(sender, instance, created, **kwargs):
    if created:
        Actor.objects.create(user=instance)
    else:
        actor = instance.get_profile()
        actor.name = '%s %s' % (instance.first_name, instance.last_name)
        actor.save()

post_save.connect(create_actor, sender=User)

class Actor(models.Model):
    """A person with access to FNCS and who is able to interact with the
    data avaible."""
    user = models.OneToOneField('auth.User')
    # TODO: do we need a name here, it's duplicated from the Django User model
    name = models.CharField(blank=False, max_length=255)
    
    class Meta:
        ordering = ['-name']
        get_latest_by = 'pk'
        app_label = 'fncs'
    
    def __unicode__(self):
        return u"%s (Actor)" % self.name
    

class Farmer(models.Model):
    """A farmer is an actor that provides goods to be sold in a market"""
    actor = models.ForeignKey('fncs.Actor')
    farmergroup = models.ForeignKey('fncs.FarmerGroup')
    agents = models.ManyToManyField('fncs.Agent')
    markets = models.ManyToManyField('fncs.Market')
    crops = models.ManyToManyField('fncs.Crop')
    
    class Meta:
        app_label = 'fncs'
        get_latest_by = 'actor__pk'
    
    def grows_crop(self, crop):
        self.crops.add(crop)
    
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

    def __unicode__(self):
        return self.actor.name


class FarmerGroup(models.Model):
    """A collection of farmers in a geographic area"""
    name = models.CharField(blank=False, max_length=255)
    zone = models.ForeignKey('fncs.Zone')
    district = models.ForeignKey('fncs.District')
    villages = models.ManyToManyField('fncs.Village')
    extensionofficer = models.ForeignKey('fncs.ExtensionOfficer', null=True)
    
    class Meta:
        ordering = ['-name']
        get_latest_by = 'pk'
        app_label = 'fncs'
    
    def __unicode__(self):
        return u"%s (FarmerGroup)" % (self.name,)


class ExtensionOfficer(models.Model):
    """A extension officer is an actor that is linked to a geographic zone and
    communicates with farmer groups"""
    actor = models.ForeignKey('fncs.Actor')
    
    class Meta:
        app_label = 'fncs'
    
    def __unicode__(self):
        return u"%s (ExtensionOfficer)" % (self.actor,)

class MarketMonitor(models.Model):
    """A market monitor is an actor that is linked to a market and provides
    input on opening prices of goods availabe in that market"""
    actor = models.ForeignKey('fncs.Actor')
    markets = models.ManyToManyField('fncs.Market')
    rpiareas = models.ManyToManyField('fncs.RPIArea')
    
    def register_offer(self, market, agent, crop, unit, price):
        offer = self.offer_set.create(crop=crop, unit=unit, agent=agent, 
                                        price=price, market=market)
        self.markets.add(market)
        self.rpiareas.add(market.district.rpiarea)
        return offer
        
    
    def is_monitoring(self, market):
        return self.markets.filter(pk=market.pk).exists()
    
    class Meta:
        app_label = 'fncs'
    
    def __unicode__(self):
        return u"%s at %s (MarketMonitor)" % (self.actor, self.market)

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
                    amount=amount)
        self.markets.add(market)
        self.farmers.add(farmer)
        farmer.markets.add(market)
        return transaction
    
    def __unicode__(self):
        return self.actor.name
