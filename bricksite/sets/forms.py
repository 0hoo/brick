from django import forms

from common.forms import Html5TelInput
from .views import BrickSet


class ProductForm(forms.ModelForm):
    official_price = forms.DecimalField(label='Official Price', widget=Html5TelInput(), required=False)

    class Meta:
        model = BrickSet
        fields = ['brick_code', 'title', 'official_price', 'pieces']
        error_messages = {
            'brick_code': {
                'unique': 'Registering this product is under the review. Please wait a more! Thanks!'
            },
        }
