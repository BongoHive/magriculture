from django import forms
from django.contrib.auth.models import User
from django.forms.widgets import HiddenInput, Textarea, CheckboxSelectMultiple
from magriculture.fncs.models.props import (Crop, Transaction, Message, 
                                            GroupMessage, Note, Offer)
from magriculture.fncs.models.geo import Market
from magriculture.fncs.models.actors import Actor, FarmerGroup
from magriculture.fncs.widgets import SplitSelectDateTimeWidget

class SelectCropForm(forms.Form):
    crop = forms.ModelChoiceField(label='Which crop?', required=True, 
        empty_label=None, queryset=Crop.objects.all())

class TransactionForm(forms.ModelForm):
    crop = forms.ModelChoiceField(queryset=Crop.objects.all(), 
                    widget=HiddenInput())
    market = forms.ModelChoiceField(label='Which market?', required=True,
                    queryset=Market.objects.all(), empty_label=None)
    created_at = forms.DateTimeField(label='Date', required=True, 
                    widget=SplitSelectDateTimeWidget(attrs={
                        'class':'date-form'
                    }))
    
    class Meta:
        model = Transaction
        fields = [
            'amount',
            'quality',
            'unit',
            'price',
            'created_at'
        ]

class OfferForm(forms.ModelForm):
    crop = forms.ModelChoiceField(queryset=Crop.objects.all())
    market = forms.ModelChoiceField(queryset=Market.objects.all(), 
                                        widget=HiddenInput())
    # created_at = forms.DateTimeField(label='Date', required=True, 
    #                 widget=SplitSelectDateTimeWidget(attrs={
    #                     'class':'date-form'
    #                 }))

    class Meta:
        model = Offer
        fields = [
            'crop',
            'unit',
            'price_floor',
            'price_ceiling',
            # 'created_at'
        ]
    

class FarmerForm(forms.Form):
    name = forms.CharField(label='Name', required=True)
    surname = forms.CharField(label='Surname', required=True)
    msisdn = forms.CharField(label='Mobile Number', required=True)
    farmergroup = forms.ModelChoiceField(label='Farmer Group', required=True,
        empty_label=None, queryset=FarmerGroup.objects.all())
    markets = forms.ModelMultipleChoiceField(label='Markets', required=True, 
        queryset=Market.objects.all())

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