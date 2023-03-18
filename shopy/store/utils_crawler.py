
import re
import json
import requests
from pprint import pprint
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from miq.core.utils import clean_img_url, get_dict_key

SUPPLIER_SHEIN = 'SHEIN'

SUPPLIER_MAP = {
    SUPPLIER_SHEIN: {
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


_s = requests.Session()
_s.headers = {
    # "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4240.198 Safari/537.36",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1"
}


def print_session(session=_s):
    pass
    # print('-<\n-')
    # pprint(dict(_s.cookies))
    # print('---------------\n-\n-')
    # pprint(_s.headers)

    # print('Session:')


def get(url, **kwargs):
    return _s.get(
        url,
        headers={
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1"
        },
        cookies=kwargs.get('cookies', ),
        allow_redirects=False
    )


terms = [
    'SHEIN', 'PETITE', 'SXY',
    'PRETTYLITTLETHING', 'PRETTYLITTLETHING Shape - '
]


def clean_product_name(name: str) -> str:
    for term in terms:
        if term in name:
            name = name.replace(term, '')
    return name.strip()


#
# PLT
#

def plt_url_to_data(url: str) -> dict:
    def get_text(url):
        page = get(url)
        soup = BeautifulSoup(page.text, "html.parser")

        script = soup.find("script", type="application/ld+json")

        text = script.string.replace('\n', ' ')
        return soup, text

    soup, eng = get_text(url)
    href = soup.find("link", hreflang="fr-fr")['href']

    _soup, fr = get_text(href)

    data = load_raw_data(json.loads(fr), 'PLT')
    _data = load_raw_data(json.loads(eng), 'PLT')

    cost = _data.get('cost')
    if cost:
        data['cost'] = cost
        data['cost_currency'] = _data['cost_currency']

    carousel = _soup.find('div', id="product-carousel")
    imgs = carousel.select('img.gallery-image')
    data_imgs = []
    for i in imgs:
        data_imgs.append(clean_img_url(i['data-lazy']))

    data['imgs'] = data_imgs

    attrs = []
    for k in data.keys():
        if k.startswith('attrs__') and (value := data.get(k, None)):
            attrs.append({'name': k.replace('attrs__', ''), 'value': value})

    data['attrs'] = attrs
    data['url'] = url

    return data

#
# SHEIN
#


def shein_url_to_data(url: str):
    assert url, 'shein product url required'

    goods_id = shein_goods_id_from_url(url)
    if not goods_id:
        raise Exception('shein goods_id not found in url: ' + url)

    parsed_url = urlparse(url)
    if 'us.shein.com' not in parsed_url.netloc:
        url = 'https://us.shein.com' + parsed_url.path

    data = get_shein_us_data(url, goods_id)
    # if 'us.shein.com' in urlparse(url).netloc:
    #     data = get_shein_us_data(url, goods_id)
    # else:
    # data = get_shein_com_data(url, goods_id)

    if (cover := data.get('cover')) and isinstance(cover, str):
        data['cover'] = clean_img_url(cover)

    data['url'] = url

    return data


def get_shein_com_data(url: str, goods_id: str):
    assert url and goods_id, 'shein product url/goods_id required'

    raw = shein_data_from_mobile(goods_id, url)
    assert isinstance(raw, dict), 'shein_data_from_mobile() failed'

    data = load_raw_data(raw, SUPPLIER_SHEIN)
    data.update(get_shein_us_price(goods_id))

    data['cost'] = min(data.get('retail_price', 0), data.get('sale_price', 0))

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

    return data


def get_shein_us_data(url: str, goods_id: str):
    assert url and goods_id, 'shein product url/goods_id required'

    raw = shein_data_from_mobile(goods_id, url)
    # raw = shein_data_from_web(goods_id, url)

    # _raw = shein_data_from_web(goods_id, url)
    # if not raw:
    #     raw = _raw

    assert isinstance(raw, dict), 'Could not get data from url: ' + url

    data = load_raw_data(raw, SUPPLIER_SHEIN)
    # _data = load_raw_data(_raw, SUPPLIER_SHEIN)

    data['cost'] = min(data.get('retail_price', 0), data.get('sale_price', 0))
    # data['cost'] = min(_data.get('retail_price', 0), _data.get('sale_price', 0))

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

    return data


def shein_data_from_mobile(goods_id: str, url: str):
    api_url = f'https://m.shein.com/fr/product-xhr-{goods_id}.html?currency=USD&fromSpa=1&withI18n=0&_ver=1.1.8&_lang=fr'
    print('====>>> ', api_url)

    raise

    r = get(api_url)

    assert r.status_code == 200, 'Mobile Request failed with status code ' + \
        str(r.status_code) + '\n' + url + f'\n{r.text}'

    try:
        return r.json()
    except Exception:
        pass


def get_shein_us_price(goods_id: str):
    api_url = 'https://www.shein.com/atomic/getAtomicInfo?_ver=1.1.8&_lang=en'

    r = _s.post(api_url, json={
        "atomicParams": [{"mall_code": "1", "goods_id": goods_id}],
        "fields": {"realTimePricesWithPromotion": True}
    })
    if r.status_code != 200:
        print('Price Request failed with status code', r.status_code, '\n')
        return

    try:
        return {
            'retail_price': get_dict_key(r.json(), f'data__{goods_id}__retailPrice').get('amount'),
            'sale_price': get_dict_key(r.json(), f'data__{goods_id}__salePrice').get('amount'),
            'is_on_sale': '0' if get_dict_key(r.json(), f'data__{goods_id}__unit_discount') == '0' else '1'

        }
    except Exception:
        pass


def shein_data_from_web(goods_id: str, url: str):
    api_url = f'https://us.shein.com/product-itemv2-{goods_id}.html?_lang=en&_ver=1.1.8'

    # m_url = 'https://m.shein.com' + urlparse(url).path
    # _s.cookies.clear()

    r = get(api_url)
    #
    # print(r.json())
    #
    if r.status_code != 200:
        print('Web Request failed with status code', r.status_code, '\n', url, '\n')
        return

    soup = BeautifulSoup(r.text, 'html.parser')
    soup = soup.find("script", text=re.compile('productIntroData'))

    assert isinstance(f'{soup}', str), 'invalid soup'

    script = soup.string
    start = re.search('productIntroData: ', script)
    end = re.search('abt: {"', script)

    assert start and end, 'shein_data_from_web() failed'

    if not start or not end:
        return

    script = script[start.end():end.start()].strip()[:-1]
    data = json.loads(script)
    assert isinstance(data, dict), 'shein_data_from_web() failed'
    return data


def shein_goods_id_from_url(url: str):
    if (match := re.search(r'p-(\d+)', url)) and (groups := match.groups()):
        return groups[0]
    return


#
# UTILS
#

def load_raw_data(raw: dict, map_key: str) -> dict:
    data = {}
    for key, value in SUPPLIER_MAP.get(map_key).get('keys').items():
        # value = value.get(map_key)
        # if not value or '__' in key:
        #     continue
        data[key] = get_dict_key(raw, value)

    return data
