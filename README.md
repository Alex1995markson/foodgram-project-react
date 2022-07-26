# Foodgram
Cервис для публикаций и обмена рецептами.

Авторизованные пользователи могут подписываться на понравившихся авторов, добавлять рецепты  в покупки, скачивать список покупок. Неавторизованным пользователям доступна регистрация, авторизация, просмотр рецептов других пользователей. Создавать теги, через панель администратора давать права другим пользователям.

## Стек технологий
Python, Django, Django REST Framework, PostgresQL, Docker, Yandex.Cloud.

## Установка
Для запуска локально, создайте файл `.envfiles` в корне проекта с содержанием:
```
[GENERAL]
DEBUG=1
SECRET_KEY=секретный ключ
DJANGO_ALLOWED_HOSTS=localhost 0.0.0.0 127.0.0.1 [::1]
DJANGO_SETTINGS_MODULE=config.settings.dev

[DATABASE]
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=postgres
SQL_USER=postgres
SQL_PASSWORD=postgres
SQL_HOST=db
SQL_PORT=5432

[ADMIN]
DJANGO_SU_EMAIL=admin@admin.ru
DJANGO_SU_PASSWORD=admin
DJANGO_SU_USERNAME=admin
```

#### Установка Docker
Для запуска проекта вам потребуется установить Docker и docker-compose.

Для установки на ubuntu выполните следующие команды:
```bash
sudo apt install docker docker-compose
```

Про установку на других операционных системах вы можете прочитать в [документации](https://docs.docker.com/engine/install/) и [про установку docker-compose](https://docs.docker.com/compose/install/).


### Настройка проекта
1. Запустите docker compose:
```bash
docker-compose up -d
```
2. Примените миграции:
```bash
docker-compose exec backend python manage.py migrate
```
3. Заполните базу начальными данными (необязательно):
```bash
docker-compose exec backend python manange.py loaddata data/fixtures.json
```
4. Создайте администратора:
```bash
docker-compose exec backend python manage.py createsuperuser
```
5. Соберите статику:
```bash
docker-compose exec backend python manage.py collectstatic
```

## Сайт
Сайт доступен по ссылке:
http://51.250.25.216/

## Над проектом работал:

**[Маценко Александр](https://github.com/Alex1995markson)**

## Документация к API
Чтобы открыть документацию локально, запустите сервер и перейдите по ссылке:
[http://127.0.0.1/api/docs/](http://127.0.0.1/api/docs/)

