import requests
import json
from loguru import logger


def get_destination_id(destination: str, api_key: str) -> str:
    """
    Функция get_destination_id. Возвращает уникальный номер искомой локации, под которым она находится в API Hotels
    :param api_key: Ключ для использования API
    :param destination: Наименование искомой локации
    :return: Уникальный номер искомой локации
    """
    try:
        url = "https://hotels4.p.rapidapi.com/locations/search"

        querystring = {"query": destination, "locale": "ru_RU"}

        headers = {
            'x-rapidapi-host': "hotels4.p.rapidapi.com",
            'x-rapidapi-key': api_key
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        data = json.loads(response.text)
        logger.info('Hotel id for hotel: {hotel_name} found successfully'.format(hotel_name=destination))

        return data['suggestions'][0]['entities'][0]['destinationId']
    except Exception as ex:
        logger.error(f'Raised exception {ex}')
