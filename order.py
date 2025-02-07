import requests
import json
from collections import Counter
from datetime import datetime
import pprint
import logging
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из .env файла
load_dotenv()
API_LOGIN = os.getenv('API_LOGIN')

# Настройка логирования
logging.basicConfig(filename='script.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

# Функция для получения токена доступа
def get_access_token(api_login):
    url = "https://api-eu.syrve.live/api/1/access_token"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "apiLogin": api_login
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        token = data.get('token')
        if not token:
            logging.error("Не удалось получить токен из ответа.")
            print("Не удалось получить токен из ответа.")
            return None
        logging.info(f"Получен токен доступа: {token}")
        print(f"Получен токен доступа: {token}")
        return token
    except requests.HTTPError as http_err:
        logging.error(f"HTTP ошибка: {http_err} - Ответ: {response.text}")
        print(f"HTTP ошибка: {http_err} - Ответ: {response.text}")
    except Exception as err:
        logging.error(f"Произошла ошибка: {err}")
        print(f"Произошла ошибка: {err}")
    return None

# Функция для получения списка организаций
def get_organizations(token):
    url = "https://api-eu.syrve.live/api/1/organizations"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        organizations = data.get('organizations', [])
        logging.info(f"Получено организаций: {len(organizations)}")
        return organizations
    except requests.HTTPError as http_err:
        logging.error(f"HTTP ошибка при получении организаций: {http_err} - Ответ: {response.text}")
        print(f"HTTP ошибка при получении организаций: {http_err} - Ответ: {response.text}")
    except Exception as err:
        logging.error(f"Произошла ошибка при получении организаций: {err}")
        print(f"Произошла ошибка при получении организаций: {err}")
    return None

# Функция для получения терминальных групп
def get_terminal_groups(token, organization_ids):
    url = "https://api-eu.syrve.live/api/1/terminal_groups"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "organizationIds": organization_ids,
        "includeDisabled": True,
        "returnExternalData": ["string"]  # Убедись, что это соответствует требованиям API
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        terminal_groups_data = data.get('terminalGroups', []) + data.get('terminalGroupsInSleep', [])
        terminal_groups = []
        for group in terminal_groups_data:
            items = group.get('items', [])
            for item in items:
                terminal_group_id = item.get('id')
                terminal_group_name = item.get('name')
                if terminal_group_id:
                    terminal_groups.append({
                        'id': terminal_group_id,
                        'name': terminal_group_name
                    })
        logging.info(f"Получено терминальных групп: {len(terminal_groups)}")
        return terminal_groups
    except requests.HTTPError as http_err:
        logging.error(f"HTTP ошибка при получении терминальных групп: {http_err} - Ответ: {response.text}")
        print(f"HTTP ошибка при получении терминальных групп: {http_err} - Ответ: {response.text}")
    except Exception as err:
        logging.error(f"Произошла ошибка при получении терминальных групп: {err}")
        print(f"Произошла ошибка при получении терминальных групп: {err}")
    return None

# Функция для получения доступных секций ресторанов (таблиц)
def get_available_restaurant_sections(token, terminal_group_ids, return_schema=False, revision=0):
    url = "https://api-eu.syrve.live/api/1/reserve/available_restaurant_sections"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "terminalGroupIds": terminal_group_ids,
        "returnSchema": return_schema,
        "revision": revision
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        restaurant_sections = data.get('restaurantSections', [])
        logging.info(f"Получено секций ресторанов: {len(restaurant_sections)}")
        return restaurant_sections
    except requests.HTTPError as http_err:
        logging.error(f"HTTP ошибка при получении секций ресторанов: {http_err} - Ответ: {response.text}")
        print(f"HTTP ошибка при получении секций ресторанов: {http_err} - Ответ: {response.text}")
    except Exception as err:
        logging.error(f"Произошла ошибка при получении секций ресторанов: {err}")
        print(f"Произошла ошибка при получении секций ресторанов: {err}")
    return None

# Функция для получения заказов по таблицам
def get_orders_by_table(token, organization_ids, table_ids, date_from, date_to, statuses=["New", "Closed"]):
    url = "https://api-eu.syrve.live/api/1/order/by_table"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "organizationIds": organization_ids,
        "tableIds": table_ids,
        "statuses": statuses,
        "dateFrom": date_from,
        "dateTo": date_to
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()

        # Инициализируем пустой список для заказов
        orders = []

        # Извлекаем заказы из 'orders'
        orders_list = data.get('orders', [])
        orders.extend(orders_list)

        logging.info(f"Получено заказов: {len(orders)}")

        # Выводим пример первого заказа
        if orders:
            print("\nПример первого заказа:")
            pprint.pprint(orders[0])

        return orders
    except requests.HTTPError as http_err:
        logging.error(f"HTTP ошибка при получении заказов по таблицам: {http_err} - Ответ: {response.text}")
        print(f"HTTP ошибка при получении заказов по таблицам: {http_err} - Ответ: {response.text}")
    except Exception as err:
        logging.error(f"Произошла ошибка при получении заказов по таблицам: {err}")
        print(f"Произошла ошибка при получении заказов по таблицам: {err}")
    return None

# Функция для красивого вывода заказов в консоль
def display_orders(orders):
    if not orders:
        print("Нет заказов для отображения.")
        return

    print("\nСписок заказов:")
    for idx, order in enumerate(orders, 1):
        order_info = order.get('order', {})
        print(f"\nЗаказ {idx}:")
        print(f"  ID: {order.get('id', 'N/A')}")
        print(f"  Внешний номер: {order.get('externalNumber', 'N/A')}")
        print(f"  Организация ID: {order.get('organizationId', 'N/A')}")
        print(f"  Время создания: {order_info.get('whenCreated', 'N/A')}")
        print(f"  Статус: {order_info.get('status', 'N/A')}")
        customer = order_info.get('customer', {})
        print(f"  Имя заказчика: {customer.get('name', 'N/A')} {customer.get('surname', 'N/A')}")
        print(f"  Телефон: {order_info.get('phone', 'N/A')}")
        print(f"  Сумма заказа: {order_info.get('sum', 'N/A')}")
        print(f"  Таблицы: {', '.join(order_info.get('tableIds', []))}")
        print(f"  Номер стола: {order_info.get('tabName', 'N/A')}")
        print(f"  Комментарий: {customer.get('comment', 'N/A')}")
        # Добавь другие поля по необходимости

# Основная функция
def main():
    date_from = "2025-01-01 00:00:00.000"
    date_to = "2025-01-13 23:59:59.999"

    # Получение токена доступа
    token = get_access_token(API_LOGIN)
    if not token:
        print("Не удалось получить токен доступа.")
        return

    # Получение списка организаций
    organizations = get_organizations(token)
    if not organizations:
        print("Не удалось получить список организаций.")
        return

    # Вывод списка организаций
    print("\nСписок доступных организаций:")
    for idx, org in enumerate(organizations, 1):
        print(f"{idx}. {org.get('name')} (ID: {org.get('id')})")

    # Запрос выбора организаций
    selected_indices = input("\nВведите номера организаций, для которых нужно получить заказы (через запятую), или '0' для выбора всех: ")

    if selected_indices.strip() == '0':
        # Выбраны все организации
        organization_ids = [org.get('id') for org in organizations if 'id' in org]
    else:
        try:
            # Парсим введённые номера
            indices = [int(i.strip()) for i in selected_indices.split(',')]
            # Проверяем корректность номеров
            if any(i < 1 or i > len(organizations) for i in indices):
                print("Пожалуйста, введите корректные номера организаций.")
                return
            # Получаем выбранные organization_ids
            organization_ids = [organizations[i-1].get('id') for i in indices]
        except ValueError:
            print("Пожалуйста, введите номера организаций через запятую.")
            return

    # Проверка полученных идентификаторов организаций
    print(f"\nИдентификаторы выбранных организаций: {organization_ids}")

    # Получение терминальных групп для выбранных организаций
    terminal_groups = get_terminal_groups(token, organization_ids)
    if not terminal_groups:
        print("Не удалось получить терминальные группы.")
        return

    # Вывод доступных терминальных групп
    print("\nДоступные терминальные группы:")
    terminal_group_dict = {}  # Словарь для хранения терминальных групп по номерам
    for idx, group in enumerate(terminal_groups, 1):
        group_id = group.get('id')
        group_name = group.get('name')
        organization_id = group.get('organizationId')
        organization_name = next((org.get('name') for org in organizations if org.get('id') == organization_id), "Unknown")
        print(f"{idx}. {group_name} (ID: {group_id}) - Организация: {organization_name}")
        terminal_group_dict[idx] = group_id

    # Запрос выбора терминальных групп
    selected_group_indices = input("\nВведите номера терминальных групп, для которых нужно получить секции (через запятую), или '0' для выбора всех: ")

    if selected_group_indices.strip() == '0':
        # Выбраны все терминальные группы
        terminal_group_ids = list(terminal_group_dict.values())
    else:
        try:
            # Парсим введённые номера
            group_indices = [int(i.strip()) for i in selected_group_indices.split(',')]
            # Проверяем корректность номеров
            if any(i < 1 or i > len(terminal_group_dict) for i in group_indices):
                print("Пожалуйста, введите корректные номера терминальных групп.")
                return
            # Получаем выбранные terminal_group_ids
            terminal_group_ids = [terminal_group_dict[i] for i in group_indices]
        except ValueError:
            print("Пожалуйста, введите номера терминальных групп через запятую.")
            return

    print(f"\nИдентификаторы выбранных терминальных групп: {terminal_group_ids}")

    # Получение доступных секций ресторанов (таблиц)
    restaurant_sections = get_available_restaurant_sections(token, terminal_group_ids, return_schema=False, revision=0)
    if not restaurant_sections:
        print("Не удалось получить секции ресторанов.")
        return

    # Вывод доступных секций и таблиц
    print("\nДоступные секции ресторанов и таблицы:")
    table_dict = {}  # Словарь для хранения таблиц по номерам
    table_counter = 1
    for section in restaurant_sections:
        section_id = section.get('id')
        section_name = section.get('name')
        tables = section.get('tables', [])
        print(f"\nСекция: {section_name} (ID: {section_id})")
        for table in tables:
            table_id = table.get('id')
            table_number = table.get('number')
            table_name = table.get('name')
            print(f"  {table_counter}. Таблица {table_number}: {table_name} (ID: {table_id})")
            table_dict[table_counter] = table_id
            table_counter += 1

    # Запрос выбора таблиц
    selected_table_indices = input("\nВведите номера таблиц, для которых нужно получить заказы (например, 1,3,5), или '0' для выбора всех: ")

    if selected_table_indices.strip() == '0':
        # Выбраны все таблицы
        selected_table_ids = list(table_dict.values())
    else:
        try:
            # Парсим введённые номера
            table_indices = [int(i.strip()) for i in selected_table_indices.split(',')]
            # Проверяем корректность номеров
            if any(i < 1 or i > len(table_dict) for i in table_indices):
                print("Пожалуйста, введите корректные номера таблиц.")
                return
            # Получаем выбранные table_ids
            selected_table_ids = [table_dict[i] for i in table_indices]
        except ValueError:
            print("Пожалуйста, введите номера таблиц через запятую.")
            return

    print(f"\nИдентификаторы выбранных таблиц: {selected_table_ids}")

    # Получение заказов по таблицам
    orders = get_orders_by_table(token, organization_ids, selected_table_ids, date_from, date_to, statuses=["New", "Closed"])
    if not orders:
        print("Не найдено заказов или произошла ошибка при получении заказов.")
        return

    # Вывод заказов в консоль
    display_orders(orders)

if __name__ == "__main__":
    main()
