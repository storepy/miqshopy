
import random
import time
import requests

from utils_crawler import plt_url_to_data
from _scripts_constants import domain, baseheaders


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


order_slug = '387008fd-421b-4da1-8698-40819b34372c'  # local
# order_slug = ''


p_ = []

count = len(set(p_))

s = requests.Session()
headers = {
    **baseheaders
}


def post(url):
    global count

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
