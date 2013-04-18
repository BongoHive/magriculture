from django.db import models
from django.template.defaultfilters import floatformat


CROP_QUALITY_CHOICES = (
    (10, 'Excellent'),
    (7, 'Good'),
    (5, 'Standard'),
    (3, 'Mediocre'),
    (0, 'Poor'),
)


class Crop(models.Model):
    """
    A crop is an item that is being traded
    """
    #: name of the crop, :func:`str`
    name = models.CharField(blank=False, max_length=255)
    #: the description of the crop, :func:`str`
    description = models.TextField(blank=True)
    #: the units this crop is available in, :class:`CropUnit`
    units = models.ManyToManyField('fncs.CropUnit')

    class Meta:
        ordering = ['name']
        get_latest_by = 'pk'
        app_label = 'fncs'

    def __unicode__(self):
        return self.name


class CropUnit(models.Model):
    """
    A unit that a crop is traded in
    """
    #: name of the unit, e.g. 'box', :func:`str`
    name = models.CharField(blank=False, max_length=255)
    #: description of the unit, e.g. '30x30x30 in dimensions', :func:`str`
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-name']
        get_latest_by = 'pk'
        app_label = 'fncs'

    def __unicode__(self):
        return self.name


class CropReceipt(models.Model):
    """
    A receipt records crops left with an agent by a farmer
    """
    #: the :class:`Crop` being supplied
    crop = models.ForeignKey('fncs.Crop')
    # the :class:`CropUnit` it is being supplied in
    unit = models.ForeignKey('fncs.CropUnit')
    #: the :class:`magriculture.fncs.models.actors.Farmer` that supplied it
    farmer = models.ForeignKey('fncs.Farmer')
    #: the :class:`magriculture.fncs.models.actors.Agent` that received it
    agent = models.ForeignKey('fncs.Agent')
    #: the :class:`magriculture.fncs.models.geo.Market` it took place at
    market = models.ForeignKey('fncs.Market')
    #: the quality of the crop, :func:`int`, choices in
    #: `CROP_QUALITY_CHOICES`
    quality = models.IntegerField(blank=False, default=5,
                                  choices=CROP_QUALITY_CHOICES)
    #: the amount of delivered in :class:`CropUnit`
    amount = models.FloatField('Quantity')
    created_at = models.DateTimeField(blank=False)
    #: whether all of the delivered goods have been sold or not
    reconciled = models.BooleanField(blank=False, default=False)

    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'
        app_label = 'fncs'

    def remaining_inventory(self):
        """
        Calculate how much inventory is still left based on the transaction
        history

        :returns: :func:`int`
        """
        aggregate = Transaction.objects.filter(crop_receipt=self).aggregate(
            total_sold=models.Sum('amount'))
        # If there are no transactions, total_sold will be None, if
        # that's the case then we want to return zero
        sold_inventory = aggregate.get('total_sold') or 0
        return self.amount - sold_inventory

    def as_sms(self):
        """Return an SMS representation of a crop receipt."""
        if self.reconciled:
            fmt_str = ("%(quantity)g %(unit)s(s) of %(crop)s"
                       " all sold by %(agent)s")
            remaining = 0.0
        else:
            fmt_str = ("%(remaining)g of %(quantity)g %(unit)s(s) of %(crop)s"
                       " left to be sold by %(agent)s")
            remaining = self.remaining_inventory()
        return fmt_str % {
            "quantity": self.amount,
            "unit": self.unit,
            "crop": self.crop,
            "agent": self.agent,
            "remaining": remaining,
        }

    def __unicode__(self):  # pragma: no cover
        return u"%s %s %s of %s from %s" % (
            self.remaining_inventory(),
            self.get_quality_display(), self.unit, self.crop,
            self.created_at.strftime('%d %b'),)


class DirectSale(models.Model):
    """
    A direct sale is when an agent buys crops directly from a farmer.

    """
    transaction = models.ForeignKey('fncs.Transaction')
    created_at = models.DateTimeField(blank=False, auto_now_add=True)

    class Meta:
        app_label = 'fncs'


class Transaction(models.Model):
    """
    A transaction is an exchange of a crop at a certain unit
    at a given price
    """
    #: the :class:`CropReceipt` this transaction is going off of
    crop_receipt = models.ForeignKey('fncs.CropReceipt')
    #: the amount sold, :func:`float`
    amount = models.FloatField('Quantity')
    #: at what price, :func:`float`
    price = models.FloatField()
    #: the total, calculated automatically unless specified
    total = models.FloatField()
    created_at = models.DateTimeField(blank=False)

    @classmethod
    def price_history_for(cls, market, crop, unit):
        """
        Return the price history for a given crop/unit combination
        at the given market.

        :param market: :class:`magriculture.fncs.models.geo.Market`
        :param crop: :class:`Crop`
        :param unit: :class:`CropUnit`
        :returns: list of prices as floats.
        """
        return cls.objects.filter(
            crop_receipt__market=market,
            crop_receipt__crop=crop, crop_receipt__unit=unit). \
            values_list('price', flat=True)

    def as_sms(self):
        """Return an SMS representation of this transaction."""
        crop_receipt = self.crop_receipt
        return (
            "%(agent)s sold %(quantity)g %(unit)s(s) of %(crop)s"
            " for %(total).2f (%(price).2f per %(unit)s)"
        ) % {
            "agent": crop_receipt.agent,
            "quantity": self.amount,
            "unit": crop_receipt.unit,
            "crop": crop_receipt.crop,
            "price": self.price,
            "total": self.total,
        }

    def save(self, *args, **kwargs):
        if not self.total:
            self.total = self.amount * self.price
        super(Transaction, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'
        app_label = 'fncs'

    def __unicode__(self):
        return u"%s %s of %s" % (
            floatformat(self.amount), self.crop_receipt.unit,
            self.crop_receipt.crop)


class Offer(models.Model):
    """
    An offer is like a transaction but differs because no goods
    are being exchanged. It is setting the opening prices of goods
    at the start of the day
    """
    #: the :class:`Crop` this offer is made for
    crop = models.ForeignKey('fncs.Crop')
    #: the :class:`CropUnit` this offer is made for
    unit = models.ForeignKey('fncs.CropUnit')
    #: at which :class:`magriculture.fncs.models.geo.Market` this offer
    #: stands
    market = models.ForeignKey('fncs.Market')
    #: the :class:`magriculture.fncs.models.actors.MarketMonitor` reporting
    #: this offer
    marketmonitor = models.ForeignKey('fncs.MarketMonitor')
    #: :func:`float` the lowest opening price for this crop
    price_floor = models.FloatField('Floor price')
    #: :func:`float` the highest opening price for this crop
    price_ceiling = models.FloatField('Ceiling price')
    #: :func:`datetime.datetime` time of the offer
    created_at = models.DateTimeField(blank=False, auto_now_add=True)

    @classmethod
    def price_history_for(cls, market, crop, unit):
        """
        Return the offer history for the crop, unit, market combination

        :param market: :class:`magriculture.fncs.models.geo.Market`
        :param crop: :class:`Crop`
        :param unit: :class:`CropUnit`
        :returns: list of (`price_floor`,`price_ceiling`) tuples.
        """
        return cls.objects.filter(market=market, crop=crop, unit=unit). \
            values_list('price_floor', 'price_ceiling')

    @classmethod
    def average_price_history_for(cls, market, crop, unit):
        """
        Like :func:`price_history_for` but averages the floor & ceiling
        prices

        :returns: list of average prices as floats
        """
        return [sum(price_range) / 2.0 for price_range in
                cls.price_history_for(market, crop, unit)]

    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'
        app_label = 'fncs'

    def __unicode__(self):
        return u"%s of %s between %s and %s (Offer)" % (
            self.unit, self.crop, self.price_floor, self.price_ceiling)


class Message(models.Model):
    """
    A message sent or received via FNCS
    """
    #: the :class:`magriculture.fncs.models.actors.Actor` sending the message
    sender = models.ForeignKey('fncs.Actor', related_name='sentmessages_set')
    #: the :class:`magriculture.fncs.models.actors.Actor` receiving the
    #: message
    recipient = models.ForeignKey('fncs.Actor',
                                  related_name='receivedmessages_set')
    # the content of the message, :func:`str`
    content = models.CharField(max_length=120)
    # the timestamp :func:`datetime.datetime` of the message
    created_at = models.DateTimeField(auto_now_add=True)
    #: the :class:`GroupMessage` this message is part of
    group = models.ForeignKey('fncs.GroupMessage', null=True)

    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'
        app_label = 'fncs'

    def __unicode__(self):
        return u"Message from %s to %s at %s" % (
            self.sender, self.recipient, self.created_at)


class GroupMessage(models.Model):
    """
    A message being sent out to a group of recipients
    """
    #: the :class:`magriculture.fncs.models.actors.Actor` sending the message
    sender = models.ForeignKey('fncs.Actor')
    #: the :class:`magriculture.fncs.models.actors.FarmerGroup` receiving
    #: the message
    farmergroups = models.ManyToManyField('fncs.FarmerGroup')
    #: the content of the message, :func:`str`
    content = models.CharField(max_length=120)
    #: the timestamp :func:`datetime.datetime` of the message
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'
        app_label = 'fncs'

    def __unicode__(self):
        return 'GroupMessage from %s to %s groups at %s' % (
            self.sender, self.farmergroups.count(), self.created_at)


class Note(models.Model):
    """
    A note written by an actor and having another actor as the subject
    of the note
    """
    #: the :class:`magriculture.fncs.models.actors.Actor` owning the note
    owner = models.ForeignKey('fncs.Actor')
    #: the :class:`magriculture.fncs.models.actors.Actor` who this note is
    #: about
    about_actor = models.ForeignKey('fncs.Actor',
                                    related_name='attachednote_set')
    #: the content of the note
    content = models.TextField()
    #: the :func:`datetime.datetime` timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'
        app_label = 'fncs'

    def __unicode__(self):
        return u"Note from %s to %s at %s" % (
            self.owner, self.about_actor, self.created_at)
