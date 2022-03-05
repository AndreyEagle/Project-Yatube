## Проект «Yatube»
Проект Yatube это социальная сеть для публикации личных дневников. Можно создать свою страницу.
Имеются подписки на интересных авторов и комментирование их записей.
Посты можно отправить в тематические сообщества и посмотреть там записи разных авторов.

### Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:
```
git clone
```
```
cd yatube
```
Cоздать и активировать виртуальное окружение:
```
python3 -m venv env
```
```
source env/bin/activate
```
Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
Выполнить миграции:
```
python3 manage.py makemigrations
```
```
python3 manage.py migrate
```
Запустить проект:
```
python3 manage.py runserver
```
[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)
