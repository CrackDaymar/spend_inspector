import pymongo
import datetime
import calendar

host = 'localhost'
port = 27017
client = pymongo.MongoClient(host, port)
# Выберите базу данных
db = client['Money']
collections_categories = db['categories']
collections_white_list = db['white list']
collections_spending = db['spending']


def add_categories(categories):
    if check_category(categories) is True:
        add_contant = {
            'categories': categories
        }

        collections_categories.insert_one(add_contant)
        return 'Додано нову категорію'
    else:
        return 'Ця категорія вже є'


def get_all_categories():
    all_categories = collections_categories.find()
    list = []
    for cat in all_categories:
        list.append(cat['categories'])

    return list


def add_spending(categories, money, date, id_telegram):
    add_contain = {
        'categories': categories,
        'money spending': money,
        'date spending': date,
        'who spending': id_telegram
    }

    collections_spending.insert_one(add_contain)


def add_user(name, id_telegram, telegram_link):
    if check_users(id_telegram) is True:
        add_user = {
            'name': name,
            'id telegram': id_telegram,
            'link user': telegram_link
        }

        collections_white_list.insert_one(add_user)
        return 'Додано нового користувача'
    else:
        return 'Цей користувач вже доданий'


def find_user(id_telegram):
    query = {'id telegram': id_telegram}
    data = collections_white_list.find(query)
    for name in data:
        return name['name']


def check_users(id_telegam):
    all_id = collections_white_list.find()
    read = True
    for id in all_id:
        if id_telegam == id['id telegram']:
            read = False

    return read


def check_category(category):
    all_cat = collections_categories.find()
    read = True
    for categ in all_cat:
        if category == categ['categories']:
            read = False

    return read


def find_month_data(find_query):
    month_expenses = collections_spending.find(find_query)
    return month_expenses


def update_categories_spending():
    collections_categories.update_many({}, {'$set': {'summary': 0}})


def update_spending():
    collections_spending.update_many({}, {'$set': {'add summary categories': False}})


def month_data(start_of_time):
    find_query = {"date spending": {"$gte": start_of_time}}

    month_data = find_month_data(find_query)

    categories = get_all_categories()

    for sells in month_data:


        sum+=int(sells['money spending'])
        list.append(sells['money spending'])
    print(list)
    return sum


def get_category_summary_spending_in_this_month():
    # Установите начальную и конечную дату
    current_date = datetime.datetime.now()  # Начальная дата
    start_date = current_date.replace(day=1, hour=0)
    pipeline = [
        {
            "$match": {
                "date spending": {"$gte": start_date}
            }
        },
        {
            "$lookup": {
                "from": "categories",  # Имя коллекции, с которой нужно объединить данные
                "localField": "categories",  # Поле из коллекции "spending", по которому будет объединение
                "foreignField": "categories",  # Поле из коллекции "categories", по которому будет объединение
                "as": "category_data"  # Название нового поля, в котором будет храниться объединенная информация
            }
        },
        {
            "$unwind": "$category_data"  # Развернуть объединенный список
        },
        {
            "$group": {
                "_id": "$category_data.categories",  # Группировка по категориям
                "total_amount": {"$sum": "$money spending"},  # Сумма затрат для каждой категории
                "summary": {"$first": "$category_data.summary"}  # Значение "summary" из коллекции "categories"
            }
        }
    ]

        # Получите результаты агрегации
    results = collections_spending.aggregate(pipeline)
    list = []
    # Выведите результаты
    for result in results:
        category = result["_id"]
        total_amount = result["total_amount"]
        summary = result["summary"]
        list.append(f"Категория: {category}, Сумма затрат: {total_amount} грн")
    return list


def get_users_summary_spending_in_this_month():
    # Установите начальную и конечную дату
    current_date = datetime.datetime.now()  # Начальная дата
    start_date = current_date.replace(day=1, hour=0)
    pipeline = [
        {
            "$match": {
                "date spending": {"$gte": start_date}
            }
        },
        {
            "$lookup": {
                "from": "white list",  # Имя коллекции, с которой нужно объединить данные
                "localField": "who spending",  # Поле из коллекции "spending", по которому будет объединение
                "foreignField": "id telegram",  # Поле из коллекции "categories", по которому будет объединение
                "as": "user_data"  # Название нового поля, в котором будет храниться объединенная информация
            }
        },
        {
            "$unwind": "$user_data"  # Развернуть объединенный список
        },
        {
            "$group": {
                "_id": "$user_data.name",  # Группировка по категориям
                "total_amount": {"$sum": "$money spending"},  # Сумма затрат для каждой категории
                "summary": {"$first": "$category_data.summary"}  # Значение "summary" из коллекции "categories"
            }
        }
    ]

        # Получите результаты агрегации
    results = collections_spending.aggregate(pipeline)

    # Выведите результаты
    for result in results:
        user_name = result["_id"]
        total_amount = result["total_amount"]
        summary = result["summary"]
        print(f"{user_name} - сума затрат за місяць: {total_amount} грн")


def get_users_category_summary_in_this_month():
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month
    list = {}
    return_list = {}
    for num_day in range(1, day_in_current_month()+1):
        list = []
        day_start_info = datetime.datetime(current_year, current_month, num_day, 0, 0, 0)
        day_end_info = datetime.datetime(current_year, current_month, num_day, 23, 59, 59)
        result = {
            "date spending": {
                "$gte": day_start_info,
                "$lte": day_end_info
            }
        }
        day = collections_spending.find(result)
        for d in day:
            list.append(f'Оплатил - {find_user(d["who spending"])} категория - {d["categories"]} оплата - {d["money spending"]}')
        if list != []:
            return_list.update({str(num_day): list})
    return return_list


def day_in_current_month():
    current_date = datetime.datetime.now()
    current_month = current_date.month
    current_year = current_date.year
    _, num_days = calendar.monthrange(current_year, current_month)

    return num_days


def delete():
    criteria = {}
    query = {"$unset": {"summary": ""}}
    collections_categories.update_many(criteria, query)


