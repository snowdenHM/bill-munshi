from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import BillAnalyzer, ZohoBill
# ZohoProduct)
from .utils import analyse


@receiver(post_save, sender=BillAnalyzer)
def my_django_signal_handler(sender, instance, created, **kwargs):
    if created:
        print("Signal Called")
        bucket = 'billmunshi'
        document = 'media/' + str(instance.file)
        final_data, table_data = analyse.analyze_document(bucket, document)
        instance.formData = final_data
        instance.tableData = table_data
        instance.save(update_fields=['formData', 'tableData'])
        # Look up or create a BillAnalyzer instance based on the billName
        bill_analyzer_instance, created = BillAnalyzer.objects.get_or_create(billName=instance.billName)
        # Create a ZohoBill instance with the BillAnalyzer instance
        billCreate = ZohoBill.objects.create(selectBill=bill_analyzer_instance)
        # billProduct = ZohoProduct.objects.create(zohoBill=billCreate)
        return True
