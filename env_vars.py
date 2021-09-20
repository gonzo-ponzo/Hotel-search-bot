import os
from my_vars import MY_TOKEN, MY_API_KEY

os.environ['TOKEN'] = MY_TOKEN
os.environ['API_KEY'] = MY_API_KEY
TOKEN = os.getenv('TOKEN')  # Здесь должен быть ваш токен
API_KEY = os.getenv('API_KEY')  # Здесь должен быть ваш ключ API
