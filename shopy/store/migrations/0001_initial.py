# Generated by Django 4.0.2 on 2022-03-31 01:31

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import models.m_setting
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(default=uuid.uuid4, editable=False, max_length=100, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='creation date and time')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='update date and time')),
                ('name', models.CharField(db_index=True, max_length=100)),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('is_published', models.BooleanField(default=False, help_text='Publish this category')),
                ('dt_published', models.DateTimeField(blank=True, help_text='Publication date', null=True)),
                ('position', models.PositiveIntegerField(default=1)),
                ('meta_title', models.CharField(blank=True, help_text='Cat Meta title', max_length=250, null=True)),
                ('meta_description', models.CharField(blank=True, help_text='Cat Meta description', max_length=500, null=True)),
                ('meta_slug', models.SlugField(blank=True, max_length=100, null=True, unique=True)),
                ('cover', models.OneToOneField(blank=True, null=True,
                 on_delete=django.db.models.deletion.SET_NULL, to='core.image', verbose_name='Cover')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'ordering': ('position', '-created', 'name'),
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(default=uuid.uuid4, editable=False, max_length=100, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='creation date and time')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='update date and time')),
                ('retail_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10,
                 null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('is_pre_sale', models.BooleanField(default=False, verbose_name='Available for pre sale')),
                ('is_pre_sale_text', models.TextField(blank=True, null=True, verbose_name='Pre sale description')),
                ('is_pre_sale_dt', models.DateTimeField(blank=True, null=True, verbose_name='Availability date time')),
                ('is_on_sale', models.BooleanField(default=False, verbose_name='Is on sale')),
                ('sale_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10,
                 null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('name', models.CharField(max_length=99, verbose_name='Name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('color_group_pk', models.CharField(blank=True, max_length=99, null=True, verbose_name='Color group identifier')),
                ('supplier', models.CharField(blank=True, choices=[('SHEIN', 'Shein'), ('PLT', 'Pretty Little Thing'), (
                    'ASOS', 'Asos'), ('FNOVA', 'Fashion Nova')], max_length=50, null=True, verbose_name='Supplier')),
                ('supplier_item_id', models.CharField(blank=True, max_length=99,
                 null=True, unique=True, verbose_name='Item identifier')),
                ('stage', models.CharField(choices=[('A_VIRTUAL', 'Virtual stock'), ('B_SUPPLIER_TRANSIT', 'Ordered from supplier'), ('C_INSTORE_WAREHOUSE', 'Received from supplier'), (
                    'D_INSTORE_TRANSIT', 'In transit to store'), ('E_INSTORE', 'Available for purchase'), ('F_SOLDOUT', 'Sold Out')], default='A_VIRTUAL', max_length=30, verbose_name='Stage')),
                ('position', models.PositiveIntegerField(default=1)),
                ('is_published', models.BooleanField(default=False, help_text='Publish this product')),
                ('dt_published', models.DateTimeField(blank=True, help_text='Publication date', null=True)),
                ('meta_title', models.CharField(blank=True, help_text='Product Meta title', max_length=250, null=True)),
                ('meta_description', models.CharField(blank=True, help_text='Product Meta description', max_length=500, null=True)),
                ('meta_slug', models.SlugField(blank=True, max_length=100, null=True, unique=True)),
                ('category', models.ForeignKey(blank=True, null=True,
                 on_delete=django.db.models.deletion.PROTECT, related_name='products', to='store.category')),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
                'ordering': ('position', '-created', 'name'),
            },
        ),
        migrations.CreateModel(
            name='SupplierItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(default=uuid.uuid4, editable=False, max_length=100, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='creation date and time')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='update date and time')),
                ('item_sn', models.CharField(blank=True, max_length=99, null=True, verbose_name='Item serial number')),
                ('category', models.CharField(blank=True, max_length=99, null=True, verbose_name='Supplier category')),
                ('url', models.URLField(blank=True, max_length=500, null=True, verbose_name='Supplier url')),
                ('cost', models.DecimalField(blank=True, decimal_places=2,
                 help_text='FOB Price, excluding inbound shipping, taxes and others costs', max_digits=10, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CategoryPage',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('core.page',),
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('core.image',),
        ),
        migrations.CreateModel(
            name='ProductPage',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('core.page',),
        ),
        migrations.CreateModel(
            name='SupplierOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(default=uuid.uuid4, editable=False, max_length=100, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='creation date and time')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='update date and time')),
                ('name', models.CharField(default='New supplier order', max_length=99, verbose_name='Name')),
                ('order_id', models.CharField(blank=True, max_length=99, null=True, verbose_name='Order ID')),
                ('currency', models.CharField(blank=True, choices=[('XOF', 'Franc CFA'), ('XAF', 'Franc CFA (BEAC)'), ('GHC', 'Ghanaian Cedi'), (
                    'NGN', 'Nigerian Naira'), ('EUR', 'Euro'), ('USD', 'United States Dollar')], max_length=10, null=True, verbose_name='Currency')),
                ('supplier', models.CharField(choices=[('SHEIN', 'Shein'), ('PLT', 'Pretty Little Thing'), (
                    'ASOS', 'Asos'), ('FNOVA', 'Fashion Nova')], default='SHEIN', max_length=50, verbose_name='Supplier')),
                ('is_paid', models.BooleanField(default=False, verbose_name='Is paid')),
                ('is_paid_dt', models.DateTimeField(blank=True, null=True, verbose_name='Date of payment')),
                ('is_fulfilled_dt', models.DateTimeField(blank=True, null=True, verbose_name='Date of fulfillment')),
                ('total_cost', models.DecimalField(blank=True, decimal_places=2,
                 help_text='FOB Price, excluding inbound shipping, taxes and others costs', max_digits=10, null=True)),
                ('products', models.ManyToManyField(blank=True, related_name='supplier_orders',
                 through='store.SupplierItem', to='store.Product', verbose_name='Products')),
            ],
            options={
                'verbose_name': 'Supplier Order',
                'verbose_name_plural': 'Supplier Orders',
                'ordering': ('-created',),
            },
        ),
        migrations.AddField(
            model_name='supplieritem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='items', to='store.supplierorder', verbose_name='Order'),
        ),
        migrations.AddField(
            model_name='supplieritem',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='supplier_items', to='store.product', verbose_name='Product'),
        ),
        migrations.CreateModel(
            name='ShopSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(default=uuid.uuid4, editable=False, max_length=100, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='creation date and time')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='update date and time')),
                ('config', models.JSONField(default=shopy.store.models.m_setting.jsondef, verbose_name='Config')),
                ('currency', models.CharField(choices=[('XOF', 'Franc CFA'), ('XAF', 'Franc CFA (BEAC)'), ('GHC', 'Ghanaian Cedi'), (
                    'NGN', 'Nigerian Naira'), ('EUR', 'Euro'), ('USD', 'United States Dollar')], default='XOF', max_length=10, verbose_name='Currency')),
                ('returns', models.TextField(blank=True, null=True, verbose_name='Returns Policy')),
                ('size_guide', models.TextField(blank=True, null=True, verbose_name='Size Guide')),
                ('site', models.OneToOneField(blank=True, default=1, null=True,
                 on_delete=django.db.models.deletion.SET_NULL, related_name='shopy', to='sites.site', verbose_name='Site')),
            ],
            options={
                'verbose_name': 'Shop settings',
                'verbose_name_plural': 'Shop settings',
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='ProductSize',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(default=uuid.uuid4, editable=False, max_length=100, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='creation date and time')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='update date and time')),
                ('name', models.CharField(help_text='Select size', max_length=20)),
                ('code', models.CharField(max_length=10)),
                ('quantity', models.PositiveIntegerField(default=1, help_text='Enter quantity',
                 validators=[django.core.validators.MinValueValidator(0)])),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sizes', to='store.product')),
            ],
            options={
                'verbose_name': 'Product size',
                'verbose_name_plural': 'Product sizes',
                'ordering': ('created', 'name'),
            },
        ),
        migrations.CreateModel(
            name='ProductAttribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(default=uuid.uuid4, editable=False, max_length=100, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='creation date and time')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='update date and time')),
                ('name', models.CharField(help_text='Name', max_length=30)),
                ('value', models.CharField(help_text='Value', max_length=99)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                 related_name='attributes', to='store.product')),
            ],
            options={
                'verbose_name': 'Product attribute',
                'verbose_name_plural': 'Product attributes',
                'ordering': ('created', 'name'),
            },
        ),
        migrations.AddField(
            model_name='product',
            name='cover',
            field=models.OneToOneField(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.productimage', verbose_name='Cover'),
        ),
        migrations.AddField(
            model_name='product',
            name='images',
            field=models.ManyToManyField(blank=True, related_name='shopy_products', to='store.ProductImage'),
        ),
        migrations.AddField(
            model_name='product',
            name='page',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                       related_name='shopy_product', to='store.productpage'),
        ),
        migrations.AddField(
            model_name='category',
            name='page',
            field=models.OneToOneField(blank=True, on_delete=django.db.models.deletion.PROTECT,
                                       related_name='shopy_category', to='store.categorypage'),
        ),
        migrations.AddConstraint(
            model_name='productsize',
            constraint=models.UniqueConstraint(fields=('product', 'name', 'code'),
                                               name='unique_product_size_name_code'),
        ),
        migrations.AddConstraint(
            model_name='productattribute',
            constraint=models.UniqueConstraint(fields=('product', 'name'), name='unique_product_attribute_name'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['name'], name='shopy_product_name_idx'),
        ),
    ]
