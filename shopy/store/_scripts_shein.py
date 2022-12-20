
import time
import random
import requests

from utils_crawler import shein_url_to_data
from _scripts_constants import domain, baseheaders


"""
Array.from(trs).forEach((i=>{
    const data = {}
    Array.from(i.getElementsByClassName('ga-order-goods')).forEach(link=>{
        data.href = link.getAttribute('href');
    });
    
    console.log(data)
}))



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


order_slug = '03ec7a72-3629-4c74-b4bc-6c077e8ccae6'  # local
# order_slug = ''


p_ = []


count = len(set(p_))

headers = {**baseheaders}

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

    try:
        post(link)
    except Exception as e:
        print('Error in post', link)
        print(e)

    if len(p_) > 1:
        time.sleep(random.randint(1, 5))

print('Crawled', count, 'links')

if errors:
    print('Errors with')
    print(errors)
