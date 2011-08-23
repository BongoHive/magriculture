from django.db import models
from django.template.defaultfilters import floatformat

class Crop(models.Model):
    """A crop is an item that is being traded"""
    name = models.CharField(blank=False, max_length=255)
    description = models.TextField(blank=True)
    units = models.ManyToManyField('fncs.CropUnit')
    
    class Meta:
        ordering = ['name']
        get_latest_by = 'pk'
        app_label = 'fncs'

    def __unicode__(self): # pragma: no cover
        return self.name

class CropUnit(models.Model):
    """A unit that a crop is traded in"""
    name = models.CharField(blank=False, max_length=255)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-name']
        get_latest_by = 'pk'
        app_label = 'fncs'
    
    def __unicode__(self): # pragma: no cover
        return self.name

class Transaction(models.Model):
    """A transaction is an exchange of a crop at a certain unit
    at a given price"""
    crop = models.ForeignKey('fncs.Crop')
    unit = models.ForeignKey('fncs.CropUnit')
    farmer = models.ForeignKey('fncs.Farmer')
    agent = models.ForeignKey('fncs.Agent')
    market = models.ForeignKey('fncs.Market')
    quality = models.IntegerField(blank=False, default=5, choices=(
        (10, 'Excellent'),
        (7, 'Good'),
        (5, 'Standard'),
        (3, 'Mediocre'),
        (0, 'Poor'),
    ))
    amount = models.FloatField('Quantity')
    price = models.FloatField()
    total = models.FloatField()
    created_at = models.DateTimeField(blank=False)
    
    @classmethod
    def price_history_for(cls, market, crop, unit):
        return cls.objects.filter(market=market, crop=crop, unit=unit).\
                values_list('price', flat=True)
    
    def save(self, *args, **kwargs):
        if not self.total:
            self.total = self.amount * self.price
        super(Transaction, self).save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'
        app_label = 'fncs'
    
    def __unicode__(self): # pragma: no cover
        return u"%s %s of %s" % (floatformat(self.amount), self.unit, self.crop)

class Offer(models.Model):
    """An offer is like a transaction but differs because no goods
    are being exchanged. It is setting the opening prices of goods
    at the start of the day
    """
    
    crop = models.ForeignKey('fncs.Crop')
    unit = models.ForeignKey('fncs.CropUnit')
    market = models.ForeignKey('fncs.Market')
    marketmonitor = models.ForeignKey('fncs.MarketMonitor')
    price_floor = models.FloatField('Floor price')
    price_ceiling = models.FloatField('Ceiling price')
    created_at = models.DateTimeField(blank=False, auto_now_add=True)
    
    @classmethod
    def price_history_for(cls, market, crop, unit):
        return cls.objects.filter(market=market, crop=crop, unit=unit). \
                values_list('price_floor', 'price_ceiling')
    
    @classmethod
    def average_price_history_for(cls, market, crop, unit):
        return [sum(price_range) / 2.0 for price_range in 
                    cls.price_history_for(market, crop, unit)]
    
    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'
        app_label = 'fncs'

    def __unicode__(self): # pragma: no cover
        return u"%s of %s between %s and %s (Offer)" % (self.unit, self.crop,
            self.price_floor, self.price_ceiling)

class Message(models.Model):
    """A message sent or received via FNCS"""
    sender = models.ForeignKey('fncs.Actor', related_name='sentmessages_set')
    recipient = models.ForeignKey('fncs.Actor', related_name='receivedmessages_set')
    content = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey('fncs.GroupMessage', null=True)
    
    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'
        app_label = 'fncs'
    
    def __unicode__(self): # pragma: no cover
        return u"Message from %s to %s at %s" % (self.sender, self.recipient,
            self.created_at)

class GroupMessage(models.Model):
    sender = models.ForeignKey('fncs.Actor')
    farmergroups = models.ManyToManyField('fncs.FarmerGroup')
    content = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'
        app_label = 'fncs'
    
    def __unicode__(self): # pragma: no cover
        return 'GroupMessage from %s to %s groups at %s' % (self.sender, 
            self.farmergroups.count(), self.created_at)

class Note(models.Model):
    """A note written by an actor and having another actor as the subject
    of the note"""
    owner = models.ForeignKey('fncs.Actor')
    about_actor = models.ForeignKey('fncs.Actor', related_name='attachednote_set')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'
        app_label = 'fncs'
    
    def __unicode__(self): # pragma: no cover
        return u"Note from %s to %s at %s" % (self.owner, self.about_actor,
            self.created_at)
