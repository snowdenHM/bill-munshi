from django.contrib import admin

# Register your models here.
from .models import ZohoTaxes, ZohoVendor, ZohoCredentials, ZohoChartOfAccount

admin.site.register(ZohoTaxes)
admin.site.register(ZohoVendor)
admin.site.register(ZohoCredentials)
admin.site.register(ZohoChartOfAccount)
