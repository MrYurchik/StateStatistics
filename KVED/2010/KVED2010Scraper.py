import json
from dataclasses import asdict

from KVED import KvedScraper, fill_out_csv_2010
from models import KvedModel

start_page = 'https://kved.ukrstat.gov.ua/KVED2010/kv10_i.html'
csv_file_path = 'KVED_2010.csv'
json_file_path = 'KVED_data_2010.json'

class Kved2010Scraper(KvedScraper):
    def start(self) -> list:
        all_kved_obj_list = []
        soup = self.get_soup_from_link(start_page)
        table = soup.find_all('table')[1]

        # Loop through each row in the table except for the header row
        for row in table.find_all('tr')[1:]:  # [1:] to skip the header row
            # Extract the letter reference, which is the text of the first <a> tag in each row
            letter_ref = row.find('td', class_='LC1_DR').a.text.strip()

            # Extract the link, which is the href attribute of the first <a> tag in each row
            link = 'https://kved.ukrstat.gov.ua' + row.find('td', class_='LC1_DR').a['href'].strip()

            # Extract the short description, which is the text of the first <p> tag in the second <td>
            name = row.find('td').find_next_sibling('td').p.text.strip()
            long_description, sub_sections = self.sub_section(link, name, parent=letter_ref)
            main_section_obj = KvedModel(letter_ref=letter_ref, name=name, parent='', long_description=long_description)
            # Append the extracted data to the list
            all_kved_obj_list.append(asdict(main_section_obj))
            for sub_s in sub_sections:
                all_kved_obj_list.append(asdict(sub_s))

        print(all_kved_obj_list)
        return all_kved_obj_list


if __name__ == "__main__":
    kved = Kved2010Scraper(start_page=start_page)
    list_results = kved.start()
    with open(json_file_path, 'w', encoding='utf-8') as file:
        file.write(json.dumps(list_results, ensure_ascii=False, indent=4))

    fill_out_csv_2010(csv_file_path=csv_file_path)

