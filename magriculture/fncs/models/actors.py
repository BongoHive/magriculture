from django.db import models

class Actor(models.Model):
    """A person with access to FNCS and who is able to interact with the
    data avaible"""
    name = models.CharField(blank=False, max_length=255)
    farmergroup = models.ForeignKey('fncs.FarmerGroup', null=True)
    
    class Meta:
        ordering = ['-name']
        get_latest_by = 'pk'
        app_label = 'fncs'
    
    def __unicode__(self):
        return u"%s (Actor)" % self.name
    

class FarmerGroup(models.Model):
    """A collection of farmers in a geographic area"""
    name = models.CharField(blank=False, max_length=255)
    zone = models.ForeignKey('fncs.Zone')
    district = models.ForeignKey('fncs.District')
    villages = models.ManyToManyField('fncs.Village')

    class Meta:
        ordering = ['-name']
        get_latest_by = 'pk'
        app_label = 'fncs'
    
    def __unicode__(self):
        return u"%s (FarmerGroup)" % self.name


class ExtensionOfficer(models.Model):
    """A extension officer is linked to a geographic zone and
    communicates with farmer groups"""
    actor = models.ForeignKey('fncs.Actor')
    farmergroup = models.ForeignKey('fncs.FarmerGroup')

    class Admin:
        list_display = ('',)
        search_fields = ('',)

    def __unicode__(self):
        return u"ExtensionOfficer"
