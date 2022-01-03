"""
2. Задание на закрепление знаний по модулю json. Есть файл orders в формате JSON с информацией о заказах.
Написать скрипт, автоматизирующий его заполнение данными
"""
import json


def write_order_to_json(item, quantity, price, buyer, date):
    order_dict = {
        "item": item,
        "quantity": quantity,
        "price": price,
        "buyer": buyer,
        "date": date
    }
    with open('orders.json', 'w', encoding='utf-8') as f:
        json.dump(order_dict, f, sort_keys=True, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    write_order_to_json('Кроссовки', 30, 5600, 'Иванова.П.И', '12.12.2020')
