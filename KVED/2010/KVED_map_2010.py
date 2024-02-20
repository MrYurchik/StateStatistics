import json

with open('KVED_data_UPDATED.json', 'r', encoding='utf8') as f:
    data = json.load(f)
    print(len(data))

# list1 = [{'id': 1, 'name': 'Item 1'}, {'id': 2, 'name': 'Item 2'}]
# list2 = [{'letter_ref': 1, 'value': 'A'}, {'letter_ref': 2, 'value': 'B'}]

# Створення словника для швидкого доступу до елементів другого списку по 'letter_ref'
ref_map = {item['letter_ref']: item for item in data}

with open('KVED_ORIGIN.json', 'r+', encoding='utf-8') as file:
    data = json.load(file)
    list1 = data['terms']

    # Маппінг елементів
    for item in list1:
        if '_' in item['id']:
            origin_id = item['id'].replace('_', '.')
            if origin_id in ref_map:
                print(origin_id, ref_map[origin_id])
                if len(item['annotations']) != len(ref_map[origin_id]['long_description']['annotations']):
                    item['annotations'].extend(ref_map[origin_id]['long_description']['annotations'])
                    item['attributes'].extend(ref_map[origin_id]['long_description']['attributes'])
                    print(f"{origin_id} updated!")
                else:
                    print(f"{origin_id} found but nothing to update")

        elif item['id'] in ref_map:
            if len(item['annotations']) != len(ref_map[item['id']]['long_description']['annotations']):
                item['annotations'].extend(ref_map[item['id']]['long_description']['annotations'])
                item['attributes'].extend(ref_map[item['id']]['long_description']['attributes'])
                print(f"{item['id']} updated!")
            else:
                print(f"{item['id']} found but nothing to update")
        else:
            print(f'No reference found for {item["id"]}')

    data['terms'] = list1
    file.seek(0)  # Повертаємось на початок файлу для запису
    json.dump(list1, file, ensure_ascii=False, indent=4)
    file.truncate()






