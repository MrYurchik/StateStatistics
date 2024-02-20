import json

import requests
from requests.exceptions import Timeout
from bs4 import BeautifulSoup, NavigableString, Tag
from dataclasses import asdict
from models import KvedModel
from KVED import fill_out_csv_2005

start_page = 'https://kved.ukrstat.gov.ua/KVED2005/kv05_i.html'
BASE_URL = "https://kved.ukrstat.gov.ua"
csv_file_path = 'KVED_2005.csv'
json_file_path = 'KVED_data_2005.json'


class KvedScraper:
    def __init__(self, start_page):
        self.start_page = start_page

    @staticmethod
    def get_soup_from_link(link):
        attempts = 5
        for i in range(attempts):
            try:
                resp = requests.get(link, timeout=10)
                resp.encoding = 'windows-1251'
                soup = BeautifulSoup(resp.text, 'html.parser')
                return soup
            except Timeout:
                print(f"Спроба {i + 1} з {attempts} - час очікування вичерпано.")
                if i < attempts - 1:
                    print("Спробуємо ще раз...")
                else:
                    print("Не вдалося з'єднатися з сервером.")

    def start(self) -> list:
        all_kved_obj_list = []
        soup = self.get_soup_from_link(self.start_page)
        table = soup.find_all('table')[1]
        # Loop through each row in the table except for the header row
        for row in table.find_all('tr')[1:]:  # [1:] to skip the header row

            letter_ref = row.find('td', class_='LC1_DR').a.text.strip()
            link = 'https://kved.ukrstat.gov.ua' + row.find('td', class_='LC1_DR').a['href'].strip()
            name = row.find('td').find_next_sibling('td').p.text.strip()
            # check if its subsection or chapter
            long_description, sub_sections = self.check_if_subsection(link, name, parent=letter_ref)
            main_section_obj = KvedModel(letter_ref=letter_ref, name=name, parent='', long_description=long_description)
            all_kved_obj_list.append(asdict(main_section_obj))
            for sub_s in sub_sections:
                all_kved_obj_list.append(asdict(sub_s))

        print(all_kved_obj_list)
        return all_kved_obj_list

    def check_if_subsection(self, link, name_not_details, parent):
        soup = self.get_soup_from_link(link)
        if "Підсекція" in soup.find('table', class_='Sub_List').find_all('tr', class_='List_Row')[0].text:
            sub_section_list = []
            long_desc_tag = soup.find_all('table')[3]
            long_desc = self.extract_description(long_desc_tag, name_not_details)
            sub_sections = soup.find('table', class_='Sub_List').find_all('tr', class_='List_Row')[
                           1:]  # Skip header row
            for row in sub_sections:
                letter_ref = row.find('td', class_='LC1_DR').text.strip()
                name = row.find('td').find_next_sibling('td').text.strip()
                sub_group_link = 'https://kved.ukrstat.gov.ua' + row.find('a')['href']
                long_description, sub_groups = self.sub_section(sub_group_link, name, letter_ref)
                sub_section_obj = KvedModel(letter_ref=letter_ref, name=name, parent=parent,
                                            long_description=long_description)
                sub_section_list.append(sub_section_obj)
                sub_section_list.extend(sub_groups)

            return long_desc, sub_section_list
        else:
            return self.sub_section(link, name_not_details, parent)

    def sub_section(self, link, name_not_details, parent) -> (list[dict], list[KvedModel]):
        sub_group_list = []
        print(f'requesting {link}')
        soup = self.get_soup_from_link(link)
        long_desc_tag = soup.find_all('table')[-3]
        long_desc = self.extract_description(long_desc_tag, name_not_details)
        sub_groups = soup.find('table', class_='Sub_List').find_all('tr', class_='List_Row')[1:]  # Skip header row
        for row in sub_groups:
            letter_ref = row.find('td', class_='LC1_DR').text.strip()
            name = row.find('td').find_next_sibling('td').text.strip()
            sub_group_link = 'https://kved.ukrstat.gov.ua' + row.find('a')['href']
            long_description, sub_groups = self.sub_group(sub_group_link, name, letter_ref)
            sub_section_obj = KvedModel(letter_ref=letter_ref, name=name, parent=parent,
                                        long_description=long_description)
            sub_group_list.append(sub_section_obj)
            sub_group_list.extend(sub_groups)
        return long_desc, sub_group_list

    def sub_group(self, link, name_not_details, parent) -> (list[dict], list[KvedModel]):
        # List to store each sub_class info
        sub_group_list = []
        print(f'requesting {link}')
        soup = self.get_soup_from_link(link)
        desc_table = soup.find_all('table')[4]
        long_descr = self.extract_description(desc_table, name_not_details)

        rows = soup.select('.Sub_List tr')[1:]  # CSS selector to skip header

        # Iterate over the rows to extract info
        for row in rows:
            # Extract the letter reference from the text within the <a> tag
            letter_ref = row.find('a').text.strip()
            # Extract the name from the text within the <p> tag
            name = row.find('p').text.strip()

            # Construct the full link by appending the href attribute to the base URL
            sub_group_link = BASE_URL + row.find('a')['href']
            long_description, sub_classes = self.sub_class(sub_group_link, name, letter_ref)
            sub_group_obj = KvedModel(letter_ref=letter_ref, name=name, parent=parent,
                                      long_description=long_description)
            # Append the extracted data to the list
            sub_group_list.append(sub_group_obj)
            sub_group_list.extend(sub_classes)

        return long_descr, sub_group_list

    def sub_class(self, link, name_not_details, parent) -> (list[dict], list[KvedModel]):
        print(f'requesting {link}')
        soup = self.get_soup_from_link(link)
        desc_table = soup.find_all('table')[-3]
        long_descr = self.extract_description(desc_table, name_not_details)
        subclasses_table = soup.find_all('table')[-2]
        subclass_rows = subclasses_table.find_all('tr', class_='List_Row')[1:]  # Skip header row

        # List to store subclass info
        subclasses_list = []
        # Extract subclass info from each row
        for row in subclass_rows:
            # Extract letter_ref from the link text
            letter_ref = row.find('a').text.strip()
            # Extract name from the paragraph text
            name = row.find('p').text.strip()
            # Construct the full link by appending the href attribute to the base URL
            sub_class_link = BASE_URL + row.find('a')['href']
            long_description, sub_classes = self.classes(sub_class_link, name, letter_ref)
            sub_class_obj = KvedModel(name=name, letter_ref=letter_ref, parent=parent,
                                      long_description=long_description)
            # Append subclass info to the list

            subclasses_list.append(sub_class_obj)
            subclasses_list.extend(sub_classes)

        return long_descr, subclasses_list

    def classes(self, link, name_not_details, parent):
        print(f'requesting {link}')
        soup = self.get_soup_from_link(link)

        if len(soup.find_all('table')) > 8:
            desc_table = soup.find_all('table')[-3]  # len all tables 9
            description = self.extract_description(desc_table, name_not_details)
            subsubclasses_table = soup.find_all('table')[-2]
            subsubclass_rows = subsubclasses_table.find_all('tr', class_='List_Row')[1:]  # Skip header row

            # List to store subclass info
            subsubclasses_list = []
            # Extract subclass info from each row
            for row in subsubclass_rows:
                # Extract letter_ref from the link text
                letter_ref = row.find('a').text.strip()
                # Extract name from the paragraph text
                name = row.find('p').text.strip()
                # Construct the full link by appending the href attribute to the base URL
                sub_sub_class_link = BASE_URL + row.find('a')['href']
                print('classes')
                long_description = self.sub_sub_classes(sub_sub_class_link, name)
                sub_class_obj = KvedModel(name=name, letter_ref=letter_ref, parent=parent,
                                          long_description=long_description)
                # Append subclass info to the list

                subsubclasses_list.append(sub_class_obj)
            return description, subsubclasses_list
        else:
            desc_table = soup.find_all('table')[-2]  # len all tables 8
            description = self.extract_description(desc_table, name_not_details)
            return description, []

    def sub_sub_classes(self, link, name_not_details):
        print(f'its sub_sub_classes requesting {link}')
        soup = self.get_soup_from_link(link)
        desc_table = soup.find_all('table')[-2]
        description = self.extract_description(desc_table, name_not_details)
        return description

    @staticmethod
    def check_inclusion(text, included_list, excluded_list):
        if any(phrase in text for phrase in included_list):
            return "included"
        elif any(phrase in text for phrase in excluded_list):
            return "excluded"
        return None

    @staticmethod
    def format_output(details, included_items, excluded_items):
        attributes = []

        if details.strip():
            attributes.append({
                "name": "Details",
                "value": details.strip()
            })

        if included_items.strip():
            attributes.append({
                "name": "Included Items",
                "value": included_items.strip()
            })

        if excluded_items.strip():
            attributes.append({
                "name": "Excluded Items",
                "value": excluded_items.strip()
            })

        return {'attributes': attributes}

    def extract_description(self, soup, name_not_details):
        list_included = ["Ця секція включає", "Цей розділ включає", "Цей розділ також включає", "Ця група включає",
                         "Цей клас включає", "Ця група також включає", "Ця група включає також", "Цей підклас включає"]
        list_excluded = ["Ця секція не включає", "Цей розділ не включає", "Ця група не включає", "Цей клас не включає",
                         "Цей підклас не включає"]
        details = ""
        included_items = ""
        excluded_items = ""
        current_section = "details"
        for element in soup.find_all('td')[-1].children:
            if element == ' КЗП ' or element == ' ПЗП ':
                continue
            if isinstance(element, (NavigableString, Tag)):
                text = ""
                if isinstance(element, Tag):
                    if element.get_text() == name_not_details:
                        continue
                    if element.get_text() == name_not_details + " ":
                        continue
                    # Створюємо новий тег з тим же ім'ям, що й оригінальний
                    new_tag = BeautifulSoup('', 'html.parser').new_tag(element.name)
                    # Додаємо внутрішній текст тега
                    new_tag.string = element.get_text()
                    # Конвертуємо новий тег у рядок
                    text = str(new_tag)
                elif isinstance(element, NavigableString):
                    text = str(element).strip()
                section_type = self.check_inclusion(text, list_included, list_excluded)
                if section_type == "included":
                    included_items += text + " "
                    current_section = "included"
                elif section_type == "excluded":
                    excluded_items += text + " "
                    current_section = "excluded"
                else:
                    if current_section == "details":
                        details += text + " "
                    elif current_section == "included":
                        included_items += text + " "
                    elif current_section == "excluded":
                        excluded_items += text + " "
        return self.format_output(details, included_items, excluded_items)


if __name__ == "__main__":
    kved = KvedScraper(start_page=start_page)
    list_results = kved.start()
    with open(json_file_path, 'w', encoding='utf-8') as file:
        file.write(json.dumps(list_results, ensure_ascii=False, indent=4))

    fill_out_csv_2005(csv_file_path=csv_file_path)
