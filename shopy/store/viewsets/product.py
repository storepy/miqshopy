import logging


from django.db import IntegrityError
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.contrib.sites.shortcuts import get_current_site

from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAdminUser

# from rest_framework import status, mixins

from miq.core.middleware import local
from miq.core.permissions import DjangoModelPermissions

from ..services import product_list_qs, ProductListFilterSerializer
from ..models import Product, ProductAttribute, ProductStages
from ..serializers import ProductSerializer, ProductListSerializer
from ..utils import get_category_options, get_product_size_choices
from ..serializers import ProductAttributeSerializer, ProductSizeSerializer

from .mixins import ViewSetMixin

log = logging.getLogger(__name__)


class ProductViewset(ViewSetMixin, viewsets.ModelViewSet):
    lookup_field = 'slug'  # type: str
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = (JSONParser, )
    permission_classes = (IsAdminUser, DjangoModelPermissions)
    #

    @action(methods=['patch'], detail=True, url_path=r'swap-cover')
    def swap_cover(self, request, *args, **kwargs):
        obj = self.get_object()
        img_slug = request.data.get('slug')
        if not img_slug:
            raise serializers.ValidationError({'slug': _('Image slug required')})

        img = obj.images.filter(slug=img_slug).first()
        if img:
            cover = obj.cover
            if cover:
                cover_alt_text = cover.alt_text
                cover_position = cover.position
                cover_caption = cover.caption

                cover.alt_text = img.alt_text
                cover.position = img.position
                cover.caption = img.caption
                cover.save()
                obj.images.add(cover)

                img.alt_text = cover_alt_text
                img.position = cover_position
                img.caption = cover_caption
                img.save()

            obj.cover = img
            obj.images.remove(img)
            obj.save()

        return self.retrieve(self, request, *args, **kwargs)

    @action(methods=['patch'], detail=True, url_path=r'publish')
    def publish(self, request, *args, **kwargs):
        obj = self.get_object()
        obj_id = obj.id

        pub = request.data.get('is_published', False)
        if not pub:
            obj.is_published = False
            obj.save()

            log.info(f'unpublished product[{obj_id}]')
            return self.retrieve(self, request, *args, **kwargs)

        log.info(f'Publishing product[{obj_id}]')
        required = ['retail_price', 'meta_slug', 'meta_title', 'category']
        for field in required:
            if getattr(obj, field, None):
                continue
            log.error(f'Cannot publish product[{obj_id}]: {field} required')
            raise serializers.ValidationError({field: _('Required')}, code='required')

        category = obj.category
        if not category.is_published:
            log.error(
                f'Cannot publish product[{obj_id}]: category[{category.id}] is unpublished')
            raise serializers.ValidationError({'category': _('This category is unpublished')})

        obj.publish()

        return self.retrieve(self, request, *args, **kwargs)

    @action(methods=['post', 'patch', 'delete'], detail=True, url_path=r'size/(?P<size_slug>[\w-]+)')
    def size(self, request, *args, size_slug=None, ** kwargs):
        product = self.get_object()
        if request.method == 'POST':
            ser = ProductSizeSerializer(data=request.data)
            ser.is_valid(raise_exception=True)

            try:
                ser.save(product=product)
            except Exception as e:
                log.error(f'Creating size for product[{product.slug}]: {e}')
                raise serializers.ValidationError(
                    {'code': _('This size already exists')})

            get_product_size_choices(force_update=True)
            return self.retrieve(request, *args, **kwargs)

        if not size_slug:
            raise serializers.ValidationError({'size_slug': _('Size slug required')})

        size = product.sizes.filter(slug=size_slug).first()
        if not size:
            raise serializers.ValidationError(
                {'size_slug': _('Invalid size slug')}, code='invalid')

        if request.method == 'PATCH':
            ser = ProductSizeSerializer(size, data=request.data, partial=True)
            try:
                ser.is_valid(raise_exception=True)
                ser.save()
            except Exception as e:
                log.error(f'Updating size[{size.slug}]: {e}')
                raise serializers.ValidationError(
                    {'code': _('This size already exists')})

        if request.method == 'DELETE':
            size.delete()

        get_product_size_choices(force_update=True)
        return self.retrieve(self, request, *args, **kwargs)

    @action(methods=['post', 'patch', 'delete'], detail=True, url_path=r'attribute/(?P<attr_slug>[\w-]+)')
    def attribute(self, request, *args, attr_slug=None, ** kwargs):
        product = self.get_object()
        data = request.data
        if request.method == 'POST':
            try:
                attr = ProductAttribute.objects.create(
                    product=product, name=data.get('name'), value=data.get('value'),)
            except IntegrityError:
                raise serializers.ValidationError(
                    {'name': 'This attribute already exists'})

            return self.retrieve(self, request, *args, **kwargs)

        if not attr_slug:
            raise serializers.ValidationError(
                {'attr_slug': _('Attribute slug required')})

        attr = product.attributes.filter(slug=attr_slug).first()
        if not attr:
            raise serializers.ValidationError(
                {'attr_slug': _('Invalid attribute slug')}, code='invalid')

        if request.method == 'PATCH':
            ser = ProductAttributeSerializer(attr, data=request.data, partial=True)
            try:
                ser.is_valid(raise_exception=True)
                ser.save()
            except Exception:
                raise serializers.ValidationError(
                    {'name': 'This attribute already exists'})

        if request.method == 'DELETE':
            attr.delete()

        return self.retrieve(self, request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer

        return ProductSerializer

    def get_queryset(self):
        filters = ProductListFilterSerializer(data=self.request.query_params)
        filters.is_valid(raise_exception=True)
        return product_list_qs(filters=filters.validated_data).order_by('position', '-created', 'name')

    def list(self, request, *args, **kwargs):
        r = super().list(request, *args, **kwargs)
        r.data['categories'] = get_category_options()
        r.data['stages'] = ProductStages
        return r

    def perform_create(self, ser):
        name = self.request.data.get('name')
        ser.save(meta_title=name, meta_slug=slugify(name))

    def dispatch(self, request, *args, **kwargs):
        if not local.site:
            local.site = get_current_site(request)

        return super().dispatch(request, *args, **kwargs)
