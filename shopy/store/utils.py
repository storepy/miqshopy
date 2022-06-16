import re

from django.conf import settings

#


#

# https://www.facebook.com/business/help/120325381656392?id=725943027795860


def price_to_dict(price_field, currency=None):
    if not price_field and price_field != 0:
        return

    if not currency:
        from .models import ShopSetting

        setting = ShopSetting.objects.filter(site_id=settings.SITE_ID).first()
        if not setting:
            raise Exception('Currency needed')
        currency = setting.currency

    # locale.setlocale(locale.LC_MONETARY, curr_to_locale(currency))
    # locale.setlocale(locale.LC_ALL, 'fr_CH')
    # amt = locale.currency(price_field, grouping=True)

    amt = f'{price_field} {currency}'
    if currency in ['XOF', 'XAF']:
        amt = f'{intcomma(int(price_field))} CFA'

    return {
        'currency': currency,
        'amount': price_field,
        'amountWithSymbol': amt

    }


def intcomma(value):
    value = f'{value}'
    return re.sub(r"^(-?\d+)(\d{3})", r'\g<1>,\g<2>', value)
