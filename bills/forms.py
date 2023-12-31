from django import forms
from django.forms import modelformset_factory, Textarea

from .models import ZohoBill, ZohoProduct, BillAnalyzer


# from django.forms import inlineformset_factory


class BillForm(forms.ModelForm):
    class Meta:
        model = BillAnalyzer
        fields = ['file']


class ZohoBillForm(forms.ModelForm):
    class Meta:
        model = ZohoBill
        fields = ['selectBill', 'vendor', 'bill_no', 'bill_date', 'total', 'igst', 'note']


class ZohoProductForm(forms.ModelForm):
    class Meta:
        model = ZohoProduct
        fields = ['item_name', 'item_details', 'chart_of_accounts', 'taxes', 'rate', 'quantity', 'amount']

    item_details = forms.CharField(widget=Textarea(attrs={'class': 'form-control'}))


ZohoProductFormSet = modelformset_factory(
    ZohoProduct,
    form=ZohoProductForm,
    extra=0,  # The number of empty forms to display
)
