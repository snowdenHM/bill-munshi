from django.contrib import admin

# Register your models here.
from .models import BillAnalyzer, ZohoBill, ZohoProduct

admin.site.register(BillAnalyzer)
admin.site.register(ZohoBill)
admin.site.register(ZohoProduct)
