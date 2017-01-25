from django import forms
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from django.forms.widgets import Input

from braces.forms import UserKwargModelFormMixin

from .models import Item, Thing


class Html5TelInput(Input):
    input_type = 'tel'


class ProductKwargModelFormMixin(object):
    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop("product", None)
        super(ProductKwargModelFormMixin, self).__init__(*args, **kwargs)


class ItemForm(UserKwargModelFormMixin, ProductKwargModelFormMixin, ModelForm):
    target_price = forms.DecimalField(label='Target Price', widget=Html5TelInput(), required=False)

    class Meta:
        model = Item
        fields = ['target_price']

    def save(self, force_insert=False, force_update=False, commit=True):
        obj = super(ItemForm, self).save(commit=False)
        obj.user = self.user
        if self.product:
            obj.product = self.product
        if commit:
            obj.save()
        return obj


class ThingForm(ModelForm):
    buying_price = forms.DecimalField(label='Buying Price', widget=Html5TelInput(), required=False)

    class Meta:
        model = Thing
        fields = ['buying_price', 'opened', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 1, 'style': 'padding: 9px 14px'}),
        }

ThingFormCreateSet = inlineformset_factory(Item, Thing, form=ThingForm, extra=1)
ThingFormUpdateSet = inlineformset_factory(Item, Thing, form=ThingForm, extra=0)
