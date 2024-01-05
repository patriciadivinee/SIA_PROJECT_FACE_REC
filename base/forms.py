from django import forms
from .models import Category, Product


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['cat_name']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['prod_brand', 'prod_name', 'prod_desc', 'prod_price', 'prod_pack_size', 'cat_id']
