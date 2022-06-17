
import random
import time
import requests

from utils_crawler import shein_url_to_data


s = requests.Session()

"""
const getOrderLinks = () => {
  const r = document.getElementsByClassName('ga-order-goods');
  const links = [];

  let txt = '';
  Array.from(r).forEach((i) => {
    const href = i.getAttribute('href');
    links.push(`${href}`);
    txt += `"${href}",`;
  });

  txt += '';
  console.log(txt);
  return links;
};
"""

domain = 'http://127.0.0.1:8000'
domain = 'http://feminity.africa'

order_slug = 'f482d031-61f4-437e-93d8-fcf4217a9be9'  # local
order_slug = ''

api = f'{domain}/shop/feed/{order_slug}/'

p_ = [
]


def post(url):
    api_url = api

    data = shein_url_to_data(url)
    if not data:
        print('Data ERROR', data)
        return

    r = s.post(api_url, json=data)
    if r.status_code == 200:
        print(f': ADDED : {url}')
    else:
        print('Something went wrong\n')
        print(r.status_code, r)


for link in p_:
    if not link:
        continue

    post(link)
    if len(p_) > 1:
        time.sleep(random.randint(1, 5))
