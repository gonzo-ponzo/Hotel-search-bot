import telebot
from telebot.types import Message
from database.users_database import users
from classes.user_class import User
from botrequests import lowprice, highprice, bestdeal
from loguru import logger
import time
from bot_init import bot
from loguru import logger


logger.add('debug.log', format='{time} {level} {message}', level='DEBUG', rotation='10 MB', compression='zip')



@bot.message_handler(commands=['start', 'hello-world'])
def send_start(message: Message) -> None:
    logger.info('Start bot by user_id: {user_id}'.format(user_id=message.from_user.id))
    """
    Функция-приветствие. Выводит приветственное сообщение пользователю, дает подсказку на использование команды /help
    :param message: (str) Принимает в качестве аргумента последнее отправленное пользователем сообщение
    :return: None
    """
    bot.send_message(message.from_user.id, '/lowprice — вывод самых дешёвых отелей в городе.')
    user = User(message.from_user.id, message.from_user.first_name, message.from_user.last_name)
    user.add_to_base(user.USER_ID, user.FIRST_NAME, user.SECOND_NAME)
    bot.send_message(message.from_user.id, 'Привет, {first_name}! Я бот для поиска лучших вариантов отелей.'
                                           '\nДля ознакомления с моими возможностями введи /help'.format(
        first_name=users[message.from_user.id].FIRST_NAME))


@bot.message_handler(commands=['help'])
def send_help(message: Message) -> None:
    logger.info('Send help command by user: {user_id}'.format(user_id=message.from_user.id))
    """
    Функция-помощник. Оказывает помощь с навигацией по командам бота
    :param message: (str) Принимает в качестве аргумента последнее отправленное пользователем сообщение
    :return: None
    """

    bot.send_message(message.from_user.id, '''
    /lowprice — вывод самых дешёвых отелей в городе.
    \n/highprice — вывод самых дорогих отелей в городе.
    \n/bestdeal — вывод отелей, наиболее подходящих по цене и расположению от центра.
    \n/history — вывод истории поиска отелей.
    ''')


@bot.message_handler(commands=['lowprice', 'highprice', 'bestedal'])
def search(message: Message) -> None:
    logger.info('Send {command} by user id: {user_id}'.format(user_id=message.from_user.id, command=message.text))
    users[message.from_user.id].operation = message.text
    bot.send_message(message.from_user.id, 'По какому городу будем искать?')
    bot.register_next_step_handler(message, get_city)


def get_city(message: Message) -> None:
    logger.info('Get city: {city} by user: {user_id}'.format(user_id=message.from_user.id, city=message.text))
    users[message.from_user.id].city = message.text
    bot.send_message(message.from_user.id, 'Сколько отелей показать?')
    bot.register_next_step_handler(message, get_count)


def get_count(message: Message) -> None:
    logger.info('Get hotels count: {hotels_count} by user: {user_id}'.format(user_id=message.from_user.id,
                                                                             hotels_count=message.text))
    users[message.from_user.id].hotels_count = message.text
    next_step = users[message.from_user.id].operation
    if next_step == 'bestdeal':
        bot.send_message(message.from_user.id, 'Какая максимальная стоимость отеля?')
        bot.register_next_step_handler(message, get_max_price)
    else:
        keyboard = telebot.types.InlineKeyboardMarkup()
        key_yes = telebot.types.InlineKeyboardButton(text='Да', callback_data='yes')
        keyboard.add(key_yes)
        key_no = telebot.types.InlineKeyboardButton(text='Нет', callback_data='no')
        keyboard.add(key_no)
        bot.send_message(message.from_user.id, 'Показывать фотографии отелей?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'yes' or call.data == 'no')
def callback_worker(call):
    logger.info('Get answer: {answer} by user: {user_id}'.format(user_id=call.from_user.id, answer=call.data))
    if call.data == 'yes':
        users[call.from_user.id].show_photos = True
    else:
        users[call.from_user.id].show_photos = False
    next_step = users[call.from_user.id].operation
    if next_step == '/lowprice':
        lowprice.api_lowprice(users[call.from_user.id])
    elif next_step == '/highprice':
        highprice.api_highprice(users[call.from_user.id])
    else:
        bestdeal.api_bestdeal(users[call.from_user.id])


def get_max_price(message: Message) -> None:
    logger.info('Get cost: {cost} by user: {user_id}'.format(user_id=message.from_user.id, cost=message.text))
    users[message.from_user.id].max_price = message.text
    bot.send_message(message.from_user.id, 'Какая максимальная удаленность отеля?')
    bot.register_next_step_handler(message, get_max_distance)


def get_max_distance(message: Message) -> None:
    logger.info(
        'Get distance: {distance} by user: {user_id}'.format(user_id=message.from_user.id, distance=message.text))
    users[message.from_user.id].max_distance = message.text
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_yes = telebot.types.InlineKeyboardButton(text='Да', callback_data='yes')
    keyboard.add(key_yes)
    key_no = telebot.types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    bot.send_message(message.from_user.id, 'Показывать фотографии отелей?', reply_markup=keyboard)


@bot.message_handler(commands=['history'])
def send_history(message: str) -> None:
    logger.info('Send history to user: {user_id}'.format(user_id=message.from_user.id))

    '''
    Функция history. Выводит пользователю историю его запросов.
    :param message: (str) Принимает в качестве аргумента последнее отправленное пользователем сообщение
    :return: None
    '''
    history = users[message.from_user.id].history
    for i_search in history:
        history_result = '''
        Команда: {command}
        Время: {time}
        Отели: {hotels}
        '''.format(command=history[i_search]['Команда'],
                   time=history[i_search]['Время'],
                   hotels=', '.join(history[i_search]['Отели']))
        bot.send_message(message.from_user.id, history_result)


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
            # bot.infinity_polling()
        except Exception as ex:
            logger.error(f'Raised exception {ex}')
            time.sleep(10)
