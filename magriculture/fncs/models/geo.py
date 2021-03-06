from django.db import models
from magriculture.fncs.models.props import Crop, Transaction


class Province(models.Model):
    """
    A province, the normal geographic kind
    """
    #: the code of the province, country specific
    code = models.IntegerField(blank=True, null=True)
    #: the name of the province
    name = models.CharField(blank=False, max_length=255)
    #: the country the province is part of, this is a two letter country code.
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

    def __unicode__(self):
        return u"%s (Province)" % (self.name,)


class RPIArea(models.Model):
    """
    An area containing districts with multiple extension units
    each with their own responsible extension officer

    :note: this is specific to IDE's view of the world
    """
    #: the name of the RPI area
    name = models.CharField(blank=False, max_length=255)
    #: the provinces this RPI area covers, :class:`Province`
    provinces = models.ManyToManyField('fncs.Province')

    class Meta:
        ordering = ['-name']
        get_latest_by = 'pk'
        app_label = 'fncs'

    def __unicode__(self):
        return u"%s (RPIArea)" % (self.name,)


class Zone(models.Model):
    """
    An organizational geographic unit, each zone has a leader which is
    the responsible extension officer

    :note: this is specific to IDE's view of the world
    """
    #: the rpi area this zone is part of, :class:`RPIArea`
    rpiarea = models.ForeignKey('fncs.RPIArea')
    #: the name of this zone
    name = models.CharField(blank=False, max_length=255)

    class Meta:
        ordering = ['-name']
        get_latest_by = 'pk'
        app_label = 'fncs'

    def __unicode__(self):
        return u"%s (Zone)" % (self.name,)


class District(models.Model):
    """
    A geographic area
    """
    #: the :class:`Province` this district is part of
    province = models.ForeignKey('fncs.Province')
    #: the name of this district, :func:`str`
    name = models.CharField(blank=False, max_length=255)
    #: the code of this district, :func:`str`
    code = models.CharField(blank=True, max_length=100)

    class Meta:
        ordering = ['-name']
        get_latest_by = 'pk'
        app_label = 'fncs'

    def __unicode__(self):
        return self.name

    def get_farmer_count(self, agent, crop):
        """
        Get the total farmers based on the agent and crop selection
        """
        return self.farmer_district.filter(agent_farmer=agent,
                                           crops=crop).count()


class Ward(models.Model):
    """
    A geographic area, smaller than a District
    """
    #: the :class:`District` this ward is part of
    district = models.ForeignKey('fncs.District')
    #: the name of this ward, :func:`str`
    name = models.CharField(blank=False, max_length=255)
    #: the code of this ward, :func:`str`
    code = models.CharField(blank=True, max_length=100)

    class Meta:
        ordering = ['-name']
        get_latest_by = 'pk'
        app_label = 'fncs'

    def __unicode__(self):
        return u"%s (Ward)" % (self.name,)


class Market(models.Model):
    """
    A market is a location of trade in a certain district
    """
    #: name of the market, :func:`str`
    name = models.CharField(blank=False, max_length=255)
    #: the :class:`District` it is part of
    district = models.ForeignKey('fncs.District')
    #: the geo location of this market, currently unused
    latitude = models.FloatField(blank=True, null=True)
    #: the geo location of this market, currently unused
    longitude = models.FloatField(blank=True, null=True)
    #: the geo location of this market, currently unused
    altitude = models.FloatField(blank=True, null=True)
    #: the volume of this market, choices 'unknown', 'low' or 'high'
    volume = models.CharField(blank=True, max_length=100, default='unknown',
                              choices=(
                                  ('unknown', 'Unknown'),
                                  ('low', 'Low'),
                                  ('high', 'High'),
                              ))

    def rpiareas(self):
        """
        List of :class:`RPIArea` this market falls under
        """
        province = self.district.province
        return RPIArea.objects.filter(provinces=province)

    def crops(self):
        """
        List of :class:`magriculture.fncs.models.props.Crop` available
        in this market
        """
        return Crop.objects.filter(cropreceipt__market=self).distinct()

    def transactions(self):
        """
        Return a list of transactions that took place at this market

        :returns: :class:`magriculture.fncs.models.props.Transaction`
        """
        return Transaction.objects.filter(crop_receipt__market=self)

    @classmethod
    def highest_markets_for(cls, crop, window_size=5):
        """
        Return a list of markets ordered by most recent price of
        the given crop at each market.

        :param crop: :class:`magriculture.fncs.models.props.Crop`
        :param windows_size: int (how many samples to average the price over)
        :returns: :class:`magriculture.fncs.models.geo.Market`
        """
        markets = Market.objects.all()
        avg_prices = {}
        for market in markets:
            prices = Transaction.objects.filter(crop_receipt__market=market,
                                                crop_receipt__crop=crop
                                                ).order_by('-created_at')
            # '-created_at' puts most recent price first
            prices = prices.values_list('price', flat=True)[:window_size]
            avg_prices[market.pk] = sum(prices) / float(window_size)
        return sorted(markets, key=lambda market: avg_prices[market.pk], reverse=True)

    class Meta:
        ordering = ['name']
        get_latest_by = 'pk'
        app_label = 'fncs'

    def __unicode__(self):
        return self.name
