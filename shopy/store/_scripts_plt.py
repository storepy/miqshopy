
import random
import time
import requests

from utils_crawler import plt_url_to_data


"""
const getPLTOrderProductLinks = () => {
  const r = document.getElementsByClassName('cta cta--secondary w-full block text-center');
  const links = [];

  let txt = '';
  Array.from(r).forEach((i) => {
    const href = i.getAttribute('href');
    const link =`https://www.prettylittlething.us${href}` 
    links.push(link);
    txt += `"${link}",`;
  });

  txt += '';
  console.log(txt);
  return links;
};
"""

domain = 'http://127.0.0.1:8000'
domain = 'http://192.168.1.231:8000'
# domain = 'http://feminity.africa'

order_slug = '387008fd-421b-4da1-8698-40819b34372c'  # local
# order_slug = ''


p_ = []

count = len(set(p_))

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
}


def post(url):
    global count

    s = requests.Session()
    api = f'{domain}/shop/feed/{order_slug}/plt/'

    data = plt_url_to_data(url)
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
