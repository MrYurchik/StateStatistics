import json

import pandas as pd

# Шлях до вашого CSV файлу
csv_file_path = 'KVED_2005.csv'
dtype_dict = {
    'Structure URN': str,
    'ID': str,
    'Name EN': str,
    'Name UK': str,
    'Description EN': str,
    'Description UK': str,
    'ID_orig': str,
    'ID_orig_without_sek': str,
    'Details': str,
    'Included Items': str,
    'Excluded Items': str,
    'parent': str  # Якщо 'parent' вже існує в даних; інакше цей стовпець буде додано пізніше
}


def fill_out_csv_2005(csv_file_path):
    def get_attribute_value(attributes, field_name):
        for attribute in attributes:
            if attribute['name'] == field_name:
                return attribute['value']
        return ''  # Повертаємо порожній рядок, якщо атрибут не знайдено


    # Читання CSV файлу в DataFrame
    df = pd.read_csv(csv_file_path, dtype=dtype_dict, encoding='utf-8')
    parent_map_dict = {}
    # Перевірка, чи існує колонка 'parent' і додавання її, якщо потрібно

    if 'Details' not in df.columns:
        df['Details'] = pd.NA
    if 'Included Items' not in df.columns:
        df['Included Items'] = pd.NA
    if 'Excluded Items' not in df.columns:
        df['Excluded Items'] = pd.NA
    if 'parent' not in df.columns:
        df['parent'] = pd.NA
    #
    with open('KVED_data_2005.json', 'r', encoding='utf8') as f:
        data = json.load(f)
        print(len(data))


    ref_map = {item['letter_ref']: item for item in data}

    # Ітерація через DataFrame і оновлення даних
    for index, row in df.iterrows():
        id_orig = row['ID']
        id_orig_without_sec = row['ID_orig_without_sek']
        parent_map_dict[id_orig_without_sec] = id_orig
        if id_orig_without_sec in ref_map:
            attributes = ref_map[id_orig_without_sec]['long_description'].get('attributes', [])
            # Перевіряємо і оновлюємо поля, якщо вони пусті
            for field in ['Details', 'Included Items', 'Excluded Items']:
                if pd.isnull(row[field]) or row[field] == '':
                    print(f"{field} {get_attribute_value(attributes, field)}")
                    df.at[index, field] = get_attribute_value(attributes, field)
            # Додавання або оновлення поля parent
            parent_orig = ref_map[id_orig_without_sec].get('parent', '')
            if parent_orig:
                df.at[index, 'parent'] = parent_map_dict.get(parent_orig, '')
            else:
                df.at[index, 'parent'] = parent_orig
    # Запис оновленого DataFrame назад у CSV
    df.to_csv(csv_file_path, index=False, encoding='utf-8')

    print("CSV файл успішно оновлено.")
