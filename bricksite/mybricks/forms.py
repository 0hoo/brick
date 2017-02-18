from django import forms
from django.forms import ModelForm, modelformset_factory
from django.forms.models import inlineformset_factory

from braces.forms import UserKwargModelFormMixin

from common.forms import Html5TelInput
from .models import MyBrick, Thing


class ProductKwargModelFormMixin(object):
    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop("product", None)
        super(ProductKwargModelFormMixin, self).__init__(*args, **kwargs)


class ItemForm(UserKwargModelFormMixin, ProductKwargModelFormMixin, ModelForm):
    target_price = forms.DecimalField(label='Target Price', widget=Html5TelInput(), required=False)

    class Meta:
        model = MyBrick
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

ThingFormCreateSet = inlineformset_factory(MyBrick, Thing, form=ThingForm, extra=1)
ThingFormUpdateSet = inlineformset_factory(MyBrick, Thing, form=ThingForm, extra=0)


class ThingSoldForm(ModelForm):
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
        model = Thing
        fields = ['sold', 'sold_price', 'sold_at']

ThingSoldFormSet = modelformset_factory(Thing, form=ThingSoldForm, extra=0)
