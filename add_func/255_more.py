import json
import os
import pdb


def analyze_book_descriptions(data):
    folders_with_long_descriptions = []
    year = data[0]['FolderPath'].split('/')[-1]
    for index, record in enumerate(data):
        if len(record['BookContentDescription']) > 255:
            folders_with_long_descriptions.append(record['FolderName'])
            data[index]['BookContentDescription']= data[index]['BookContentDescription'][:255]
    total_records = len(data)
    long_description_count = len(folders_with_long_descriptions)

    return total_records, long_description_count, year, data, folders_with_long_descriptions


def load_json_to_list(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file: {file_path}")
        return []

def save_updated_data(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def find_json_files(folder_path):
    json_files = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            json_files.append(file_path)

    return json_files


folder_path = 'order data'
file_pathes = find_json_files(folder_path)
for file_path in file_pathes:
    data = load_json_to_list(file_path)
    total_records, long_description_count, year, new_data, folders_with_long_descriptions = analyze_book_descriptions(data)
    print(f"YEAR: {year}!  Total records: {total_records}, Records with long descriptions: {long_description_count}")
    # Відкриття файлу у режимі додавання
    with open('great_than_255.txt', 'a') as file:
        # Запис даних у файл
        file.write(str(folders_with_long_descriptions))
        file.write('_____')
        file.write('\n')
    if long_description_count > 0:
        print('saved? ')
        save_updated_data(new_data, file_path)




# обрізати залишати перші 255 символів