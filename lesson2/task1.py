"""
1. Задание на закрепление знаний по модулю CSV. Написать скрипт, осуществляющий выборку определенных данных из файлов
info_1.txt, info_2.txt, info_3.txt и формирующий новый «отчетный» файл в формате CSV
"""
import csv

import chardet
import re


def get_data(*filenames_list):
    os_headers_list = ['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']
    main_data = [os_headers_list]

    for filename in filenames_list:
        os_prod_list = []
        with open(filename, 'rb') as f:
            result = chardet.detect(f.read())

        with open(filename, 'r', encoding=result['encoding']) as f:
            text = f.readlines()
            for line in text:
                for item in os_headers_list:
                    if item in line:
                        result = re.findall(r"(?<=" + item + ":).*", line)[0].strip()
                        os_prod_list.append(result)
        main_data.append(os_prod_list)
    return main_data


def write_to_csv():
    filenames = ['info_1.txt', 'info_2.txt', 'info_3.txt']
    main_list = get_data(*filenames)
    with open('info_os.csv', 'w', encoding='utf-8') as f:
        f_writer = csv.writer(f)
        for row in main_list:
            f_writer.writerow(row)


if __name__ == '__main__':
    write_to_csv()
