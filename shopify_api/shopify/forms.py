from django import forms
from shopify.models import *

class BulkUpdatePriceForm(forms.Form):
    price = forms.DecimalField(max_digits=10, decimal_places=2, required=True, label="New Price")
    
class ApplyDiscountForm(forms.Form):
    discount = forms.ModelChoiceField(queryset=Discount.objects.all(), required=True)