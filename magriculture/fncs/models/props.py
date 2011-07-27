from django.db import models
from django.template.defaultfilters import floatformat

class Crop(models.Model):
    """A crop is an item that is being traded"""
    name = models.CharField(blank=False, max_length=255)
    units = models.ManyToManyField('fncs.CropUnit')
    
    class Meta:
        ordering = ['name']
        get_latest_by = 'pk'
        app_label = 'fncs'

    def __unicode__(self):
        return self.name

class CropUnit(models.Model):
    """A unit that a crop is traded in"""
    name = models.CharField(blank=False, max_length=255)
    
    class Meta:
        ordering = ['-name']
        get_latest_by = 'pk'
        app_label = 'fncs'
    
    def __unicode__(self):
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
    
    def save(self, *args, **kwargs):
        if not self.total:
            self.total = self.amount * self.price
        super(Transaction, self).save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'
        app_label = 'fncs'
    
    def __unicode__(self):
        return u"%s %s of %s" % (floatformat(self.amount), self.unit, self.crop)

class Offer(models.Model):
    """An offer is like a transaction but differs because no goods
    are being exchanged. It is setting the opening prices of goods
    at the start of the day
    """
    crop = models.ForeignKey('fncs.Crop')
    unit = models.ForeignKey('fncs.CropUnit')
    agent = models.ForeignKey('fncs.Agent')
    market = models.ForeignKey('fncs.Market')
    marketmonitor = models.ForeignKey('fncs.MarketMonitor')
    price = models.FloatField()
    created_at = models.DateTimeField(blank=False, auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'
        app_label = 'fncs'

    def __unicode__(self):
        return u"%s of %s at %s (Offer)" % (self.unit, self.crop, self.price)

