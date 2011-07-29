from django.db import models

class Province(models.Model):
    """A province, the normal geographic kind"""
    name = models.CharField(blank=False, max_length=255)
    
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
    rpiarea = models.ForeignKey('fncs.RPIArea')
    name = models.CharField(blank=False, max_length=255)
    
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

    class Meta:
        ordering = ['-name']
        get_latest_by = 'pk'
        app_label = 'fncs'
    
    def __unicode__(self): # pragma: no cover
        return u"%s (Ward)" % (self.name,)
    

class Village(models.Model):
    """A village, part of a ward, in a district"""
    ward = models.ForeignKey('fncs.Ward')
    name = models.CharField(blank=False, max_length=255)
    
    class Meta:
        ordering = ['-name']
        get_latest_by = 'pk'
        app_label = 'fncs'
    
    def __unicode__(self): # pragma: no cover
        return u"%s (Village)"  % (self.name,)

class Market(models.Model):
    """A market is a location of trade in a certain district"""
    name = models.CharField(blank=False, max_length=255)
    district = models.ForeignKey('fncs.District')

    class Meta:
        ordering = ['name']
        get_latest_by = 'pk'
        app_label = 'fncs'

    def __unicode__(self): # pragma: no cover
        return self.name
