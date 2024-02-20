import json
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from scrape import BASE_URL


# URL веб-сторінки для скрапінгу

url_dict = {'https://www.ukrstat.gov.ua/norm_doc/norm_rozd/nasel.htm': 346,
            "https://www.ukrstat.gov.ua/norm_doc/norm_rozd/praci.htm": 347,
            "https://www.ukrstat.gov.ua/norm_doc/norm_rozd/osv.htm": 348,
            "https://www.ukrstat.gov.ua/norm_doc/norm_rozd/o_z.htm": 349,
            "https://www.ukrstat.gov.ua/norm_doc/norm_rozd/domgosp.htm": 350,
            "https://www.ukrstat.gov.ua/norm_doc/norm_rozd/pz.htm": 352,
            "https://www.ukrstat.gov.ua/norm_doc/norm_rozd/prom.htm": 355,
            "https://www.ukrstat.gov.ua/norm_doc/norm_rozd/sg.htm": 356,
            "https://www.ukrstat.gov.ua/norm_doc/norm_rozd/byd.htm": 357,
            "https://www.ukrstat.gov.ua/norm_doc/norm_rozd/oz.htm": 358,
            "https://www.ukrstat.gov.ua/norm_doc/norm_rozd/invest.htm": 358,
            "https://www.ukrstat.gov.ua/norm_doc/norm_rozd/torg.htm": 359,
            "https://www.ukrstat.gov.ua/norm_doc/norm_rozd/posl.htm": 359,
            "https://www.ukrstat.gov.ua/norm_doc/norm_rozd/tz.htm": 360,
            "https://www.ukrstat.gov.ua/norm_doc/norm_rozd/tur.htm": 361,
            "https://www.ukrstat.gov.ua/norm_doc/norm_rozd/tend_da.htm": 362,
            "https://www.ukrstat.gov.ua/norm_doc/norm_rozd/innov.htm": 364,
            "https://www.ukrstat.gov.ua/norm_doc/norm_rozd/nps.htm": 367,
            "https://www.ukrstat.gov.ua/norm_doc/norm_rozd/energ.htm": 368,
            "https://www.ukrstat.gov.ua/norm_doc/norm_rozd/macroec.htm": 370,
            "https://www.ukrstat.gov.ua/norm_doc/norm_rozd/cin.htm": 371,
            "https://www.ukrstat.gov.ua/norm_doc/norm_rozd/z_torg.htm": 372
            }
result_dict = {}


def find_cat_order(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    all_links = [link['href'] for link in soup.find_all('a', href=True)]

    all_links = [urljoin(BASE_URL, link) if 'metod_polog' in link else urljoin(BASE_URL, link.replace("../", "norm_doc/")) for link in all_links]
    # Фільтрування посилань, які включають шаблон року та номеру наказу (наприклад, "../2023/188/188_2023.htm")
    orders_urls = [link for link in all_links if re.search(r"/\d{4}/\d+/\d+_\d{4}\.htm", link)]
    # Оновлення словника даних
    if not result_dict.get(url_dict[url]):
        result_dict[url_dict[url]] = orders_urls
    else:
        result_dict[url_dict[url]].extend(orders_urls)
    return result_dict


for url in url_dict:
    find_cat_order(url)

print(result_dict)

with open('category.json', 'w', encoding='utf-8') as file:
    file.write(json.dumps(result_dict, ensure_ascii=False, indent=4))
