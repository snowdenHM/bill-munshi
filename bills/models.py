import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

from settings.models import ZohoVendor, ZohoChartOfAccount, ZohoTaxes


def validate_file_extension(value):
    import os
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
    if ext.lower() not in valid_extensions:
        raise ValidationError("Unsupported file extension. Only JPG, JPEG, PNG, and PDF files are allowed.")


class BillAnalyzer(models.Model):
    billStatus = (
        ('Draft', 'Draft'),
        ('Analysed', 'Analysed'),
        ('Synced', 'Synced')
    )
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    billName = models.CharField(max_length=200, null=True, blank=True)
    file = models.FileField(upload_to='bills/', validators=[validate_file_extension])
    formData = models.JSONField(null=True, blank=True, default=dict)
    tableData = models.JSONField(null=True, blank=True, default=dict)
    status = models.CharField(max_length=10, choices=billStatus, default='Draft', blank=True)
    client = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.billName and self.file:
            # Get the count of existing BillAnalyzer objects
            existing_count = BillAnalyzer.objects.count()
            # Generate the billName with the prefix "BM-" and the dynamic counting number
            self.billName = f"BM-{existing_count + 1}"
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.client and not self.client.is_authenticated:
            raise ValidationError("Only authenticated users can be assigned as clients.")

    class Meta:
        verbose_name_plural = 'Bill'

    def __str__(self):
        return self.billName


class ZohoBill(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    selectBill = models.ForeignKey(BillAnalyzer, on_delete=models.CASCADE, null=True, blank=True)
    vendor = models.ForeignKey(ZohoVendor, on_delete=models.CASCADE, null=True, blank=True)
    bill_no = models.CharField(max_length=50, null=True, blank=True)
    bill_date = models.CharField(max_length=50, null=True, blank=True)
    total = models.CharField(max_length=50, null=True, blank=True, default=0)
    igst = models.CharField(max_length=50, null=True, blank=True, default=0)
    note = models.CharField(max_length=100, null=True, blank=True, default="Enter Your Description")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Zoho Bill Analysis Report"


class ZohoProduct(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    zohoBill = models.ForeignKey(ZohoBill, on_delete=models.CASCADE, related_name='products')
    item_name = models.CharField(max_length=100, null=True, blank=True)
    item_details = models.CharField(max_length=200, null=True, blank=True)
    chart_of_accounts = models.ForeignKey(ZohoChartOfAccount, on_delete=models.CASCADE, null=True, blank=True)
    taxes = models.ForeignKey(ZohoTaxes, on_delete=models.CASCADE, null=True, blank=True)
    rate = models.CharField(max_length=10, null=True, blank=True)
    quantity = models.CharField(max_length=10, null=True, blank=True, default=0)
    amount = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Zoho Bill Product Analysis Report"
