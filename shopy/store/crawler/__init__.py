
import re
import json
import requests
from bs4 import BeautifulSoup
from django.utils.text import capfirst

from miq.core.utils import clean_img_url, get_dict_key
from ..models import SupplierChoice, SUPPLIER_MAP


KEYS_MAP = {
    'brand': {'asos': 'brand__name', 'fnova': 'brand'},
    'id': {'asos': 'id'},
    'productCode': {'asos': 'productCode'},
    #
    'category': {'asos': 'productType__name', },
    'name': {'asos': 'name', },
    #

    #
    'gender': {'asos': 'gender'},
    #
    'cost': {'asos': 'price__current__value'},

    'cost_currency': {'asos': 'price__currency'},
    #
    'in_stock': {'asos': 'isInStock', },
    'isNoSize': {'asos': 'isNoSize'},
    'isOneSize': {'asos': 'isOneSize'},
}


class Crawler:
    _s = None  # type: 'requests.Session'
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
    }

# ZARA

    def zara_url_to_data(self, url: str):
        # https://www.zara.com/fr/fr/products-details?productIds=156517658&ajax=true
        # https://www.zara.com/us/en/product/111677272/extra-detail?ajax=true
        # jsonld
        return

# FNOVA

    def fnova_url_to_data(self, url: str) -> dict:
        r = self.get(f'{url}?view=pdp-json')
        raw = r.json().get('products', [])[0]
        data = self.load_raw_data(raw, SupplierChoice.FNOVA)
        data['imgs'] = [img.get('src') for img in data.get('imgs', []) if img.get('src') != data.get('cover')]
        data['cost'] = data.get('cost', 0) / 100
        return data

# PLT

    def plt_url_to_data(self, url: str) -> dict:
        def get_text(url):
            page = self.get(url)
            soup = BeautifulSoup(page.text, "html.parser")

            script = soup.find("script", type="application/ld+json")

            text = script.string.replace('\n', ' ')
            return soup, text

        soup, eng = get_text(url)
        href = soup.find("link", hreflang="fr-fr")['href']

        _soup, fr = get_text(href)

        data = self.load_raw_data(json.loads(fr), SupplierChoice.PLT)
        _data = self.load_raw_data(json.loads(eng), SupplierChoice.PLT)

        cost = _data.get('cost')
        if cost:
            data['cost'] = cost

        carousel = _soup.find('div', id="product-carousel")
        imgs = carousel.select('img.gallery-image')
        data_imgs = []
        for i in imgs:
            data_imgs.append(clean_img_url(i['data-lazy']))

        data['imgs'] = data_imgs

        return data

# ASOS

    def asos_url_to_data(self, url: str) -> dict:
        match = re.search(r'/prd/(\d+)', url)
        if not match:
            return
        id = match.groups()[0]
        if not id:
            return

        api_url = f'https://www.asos.com/api/product/catalogue/v3/products/{id}?store=US&currency=usd'
        raw = self.get(api_url)
        if raw.status_code != 200:
            return

        raw = raw.json()
        data = self.load_raw_data(raw, SupplierChoice.PLT)

        if names := raw.get('alternateNames'):
            for name_data in names:
                if name_data.get('locale') == 'fr-FR':
                    data['name'] = name_data.get('title')

        imgs = []
        attrs = []
        for img in raw.get('media', {}).get('images', []):
            if color := img.get('colour'):
                attrs.append({'couleur': capfirst(color.lower())})

            src = clean_img_url(img.get('url'))
            if img.get('isPrimary', False):
                data['cover'] = src
                continue
            imgs.append(src)

        data['imgs'] = imgs
        data['attrs'] = attrs

        if (info := raw.get('info')):
            text = getattr(info, 'aboutMe', '').replace('<br>', '\n') + '\n'\
                + getattr(info, 'sizeAndFit', '').replace('<br>', '\n') + '\n' \
                + getattr(info, 'careInfo', '').replace('<br>', '\n')
            data['description'] = text.replace('</br>', '\n')
        return data

# SHEIN

    def shein_url_to_data(self, url: str):
        goods_id = self.shein_goods_id_from_url(url)
        if not goods_id:
            return

        raw = self.shein_data_from_mobile(goods_id, url)
        _raw = self.shein_data_from_web(goods_id, url)
        if not raw:
            raw = _raw

        if not isinstance(raw, dict):
            return

        supplier = SupplierChoice.SHEIN
        data = self.load_raw_data(raw, supplier)
        _data = self.load_raw_data(_raw, supplier)

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

        return data

    def shein_data_from_mobile(self, goods_id: str, url: str):
        api_url = f'https://m.shein.com/fr/product-xhr-{goods_id}.html?currency=USD&fromSpa=1&withI18n=0&_ver=1.1.8&_lang=fr'
        r = self.get(api_url)
        if r.status_code != 200:
            print('Request failed with status code', r.status_code, '\n', url, '\n')
            return

        try:
            return r.json()
        except Exception:
            pass

    def shein_data_from_web(self, goods_id: str, url: str):
        api_url = f'https://us.shein.com/product-itemv2-{goods_id}.html?_lang=en&_ver=1.1.8'
        r = self.get(api_url)
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

    def shein_goods_id_from_url(self, url: str):
        if (match := re.search(r'p-(\d+)', url)) and (groups := match.groups()):
            return groups[0]
        return
#

    def load_raw_data(self, raw: dict, map_key: str) -> dict:
        data = {}
        for key, value in SUPPLIER_MAP.get(map_key).items():
            # value = value.get(map_key)
            # if not value or '__' in key:
            #     continue
            data[key] = get_dict_key(raw, value)

        return data

#

    def __init__(self, *args, **kwargs):
        if not kwargs.get('session'):
            self._s = requests.Session()

    def get(self, url: str):
        return self._s.get(url, headers=self.headers)


c = Crawler()

# url = 'https://www.prettylittlething.fr/robe-moulante-gris-pierre-cotelee-a-col-rond.html'
# # c.plt_url_to_data(url)

# url = 'https://www.asos.com/us/closet-london/closet-london-puff-shoulder-pencil-dress-with-bodice-detail-in-mink/prd/201364766?clr=mink&colourWayId=201364770&cid=19645'
# # c.asos_url_to_data(url)

# url = 'https://fr.shein.com/Lapel-Neck-PU-Blazer-p-4968967-cat-1739.html'
# # c.shein_url_to_data(url)

# url = 'https://www.fashionnova.com/products/soothe-off-shoulder-jumpsuit-burgundy'
# c.fnova_url_to_data(url)
