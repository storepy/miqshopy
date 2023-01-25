from decimal import Decimal
from typing import Optional
from typing_extensions import TypedDict, Unpack

from django.db import transaction
from django.utils.text import slugify
from django.utils.crypto import get_random_string

from rest_framework import serializers

from ..models import Product


class ProductListFilterSerializer(serializers.Serializer):
    q = serializers.CharField(required=False)
    cat = serializers.CharField(required=False)
    size = serializers.CharField(required=False)
    sale = serializers.BooleanField(required=False)
    presale = serializers.BooleanField(required=False)
    is_oos = serializers.BooleanField(required=False)
    is_no_des = serializers.BooleanField(required=False)
    published = serializers.CharField(required=False)
    atc = serializers.BooleanField(required=False)
    supplier_order_slug = serializers.CharField(required=False)


class ProductCreateOptionalParams(TypedDict, total=False):
    description: Optional[str]
    meta_title: Optional[str]
    meta_slug: Optional[str]
    supplier: Optional[str]
    supplier_item_id: Optional[str]


@transaction.atomic
def product_create_from_supplier_item(*, name: str, retail_price: Decimal, supplier: str, supplier_item_id: str, **kwargs) -> Product:
    p = product_create(
        **kwargs, commit=False,
        name=name, retail_price=retail_price,
        supplier_item_id=supplier_item_id, supplier=supplier,
        slug=kwargs.get('slug')
    )

    print('==>', p.slug)

    # add attributes
    # add images

    # p.save()

    # Run the task once the transaction has commited,
    # guaranteeing the object has been created.
    # transaction.on_commit(
    # lambda: payment_charge.delay(payment_id=payment.id)
    # )


def product_create(*, name: str, retail_price: Decimal, slug: Optional[str] = None, commit: bool = True, **kwargs: Unpack[ProductCreateOptionalParams]) -> Product:

    name = product_clean_name(name)

    slug = slug or slugify(name)
    if Product.objects.filter(meta_slug=slug).exists():
        slug += '-' + get_random_string(length=32)

    p = Product(
        name=name, slug=slug,
        retail_price=retail_price,
        description=kwargs.get('description', ''),
        meta_title=kwargs.get('meta_title', name),
        meta_slug=kwargs.get('meta_slug', slug),

        #
        supplier=kwargs.get('supplier', None),
        supplier_item_id=kwargs.get('supplier_item_id', None),
    )

    p.full_clean()

    if commit:
        p.save()

    return p


def product_list_qs(*, filters: dict = None) -> list[Product]:

    qs = Product.objects.all()
    if not filters:
        return qs

    if supplier_order_slug := filters.get('supplier_order_slug'):
        if supplier_order_slug == '':
            return qs.none()

        qs = qs.filter(supplier_orders__slug=supplier_order_slug)

    if q := filters.get('q'):
        qs = qs.search_by_query(q)

    if cat_slug := filters.get('cat'):
        if cat_slug == 'no-cat':
            qs = qs.has_no_category()
        else:
            qs = qs.filter(category__slug=cat_slug)

    if filters.get('sale') is True:
        qs = qs.filter(is_on_sale=True)
    elif filters.get('presale') is True:
        qs = qs.filter(is_pre_sale=True)

    if published := filters.get('published'):
        if published == 'include':
            qs = qs.published()
        if published == 'pinned':
            qs = qs.filter(is_pinned=True)
        if published == 'explicit':
            qs = qs.filter(is_explicit=True)
        if published == 'exclude':
            qs = qs.draft()

    if size := filters.get('size'):
        if size == 'nosize':
            qs = qs.has_no_sizes()
        else:
            qs = qs.filter(sizes__code=size.lower())

    if filters.get('is_oos') is True:
        qs = qs.filter(is_oos=True)

    if filters.get('is_no_des'):
        qs = qs.has_no_description()

    if filters.get('atc') is True:
        qs = qs.to_cart()

    return qs


terms = (
    'SHEIN', 'PETITE', 'SXY',
    'PRETTYLITTLETHING', 'PRETTYLITTLETHING Shape - '
)


def product_clean_name(name: str) -> str:
    for term in terms:
        if term in name:
            name = name.replace(term, '')
    return name.strip()
