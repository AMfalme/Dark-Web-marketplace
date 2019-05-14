from django import forms
from main.models import Product


class ProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['category'].widget.attrs['class'] = 'new-form-control'
        self.fields['name'].widget.attrs['class'] = 'new-form-control'
        self.fields['slug'].widget.attrs['class'] = 'new-form-control'
        self.fields['description'].widget.attrs['class'] = 'new-form-control'
        self.fields['price'].widget.attrs['class'] = 'new-form-control'
        self.fields['price'].widget.attrs['min'] = '1.0'
        self.fields['available'].widget.attrs['class'] = 'new-form-control'
        self.fields['stock'].widget.attrs['class'] = 'new-form-control'
        self.fields['payout_address'].widget.attrs['class'] = 'new-form-control'
        self.fields['image'].widget.attrs['class'] = 'new-form-control'
        self.fields['country'].widget.attrs['class'] = 'new-form-control'

    class Meta:
        model = Product
        fields = ['category', 'name', 'slug', 'description', 'price', 'available', 'stock', 'payout_address', 'image', 'country']
