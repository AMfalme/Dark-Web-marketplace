from django import forms
from main.models import Product, Category, SubCategory


class ProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['category'].widget.attrs['class'] = 'new-form-control'
        self.fields['subcategory'].widget.attrs['class'] = 'new-form-control'
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
        fields = ['category', 'subcategory', 'name', 'slug', 'description', 'price', 'available', 'stock', 'payout_address', 'image', 'country']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # qs_category = self.fields['category'].queryset
        # qs_subcategory = self.fields['category'].queryset
        # for row in qs_category:
        #     qs2 = qs2 | SubCategory.objects.filter(category_id=row.id)
            # mydb2_query.extend(list(SubCategory.objects.filter(category_id=row.id)))
        
        # for row in qs2:
        #     print(row.name)
        
        #self.fields['subcategory'].queryset = SubCategory.objects.none()

        # if 'category' in self.data:
        #     try:
        #         category_id = int(self.data.get('category'))
        #         self.fields['subcategory'].queryset = SubCategory.objects.filter(category_id=category_id).order_by('name')
        #     except (ValueError, TypeError):
        #         pass  # invalid input from the client; ignore and fallback to empty City queryset
        # elif self.instance.pk:
        #     self.fields['subcategory'].queryset = self.instance.category.city_set.order_by('name')