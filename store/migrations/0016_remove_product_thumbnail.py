# Generated by Django 3.0.3 on 2020-12-11 15:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0015_product_thumbnail'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='thumbnail',
        ),
    ]