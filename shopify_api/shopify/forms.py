from django import forms

class BulkUpdatePriceForm(forms.Form):
    price = forms.DecimalField(max_digits=10, decimal_places=2, required=True, label="New Price")