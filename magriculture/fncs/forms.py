from django import forms
from django.forms.widgets import HiddenInput, Textarea
from magriculture.fncs.models.props import (Crop, Transaction, Message,
                                            GroupMessage, Note, Offer,
                                            CropReceipt, CROP_QUALITY_CHOICES,
                                            CropUnit)
from magriculture.fncs.models.geo import Market
from magriculture.fncs.models.actors import (FarmerGroup, Farmer)
from magriculture.fncs.widgets import SplitSelectDateTimeWidget


class SelectCropForm(forms.Form):
    crop_receipt = forms.ModelChoiceField(
        label='Which crop?', required=True, empty_label=None,
        queryset=CropReceipt.objects.all())


class DirectSaleForm(forms.Form):
    amount = forms.FloatField(required=True, min_value=0.1, label='How many?')
    price = forms.FloatField(required=True, min_value=0.1,
                             label='At what price?')
    crop_receipt = forms.ModelChoiceField(
        label='Which crop?', required=True, empty_label=None,
        queryset=CropReceipt.objects.all(), widget=HiddenInput())

    def clean_crop_receipt(self):
        data = self.cleaned_data
        if data['crop_receipt'].remaining_inventory() < data['amount']:
            raise forms.ValidationError("Not enough inventory")
        return self.data


class TransactionForm(forms.ModelForm):
    crop_receipt = forms.ModelChoiceField(queryset=CropReceipt.objects.all(),
                                          widget=HiddenInput())
    market = forms.ModelChoiceField(label='Which market?', required=True,
                                    queryset=Market.objects.all(),
                                    empty_label=None)
    created_at = forms.DateTimeField(
        label='Date', required=True,
        widget=SplitSelectDateTimeWidget(attrs={
            'class': 'date-form',
        }))

    def clean_crop_receipt(self):
        data = self.cleaned_data
        if data['crop_receipt'].remaining_inventory() < data['amount']:
            raise forms.ValidationError("Not enough inventory")
        return self.data

    class Meta:
        model = Transaction
        fields = [
            'amount',
            'price',
            'created_at'
        ]


class OfferForm(forms.ModelForm):
    crop = forms.ModelChoiceField(queryset=Crop.objects.all())
    market = forms.ModelChoiceField(queryset=Market.objects.all(),
                                    widget=HiddenInput())

    class Meta:
        model = Offer
        fields = [
            'crop',
            'unit',
            'price_floor',
            'price_ceiling',
            # 'created_at'
        ]


class AgentForm(forms.Form):
    name = forms.CharField(label='Name', required=True)
    surname = forms.CharField(label='Surname', required=True)
    msisdn = forms.CharField(label='Mobile Number', required=True)
    farmers = forms.ModelMultipleChoiceField(label='Farmers', required=True,
                                             queryset=Farmer.objects.all())
    markets = forms.ModelMultipleChoiceField(label='Markets', required=True,
                                             queryset=Market.objects.all())


class FarmerForm(forms.Form):
    name = forms.CharField(label='Name', required=True)
    surname = forms.CharField(label='Surname', required=True)
    msisdn1 = forms.CharField(label='Mobile Number 1', required=True)
    msisdn2 = forms.CharField(label='Mobile Number 2', required=False)
    msisdn3 = forms.CharField(label='Mobile Number 3', required=False)
    id_number = forms.CharField(label='National ID Number', required=False)
    farmergroup = forms.ModelChoiceField(
        label='Farmer Group', required=True,
        empty_label=None, queryset=FarmerGroup.objects.all())
    markets = forms.ModelMultipleChoiceField(
        label='Markets', required=True,
        queryset=Market.objects.all())
    matched_farmer = forms.ModelChoiceField(
        label='Matched Farmer',
        required=False, queryset=Farmer.objects.all())


class FarmerGeoForm(forms.Form):
    search = forms.CharField(label='Search for ward or district')
    location = forms.ChoiceField(label='Select ward or district')

    def __init__(self, *args, **kwargs):
        super(FarmerGeoForm, self).__init__(*args, **kwargs)
        search = self.initial.get('search') or ''
        if search:
            self.fields['location'].choices = self._location_choices(search)
        else:
            self.fields['location'].is_hidden = True

    def _location_choices(self, search):
        # TODO: put fuzzy search here
        return [('ward:1', 'Ward 1'), ('district:2', 'District 2')]


class CropsForm(forms.Form):
    crops = forms.ModelMultipleChoiceField(label='Crops', required=True,
                                           queryset=Crop.objects.all())


class MessageForm(forms.ModelForm):
    content = forms.CharField(label='Message', help_text='Max 120 characters',
                              widget=Textarea())

    class Meta:
        model = Message
        exclude = [
            'sender', 'recipient'
        ]


class GroupMessageForm(forms.ModelForm):
    content = forms.CharField(label='Message', help_text='Max 120 characters',
                              widget=Textarea())

    class Meta:
        model = GroupMessage
        exclude = [
            'sender', 'farmergroups'
        ]


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        exclude = [
            'owner', 'about_actor'
        ]


class CropReceiptStep1Form(forms.Form):
    crop = forms.ModelChoiceField(queryset=Crop.objects.all(), required=True,
                                  empty_label=None, label='Which crop?')
    market = forms.ModelChoiceField(
        queryset=Market.objects.all(), required=True,
        empty_label=None, label='Which market?')


class CropReceiptStep2Form(forms.Form):
    crop = forms.ModelChoiceField(queryset=Crop.objects.all(), required=True,
                                  widget=HiddenInput())
    market = forms.ModelChoiceField(queryset=Market.objects.all(),
                                    required=True, widget=HiddenInput())
    farmer = forms.ModelChoiceField(queryset=Farmer.objects.all(),
                                    required=True, empty_label=None,
                                    label='Which farmer?')
    crop_unit = forms.ModelChoiceField(queryset=CropUnit.objects.all(),
                                       required=True, empty_label=None,
                                       label='Which unit?')
    amount = forms.FloatField(required=True, min_value=0.1,
                              label='How many units?')
    quality = forms.TypedChoiceField(
        choices=CROP_QUALITY_CHOICES, required=True,
        label='What quality is the crop?', coerce=int)


class CropReceiptForm(forms.ModelForm):
    class Meta:
        model = CropReceipt
        exclude = [
            'agent',
            'created_at',
            'reconciled',
        ]


class CropReceiptSaleStep1Form(forms.Form):
    farmer = forms.ModelChoiceField(
        queryset=Farmer.objects.all(), required=True,
        empty_label=None, label='Which farmer?')


class CropReceiptSaleStep2Form(forms.Form):
    farmer = forms.ModelChoiceField(queryset=Farmer.objects.all(),
                                    required=True, widget=HiddenInput())
    crop_receipt = forms.ModelChoiceField(
        queryset=CropReceipt.objects.all(), required=True, empty_label=None,
        label='Sell from which crop intake?')
    amount = forms.FloatField(required=True, min_value=0.1, label='How many?')
    price = forms.FloatField(required=True, min_value=0.1,
                             label='At what price?')
