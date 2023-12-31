from django.urls import path

from . import views

app_name = 'bills'

urlpatterns = [
    # Draft Bill Section
    path('draft/', views.draftBill, name='bills-draft'),
    path('create/', views.createBill, name='bills-create'),
    path('draft/<str:billId>/', views.draftBillDelete, name='draftBillDelete'),
    # Analysed Bill Section
    path('analysed/', views.billsAnalysed, name='billsAnalysed'),
    path('startAnalyse/<str:billId>/', views.billAnalyseStart, name='billAnalyseStart'),
    path('analysed/<str:billId>/detail/', views.billAnalysedDetail, name='billAnalysedDetail'),
    # Sync Bill Section
    path('sync/', views.billsSync, name='billsSync'),
    path('startSync/<str:billId>/', views.billSyncWithZoho, name='billSyncWithZoho'),
]
