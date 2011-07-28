from django import forms
from django.forms.widgets import HiddenInput
from magriculture.fncs.models.props import Crop, Transaction
from magriculture.fncs.models.geo import Market
from magriculture.fncs.models.actors import Farmer
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
    

class FarmerForm(forms.ModelForm):
    class Meta:
        model = Farmer