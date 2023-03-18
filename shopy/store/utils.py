
import re
import logging

from django.db import models
from django.utils.text import capfirst

from ..utils import get_currency

from .models import ProductSize


logger = logging.getLogger(__name__)

# https://www.facebook.com/business/help/120325381656392?id=725943027795860

cache = {
    'sizes': [],
    'categories': []
}


def get_product_sizes_qs(category_code: str = None):
    qs = ProductSize.objects.values('code')
    # if category_code:
    # qs = qs.filter(product__category__code=category_code.lower())
    return qs.annotate(count=models.Count('code')).order_by('-count').values_list('code', flat=True)


def get_product_size_choices(*, force_update=False):
    size_choices = cache['sizes']
    if not size_choices or force_update is True:
        print('==> Updating size choices')
        cache['sizes'] = [capfirst(i) for i in get_product_sizes_qs()]
    return size_choices


def get_category_options(top: bool = False, exclude: list[str] = None) -> dict:
    from .services import category_list_qs, category_list_parent_qs

    if top:
        qs = category_list_parent_qs()
    else:
        qs = category_list_qs()

    if isinstance(exclude, list):
        qs = qs.exclude(slug__in=exclude)

    return {
        'count': qs.count(),
        'items': [
            {
                'label': cat.name,
                'slug': cat.slug,
                'value': cat.slug
            } for cat in qs
        ]
    }


def price_to_dict(price_field, currency=None):
    if not price_field and price_field != 0:
        logger.debug(f'Invalid price_field: {price_field}')
        return

    currency = currency or get_currency()
    amt: str = f'{price_field} {currency}'
    if currency in ['XOF', 'XAF']:
        amt = f'{intcomma(int(price_field))} CFA'

    return {
        'currency': currency,
        'amount': price_field,
        'amountWithSymbol': amt
    }

    # if not currency:
    #     from .models import ShopSetting

    #     setting = ShopSetting.objects.filter(site_id=settings.SITE_ID).first()
    #     if not setting:
    #         raise Exception('Currency needed')
    #     currency = setting.currency

    # locale.setlocale(locale.LC_MONETARY, curr_to_locale(currency))
    # locale.setlocale(locale.LC_ALL, 'fr_CH')
    # amt = locale.currency(price_field, grouping=True)


def intcomma(value):
    value = f'{value}'
    return re.sub(r"^(-?\d+)(\d{3})", r'\g<1>,\g<2>', value)
