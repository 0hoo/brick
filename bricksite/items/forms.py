from django import forms
from django.forms import ModelForm
from braces.forms import UserKwargModelFormMixin
from django.forms.models import inlineformset_factory

from .models import Item, Thing


class ProductKwargModelFormMixin(object):
    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop("product", None)
        super(ProductKwargModelFormMixin, self).__init__(*args, **kwargs)


class ItemForm(UserKwargModelFormMixin, ProductKwargModelFormMixin, ModelForm):
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
    class Meta:
        model = Thing
        fields = ['buying_price', 'opened', 'note']

ThingFormCreateSet = inlineformset_factory(Item, Thing, form=ThingForm, extra=1)
ThingFormUpdateSet = inlineformset_factory(Item, Thing, form=ThingForm, extra=0)
