
import re
import json
import requests
from bs4 import BeautifulSoup

from miq.core.utils import clean_img_url, get_dict_key


SUPPLIER_MAP = {
    'SHEIN': {
        'name': 'SHEIN',
        'keys': {

            'id': 'detail__goods_id',
            'productCode': 'detail__goods_sn',
            'category': 'currentCat__cat_name',
            'name': 'detail__goods_name',
            'cover': 'detail__original_img',
            'sale_price': 'detail__salePrice__amount',
            'retail_price': 'detail__retailPrice__amount',
            'is_on_sale': 'detail__is_on_sale',
            'in_stock': 'detail__is_stock_enough',
        }
    },
    'PLT': {
        'name': 'PLT',
        'keys': {
            'sku': 'sku',
            'name': 'name',
            'description': 'description',
            'cover': 'image',
            'availability': 'offers__availability',
            'attrs__couleur': 'color',
            'cost': 'offers__price',
            'cost_currency': 'offers__priceCurrency',
        }
    },
    'FNOVA': {
        'name': 'FNOVA',
        'keys': {
            'id': 'id',
            'sku': 'sku',
            'name': 'title',
            'category': 'product_type',
            'cover': 'featured_image',
            'handle': 'handle',
            'cost': 'price',
            'attrs': 'tags',
            'imgs': 'media'
        }
    }
}


headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
}

_s = requests.Session()


def get(url):
    return _s.get(url, headers=headers)


terms = [
    'SHEIN', 'PETITE', 'SXY',
    'PRETTYLITTLETHING', 'PRETTYLITTLETHING Shape - '
]


def clean_product_name(name: str) -> str:
    for term in terms:
        if term in name:
            name = name.replace(term, '')
    return name.strip()


def shein_url_to_data(url: str):
    goods_id = shein_goods_id_from_url(url)
    if not goods_id:
        return

    raw = shein_data_from_mobile(goods_id, url)
    _raw = shein_data_from_web(goods_id, url)
    if not raw:
        raw = _raw

    if not isinstance(raw, dict):
        return

    supplier = 'SHEIN'
    data = load_raw_data(raw, supplier)
    _data = load_raw_data(_raw, supplier)

    data['cost'] = min(_data.get('retail_price', 0), _data.get('sale_price', 0))

    data['attrs'] = [
        {
            'name': attr.get('attr_name', attr.get('attr_name_en')),
            'value': attr.get('attr_value', attr.get('attr_value_en')),
        } for attr in raw.get('detail', {}).get('productDetails', [])
    ]
    data['imgs'] = [
        clean_img_url(img.get('origin_image'))
        for img in raw.get('goods_imgs').get('detail_image', [])
    ]
    if (cover := data.get('cover')) and isinstance(cover, str):
        data['cover'] = clean_img_url(cover)

    data['url'] = url
    return data


def shein_data_from_mobile(goods_id: str, url: str):
    api_url = f'https://m.shein.com/fr/product-xhr-{goods_id}.html?currency=USD&fromSpa=1&withI18n=0&_ver=1.1.8&_lang=fr'
    r = get(api_url)
    if r.status_code != 200:
        print('Request failed with status code', r.status_code, '\n', url, '\n')
        return

    try:
        return r.json()
    except Exception:
        pass


def shein_data_from_web(goods_id: str, url: str):
    api_url = f'https://us.shein.com/product-itemv2-{goods_id}.html?_lang=en&_ver=1.1.8'
    r = get(api_url)
    if r.status_code != 200:
        print('Request failed with status code', r.status_code, '\n', url, '\n')
        return

    soup = BeautifulSoup(r.text, 'html.parser')\
        .find("script", text=re.compile('productIntroData'))
    if not soup:
        return

    script = soup.string
    start = re.search('productIntroData: ', script)
    end = re.search('abt: {"', script)
    if not start or not end:
        return

    script = script[start.end():end.start()].strip()[:-1]
    return json.loads(script)


def shein_goods_id_from_url(url: str):
    if (match := re.search(r'p-(\d+)', url)) and (groups := match.groups()):
        return groups[0]
    return
#


def load_raw_data(raw: dict, map_key: str) -> dict:
    data = {}
    for key, value in SUPPLIER_MAP.get(map_key).get('keys').items():
        # value = value.get(map_key)
        # if not value or '__' in key:
        #     continue
        data[key] = get_dict_key(raw, value)

    return data
