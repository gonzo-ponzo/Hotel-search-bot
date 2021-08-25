import telebot
import requests
import json
import datetime
import time

bot = telebot.TeleBot('1960878945:AAEKrmE35Yi956aOdIN7OeE9Iixj3MLLJ8Q')
history = dict()
counter = 0




def get_destination_id(destination: str) -> str:
    """
    Функция get_destination_id. Возвращает уникальный номер искомой локации, под которым она находится в API Hotels
    :param destination: (str) Наименование искомой локации
    :return: (str) Уникальный номер искомой локации
    """
    url = "https://hotels4.p.rapidapi.com/locations/search"

    querystring = {"query": destination, "locale": "ru_RU"}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': "4213f44ecbmsh474379ffdaecd3ap1b4c3ajsncc60a40a7fb1"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    data = json.loads(response.text)
    return data['suggestions'][0]['entities'][0]['destinationId']  # latitude/longitude


@bot.message_handler(commands=['start', 'hello-world'])
def send_start(message: str) -> None:
    """
    Функция-приветствие. Выводит приветственное сообщение пользователю, дает подсказку на использование команды /help
    :param message: (str) Принимает в качестве аргумента последнее отправленное пользователем сообщение
    :return: None
    """
    bot.send_message(message.from_user.id, 'Привет! Я бот для поиска лучших вариантов отелей.\nДля ознакомления с '
                                           'моими возможностями введи /help')


@bot.message_handler(commands=['help'])
def send_help(message: str) -> None:
    """
    Функция-помощник. Оказывает помощь с навигацией по командам бота
    :param message: (str) Принимает в качестве аргумента последнее отправленное пользователем сообщение
    :return: None
    """
    bot.send_message(message.from_user.id, '/lowprice — вывод самых дешёвых отелей в городе.')
    bot.send_message(message.from_user.id, '/highprice — вывод самых дорогих отелей в городе.')
    bot.send_message(message.from_user.id, '/bestdeal — вывод отелей, наиболее подходящих по цене и расположению от '
                                           'центра.')
    bot.send_message(message.from_user.id, '/history — вывод истории поиска отелей.')


@bot.message_handler(commands=['lowprice'])
def send_lowprice(message: str) -> None:
    """
    Функция send_lowprice. Выводит топ самых дешёвых отелей в городе.
    :param message: (str) Принимает в качестве аргумента последнее отправленное пользователем сообщение
    :return: None
    """

    bot.send_message(message.from_user.id, 'По какому городу осуществляем поиск?')
    bot.register_next_step_handler(message, get_low_city)

    # @bot.message_handler(content_types=['text'])


def get_low_city(message: str) -> None:
    """
    Функция get_city. Выявляет город, по которому будет осуществлен поиск
    :param message: (str) Принимает в качестве аргумента последнее отправленное пользователем сообщение
    :return: None
    """

    global low_city
    low_city = message.text
    bot.send_message(message.from_user.id, 'Какое кол-во отелей показать?')
    bot.register_next_step_handler(message, get_low_hotels_count)

    # @bot.message_handler(content_types=['text'])


def get_low_hotels_count(message: str) -> None:
    """
    Функция get_hotels_count. Выявляет кол-во отелей, необходимое к показу. Создает клавиатуру мессенджера.
    :param message: (str) Принимает в качестве аргумента последнее отправленное пользователем сообщение
    :return: None
    """

    global low_hotels_count
    low_hotels_count = message.text
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_yes = telebot.types.InlineKeyboardButton(text='Да', callback_data='low_yes')
    keyboard.add(key_yes)
    key_no = telebot.types.InlineKeyboardButton(text='Нет', callback_data='low_no')
    keyboard.add(key_no)
    bot.send_message(message.from_user.id, 'Показывать фотографии отелей?', reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data == 'low_yes' or call.data == 'low_no')
    def callback_worker(call):
        """
        Функция callback_worker. Передает в переменную тип данных bool, в зависимости от нажатой кнопки.
        :param call: (bool) Принимает одно из двух значений, в зависимости от нажатой на клавиатуре
        мессенджера кнопки
        :return: None
        """

        global low_hotels_count, low_city, history, counter
        counter += 1

        url = "https://hotels4.p.rapidapi.com/properties/list"
        low_querystring = {
            "destinationId": get_destination_id(low_city), "pageNumber": "1", "pageSize": '50',
            "checkIn": datetime.datetime.today().strftime('%Y-%m-%d'),
            "checkOut": datetime.datetime.today().strftime('%Y-%m-%d'),
            "adults1": "1", "sortOrder": "PRICE", "locale": "ru_RU", "currency": "RUB"
        }
        headers = {
            'x-rapidapi-host': "hotels4.p.rapidapi.com",
            'x-rapidapi-key': "4213f44ecbmsh474379ffdaecd3ap1b4c3ajsncc60a40a7fb1"
        }
        response = requests.request("GET", url, headers=headers, params=low_querystring)
        low_data = json.loads(response.text)
        results = low_data['data']['body']['searchResults']['results']

        history[counter] = {
            'Команда': '/lowprice',
            'Время': datetime.datetime.today().strftime('%d.%m.%Y %X'),
            'Отели': []
        }
        limit = int(low_hotels_count)
        for hotel in results:
            try:
                if limit > 0:
                    bot.send_message(message.from_user.id,
                                     'Наименование: {}\nАдрес: {}\nРасстояние до центра; {}\nСтоимость: {}'
                                     .format(hotel['name'],
                                             hotel['address']['streetAddress'],
                                             hotel['landmarks'][0]['distance'],
                                             hotel['ratePlan']['price']['current']))
                    history[counter]['Отели'].append(hotel['name'])
                    limit -= 1
                    if call.data == "low_yes":
                        photos_url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
                        photos_querystring = {"id": hotel['id']}
                        headers = {
                            'x-rapidapi-host': "hotels4.p.rapidapi.com",
                            'x-rapidapi-key': "4213f44ecbmsh474379ffdaecd3ap1b4c3ajsncc60a40a7fb1"
                        }

                        photos_response = requests.request("GET", photos_url, headers=headers, params=photos_querystring)
                        photos_data = json.loads(photos_response.text)
                        bot.send_photo(message.from_user.id, photos_data['hotelImages'][0]['baseUrl']
                                       .replace('{size}', 'z'))
                        bot.send_photo(message.from_user.id, photos_data['roomImages'][0]['images'][0]['baseUrl']
                                       .replace('{size}', 'z'))
                else:
                    break
            except KeyError:
                continue
        bot.send_message(message.from_user.id, 'Поиск окончен.')


@bot.message_handler(commands=['highprice'])
def send_highprice(message: str) -> None:
    """
    Функция send_highprice. Выводит топ самых дорогих отелей в городе.
    :param message: (str) Принимает в качестве аргумента последнее отправленное пользователем сообщение
    :return: None
    """

    bot.send_message(message.from_user.id, 'По какому городу осуществляем поиск?')
    bot.register_next_step_handler(message, get_high_city)

    # @bot.message_handler(content_types=['text'])


def get_high_city(message: str) -> None:
    """
    Функция get_city. Выявляет город, по которому будет осуществлен поиск
    :param message: (str) Принимает в качестве аргумента последнее отправленное пользователем сообщение
    :return: None
    """

    global high_city
    high_city = message.text
    bot.send_message(message.from_user.id, 'Какое кол-во отелей показать?')
    bot.register_next_step_handler(message, get_high_hotels_count)

    # @bot.message_handler(content_types=['text'])


def get_high_hotels_count(message: str) -> None:
    """
    Функция get_hotels_count. Выявляет кол-во отелей, необходимое к показу. Создает клавиатуру мессенджера.
    :param message: (str) Принимает в качестве аргумента последнее отправленное пользователем сообщение
    :return: None
    """

    global high_hotels_count
    high_hotels_count = message.text
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_yes = telebot.types.InlineKeyboardButton(text='Да', callback_data='high_yes')
    keyboard.add(key_yes)
    key_no = telebot.types.InlineKeyboardButton(text='Нет', callback_data='high_no')
    keyboard.add(key_no)
    bot.send_message(message.from_user.id, 'Показывать фотографии отелей?', reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data == 'high_yes' or call.data == 'high_no')
    def callback_worker(call):
        """
        Функция callback_worker. Передает в переменную тип данных bool, в зависимости от нажатой кнопки.
        :param call: (bool) Принимает одно из двух значений, в зависимости от нажатой на клавиатуре
                            мессенджера кнопки
        :return: None
        """

        global high_hotels_count, high_city, history, counter
        counter += 1

        url = "https://hotels4.p.rapidapi.com/properties/list"
        high_querystring = {
            "destinationId": get_destination_id(high_city), "pageNumber": "1", "pageSize": '50',
            "checkIn": datetime.datetime.today().strftime('%Y-%m-%d'),
            "checkOut": datetime.datetime.today().strftime('%Y-%m-%d'),
            "adults1": "1", "sortOrder": "PRICE_HIGHEST_FIRST", "locale": "ru_RU", "currency": "RUB"
        }
        headers = {
            'x-rapidapi-host': "hotels4.p.rapidapi.com",
            'x-rapidapi-key': "4213f44ecbmsh474379ffdaecd3ap1b4c3ajsncc60a40a7fb1"
        }
        high_response = requests.request("GET", url, headers=headers, params=high_querystring)
        high_data = json.loads(high_response.text)
        results = high_data['data']['body']['searchResults']['results']

        history[counter] = {
            'Команда': '/highprice',
            'Время': datetime.datetime.today().strftime('%d.%m.%Y %X'),
            'Отели': []
        }
        limit = int(high_hotels_count)
        for hotel in results:
            try:
                if limit > 0:
                    bot.send_message(message.from_user.id,
                                     'Наименование: {}\nАдрес: {}\nРасстояние до центра; {}\nСтоимость: {}'
                                     .format(hotel['name'],
                                             hotel['address']['streetAddress'],
                                             hotel['landmarks'][0]['distance'],
                                             hotel['ratePlan']['price']['current']))
                    history[counter]['Отели'].append(hotel['name'])
                    limit -= 1
                    if call.data == "high_yes":
                        photos_url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
                        photo_querystring = {"id": hotel['id']}
                        headers = {
                            'x-rapidapi-host': "hotels4.p.rapidapi.com",
                            'x-rapidapi-key': "4213f44ecbmsh474379ffdaecd3ap1b4c3ajsncc60a40a7fb1"
                        }

                        photos_response = requests.request("GET", photos_url, headers=headers, params=photo_querystring)
                        photos_data = json.loads(photos_response.text)
                        bot.send_photo(message.from_user.id, photos_data['hotelImages'][0]['baseUrl']
                                       .replace('{size}', 'z'))
                        bot.send_photo(message.from_user.id, photos_data['roomImages'][0]['images'][0]['baseUrl']
                                       .replace('{size}', 'z'))
                else:
                    break
            except KeyError:
                continue
        bot.send_message(message.from_user.id, 'Поиск окончен.')


@bot.message_handler(commands=['bestdeal'])
def send_bestdeal(message: str) -> None:
    '''
    Функция send_bestdeal. Выводит топ отелей по соотношению цена/удаленность от центра.
    :param message: (str) Принимает в качестве аргумента последнее отправленное пользователем сообщение
    :return: None
    '''
    bot.send_message(message.from_user.id, 'По какому городу осуществляем поиск?')
    bot.register_next_step_handler(message, get_best_city)


def get_best_city(message: str) -> None:
    '''
    Функция get_city. Выявляет город, по которому будет осуществлен поиск
    :param message: (str) Принимает в качестве аргумента последнее отправленное пользователем сообщение
    :return: None
    '''
    global best_city
    best_city = message.text
    bot.send_message(message.from_user.id, 'Какая максимальная стоимость?')
    bot.register_next_step_handler(message, get_price_limit)


def get_price_limit(message: str) -> None:
    '''
    Функция get_price_limit. Запрашивает у пользователя максимальную стоимость отеля.
    :param message: (str) Принимает в качестве аргумента последнее отправленное пользователем сообщение
    :return: None
    '''
    global price_limit
    price_limit = message.text
    bot.send_message(message.from_user.id, 'Какое максимальное расстояние от центра в км?')
    bot.register_next_step_handler(message, get_dist_limit)


def get_dist_limit(message: str) -> None:
    '''
    Функция get_price_limit. Запрашивает у пользователя максимальную удаленность отеля от центра. Создает
    клавиатуру мессенджера.
    :param message: (str) Принимает в качестве аргумента последнее отправленное пользователем сообщение
    :return: None
    '''
    global dist_limit
    dist_limit = message.text
    bot.send_message(message.from_user.id, 'Какое кол-во отелей показать?')
    bot.register_next_step_handler(message, get_best_hotels_count)


def get_best_hotels_count(message: str) -> None:
    """
    Функция get_hotels_count. Выявляет кол-во отелей, необходимое к показу. Создает клавиатуру мессенджера.
    :param message: (str) Принимает в качестве аргумента последнее отправленное пользователем сообщение
    :return: None
    """

    global best_hotels_count
    best_hotels_count = message.text
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_yes = telebot.types.InlineKeyboardButton(text='Да', callback_data='best_yes')
    keyboard.add(key_yes)
    key_no = telebot.types.InlineKeyboardButton(text='Нет', callback_data='best_no')
    keyboard.add(key_no)
    bot.send_message(message.from_user.id, 'Показывать фотографии отелей?', reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data == 'best_yes' or call.data == 'best_no')
    def callback_worker(call):
        """
        Функция callback_worker. Передает в переменную тип данных bool, в зависимости от нажатой кнопки.
        :param call: (bool) Принимает одно из двух значений, в зависимости от нажатой на клавиатуре
                            мессенджера кнопки
        :return: None
        """

        global best_hotels_count, best_city, dist_limit, price_limit, history, counter
        counter += 1

        url = "https://hotels4.p.rapidapi.com/properties/list"
        best_querystring = {
            "destinationId": get_destination_id(best_city), "pageNumber": "1",
            "pageSize": '50',
            "checkIn": datetime.datetime.today().strftime('%Y-%m-%d'),
            "checkOut": datetime.datetime.today().strftime('%Y-%m-%d'),
            "adults1": "1", "priceMin": '1', "priceMax": price_limit, "sortOrder": "BEST_SELLER",
            "locale": "ru_RU", "currency": "RUB"
        }
        headers = {
            'x-rapidapi-host': "hotels4.p.rapidapi.com",
            'x-rapidapi-key': "4213f44ecbmsh474379ffdaecd3ap1b4c3ajsncc60a40a7fb1"
        }
        best_response = requests.request("GET", url, headers=headers, params=best_querystring)
        best_data = json.loads(best_response.text)
        results = best_data['data']['body']['searchResults']['results']

        history[counter] = {
            'Команда': '/bestdeal',
            'Время': datetime.datetime.today().strftime('%d.%m.%Y %X'),
            'Отели': []
        }
        limit = int(best_hotels_count)
        for hotel in results:
            try:

                distance = hotel['landmarks'][0]['distance'].replace(' км', '')
                if float(distance.replace(',', '.')) <= float(dist_limit) and limit > 0:
                    bot.send_message(message.from_user.id,
                                     'Наименование: {}\nАдрес: {}\nРасстояние до центра; {}\nСтоимость: {}'
                                     .format(hotel['name'],
                                             hotel['address']['streetAddress'],
                                             hotel['landmarks'][0]['distance'],
                                             hotel['ratePlan']['price']['current']))
                    history[counter]['Отели'].append(hotel['name'])
                    limit -= 1
                    if call.data == "best_yes":
                        photos_url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
                        photo_querystring = {"id": hotel['id']}
                        headers = {
                            'x-rapidapi-host': "hotels4.p.rapidapi.com",
                            'x-rapidapi-key': "4213f44ecbmsh474379ffdaecd3ap1b4c3ajsncc60a40a7fb1"
                        }

                        photos_response = requests.request("GET", photos_url, headers=headers, params=photo_querystring)
                        photos_data = json.loads(photos_response.text)
                        bot.send_photo(message.from_user.id, photos_data['hotelImages'][0]['baseUrl']
                                       .replace('{size}', 'z'))
                        bot.send_photo(message.from_user.id, photos_data['roomImages'][0]['images'][0]['baseUrl']
                                       .replace('{size}', 'z'))
                else:
                    break
            except KeyError:
                continue
        bot.send_message(message.from_user.id, 'Поиск окончен.')


@bot.message_handler(commands=['history'])
def send_history(message: str) -> None:
    '''
    Функция history. Выводит пользователю историю его запросов.
    :param message: (str) Принимает в качестве аргумента последнее отправленное пользователем сообщение
    :return: None
    '''
    global history
    for i_search in history:
        history_result = '''
        Команда: {command}
        Время: {time}
        Отели: {hotels}
        '''.format(command=history[i_search]['Команда'],
                   time=history[i_search]['Время'],
                   hotels=', '.join(history[i_search]['Отели']))
        bot.send_message(message.from_user.id, history_result)

while True:
    try:
        bot.polling(none_stop=True, interval=0)
    except:
        time.sleep(10)
