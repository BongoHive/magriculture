from django.db import models
from magriculture.fncs.models.props import Crop

class Province(models.Model):
    """A province, the normal geographic kind"""
    code = models.IntegerField(blank=True, null=True)
    name = models.CharField(blank=False, max_length=255)
    country = models.CharField(blank=False, max_length=100, default='--',
        choices=(
            ('--', 'Unspecified'),
            ('ZM', 'Zambia'),
            ('KE', 'Kenya'),
        ))
    
    class Meta:
        ordering = ['-name']
        get_latest_by = 'pk'
        app_label = 'fncs'
    
    def __unicode__(self): # pragma: no cover
        return u"%s (Province)" % (self.name,)


class RPIArea(models.Model):
    """An area containing districts with multiple extension units
    each with their own responsible extension officer"""
    name = models.CharField(blank=False, max_length=255)
    provinces = models.ManyToManyField('fncs.Province')
    
    class Meta:
        ordering = ['-name']
        get_latest_by = 'pk'
        app_label = 'fncs'
    
    def __unicode__(self): # pragma: no cover
        return u"%s (RPIArea)" % (self.name,)


class Zone(models.Model):
    """An organizational geographic unit, each zone has a leader which is
    the responsible extension officer"""
    rpiarea = models.ForeignKey('fncs.RPIArea')
    name = models.CharField(blank=False, max_length=255)

    class Meta:
        ordering = ['-name']
        get_latest_by = 'pk'
        app_label = 'fncs'
    
    def __unicode__(self): # pragma: no cover
        return u"%s (Zone)" % (self.name,)


class District(models.Model):
    """A geographic area"""
    province = models.ForeignKey('fncs.Province')
    name = models.CharField(blank=False, max_length=255)
    code = models.CharField(blank=True, max_length=100)
    
    class Meta:
        ordering = ['-name']
        get_latest_by = 'pk'
        app_label = 'fncs'
    
    def __unicode__(self): # pragma: no cover
        return self.name

class Ward(models.Model):
    """A geographic area, smaller than a District"""
    district = models.ForeignKey('fncs.District')
    name = models.CharField(blank=False, max_length=255)
    code = models.CharField(blank=True, max_length=100)

    class Meta:
        ordering = ['-name']
        get_latest_by = 'pk'
        app_label = 'fncs'
    
    def __unicode__(self): # pragma: no cover
        return u"%s (Ward)" % (self.name,)
    

class Market(models.Model):
    """A market is a location of trade in a certain district"""
    name = models.CharField(blank=False, max_length=255)
    district = models.ForeignKey('fncs.District')
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    altitude = models.FloatField(blank=True, null=True)
    volume = models.CharField(blank=True, max_length=100, default='unknown',
        choices=(
            ('unknown', 'Unknown'),
            ('low', 'Low'),
            ('high', 'High'),
        ))
    
    def rpiareas(self):
        province = self.district.province
        return RPIArea.objects.filter(provinces=province)
    
    def crops(self):
        transactions = self.transaction_set.all()
        crop_ids = [tx.crop_id for tx in transactions]
        return Crop.objects.filter(pk__in=crop_ids)
    
    class Meta:
        ordering = ['name']
        get_latest_by = 'pk'
        app_label = 'fncs'

    def __unicode__(self): # pragma: no cover
        return self.name
