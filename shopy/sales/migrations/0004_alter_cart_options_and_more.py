# Generated by Django 4.0.2 on 2022-08-27 14:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0003_alter_order_options_alter_orderitem_size'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cart',
            options={'verbose_name': 'Cart', 'verbose_name_plural': 'Carts'},
        ),
        migrations.RenameField(
            model_name='order',
            old_name='is_completed',
            new_name='is_placed',
        ),
    ]
