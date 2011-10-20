from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from magriculture.fncs import errors
from magriculture.fncs.models.geo import District
from magriculture.fncs.models.props import (Message, GroupMessage, Note,
    Transaction, Crop)
from datetime import datetime
import logging

def create_actor(sender, instance, created, **kwargs):
    """
    Signal handler for Django, creates a new blank actor for
    every user created.
    """
    if created:
        Actor.objects.create(user=instance)
    else:
        actor = instance.get_profile()
        actor.name = '%s %s' % (instance.first_name.strip(),
                                    instance.last_name.strip())
        actor.save()

post_save.connect(create_actor, sender=User)


class Actor(models.Model):
    """
    A person with access to FNCS and who is able to interact with the
    data avaible.
    """
    #: the :class:`django.contrib.auth.models.User` this actor is a profile for
    user = models.OneToOneField('auth.User')
    #: the name, duplicated from the `first_name` and `last_name`
    #: from the `user` field
    name = models.CharField(blank=False, max_length=255)
    #: the gender (M/F) of this actor
    gender = models.CharField(blank=True, max_length=100, choices=(
        ('M', 'Male'),
        ('F', 'Female'),
    ))

    def as_agent(self):
        """
        Get the :class:`Agent` role for this actor, raises an
        :class:`magriculture.fncs.errors.ActorException` if there is more than
        one agent available. Returns `None` if no agent exists.
        """
        agents = self.agent_set.all()
        if agents.count() > 1:
            raise errors.ActorException, 'More than one agent for an actor'
        if agents.exists():
            return agents[0]

    def as_marketmonitor(self):
        """
        Get the :class:`MarketMonitor` role for
        this actor, raises :class:`magriculture.fncs.errors.ActorException`
        if there is more than one :class:`MarketMonitor` available.
        Returns `None` if no agent exists.
        """
        marketmonitors = self.marketmonitor_set.all()
        if marketmonitors.count() > 1:
            raise ActorException, 'More than one marketmonitor for an actor'
        if marketmonitors.exists():
            return marketmonitors[0]

    def as_farmer(self):
        """
        Get the :class:`Farmer` role for this actor, raises an
        :class:`magriculture.fncs.errors.ActorException` if there is more
        than one :class:`Farmer` available.
        Returns `None` if no farmer exists.
        """
        farmers = self.farmer_set.all()
        if farmers.count() > 1:
            raise ActorException, 'More than one farmer for an actor'
        if farmers.exists():
            return farmers[0]

    def send_message(self, recipient, message, group):
        """
        Send a message to an other actor.

        :param recipient: the actor to send a message to
        :type recipient: magriculture.fncs.models.actors.Actor

        :param message: the message to send
        :type message: str

        :param group: the group message this message is part of
        :type group: magriculture.fncs.models.props.GroupMessage

        :returns: the message sent
        :rtype: magriculture.fncs.models.props.Message

        """
        return Message.objects.create(sender=self, recipient=recipient,
            content=message, group=group)

    class Meta:
        ordering = ['-name']
        get_latest_by = 'pk'
        app_label = 'fncs'

    def __unicode__(self): # pragma: no cover
        return u"%s (Actor)" % self.name


class Farmer(models.Model):
    """
    A farmer is an actor that provides goods to be sold in a market
    """
    #: the :class:`Actor` this farmer is linked to
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
        """
        Add the `crop` to the list of known crops that this farmer produces.

        :param crop: the crop
        :type crop: magriculture.fncs.models.props.Crop

        """
        self.crops.add(crop)

    def is_growing_crop(self, crop):
        """
        Check if this farmer produces the given crop

        :param crop: the crop to check
        :type crop: magriculture.fncs.models.props.Crop
        :returns: True or False

        """
        return self.crops.filter(pk=crop.pk).exists()

    def grows_crops_exclusively(self, crops):
        """
        **Warning this is a destructive method!**

        Resets the record of crops that this farmers produces to the
        given list of crops.

        :param crops: a list of crops
        :type crops: list of magriculture.fncs.props.Crop

        """
        self.crops.clear()
        for crop in crops:
            self.grows_crop(crop)

    def districts(self):
        """
        Returns the districts that this farmer is active in

        :returns: list
        :rtype: magriculture.fncs.models.geo.District
        """
        return District.objects.filter(market__in=self.markets.all())

    def transactions(self):
        """
        Returns the transactions completed on this farmer's behalf.

        :returns: list
        :rtype: magriculture.fncs.models.props.Transaction

        """
        return Transaction.objects.filter(crop_receipt__farmer=self)

    def operates_at(self, market, agent):
        """
        Specify that this farmer operats at the given market through the
        given agent.

        :param market: the market
        :type market: magriculture.fncs.models.props.Market

        :param agent: the agent through which he operates at that market
        :type agent: magriculture.fncs.models.actors.Agent

        """
        # the farmer and the agent need to sell at the given market
        self.markets.add(market)
        agent.markets.add(market)
        # the farmer has the agent registered as an agent
        self.agents.add(agent)
        # the agent has the farmer registered as a farmer
        agent.farmers.add(self)

    def operates_at_markets_exclusively(self, markets):
        """
        **Destructive Method**

        Specify that this farmer operates at the given markets without
        specifying which agent he operates through. It just creates a
        geographical link while overwriting any previous markets information
        stored for this farmer.

        :param markets: list of markets to set
        :type markets: magriculture.fncs.models.geo.Market

        """
        self.markets.clear()
        self.markets.add(*markets)

    @classmethod
    def create(cls, msisdn, name, surname, farmergroup):
        """
        Create a new Farmer.

        If a user already exists it uses that record. If a farmer already
        exists for that user it returns that, otherwise a new farmer is created.

        :type msisdn: str
        :type name: str
        :type surname: str
        :param farmergroup: the group this farmer belongs so.
        :type farmergroup: magriculture.fncs.models.actors.FarmerGroup
        :returns: a farmer
        :rtype: magriculture.fncs.models.actors.Farmer

        """
        user, _ = User.objects.get_or_create(username=msisdn)
        user.first_name = name
        user.last_name = surname
        user.save()

        actor = user.get_profile()
        if actor.farmer_set.exists():
            return actor.as_farmer()

        farmer = cls(actor=actor, farmergroup=farmergroup)
        farmer.save()

        return farmer

    def __unicode__(self): # pragma: no cover
        return self.actor.name


class FarmerGroup(models.Model):
    """
    A collection of farmers in a geographic area

    """
    #: The name of the group
    name = models.CharField(blank=False, max_length=255)
    #: The :class:`magriculture.fncs.models.geo.Zone` this group operates in. About to be deprecated.
    zone = models.ForeignKey('fncs.Zone', null=True)
    #: The :class:`magriculture.fncs.models.geo.District` this group operates in
    district = models.ForeignKey('fncs.District', null=True)
    #: Which :class:`magriculture.fncs.models.geo.Ward` this group is active in,
    #: a M2M relationship.
    wards = models.ManyToManyField('fncs.Ward')
    #: The :class:`ExtensionOfficer` assigned to
    #: this FarmerGroup
    extensionofficer = models.ForeignKey('fncs.ExtensionOfficer', null=True)

    def members(self):
        """
        :returns: the farmers member to this group
        :rtype: magriculture.fncs.models.actors.Farmer
        """
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
        """
        Register the opening price range of a crop.

        :param market: the market the price range applies to
        :type market: magriculture.fncs.models.geo.Market

        :param crop: the crop the price range applies to
        :type crop: magriculture.fncs.models.props.Crop

        :param unit: the unit the crop is being offered in
        :type unit: magriculture.fncs.models.props.CropUnit

        :param price_floor: the cheapest the crop is going for
        :type price_floor: float

        :param price_ceiling: the most expensive the crop is going for
        :type price_ceiling: float

        :returns: the offer object
        :rtype: magriculture.fncs.models.props.Offer

        """
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
    """
    An agent is an actor that is linked to a market and does a financial
    transaction on behalf of a Farmer
    """
    #: the :class:`Actor` this agent belongs to
    actor = models.ForeignKey('fncs.Actor')
    #: the :class:`Farmer` this agent is doing
    #: business for
    farmers = models.ManyToManyField('fncs.Farmer')
    #: the :class:`Market` this agent is doing
    #: business at
    markets = models.ManyToManyField('fncs.Market')

    class Meta:
        app_label = 'fncs'

    def is_selling_for(self, farmer, market):
        """
        Check to see if an agent is selling for a farmer at a given market,
        does so by checking the crop-receipt history for the given farmer.

        :param farmer: the farmer to check
        :type farmer: magriculture.fncs.models.actors.Farmer

        :param market: the market to check
        :type market: magriculture.fncs.models.geo.Market

        :returns: True/False
        :rtype: :func:`bool`

        """
        return self.cropreceipt_set.filter(farmer=farmer,
            market=market).exists()

    def take_in_crop(self, market, farmer, amount, unit, crop):
        """
        Add to the agent's crop inventory

        :param market: the market the crop is taken in on
        :type market: magriculture.fncs.models.geo.Market

        :param farmer: the farmer the crop is taken in from
        :type farmer: magriculture.fncs.models.actors.Farmer

        :param amount: the number of goods
        :type amount: int

        :param unit: the unit the crops were delivered in
        :type unit: magriculture.fncs.models.props.CropUnit

        :param crop: the crop taken in
        :type crop: magriculture.fncs.models.props.Crop

        :returns: the crop receipt
        :rtype: magriculture.fncs.models.props.CropReceipt

        """
        # keep track of who this agent is selling for & which markets he
        # is active in
        self.markets.add(market)
        self.farmers.add(farmer)
        # keep track of which markets this farmer is active in and which
        # crops he is selling
        farmer.markets.add(market)
        farmer.crops.add(crop)
        return self.cropreceipt_set.create(market=market, farmer=farmer,
            amount=amount, unit=unit, crop=crop, created_at=datetime.now())

    def cropreceipts_available_for(self, farmer):
        """
        Get a list of :class:`magriculture.fncs.models.props.CropReceipt` avaible
        for the given :class:`Farmer`

        :param farmer: a :class:`Farmer`
        """
        return self.cropreceipt_set.filter(farmer=farmer, reconciled=False)

    def register_sale(self, crop_receipt, amount, price):
        """
        Register a sale from a given crop-receipt.

        :param crop_receipt: which crop receipt this sale is going out of
        :type crop_receipt: magriculture.fncs.models.props.CropReceipt

        :param amount: the number sold
        :type amount: int

        :param price: the price at which it was sold
        :type price: float

        :raises: :class:`magriculture.fncs.errors.CropReceiptException` if not enough inventory
        """
        if crop_receipt.remaining_inventory() < amount:
            raise errors.CropReceiptException, 'not enough inventory'
        transaction = Transaction.objects.create(crop_receipt=crop_receipt,
            amount=amount, price=price, created_at=datetime.now())

        # see if we've sold everything we have and then update the
        # reconciled boolean
        if crop_receipt.remaining_inventory() <= 0:
            crop_receipt.reconciled = True
            crop_receipt.save()
        return transaction

    def sales_for(self, farmer):
        """
        Return a list of transactions for the given farmer

        :param farmer: :class:`Farmer`
        :returns: list of :class:`magriculture.fncs.models.props.Transaction`

        """
        return Transaction.objects.filter(crop_receipt__farmer=farmer,
            crop_receipt__agent=self)

    def send_message_to_farmer(self, farmer, message, group=None):
        """
        Send a message to a farmer

        :param farmer: :class:`Farmer`
        :param message: :func:`str`, the message text
        :param group: :class:`magriculture.fncs.models.props.GroupMessage`, defaults to `None`
        :returns: the message sent, `magriculture.fncs.models.props.Message`
        """
        return self.actor.send_message(farmer.actor, message, group)

    def send_message_to_farmergroups(self, farmergroups, message):
        """
        Send a message to all farmers in the given farmer groups

        :param farmergroups: list of :class:`FarmerGroup`
        :param message: :func:`str`, message to send.
        :returns: the group message sent, :class:`magriculture.fncs.models.props.GroupMessage`

        """
        groupmessage = GroupMessage.objects.create(sender=self.actor,
                        content=message)
        for farmergroup in farmergroups:
            groupmessage.farmergroups.add(farmergroup)
            for farmer in farmergroup.members():
                self.send_message_to_farmer(farmer, message, groupmessage)
        return groupmessage

    def write_note(self, farmer, note):
        """
        Write a note about a farmer

        :param farmer: :class:`Farmer`
        :param note: the message, :func:`str`
        :returns: the note object, :class:`magriculture.fncs.models.props.Note`
        """
        return Note.objects.create(owner=self.actor, about_actor=farmer.actor,
            content=note)

    def notes_for(self, farmer):
        """
        Return all notes for the given farmer

        :param farmer: :class:`Farmer`
        :returns: list of :class:`magriculture.fncs.models.props.Note`
        """
        return self.actor.note_set.filter(about_actor=farmer.actor)

    def __unicode__(self): # pragma: no cover
        return self.actor.name

