import json
import os


def rpl_tags(data):
    for index, record in enumerate(data):
        data[index]['BookPageContentBody']['OrderText'] = data[index]['BookPageContentBody']['OrderText'].replace('<html>', '').replace('<body>',
                                                                                                       '').replace(
            '</body>', '').replace('</html>', '')

    return data


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
    new_data = rpl_tags(data)
    print(f"html in {file_path} updated")

    save_updated_data(new_data, file_path)
    print('saved???')
    print('___')
