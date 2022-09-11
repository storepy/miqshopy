

from django.test import TestCase
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File
from django.core.files.images import ImageFile
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from rest_framework.test import APIClient
from rest_framework import status

from ..models import Product, ProductImage, Category, SupplierItem
from ..serializers import ProductSerializer, ProductListSerializer

User = get_user_model()


class ProductSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username='test',)

    def test_product_serializer(self):
        category = Category.objects.create(name='test')
        product = Product.objects.create(
            name='test', category=category, user=self.user)

        serializer = ProductSerializer(product)
        self.assertEqual(serializer.data['name'], product.name)
        self.assertEqual(serializer.data['category'], product.category.slug)
        self.assertEqual(serializer.data['category_data']['name'], product.category.name)
        self.assertEqual(serializer.data['cover_data'], None)
        self.assertEqual(serializer.data['retail_price_data'], None)
        self.assertEqual(serializer.data['sale_price_data'], None)
        self.assertEqual(serializer.data['sizes'], [])
        self.assertEqual(serializer.data['supplier_item'], None)
        self.assertEqual(serializer.data['stage'], product.stage)
        self.assertEqual(serializer.data['dt_published'], product.dt_published)
        self.assertEqual(serializer.data['is_published'], product.is_published)
        self.assertEqual(serializer.data['images_data'], [])
        self.assertEqual(serializer.data['attributes'], [])
        self.assertEqual(serializer.data['stage_choices'], product.STAGE_CHOICES)
        self.assertEqual(serializer.data['created'], product.created)
        self.assertEqual(serializer.data['updated'], product.updated)

        product_image = ProductImage.objects.create(
            product=product, image=SimpleUploadedFile('test.jpg', b'content'))
        product_image.image.save('test.jpg', ContentFile(b'content'), save=True)
        product_image.save()

        serializer = ProductSerializer(product)
        self.assertEqual(serializer.data['images_data'][0]['image'], product_image.image.url)
        self.assertEqual(serializer.data['images_data'][0]['is_cover'], product_image.is_cover)
        self.assertEqual(serializer.data['images_data'][0]['position'], product_image.position)

        supplier_item = SupplierItem.objects.create(
            product=product, name='test', sku='test', price=100)
        serializer = ProductSerializer(product)
        self.assertEqual(serializer.data['supplier_item']['name'], supplier_item.name)
        self.assertEqual(serializer.data['supplier_item']['sku'], supplier_item.sku)
        self.assertEqual(serializer.data['supplier_item']['price'], supplier_item.price)

        product.is_published = True
        product.dt_published = timezone.now()
        product.save()
        serializer = ProductSerializer(product)
        self.assertEqual(serializer.data['is_published'], product.is_published)
        self.assertEqual(serializer.data['dt_published'], product.dt_published)

        product.is_on_sale = True
        product.sale_price = 100
        product.save()

        serializer = ProductSerializer(product)
        self.assertEqual(serializer.data['is_on_sale'], product.is_on_sale)
        self.assertEqual(serializer.data['sale_price'], product.sale_price)
        self.assertEqual(serializer.data['sale_price_data']['amount'], product.sale_price)
        self.assertEqual(serializer.data['sale_price_data']['formatted'], '$1.00')

        product.is_pre_sale = True
        product.is_pre_sale_text = 'test'
        product.is_pre_sale_dt = timezone.now()
        product.save()

        serializer = ProductSerializer(product)
        self.assertEqual(serializer.data['is_pre_sale'], product.is_pre_sale)
        self.assertEqual(serializer.data['is_pre_sale_text'], product.is_pre_sale_text)
        self.assertEqual(serializer.data['is_pre_sale_dt'], product.is_pre_sale_dt)

        product.retail_price = 100
        product.save()

        serializer = ProductSerializer(product)
        self.assertEqual(serializer.data['retail_price'], product.retail_price)
        self.assertEqual(serializer.data['retail_price_data']['amount'], product.retail_price)
        self.assertEqual(serializer.data['retail_price_data']['formatted'], '$1.00')

        product.cover = SimpleUploadedFile('test.jpg', b'content')
        product.cover.save('test.jpg', ContentFile(b'content'), save=True)
        product.save()

        serializer = ProductSerializer(product)
        self.assertEqual(serializer.data['cover'], product.cover.url)
        self.assertEqual(serializer.data['cover_data']['url'], product.cover.url)
        self.assertEqual(serializer.data['cover_data']['width'], 0)
        self.assertEqual(serializer.data['cover_data']['height'], 0)

        product.sizes = ['test']
        product.save()

        serializer = ProductSerializer(product)
        self.assertEqual(serializer.data['sizes'], product.sizes)

        product.attributes = {'test': 'test'}
        product.save()

        serializer = ProductSerializer(product)
        self.assertEqual(serializer.data['attributes'], product.attributes)

        product.stage = Product.STAGE_DRAFT
        product.save()

        serializer = ProductSerializer(product)
        self.assertEqual(serializer.data['stage'], product.stage)

        product.stage = Product.STAGE_PUBLISHED
        product.save()

        serializer = ProductSerializer(product)
        self.assertEqual(serializer.data['stage'], product.stage)
