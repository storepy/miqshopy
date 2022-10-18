
import random
import time
import requests

from utils_crawler import shein_url_to_data
from _scripts_constants import domain, baseheaders


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


order_slug = '0eeefd77-2ebd-4c43-9425-559219a2fc28'  # local
order_slug = '90e89872-7d6d-46a3-8122-3d1f62ffe9f6'


p_ = [
    'https://www.shein.com/Structured-Cuff-Choker-p-11214980-cat-1755.html?mallCode=1',
    'https://www.shein.com/Wave-Design-Cuff-Choker-p-11500541-cat-1755.html?mallCode=1',
    'https://www.shein.com/Minimalist-Cuff-Choker-p-11275860-cat-1755.html?mallCode=1',
    'https://www.shein.com/Minimalist-Cuff-Choker-p-11073905-cat-1755.html?mallCode=1',
    'https://www.shein.com/Solid-Minimalist-Layered-Cuff-Choker-p-11375205-cat-1755.html?mallCode=1',
    'https://www.shein.com/Solid-Minimalist-Layered-Choker-p-11375203-cat-1755.html?mallCode=1',
    'https://www.shein.com/Minimalist-Layered-Cuff-Choker-p-11143322-cat-1755.html?mallCode=1',
    'https://www.shein.com/Snake-Decor-Choker-p-11271928-cat-1755.html?mallCode=1',
    'https://www.shein.com/Knot-Decor-Cuff-Choker-p-11093360-cat-1755.html?mallCode=1',
    'https://www.shein.com/Minimalist-Cuff-Choker-p-11275772-cat-1755.html?mallCode=1',
    'https://www.shein.com/Cylindrical-Charm-Choker-p-11324983-cat-1755.html?mallCode=1',
    'https://www.shein.com/Minimalist-Layered-Cuff-Choker-p-11073934-cat-1755.html?mallCode=1',
    # '',
    'https://www.shein.com/3pcs-Layered-Minimalist-Ring-p-11323858-cat-1759.html?mallCode=1',
    'https://www.shein.com/2pcs-Circle-Decor-Ring-p-11275963-cat-1759.html?mallCode=1',
    'https://www.shein.com/4pcs-Minimalist-Metal-Ring-p-11205845-cat-1759.html?mallCode=1',
    'https://www.shein.com/Hollow-Out-Cuff-Choker-p-11073992-cat-1755.html?mallCode=1',
]


count = len(set(p_))

headers = {
    **baseheaders,
    'referrer': 'https://us.shein.com/'
}

s = requests.Session()
errors = []


def post(url):
    global count

    api = f'{domain}/shop/feed/{order_slug}/shein/'

    data = shein_url_to_data(url)
    if not data:
        print('Data ERROR', data)
        return

    try:
        r = s.post(api, json=data, headers=headers)
    except requests.exceptions.ConnectionError as e:
        print('Connection refused', url)
        print(e)

        errors.append(url)

    else:
        if r.status_code == 200:
            print(f': ADDED : {url}')
        else:
            print(f'Something went wrong\n{url}')
            print(r.status_code, r)
            count -= 1
            errors.append(url)


# p_.reverse()
for link in set(p_):
    if not link:
        continue

    post(link)
    if len(p_) > 1:
        time.sleep(random.randint(1, 5))

print('Crawled', count, 'links')

if errors:
    print('Errors with')
    print(errors)
