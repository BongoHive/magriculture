from django.db import models

class Actor(models.Model):
    """A person with access to FNCS and who is able to interact with the
    data avaible."""
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
    
    class Meta:
        app_label = 'fncs'
    
    def __unicode__(self):
        return u"%s (Farmer)" % (self.actor,)


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
    
    def __unicode__(self):
        return u"%s (Agent)" % (self.actor,)
