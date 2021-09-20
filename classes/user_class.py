from database.users_database import users
import datetime
from loguru import logger


class User:
    """
    Класс пользователя. Хранит в себе неизменные параметры пользователя, такие как уникальный номер, имя и фамилию.
    Также устанавливает параметры для осуществления поиска
    """

    def __init__(self, user_id: str, first_name: str, second_name: str):
        self.USER_ID = user_id
        self.FIRST_NAME = first_name
        self.SECOND_NAME = second_name
        self.history = dict()
        self.search_counter = 0
        self.operation = None
        self.city = None
        self.hotels_count = None
        self.show_photos = None
        self.max_price = None
        self.max_distance = None
        self.data = None
        self.search_result = dict()

    def add_to_base(self, user_id: str, first_name: str, second_name: str) -> None:
        """
        Добавляет пользователя в общую базу
        :param user_id: Уникальный идентификатор пользователя
        :param first_name: Имя
        :param second_name: Фамилия
        :return: None
        """
        try:
            if user_id not in users:
                logger.info('Added new user to base: {first_name} {second_name} user id: {user_id}'.format(
                    first_name=first_name,
                    second_name=second_name,
                    user_id=user_id
                ))
                users[user_id] = User(user_id, first_name, second_name)
        except Exception as ex:
            logger.error(f'Raised exception {ex}')

    def create_history(self, ) -> None:
        """
        Создает пустую историю поиска
        :return: None
        """
        try:
            logger.info('Created history for user: {user_id}'.format(user_id=self.USER_ID))
            self.search_counter += 1
            self.history[self.search_counter] = {
                'Команда': self.operation,
                'Время': datetime.datetime.today().strftime('%d.%m.%Y %X'),
                'Отели': []
            }
        except Exception as ex:
            logger.error(f'Raised exception {ex}')

    def add_to_history(self, hotel_name: str) -> None:
        """
        Добавляет отель в историю поиска
        :param hotel_name: Название отеля
        :return: None
        """
        try:
            logger.info('Hotel: {hotel_name} added to user {user_id} history'.format(
                user_id=self.USER_ID,
                hotel_name=hotel_name
            ))
            self.history[self.search_counter]['Отели'].append(hotel_name)
        except Exception as ex:
            logger.error(f'Raised exception {ex}')
