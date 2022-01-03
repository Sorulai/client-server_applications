"""
Задание на закрепление знаний по модулю yaml.
Написать скрипт, автоматизирующий сохранение данных в файле YAML-формата.
"""

import yaml


def write_yaml():
    data_yaml = {
        'one': ['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы'],
        'two': 4567,
        'three': {
            '5@': 567,
            '30€': 5246
        }
    }
    with open('file.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(data_yaml, f, default_flow_style=False, allow_unicode=True)

    with open('file.yaml', encoding='utf-8') as f:
        yaml_dict = yaml.load(f, Loader=yaml.FullLoader)

    for key, value in data_yaml.items():
        try:
            if yaml_dict[key] and yaml_dict[key] == value:
                print(f'Ключ {key} со значением {value} есть в словаре yaml_dict')
        except Exception:
            print(f'Ключа {key} со значением {value} нет в словаре yaml_dict')


if __name__ == '__main__':
    write_yaml()
