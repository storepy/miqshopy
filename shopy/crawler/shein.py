
import re
import json
import requests
from bs4 import BeautifulSoup


def get_product_data(url: str, _s: requests.Session = None):
    if not _s:
        _s = requests.Session()

    goods_id = get_goods_id_from_url(url)
    if not goods_id:
        return

    print(goods_id)

    raw = get_mobile_data(goods_id, url, _s=_s)
    web = get_web_data(goods_id, url, _s=_s)

    # _raw = shein_data_from_web(goods_id, url)
    if not raw:
        raw = web

    if not isinstance(raw, dict):
        return

    # supplier = SupplierChoice.SHEIN
    # data = load_raw_data(raw, supplier)
    # _data = load_raw_data(_raw, supplier)

    # data['cost'] = min(_data.get('retail_price', 0), _data.get('sale_price', 0))

    # data['attrs'] = [
    #     {
    #         'name': attr.get('attr_name', attr.get('attr_name_en')),
    #         'value': attr.get('attr_value', attr.get('attr_value_en')),
    #     } for attr in raw.get('detail', {}).get('productDetails', [])
    # ]
    # data['imgs'] = [
    #     clean_img_url(img.get('origin_image'))
    #     for img in raw.get('goods_imgs').get('detail_image', [])
    # ]
    # if (cover := data.get('cover')) and isinstance(cover, str):
    #     data['cover'] = clean_img_url(cover)

    # return data


def get_mobile_data(goods_id: str, url: str, *, _s: requests.Session = None):
    if not _s:
        _s = requests.Session()

    api_url = f'https://m.shein.com/fr/product-xhr-{goods_id}.html?currency=USD&fromSpa=1&withI18n=0&_ver=1.1.8&_lang=fr'
    r = _s.get(api_url)
    if r.status_code != 200:
        print('Request failed with status code', r.status_code, '\n', url, '\n')
        return

    try:
        return r.json()
    except Exception:
        pass


def get_web_data(goods_id: str, url: str, _s: requests.Session = None):
    if not _s:
        _s = requests.Session()

    api_url = f'https://us.shein.com/product-itemv2-{goods_id}.html?_lang=en&_ver=1.1.8'
    r = _s.get(api_url)
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


def get_goods_id_from_url(url: str):
    if (match := re.search(r'p-(\d+)', url)) and (groups := match.groups()):
        return groups[0]
    return


get_product_data('https://us.shein.com/SHEIN-PETITE-Solid-Cami-Bodycon-Dress-p-8000492-cat-1727.html')
