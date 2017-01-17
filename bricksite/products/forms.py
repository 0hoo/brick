from django import forms

from .views import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_code', 'title', 'official_price', 'pieces']
        error_messages = {
            'product_code': {
                'unique': 'Registering this product is under the review. Please wait a more! Thanks!'
            },
        }
