
from django.db import models
from django.urls import reverse_lazy
from django.utils.text import capfirst
from django.utils.text import Truncator

from ..sales.api import APIProductImageSerializer


def get_category_url(cat: 'models.Model') -> str:
    if cat.get_is_public():
        return reverse_lazy('shopy:category', args=[cat.meta_slug])
    return ''


def category_to_dict(cat: 'models.Model') -> dict:
    return {
        'name': capfirst(cat.name),
        'name_truncated': capfirst(Truncator(cat.name).chars(30)),
        'meta_slug': cat.meta_slug,
        'url': get_category_url(cat),
        'cover': APIProductImageSerializer(cat.cover).data,
        'description': cat.description,
    }


# def getImageSerializer(*, modelCls=Image):
#     class ImageSerializer(serializers.ModelSerializer):
#         class Meta:
#             model = modelCls
#             fields = (
#                 'src', 'height', 'width',
#                 'src_mobile', 'height_mobile', 'width_mobile',
#                 'thumb', 'height_thumb', 'width_thumb',
#                 'thumb_sq', 'height_thumb_sq', 'width_thumb_sq',
#                 'caption', 'alt_text'
#             )

#     return ImageSerializer


# class ProductSizeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductSize
#         read_only_fields = ('slug', 'name', 'code', 'quantity')
#         fields = read_only_fields


# def get_product_url(prod: 'Product') -> str:
#     if prod.get_is_public():
#         url = reverse_lazy(
#             'shopy:product',
#             args=[prod.category.meta_slug, prod.meta_slug]
#         )
#         return f'{url}'
#     return ''


# def getProductSerializer(*, fields: tuple = None, request=None, whatsapp_number=None):
#     _fields = (
#         'meta_slug', 'url', 'cover', 'shop_link',
#         'name', 'name_truncated', 'price', 'is_oos',
#         'is_pre_sale', 'retail_price', 'is_on_sale', 'sale_price',
#         'sizes'
#     )

#     class Serializer(serializers.ModelSerializer):
#         class Meta:
#             model = Product
#             fields = _fields

#         price = serializers.SerializerMethodField()
#         shop_link = serializers.SerializerMethodField()
#         url = serializers.CharField(source='path', read_only=True)
#         retail_price = serializers.SerializerMethodField()
#         sale_price = serializers.SerializerMethodField()
#         cover = getImageSerializer(modelCls=ProductImage)(read_only=True)
#         sizes = ProductSizeSerializer(many=True, read_only=True)

#         def get_attributes(self, inst: 'Product'):
#             return [
#                 {'name': capfirst(attr.name), 'value': attr.value}
#                 for attr in inst.attributes.all()
#             ]

#         def get_retail_price(self, inst: 'Product'):
#             return price_to_dict(inst.retail_price)

#         def get_sale_price(self, inst: 'Product'):
#             return price_to_dict(inst.sale_price)

#         def get_shop_link(self, inst: 'Product'):
#             return inst.get_whatsapp_link(request, whatsapp_number)

#         def get_price(self, inst: 'Product'):
#             return price_to_dict(inst.get_price())

#     if isinstance(fields, tuple):
#         _fields = (*_fields, *fields)

#         class Serializer(Serializer):
#             class Meta(Serializer.Meta):
#                 fields = _fields
#             images = getImageSerializer(modelCls=ProductImage)(many=True, read_only=True)
#             has_attributes = serializers.BooleanField(source='attributes.count', read_only=True)
#             attributes = serializers.SerializerMethodField()

#     return Serializer


# # ProductListSerializer = getProductSerializer()
# # ProductDetailSerializer = getProductSerializer(
# #     fields=(
# #         'description', 'is_pre_sale_text', 'is_pre_sale_dt',
# #         'images', 'has_attributes', 'attributes',
# #     )
# # )
