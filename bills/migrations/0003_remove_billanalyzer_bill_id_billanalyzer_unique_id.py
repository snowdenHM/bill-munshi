# Generated by Django 4.2.8 on 2023-12-17 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bills', '0002_billanalyzer_bill_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='billanalyzer',
            name='bill_id',
        ),
        migrations.AddField(
            model_name='billanalyzer',
            name='unique_id',
            field=models.SlugField(default='BM000001', max_length=12, unique=True),
        ),
    ]