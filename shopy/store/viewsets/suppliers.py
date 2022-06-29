

import json
import logging

from django import http
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAdminUser

# from rest_framework import status, mixins

from miq.core.models import Currencies, Currency
from miq.core.permissions import DjangoModelPermissions
from miq.core.utils import get_file_ext, download_img_from_url, img_file_from_response

from ..utils_crawler import clean_product_name


from ..crawler import Crawler
from ..serializers import SupplierOrderSerializer
from ..models import Product, ProductAttribute, ProductImage, ProductStages, Category
from ..models import SupplierOrder, SupplierItem

from .mixins import ViewSetMixin

User = get_user_model()
log = logging.getLogger(__name__)
loginfo = log.info
logerror = log.error


def estimate_retail_price(cost, frm=Currency.USD, to=Currency.XOF):
    if not cost:
        return 0
    return int(float(cost) * 2.6 * 600)


def add_product_images(product, product_data: dict, user=None):
    name = product_data.get('name')
    img_data = {
        # 'site': get_current_site(self.request),
    }

    if user:
        img_data['user'] = user

    position = 1
    if (cover := product_data.get('cover')) and (res := download_img_from_url(cover)) and res.status_code == 200:
        if product.cover:
            product.cover.delete()

        product.cover = ProductImage.objects.create(
            **img_data, alt_text=name, position=position,
            src=img_file_from_response(res, None, get_file_ext(cover))
        )

    if imgs := product_data.get('imgs'):
        product.images.all().delete()
        position = 1
        for url in imgs:
            res = download_img_from_url(url)
            if not res or res.status_code != 200:
                continue

            position += 1
            img = ProductImage.objects.create(
                **img_data, alt_text=f'{name} {position}', position=position,
                src=img_file_from_response(res, None, get_file_ext(url))
            )
            product.images.add(img)


def add_product_attributes(product, product_data: dict):
    attrs = product.attributes
    for _attr in product_data.get('attrs'):  # type: dict
        name = _attr.get('name').lower()  # type: str
        value = _attr.get('value')  # type: str
        if attrs.filter(name=name).exists():
            attr = attrs.get(name=name)  # type: ProductAttribute
            if attr.value != value:
                attr.value = value
                attr.save()

        else:
            attr = ProductAttribute\
                .objects.create(product=product, name=name, value=value)


def add_shein_product_to_order(order, data, user=None, url=None):
    p_name = clean_product_name(data.get('name'))
    goods_id = data.get('id')

    qs = Product.objects
    if qs.filter(supplier_item_id=goods_id).exists():
        product = qs.get(supplier_item_id=goods_id)
    else:
        product = qs.create(
            supplier=order.supplier, name=p_name,
            description=data.get('description', ''),
            meta_title=p_name, meta_slug=slugify(p_name),
            supplier_item_id=goods_id,
            retail_price=estimate_retail_price(data.get('cost', 0))
        )
        add_product_attributes(product, data)
        add_product_images(product, data, user=user)
        product.save()

    item, new = SupplierItem.objects.get_or_create(order=order, product=product)
    if new:
        if url:
            item.url = url

        item.item_sn = data.get('productCode', '')

    item.data = data
    item.cost = data.get('cost')
    item.category = data.get('category')
    item.save()


class SupplierOrderViewset(ViewSetMixin, viewsets.ModelViewSet):
    lookup_field = 'slug'
    queryset = SupplierOrder.objects.all()
    serializer_class = SupplierOrderSerializer
    parser_classes = (JSONParser, )
    permission_classes = (IsAdminUser, DjangoModelPermissions)

    #

    crawler = Crawler()

    @action(methods=['post'], detail=True, url_path=r'batch')
    def batch(self, request, *args, **kwargs):
        slugs = request.data.get('slugs')

        if not isinstance(slugs, list):
            raise serializers.ValidationError({'slugs': 'invalid'})

        order = self.get_object()
        category = request.data.get('category')
        qs = order.products.filter(slug__in=slugs)

        if qs.exists():
            cat = Category.objects.filter(slug=category).first()
            qs.all().update(category=cat)

        return self.retrieve(request, *args, **kwargs)

    @action(methods=['patch', 'delete'], detail=True, url_path=r'item/(?P<product_slug>[\w-]+)')
    def item(self, request, *args, product_slug: str = None, **kwargs):
        if not product_slug:
            raise serializers.ValidationError({'product': 'Slug required'})

        item = self.get_object().items.filter(product__slug=product_slug).first()  # type: SupplierOrder
        if not item:
            raise serializers.ValidationError({'product': 'Not found'})

        if request.method == 'DELETE':
            item.delete()

        if request.method == 'PATCH':
            pass

        return self.retrieve(request, *args, **kwargs)

    @action(methods=['post'], detail=True, url_path=r'fnova')
    def fnova(self, request, *args, **kwargs):
        url = request.data.get('url')  # type: str
        if not url:
            raise serializers.ValidationError({'url': _('url required')})

        p_data = self.crawler.fnova_url_to_data(url)
        if not isinstance(p_data, dict):
            raise serializers.ValidationError(
                {'data': _('can not perform this action')}
            )

        qs = Product.objects
        p_name = clean_product_name(p_data.get('name'))
        goods_id = p_data.get('sku')
        order = self.get_object()

        if qs.filter(supplier_item_id=goods_id).exists():
            product = qs.get(supplier_item_id=goods_id)
        else:
            product = qs.create(
                supplier=order.supplier,
                name=p_name, description=p_data.get('description', ''),
                meta_title=p_name, meta_slug=slugify(p_name),
                supplier_item_id=goods_id,
                retail_price=estimate_retail_price(p_data.get('cost', 0)),
            )
            self.add_product_images(product, p_data)
            product.save()

        item, new = SupplierItem.objects.get_or_create(order=order, product=product)
        if new:
            item.url = url
            item.item_sn = p_data.get('sku')

        item.cost = p_data.get('cost')
        item.category = p_data.get('category')
        item.save()

        return self.retrieve(request, *args, **kwargs)

    @action(methods=['post'], detail=True, url_path=r'plt')
    def plt(self, request, *args, **kwargs):
        url = request.data.get('url')  # type: str
        if not url:
            raise serializers.ValidationError({'url': _('url required')})

        p_data = self.crawler.plt_url_to_data(url)
        if not isinstance(p_data, dict):
            raise serializers.ValidationError(
                {'data': _('can not perform this action')}
            )

        qs = Product.objects
        p_name = clean_product_name(p_data.get('name'))
        goods_id = p_data.get('sku')
        order = self.get_object()

        if qs.filter(supplier_item_id=goods_id).exists():
            product = qs.get(supplier_item_id=goods_id)
        else:
            product = qs.create(
                supplier=order.supplier,
                name=p_name, description=p_data.get('description'),
                meta_title=p_name, meta_slug=slugify(p_name),
                supplier_item_id=goods_id,
                retail_price=estimate_retail_price(p_data.get('cost', 0)),
            )
            self.add_product_images(product, p_data)
            product.save()

        item, new = SupplierItem.objects.get_or_create(order=order, product=product)
        if new:
            item.url = url
            item.item_sn = p_data.get('sku')

        item.cost = p_data.get('cost')
        item.category = p_data.get('category')
        item.save()

        # if not order.items.filter(slug=product.slug).exists():
        #     order.items.add(product)

        return self.retrieve(request, *args, **kwargs)

    @action(methods=['post'], detail=True, url_path=r'shein')
    def shein(self, request: 'http.HttpRequest', *args: tuple, **kwargs: dict) -> 'Response':
        url = request.data.get('url')  # type: str
        if not url:
            raise serializers.ValidationError({'url': _('url required')})

        p_data = self.crawler.shein_url_to_data(url)
        if not isinstance(p_data, dict):
            raise serializers.ValidationError(
                {'data': _('can not perform this action')}
            )

        order = self.get_object()

        add_shein_product_to_order(order, p_data, url=url, user=self.request.user)
        return self.retrieve(request, *args, **kwargs)

        p_name = clean_product_name(p_data.get('name'))
        goods_id = p_data.get('id')

        qs = Product.objects
        if qs.filter(supplier_item_id=goods_id).exists():
            product = qs.get(supplier_item_id=goods_id)
        else:
            product = qs.create(
                supplier=order.supplier, name=p_name,
                description=p_data.get('description', ''),
                meta_title=p_name, meta_slug=slugify(p_name),
                supplier_item_id=goods_id,
                retail_price=estimate_retail_price(p_data.get('cost', 0))
            )
            self.add_product_attributes(product, p_data)
            self.add_product_images(product, p_data)
            product.save()

        item, new = SupplierItem.objects.get_or_create(order=order, product=product)
        if new:
            item.url = url
            item.item_sn = p_data.get('productCode', '')

        item.data = p_data
        item.cost = p_data.get('cost')
        item.category = p_data.get('category')
        item.save()

        return self.retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        r = super().update(request, *args, **kwargs)
        stage = request.data.get('stage')
        if stage:
            self.get_object().products.update(stage=stage)

        return r

    def retrieve(self, *args, **kwargs):
        r = super().retrieve(*args, **kwargs)
        r.data['categories'] = self.get_category_options()
        r.data['currencies'] = Currencies
        r.data['stages'] = ProductStages

        r.data['by_categories'] = self.get_object().get_category_count()
        return r

    def add_product_images(self, product, product_data: dict):
        name = product_data.get('name')
        img_data = {
            # 'site': get_current_site(self.request),
            # 'user': self.request.user,
        }

        position = 1
        if (cover := product_data.get('cover')) and (res := download_img_from_url(cover)) and res.status_code == 200:
            if product.cover:
                product.cover.delete()

            product.cover = ProductImage.objects.create(
                **img_data, alt_text=name, position=position,
                src=img_file_from_response(res, None, get_file_ext(cover))
            )

        if imgs := product_data.get('imgs'):
            product.images.all().delete()
            position = 1
            for url in imgs:
                res = download_img_from_url(url)
                if not res or res.status_code != 200:
                    continue

                position += 1
                img = ProductImage.objects.create(
                    **img_data, alt_text=f'{name} {position}', position=position,
                    src=img_file_from_response(res, None, get_file_ext(url))
                )
                product.images.add(img)

    def add_product_attributes(self, product, product_data: dict):
        attrs = product.attributes
        for _attr in product_data.get('attrs'):  # type: dict
            name = _attr.get('name').lower()  # type: str
            value = _attr.get('value')  # type: str
            if attrs.filter(name=name).exists():
                attr = attrs.get(name=name)  # type: ProductAttribute
                if attr.value != value:
                    attr.value = value
                    attr.save()

            else:
                attr = ProductAttribute\
                    .objects.create(product=product, name=name, value=value)

    def perform_create(self, serializer):
        return serializer.save()


def add_order_feed(request, *args, **kwargs):
    payload = json.loads(request.body)

    order = SupplierOrder.objects.filter(slug=kwargs.get('order_slug'))
    if not order.exists():
        return http.JsonResponse({'order_slug': 'Invalid order'}, status=404)

    add_shein_product_to_order(order.first(), payload, url=payload.get('url'), user=User.objects.first())

    return http.JsonResponse({'ok': True})
