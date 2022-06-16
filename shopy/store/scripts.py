
import random
import time
import requests

from utils_crawler import shein_url_to_data


api = 'http://127.0.0.1:8000/shop/feed/{order_slug}/'


s = requests.Session()
s.get('http://127.0.0.1:8000/')

order_slug = 'f860f375-6c07-4c6d-8209-6e1d358d9cc6'

p_ = [
    ''
]


def post(url, order_slug):
    api_url = api.format(order_slug=order_slug)

    data = shein_url_to_data(url)
    r = s.post(api_url, json=data)
    if r.status_code == 200:
        print(f': ADDED : {url}')
    else:
        print('Something went wrong\n')
        print(r.status_code, r)


for link in p_:
    if not link:
        continue

    post(link, order_slug)
    if len(p_) > 1:
        time.sleep(random.randint(1, 5))
