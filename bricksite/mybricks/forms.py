from django import forms
from django.forms import ModelForm, modelformset_factory
from django.forms.models import inlineformset_factory

from braces.forms import UserKwargModelFormMixin

from common.forms import Html5TelInput
from .models import MyBrick, MyBrickItem


class BrickSetKwargModelFormMixin(object):
    def __init__(self, *args, **kwargs):
        self.brickset = kwargs.pop('brickset', None)
        super(BrickSetKwargModelFormMixin, self).__init__(*args, **kwargs)


class MyBrickForm(UserKwargModelFormMixin, BrickSetKwargModelFormMixin, ModelForm):
    target_price = forms.DecimalField(label='Target Price', widget=Html5TelInput(), required=False)

    class Meta:
        model = MyBrick
        fields = ['target_price']

    def save(self, force_insert=False, force_update=False, commit=True):
        obj = super(MyBrickForm, self).save(commit=False)
        obj.user = self.user
        if self.brickset:
            obj.brickset = self.brickset
        if commit:
            obj.save()
        return obj


class ItemForm(ModelForm):
    buying_price = forms.DecimalField(label='Buying Price', widget=Html5TelInput(), required=False)

    class Meta:
        model = MyBrickItem
        fields = ['buying_price', 'opened', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 1, 'style': 'padding: 9px 14px'}),
        }

ItemFormCreateSet = inlineformset_factory(MyBrick, MyBrickItem, form=ItemForm, extra=1)
ItemFormUpdateSet = inlineformset_factory(MyBrick, MyBrickItem, form=ItemForm, extra=0)


class ItemSoldForm(ModelForm):
    sold_price = forms.DecimalField(label='Sold Price', widget=Html5TelInput, required=False)
    sold_at = forms.DateField(input_formats=('%m/%d/%Y',), widget=forms.DateInput(format='%m/%d/%Y'), required=False)

    def clean_sold_price(self):
        sold = self.cleaned_data['sold']
        data = self.cleaned_data['sold_price']
        if sold and not data:
            raise forms.ValidationError('Please enter sold price.')

        return data

    def clean_sold_at(self):
        sold = self.cleaned_data['sold']
        data = self.cleaned_data['sold_at']
        if sold and not data:
            raise forms.ValidationError('Please enter sold date')

        return data

    class Meta:
        model = MyBrickItem
        fields = ['sold', 'sold_price', 'sold_at']

ItemSoldFormSet = modelformset_factory(MyBrickItem, form=ItemSoldForm, extra=0)
