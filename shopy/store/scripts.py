
import random
import time
import requests

from utils_crawler import shein_url_to_data


"""
const getSheinOrderProductLinks = () => {
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
domain = 'http://192.168.1.231:8000'
domain = 'http://feminity.africa'

order_slug = 'f482d031-61f4-437e-93d8-fcf4217a9be9'  # local
order_slug = ''


p_ = [
]

count = len(set(p_))

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
}


def post(url):
    global count

    s = requests.Session()
    api = f'{domain}/shop/feed/{order_slug}/'

    data = shein_url_to_data(url)
    if not data:
        print('Data ERROR', data)
        return

    try:
        r = s.post(api, json=data, headers=headers)
    except requests.exceptions.ConnectionError as e:
        print('Connection refused', url)
        print(e)
    else:
        if r.status_code == 200:
            print(f': ADDED : {url}')
        else:
            print(f'Something went wrong\n{url}')
            print(r.status_code, r)
            count -= 1


for link in set(p_):
    if not link:
        continue

    post(link)
    if len(p_) > 1:
        time.sleep(random.randint(1, 5))

print('Crawled', count, 'links')
