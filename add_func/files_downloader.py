import json
import os
import pdb

import requests

global_htm_links = []
global_txt_links =[]
global_not_found_links = []
global_another_error = []

def download_file(url, path):
    """Функція для завантаження файлу з URL."""
    if url.endswith('\".') or url.endswith('\";'):
        url = url[:-2]
    if url.endswith('\"'):
        url = url[:-1]
    try:
        response = requests.get(url)
        response.raise_for_status()  # will raise an HTTPError if the HTTP request returned an unsuccessful status code

        # Only proceed if the directory does not exist and FileNames is not empty
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Write the content of the response to a new file in binary mode
        with open(path, 'wb') as out_file:
            out_file.write(response.content)
        return True
    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        global_not_found_links.append((path, url))
        return False
    except requests.exceptions.RequestException as err:
        print(f"Request error occurred: {err}")
        global_another_error.append((path, url))
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        global_another_error.append((path, url))
        return False




def process_files(data):
    htm_dict = {}
    text_dict = {}
    if not os.path.exists('files'):
        os.makedirs('files')

    for entry in data:
        folder_name = entry['FolderName']
        file_names = entry['FileNames']

        filtered_urls = [url for url in file_names if not url.endswith('.htm') and "#Text" not in url]
        htm_urls = [url for url in file_names if url.endswith('.htm')]
        text_files = [url for url in file_names if "#Text" in url]
        if htm_urls:
            htm_dict[folder_name] = htm_urls
        if text_files:
            text_dict[folder_name] = text_files
        try:
            order, year = folder_name.split('_')
        except ValueError:
            pdb.set_trace()
        path = os.path.join('files', year, folder_name)
        if not os.path.exists(path):
            os.makedirs(path)

        updated_file_names = []

        # Завантаження та перейменування файлів
        for index, file_url in enumerate(filtered_urls, start=1):
            file_extension = os.path.splitext(file_url)[1]
            new_file_name = f"{folder_name}_{index}{file_extension}" if len(filtered_urls) > 1 else f"{folder_name}{file_extension}"
            if download_file(file_url, os.path.join(path, new_file_name)):
                updated_file_names.append(new_file_name)

        entry['FileNames'] = updated_file_names
        if not updated_file_names and os.path.exists(path):
            os.rmdir(path)
        else:
            print(f"{folder_name} file has been downloaded and filenames has been changed")
    print("HTM Links:")
    global_htm_links.append(htm_dict)
    for folder, urls in htm_dict.items():
        print(f"{folder}: {urls}")
    print("Text Links:")
    global_txt_links.append(text_dict)
    for folder, urls in text_dict.items():
        print(f"{folder}: {urls}")

    return data

# Приклад використання
data = [
    {
        "FolderName": "354_2023",
        "FileNames": ["http://example.com/file1.pdf", "http://example.com/file2.zip", "http://example.com/page.htm"]
    }
    # ... інші записи ...
]
path_to_list_order_data = "order data/2002_1993_list_order_data.json"
with open(path_to_list_order_data, 'r', encoding='utf-8') as file:
    global_order_list = json.load(file)
    data = global_order_list


processed_data = process_files(data)

with open(path_to_list_order_data, 'w', encoding='utf-8') as file:
    json.dump(processed_data, file, ensure_ascii=False, indent=4)

year = path_to_list_order_data.split("/")[-1].split("_list_order_data")[0]
with open(f'files/{year}_bad_links', 'w', encoding='utf-8') as file:
    file.write("TXT Links:\n")
    json.dump(global_txt_links, file, ensure_ascii=False, indent=4)
    file.write("Not Found Links:\n")
    json.dump(global_not_found_links, file, ensure_ascii=False, indent=4)
    file.write("HTM Links:\n")
    json.dump(global_htm_links, file, ensure_ascii=False, indent=4)
