import json
import pdb
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from dataclasses import asdict

from models import StateStatisticsOrder, BookPageContentBody

zip_pdf_files = {}
global_list_order_data = []
global_list_order_data_alert = []
with open('category.json', 'r', encoding='utf-8') as file:
    category_dict = json.load(file)

year_dict = {2024: 706,
             2023: 710,
             2022: 776,
             2021: 777,
             2020: 778,
             2019: 779,
             2018: 780,
             2017: 781,
             2016: 782,
             2015: 783,
             2014: 784,
             2013: 785,
             2012: 786,
             2011: 787,
             2010: 788,
             2009: 789,
             2008: 790,
             2007: 791,
             2006: 792,
             2005: 793,
             2004: 794,
             2003: 795,
             2002: 796,
             2001: 797,
             2000: 798,
             1999: 799,
             1998: 800,
             1997: 801,
             1996: 802,
             1995: 803,
             1994: 804,
             }


class ScrapeOrder:
    def __init__(self, year):
        self.year = year

    def extract_data(self, soup, table_class, base_url, description):
        table = soup.find('table', class_=table_class)
        if not table:
            return None

        date, order_number = '', None
        for cell in table.find_all('td'):
            cell_text = cell.get_text(strip=True)
            if re.match(r'(\d{2}\.\d{2}\.\d{4})|(\d+\D{1,20}\d{4})', cell_text):
                date = cell_text.strip()
            elif re.match(r'№\s*\d+', cell_text):
                order_number = cell_text.strip()
                break
        if not order_number:
            print(f'ALERT! Order Number not found in {base_url}')
            pdb.set_trace()
        title = ''.join([tag.get_text(strip=True) for tag in soup.find_all('h1')]).strip()
        if not title and not soup.find_all('h1'):
            title = ''.join([item.get_text() for item in soup.find_all('p')[2:4]])

        links = self.extract_file_links(soup, base_url)
        soup('head')[0].extract()
        self.clear_bootom_tags(soup)
        page_referensec = [int(key) for key in category_dict if base_url in category_dict[key]]
        year = date.split('.')[-1]
        if not year or not year.isdigit():
            match = re.search(r'\b(19|20)\d{2}(?!\d)', date)
            year = match.group(0) if match else None
        if not year:
            pdb.set_trace()
        year_tag = year_dict[int(year)]
        order_data = StateStatisticsOrder(
            FolderPath=f"Корінь/Нормативні документи/Накази/{date.split('.')[-1]}",
            FolderName=f"{order_number.strip('№').strip()}_{date.split('.')[-1]}",
            FileNames=[*links],  # To be populated later with PDF file names
            BookContentTitle=f"Наказ від {date} {order_number}",
            BookContentDescription=description,
            BookPageReferences=[*page_referensec, 336, year_tag],  # To be populated with page references if available
            BookPageContentBody=BookPageContentBody(
                Title=title,
                DateAndNumber=f"від {date} {order_number}",
                OrderName=description,
                OrderText=soup.prettify(),  # Full order text goes here, formatted in HTML
            )
        )
        print(order_data.FolderPath, order_data.FolderName, order_data.FileNames,
              order_data.BookContentTitle, order_data.BookContentDescription)
        if not all([date, order_number, title, description]):
            global_list_order_data_alert.append(order_data)
            print(f'ALERT! date {date}, order {order_number}, title {title}, description {description}')

        global_list_order_data.append(asdict(order_data))
        return order_data

    def process_document(self, html_content, base_url, description):
        soup = BeautifulSoup(html_content, 'html.parser')
        doc_type = None
        if soup.find('table', class_='MsoTableGrid') and ".20" in soup.find('table', class_='MsoTableGrid').text:
            doc_type = 'type_1'
        elif soup.find('table', class_='MsoNormalTable'):
            doc_type = 'type_2'
        if doc_type == 'type_1':
            return self.extract_data(soup, 'MsoTableGrid', base_url, description)
        elif doc_type == 'type_2':
            return self.extract_data(soup, 'MsoNormalTable', base_url, description)

        print(f"ALERT NOT_1 NOT_2 TYPE: {base_url}")
        return None

    def find_parent_with_more_content(self, tag):
        if tag and tag.get_text(strip=True).strip() == "Про":
            return self.find_parent_with_more_content(tag.parent)
        result = re.sub(r'\s+', ' ', tag.get_text(strip=True))
        return result

    @staticmethod
    def extract_file_links(soup, base_url):
        file_links = []

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if not href.startswith('https://creativecommons.org'):
                url = urljoin(base_url, href)
                file_links.append(url)

        # Find all strings that look like URLs in the text
        text_urls = re.findall(r'(http[s]?://[^\s]+)', soup.get_text())
        for url in text_urls:
            # Exclude certain links, like the Creative Commons link
            if not url.startswith('https://creativecommons.org'):
                url = urljoin(base_url, url)
                file_links.append(url)

        return file_links

    @staticmethod
    def get_response_content(link):
        response = requests.get(link)
        response.encoding = 'windows-1251'
        return response

    @staticmethod
    def extract_description(start_tag):
        description_text = ''

        while start_tag:
            description_text += ' '.join(start_tag.stripped_strings) + ' '
            next_tag = start_tag.find_next('p', class_='MsoNormal')
            if not next_tag or not next_tag.text.strip() or not ' '.join(next_tag.stripped_strings):
                break
            description_text += ' '.join(next_tag.stripped_strings) + ' '
            start_tag = next_tag

        return description_text.strip()

    @staticmethod
    def clear_bootom_tags(soup):
        line_img = soup.find(lambda tag: tag.name == "span" and tag.find('img', src="../../../img/ua/line.gif"))
        if line_img:
            # Find all next siblings of the parent of line_img and remove them
            for sibling in line_img.find_parent().find_all_next():
                # If we reach 'body' or 'html', we stop the deletion
                if sibling.name in ['body', 'html']:
                    break
                sibling.extract()

        gerb_images = soup.find_all('img', src=lambda value: value and "GERB" in value)
        for img in gerb_images:
            img.decompose()

    def start(self):

        with open(f'link_lists/{self.year}_list_links.json', 'r', encoding='utf-8') as file:
            global_list_links = json.load(file)

        for link in global_list_links:
            if 'norm_doc/norm_doc/norm_doc' in link['link']:
                link['link'] = link['link'].replace('norm_doc/norm_doc/norm_doc', 'norm_doc')
            if link['link'].endswith('.zip') or link['link'].endswith('.pdf') or link['link'].endswith('.rar'):
                if zip_pdf_files.get(link['year']):
                    zip_pdf_files[link['year']].append(link['link'])
                else:
                    zip_pdf_files[link['year']] = [link['link']]
                continue
            html_content = self.get_response_content(link['link'])
            base_url = html_content.url
            description = link['title']
            self.process_document(html_content.text, base_url, description)

        with open(f'order data/{self.year}_list_order_data.json', 'w', encoding='utf-8') as file:
            file.write(json.dumps(global_list_order_data, ensure_ascii=False, indent=4))

        print(len(global_list_order_data))
        print(len(global_list_order_data_alert))
        print(f"zip_pdf order{zip_pdf_files}")
        print(f"ALL problem urls {global_list_order_data_alert}")
