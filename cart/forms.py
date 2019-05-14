from django import forms
from main.models import Product

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 26)]


class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES, coerce=int)
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)

    def get_product_stock(self, product_id):
        product = Product.objects.get(id=product_id)
        return product.stock
