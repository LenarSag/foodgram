![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)  ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)  ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)  ![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)  ![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white)  ![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)  ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)


# Проект FoodGram позволяет пользователю делиться своими рецептами, а также и просматривать и сохранять к себе рецепты других пользователей. 

## Деплой проекта foodgram в **Docker контейнерах** и CI/CD с помощью GitHub Actions на удалённый сервер 

### Описание проекта

Проект Foodgram - социальная сеть для обмена рецептами любимых блюд.

Это полностью рабочий проект, который состоит из бэкенд-приложения на **Django** и фронтенд-приложения на **React**. 

### Возможности проекта: 

Можно зарегистрироваться и авторизоваться, добавить нового котика на сайт или изменить существующего, добавить или изменить достижения, а также просмотреть записи других пользователей.

API для kittygram написан с использованием библиотеки **Django REST Framework**, используется **TokenAuthentication** для аутентификации, а также подключена библиотека **Djoser**.

Проект размещён в нескольких **Docker** контейнерах. В контейнере бэкенда настроен **WSGI-сервер Gunicorn**.
Автоматизация тестирования и деплоя проекта Foddgram осуществлена с помощью **GitHub Actions**.


### Настройка CI/CD

Деплой проекта на удалённый сервер настроен через CI/CD с помощью GitHub Actions, для этого создан workflow, в котором:

* проверяется код бэкенда в репозитории на соответствие PEP8;
* настроено автоматическое тестирование фронтенда и бэкенда;
* в случае успешного прохождения тестов образы должны обновляться на Docker Hub;
* обновляются образы на сервере и перезапускается приложение при помощи Docker Compose;
* выполняются команды для сборки статики в приложении бэкенда, переноса статики в volume; выполняются миграции;
* происходит уведомление в Telegram об успешном завершении деплоя.

Пример данного workflow сохранен в файле foodgram_workflow.yml в корневой директории проекта, при необходимости запуска перепишите содержимое файла в .github/workflows/main.yml.

Сохраните следующие переменные с необходимыми значениями в секретах GitHub Actions:

```
DOCKER_USERNAME - логин в Docker Hub
DOCKER_PASSWORD - пароль для Docker Hub
SSH_KEY - закрытый SSH-ключ для доступа к продакшен-серверу
SSH_PASSPHRASE - passphrase для этого ключа
USER - username для доступа к продакшен-серверу
HOST - адрес хоста для доступа к продакшен-серверу
TELEGRAM_TO - ID своего телеграм-аккаунта
TELEGRAM_TOKEN - токен Telegram-бота
```

Файл docker-compose.yml для локального запуска проекта и файл docker-compose.production.yml для запуска проекта на облачном сервере находятся в корневой директории проекта.


### Технологии

- Python 3.9
- Django 3.2
- Django REST framework 3.12
- Nginx
- Docker
- Postgres


### Запуск проекта в dev-режиме

Клонировать репозиторий и перейти в него в командной строке: 
```
git clone git@github.com:LenarSag/foodgram.git
```
Cоздать и активировать виртуальное окружение: 
```
python3.9 -m venv venv 
```
* Если у вас Linux/macOS 

    ```
    source venv/bin/activate
    ```
* Если у вас windows 
 
    ```
    source venv/scripts/activate
    ```
```
python3.9 -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
Задайте учётные данные БД в .env файле, используя .env.example:
```
POSTGRES_USER=логин
POSTGRES_PASSWORD=пароль
POSTGRES_DB=название БД
DB_HOST=название хоста
DB_PORT=5432
SECRET_KEY=django_settings_secret_key
ALLOWED_HOSTS=127.0.0.1, localhost
```

**Запустить Docker Compose с дефолтной конфигурацией (docker-compose.yml):**

* Выполнить сборку контейнеров: *sudo docker compose up -d --build*

* Применить миграции: *sudo docker compose exec backend python manage.py migrate*

* Создать суперпользователя: *sudo docker compose exec backend python manage.py createsuperuser*

* Добавить ингредиенты и теги:

sudo docker exec -it foodgram-app python manage.py loaddata data/ingredients_for_db.json


* Собрать файлы статики: *sudo docker compose exec backend python manage.py collectstatic*

* Скопировать файлы статики в /backend_static/static/ backend-контейнера: *sudo docker compose exec backend cp -r /app/collected_static/. /backend_static/static/*

* Перейти по адресу 127.0.0.1:8000


### Примеры запросов:

# Спецификация

При локальном запуске документация будет доступна по адресу:

```
http://127.0.0.1:8080/api/docs/
```

# Примеры запросов к API

### Регистрация нового пользователя

Описание метода: Зарегистрировать пользователя в сервисе. Права доступа: Доступно без токена.

Тип запроса: `POST`

Эндпоинт: `/api/users/`

Обязательные параметры: `email, username, first_name, last_name, password`

Пример запрос:

```
{
  "email": "vpupkin@yandex.ru",
  "username": "vasya.pupkin",
  "first_name": "Вася",
  "last_name": "Иванов",
  "password": "Qwerty123"
}
```

Пример успешного ответа:

```
{
  "email": "vpupkin@yandex.ru",
  "id": 0,
  "username": "vasya.pupkin",
  "first_name": "Вася",
  "last_name": "Иванов"
}
```

### Cписок тегов

Описание метода: Получение списка тегов. Права доступа: Доступно без токена.

Тип запроса: `GET`

Эндпоинт: `/api/tags/`

Пример запроса:

Пример успешного ответа:

```
[
  {
    "id": 0,
    "name": "Завтрак",
    "slug": "breakfast"
  }
]
```

### Добавление нового рецепта

Описание метода: Добавить новый рецепт. Права доступа: Аутентифицированные пользователи.

Тип запроса: `POST`

Эндпоинт: `/api/recipes/`

Обязательные параметры: `ingredients, tags, image, name, text, cooking_time`

Пример запроса:

```
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```

Пример успешного ответа:

```
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Иванов",
    "is_subscribed": false,
    "avatar": "http://foodgram.example.org/media/users/image.png"
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.png",
  "text": "string",
  "cooking_time": 1
}
```