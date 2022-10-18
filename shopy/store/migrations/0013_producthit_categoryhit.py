# Generated by Django 4.0.2 on 2022-10-18 05:28

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0004_alter_cart_options_and_more'),
        ('store', '0012_shophit'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductHit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(default=uuid.uuid4, editable=False, max_length=100, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='creation date and time')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='update date and time')),
                ('url', models.TextField(max_length=500)),
                ('referrer', models.TextField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True, null=True)),
                ('ip', models.GenericIPAddressField(blank=True, null=True, unpack_ipv4=True, verbose_name='Ip address')),
                ('count', models.PositiveIntegerField(default=1)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sales.customer', verbose_name='Customer')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product', verbose_name='Product Hit')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CategoryHit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(default=uuid.uuid4, editable=False, max_length=100, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='creation date and time')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='update date and time')),
                ('url', models.TextField(max_length=500)),
                ('referrer', models.TextField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True, null=True)),
                ('ip', models.GenericIPAddressField(blank=True, null=True, unpack_ipv4=True, verbose_name='Ip address')),
                ('count', models.PositiveIntegerField(default=1)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.category', verbose_name='Category Hit')),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sales.customer', verbose_name='Customer')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
