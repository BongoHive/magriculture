from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from magriculture.fncs import errors
from magriculture.fncs.models.geo import District
from magriculture.fncs.models.props import (Message, GroupMessage, Note,
    Transaction)
from datetime import datetime
import logging

def create_actor(sender, instance, created, **kwargs):
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
    name = models.CharField(blank=False, max_length=255)
    zone = models.ForeignKey('fncs.Zone', null=True)
    district = models.ForeignKey('fncs.District', null=True)
    wards = models.ManyToManyField('fncs.Ward')
    extensionofficer = models.ForeignKey('fncs.ExtensionOfficer', null=True)

    def members(self):
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
    """An agent is an actor that is linked to a market and does a financial
    transaction on behalf of a Farmer"""
    actor = models.ForeignKey('fncs.Actor')
    farmers = models.ManyToManyField('fncs.Farmer')
    markets = models.ManyToManyField('fncs.Market')

    class Meta:
        app_label = 'fncs'

    def is_selling_for(self, farmer, market):
        return self.cropreceipt_set.filter(farmer=farmer,
            market=market).exists()

    def take_in_crop(self, market, farmer, amount, unit, crop):
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

    def register_sale(self, crop_receipt, amount, price):
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
        return Transaction.objects.filter(crop_receipt__farmer=farmer,
            crop_receipt__agent=self)

    def send_message_to_farmer(self, farmer, message, group=None):
        return self.actor.send_message(farmer.actor, message, group)

    def send_message_to_farmergroups(self, farmergroups, message):
        groupmessage = GroupMessage.objects.create(sender=self.actor,
                        content=message)
        for farmergroup in farmergroups:
            groupmessage.farmergroups.add(farmergroup)
            for farmer in farmergroup.members():
                self.send_message_to_farmer(farmer, message, groupmessage)
        return groupmessage

    def write_note(self, farmer, note):
        return Note.objects.create(owner=self.actor, about_actor=farmer.actor,
            content=note)

    def notes_for(self, farmer):
        return self.actor.note_set.filter(about_actor=farmer.actor)

    def __unicode__(self): # pragma: no cover
        return self.actor.name

