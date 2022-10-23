
import re
import logging

from ..utils import get_currency
from .models import Category

logger = logging.getLogger(__name__)

# https://www.facebook.com/business/help/120325381656392?id=725943027795860


def get_category_options(top: bool = False, exclude: list = None) -> dict:
    cats = Category.objects.all()
    if top:
        cats = cats.filter(parent__isnull=True)
    if isinstance(exclude, list):
        cats = cats.exclude(slug__in=exclude)

    return {
        'count': cats.count(),
        'items': [
            {
                'label': cat.name,
                'slug': cat.slug,
                'value': cat.slug
            } for cat in cats
        ]
    }


def price_to_dict(price_field, currency=None):
    if not price_field and price_field != 0:
        logger.debug(f'Invalid price_field: {price_field}')
        return

    currency = get_currency()
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
