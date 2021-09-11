from classes.user_class import User
from env_var import API_KEY
import requests
import json
import datetime
from botrequests.get_destination_id import get_destination_id
from botrequests.get_photos import get_photo
from loguru import logger
from classes import user_class
from database.users_database import users
from bot_init import bot


def api_bestdeal(user: User) -> None:
    """
    Осуществляет запрос информации у API, применяет к полученным данным алгоритм сортировки по соотношению
    цена/удаленность от центра, заносит результаты в историю и отправляет их пользователю в чат
    :param user: Объект класса User, который вызвал команду /bestdeal
    :return: None
    """
    try:
        bot.send_message(user.USER_ID, 'Подождите, ищу...')
        url = "https://hotels4.p.rapidapi.com/properties/list"
        querystring = {
            "destinationId": get_destination_id(user.city, API_KEY), "pageNumber": "1", "pageSize": '50',
            "checkIn": datetime.datetime.today().strftime('%Y-%m-%d'),
            "checkOut": datetime.datetime.today().strftime('%Y-%m-%d'),
            "adults1": "1", "priceMin": '1', "priceMax": user.max_price,
            "sortOrder": "BEST_SELLER", "locale": "ru_RU", "currency": "RUB"
        }
        headers = {
            'x-rapidapi-host': "hotels4.p.rapidapi.com",
            'x-rapidapi-key': API_KEY
        }
        logger.info('Bestdeal request for user: {user_id} ended successfully'.format(user_id=user.USER_ID))

        user.data = json.loads(requests.request(
            "GET", url, headers=headers, params=querystring).text)['data']['body']['searchResults']['results']
        user.create_history()
        counter = 0
        for hotel in user.data:
            try:
                distance = hotel['landmarks'][0]['distance'].replace(' км', '')

                if counter < int(user.hotels_count) and float(distance.replace(',', '.')) <= float(user.max_distance):
                    counter += 1
                    user.search_result[counter] = {'text': '', 'image': ''}
                    user.search_result[counter]['text'] = 'Наименование: {}' \
                                                          '\nАдрес: {}' \
                                                          '\nРасстояние до центра: {}' \
                                                          '\nСтоимость: {}' \
                        .format(hotel['name'],
                                hotel['address']['streetAddress'],
                                hotel['landmarks'][0]['distance'],
                                hotel['ratePlan']['price']['current'])
                    if user.show_photos:
                        user.search_result[counter]['image'] = get_photo(hotel, API_KEY)
                    user.add_to_history(hotel['name'])
                    logger.info('{counter} hotel successfully added to user: {user_id} history'.
                                format(counter=counter, user_id=user.USER_ID))
                else:
                    logger.info('Search for user: {user_id} ended successfully'.format(user_id=user.USER_ID))
                    break
            except KeyError:
                logger.error('{counter} hotel has not full info. Skipped'.format(counter=counter + 1))
                continue
        for i_result in user.search_result:
            if user.show_photos:
                bot.send_photo(user.USER_ID, user.search_result[i_result]['image'],
                               caption=user.search_result[i_result]['text'])
            else:
                bot.send_message(user.USER_ID, user.search_result[i_result]['text'])
    except Exception as ex:
        logger.error(f'Raised exception {ex}')
