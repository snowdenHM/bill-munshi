from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render

from bills.models import BillAnalyzer
from settings.models import ZohoChartOfAccount, ZohoVendor, ZohoTaxes


# Create your views here.


@login_required(login_url='account_login')
def dashboard(request):
    getUser = User.objects.get(username=request.user.username)
    try:
        coaCount = ZohoChartOfAccount.objects.filter(client=getUser).count()
        vendorCount = ZohoVendor.objects.filter(client=getUser).count()
        taxCount = ZohoTaxes.objects.filter(client=getUser).count()
        # Get all possible status values
        draft = BillAnalyzer.objects.filter(client=getUser).filter(status="Draft").count()
        analysed = BillAnalyzer.objects.filter(client=getUser).filter(status="Analysed").count()
        synced = BillAnalyzer.objects.filter(client=getUser).filter(status="Synced").count()
        context = {'coaCount': coaCount, 'vendorCount': vendorCount, 'taxCount': taxCount,
                   'draftCount': draft, 'analysedCount': analysed, 'syncedCount': synced
                   }
    except Exception as e:
        # Handle exceptions or errors here
        print(e)
        context = {'error_message': str(e)}
    return render(request, 'dashboard/dashboard.html', context)


# Create your views here.
def error_404(request, exception):
    return render(request, '404.html', status=404)


def error_500(request):
    return render(request, '500.html', status=500)
