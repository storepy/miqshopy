# Generated by Django 4.0.2 on 2022-07-27 02:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_product_is_explicit'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_pinned',
            field=models.BooleanField(default=False, verbose_name='Is pinned'),
        ),
    ]
