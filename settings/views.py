import json

import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect

from .models import ZohoCredentials, ZohoVendor, ZohoChartOfAccount, ZohoTaxes


def credentials(request):
    userCredentials = ZohoCredentials.objects.filter(client=request.user)
    context = {'userCredentials': userCredentials}
    return render(request, 'settings/zoho/credentials/credentials.html', context)


def vendor(request):
    allVendor = ZohoVendor.objects.filter(client=request.user)
    context = {'allVendor': allVendor}
    return render(request, 'settings/zoho/vendor/vendor.html', context)


def chartOfAccount(request):
    allCoa = ZohoChartOfAccount.objects.filter(client=request.user)
    context = {'allCoa': allCoa}
    return render(request, 'settings/zoho/coa/coa.html', context)


def taxes(request):
    allTaxes = ZohoTaxes.objects.filter(client=request.user)
    context = {'allTaxes': allTaxes}
    return render(request, 'settings/zoho/tax/tax.html', context)


def fetchVendor(request):
    currentToken = ZohoCredentials.objects.get(client=request.user)
    url = "https://www.zohoapis.in/books/v3/contacts?organization_id=" + currentToken.organisationId
    print(url)
    payload = {}
    headers = {
        'Authorization': 'Zoho-oauthtoken ' + currentToken.bearerToken,
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    parsed_data = json.loads(response.text)
    # Extract information from contacts
    contacts = parsed_data["contacts"]
    for contact in contacts:
        contact_id = contact["contact_id"]
        company_name = contact["company_name"]
        gst_no = contact["gst_no"]
        contact_type = contact["contact_type"]
        if contact_type == "vendor":
            newVendor, created = ZohoVendor.objects.get_or_create(
                contactId=contact_id,
                companyName=company_name,
                gstNo=gst_no,
                client=request.user
            )
            if created:
                print("New contact saved successfully.")
            else:
                print("Contact already exists.")
        else:
            print("Customer Data")

    return redirect('settings:vendors')


def fetchChartAccount(request):
    currentToken = ZohoCredentials.objects.get(client=request.user)
    url = "https://www.zohoapis.in/books/v3/chartofaccounts?organization_id=" + currentToken.organisationId
    print(url)
    payload = {}
    headers = {
        'Authorization': 'Zoho-oauthtoken ' + currentToken.bearerToken,
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    parsed_data = json.loads(response.text)
    # Extract information from contacts
    chartOfAccounts = parsed_data["chartofaccounts"]
    for account in chartOfAccounts:
        account_Id = account["account_id"]
        account_Name = account["account_name"]
        newVendor, created = ZohoChartOfAccount.objects.get_or_create(
            accountId=account_Id,
            accountName=account_Name,
            client=request.user
        )
        if created:
            print("New COA saved successfully.")
        else:
            print("COA already exists.")
    return redirect('settings:chartOfAccount')


def fetchTaxes(request):
    currentToken = ZohoCredentials.objects.get(client=request.user)
    url = "https://www.zohoapis.in/books/v3/settings/taxes?organization_id=" + currentToken.organisationId
    payload = {}
    headers = {
        'Authorization': 'Zoho-oauthtoken ' + currentToken.bearerToken,
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    parsed_data = json.loads(response.text)
    # Extract information from contacts
    zohoTax = parsed_data["taxes"]
    for tax in zohoTax:
        tax_id = tax["tax_id"]
        tax_name = tax["tax_name"]

        newVendor, created = ZohoTaxes.objects.get_or_create(
            taxId=tax_id,
            taxName=tax_name,
            client=request.user
        )
        if created:
            print("New Tax saved successfully.")
        else:
            print("Tax already exists.")
    return redirect('settings:taxes')


def fetchVendorGst(request):
    if request.method == 'GET':
        vendor_id = request.GET.get('vendor_id')
        # Replace the following line with your logic to fetch GST information based on the vendor_id
        gst_info = ZohoVendor.objects.get(id=vendor_id)
        return JsonResponse({'gst': gst_info.gstNo})
    else:
        return JsonResponse({'gst': 'N/A'})
