# Generated by Django 3.0.3 on 2020-12-07 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_auto_20201207_2230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Cart_order', 'Cart_order'), ('Not confirmed', 'Не підтверджений'), ('Called', 'Підтверджений'), ('Payed', 'Оплачений'), ('Sent', 'Відправлений'), ('Delivered', 'Виконаний'), ('Canceled', 'Скасований')], default='Cart_order', max_length=200),
        ),
    ]