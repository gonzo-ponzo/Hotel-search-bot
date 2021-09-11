import requests
import json
from loguru import logger


def get_photo(hotel: dict, api_key: str) -> str:
    """
    Функция get_photo. Возвращает фотографию переданного в функцию отеля
    :param hotel: Уникальный номер отеля, под которым он находится в rapidapi
    :param api_key: Ключ для использования API
    :return: Возвращает ссылку на фотографию отеля в виде строки
    """
    try:
        url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
        querystring = {"id": hotel['id']}
        headers = {
            'x-rapidapi-host': "hotels4.p.rapidapi.com",
            'x-rapidapi-key': api_key
        }

        photos_data = json.loads(requests.request("GET", url, headers=headers, params=querystring).text)
        photo = photos_data['hotelImages'][0]['baseUrl'].replace('{size}', 'b')
        logger.info('Photos request for hotel: {hotel} ended successfully'.format(hotel=hotel['name']))
        return photo
    except Exception as ex:
        logger.error(f'Raised exception {ex}')

