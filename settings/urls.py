from django.urls import path

from . import views

app_name = 'settings'

urlpatterns = [
    path('credentials/', views.credentials, name='credentials'),
    path('vendors/', views.vendor, name='vendors'),
    path('syncVendor/', views.fetchVendor, name='syncVendor'),
    path('chartOfaccounts/', views.chartOfAccount, name='chartOfAccount'),
    path('taxes/', views.taxes, name='taxes'),
    # Tax Utility Function
    path('fetchTax/', views.fetchTaxes, name='fetchTax'),
    # COA Utility Function
    path('fetchCoa/', views.fetchChartAccount, name='fetchChartAccount'),
    # Get Vendor GST
    path('vendor/', views.fetchVendorGst, name='fetchVendorGst')
]
