# Create your views here.
import json
from datetime import datetime

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from settings.models import ZohoTaxes, ZohoChartOfAccount, ZohoVendor, ZohoCredentials
from .forms import BillForm, ZohoProductFormSet, ZohoBillForm
from .models import BillAnalyzer, ZohoBill, ZohoProduct
from .utils import billTemplate


@login_required(login_url='account_login')
def draftBill(request):
    myBill = BillAnalyzer.objects.filter(client=request.user).filter(status="Draft")
    context = {'myBill': myBill}
    return render(request, 'bills/draft/draft.html', context)


@login_required(login_url='account_login')
def createBill(request):
    if request.method == 'POST':
        form = BillForm(request.POST, request.FILES)
        if form.is_valid():
            myBill = form.save(commit=False)
            myBill.client = request.user
            myBill.save()
            return redirect('bills:bills-draft')
    else:
        form = BillForm()
    return render(request, 'bills/draft/create_draft.html', {'form': form})


@login_required(login_url='account_login')
def draftBillDelete(request, billId):
    getBill = BillAnalyzer.objects.get(id=billId)
    getBill.delete()
    messages.warning(request, 'Bill Is Deleted Successfully!')
    return redirect('bills:bills-draft')


# Analysed Bill Views
@login_required(login_url='account_login')
def billsAnalysed(request):
    myBill = BillAnalyzer.objects.filter(client=request.user).filter(status="Analysed")
    context = {'myBill': myBill}
    return render(request, 'bills/analysed/analysed.html', context)


@login_required(login_url='account_login')
def billAnalyseStart(request, billId):
    myBill = BillAnalyzer.objects.get(id=billId)
    tableProcessing = billTemplate.tableDataProcessing(myBill)
    formProcessing = billTemplate.formDataProcessing(myBill)
    myBill.status = "Analysed"
    myBill.save(update_fields=['status'])
    messages.success(request, 'Bill Analysed Successfully!')
    return redirect('bills:bills-draft')


@login_required(login_url='account_login')
def billAnalysedDetail(request, billId):
    detailBill = get_object_or_404(BillAnalyzer, id=billId)
    analysed_bill = get_object_or_404(ZohoBill, selectBill=detailBill)
    analysed_products = ZohoProduct.objects.filter(zohoBill=analysed_bill).all()

    if request.method == 'POST':
        bill_form = ZohoBillForm(request.POST)
        # Update the analysed_bill and analysed_products based on POST data
        analysed_bill.vendor_id = request.POST.get('vendor')
        analysed_bill.note = request.POST.get('note')
        for index, product in enumerate(analysed_products):
            chart_key = f"form-{index}-chart_of_accounts"
            chart_of_accounts_id = request.POST.get(chart_key)
            if chart_of_accounts_id:
                product.chart_of_accounts = ZohoChartOfAccount.objects.get(id=chart_of_accounts_id)

            taxes_key = f"form-{index}-taxes"
            taxes_id = request.POST.get(taxes_key)
            if taxes_id:
                product.taxes = ZohoTaxes.objects.get(id=taxes_id)
        # Save the updated analysed_bill and analysed_products
        analysed_bill.save()
        for product in analysed_products:
            product.save()
        return redirect('bills:billsAnalysed')
    else:
        bill_form = ZohoBillForm(instance=analysed_bill)
        formset = ZohoProductFormSet(queryset=ZohoProduct.objects.filter(zohoBill=analysed_bill))

    context = {'detailBill': detailBill, 'bill_form': bill_form, 'formset': formset,
               'analysed_products': analysed_products}
    return render(request, 'bills/analysed/analysedDetail.html', context)


# Sync Bill Views
@login_required(login_url='account_login')
def billsSync(request):
    myBill = BillAnalyzer.objects.filter(client=request.user).filter(status="Synced")
    context = {'myBill': myBill}
    return render(request, 'bills/synced/synced.html', context)


def billSyncWithZoho(request, billId):
    billSyncProcess = ZohoBill.objects.get(selectBill=billId)
    zoho_products = billSyncProcess.products.all()
    # Create a dictionary to store the data
    vendorZohoId = ZohoVendor.objects.get(id=billSyncProcess.vendor_id)
    bill_date_str = billSyncProcess.bill_date
    bill_date_obj = datetime.strptime(bill_date_str, "%d-%b-%y")
    formatted_bill_date = bill_date_obj.strftime("%Y-%m-%d")
    bill_data = {
        "vendor_id": vendorZohoId.contactId,
        "bill_number": billSyncProcess.bill_no,
        "gst_no": vendorZohoId.gstNo,  # Replace with the actual GST number
        "date": formatted_bill_date,
        "line_items": []
    }
    for item in zoho_products:
        line_item = {
            "account_id": str(ZohoChartOfAccount.objects.get(accountName=item.chart_of_accounts).accountId),
            "tax_id": ZohoTaxes.objects.get(taxName=item.taxes).taxId,
            "rate": item.rate,
            "quantity": float(item.quantity),
            "discount": 0.00
        }
        bill_data["line_items"].append(line_item)
    # Serialize the dictionary to JSON format
    json_data = json.dumps(bill_data)
    # Print the JSON data (for testing purposes)
    print(json_data)
    # Sending Data to Zoho
    currentToken = ZohoCredentials.objects.get(client=request.user)
    url = "https://www.zohoapis.in/books/v3/bills?organization_id=" + currentToken.organisationId
    print(url)
    payload = json.dumps(bill_data)
    print(payload)
    headers = {
        'Authorization': 'Zoho-oauthtoken ' + currentToken.bearerToken,
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response)
    print(response.text)
    if response.status_code == 201:
        # Update the status of billSyncProcess to "Synced"
        billSyncProcess.status = "Synced"
        billSyncProcess.save()
        messages.success(request, "Bill Synced Successfully")
        return redirect('bills:billsSync')
    else:
        response_json = json.loads(response.text)
        error_message = response_json.get("message", "Failed to send data to Zoho")
        messages.error(request, error_message)
        return redirect('bills:billsAnalysed')
