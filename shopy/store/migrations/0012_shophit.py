# Generated by Django 4.0.2 on 2022-08-19 16:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0010_delete_campaign_delete_searchterm_hit_is_bot_and_more'),
        ('store', '0011_alter_product_meta_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShopHit',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('analytics.hit',),
        ),
    ]
