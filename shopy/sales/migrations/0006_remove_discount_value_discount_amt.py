# Generated by Django 4.0.2 on 2022-12-31 03:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0005_discount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='discount',
            name='value',
        ),
        migrations.AddField(
            model_name='discount',
            name='amt',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='amount'),
            preserve_default=False,
        ),
    ]