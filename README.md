# Домашнее задание VK по web.

## Цель
Создать аналог Stack Overflow с возможностью задавать вопросы и отвечать на них.

### Технологический стек:
- Python
- Django
- Gunicorn
- Nginx
- MySQL

### Создание mysql базы данных (если необходимо)
1. Установить mysql:
   ```shell
   sudo apt install mysql-server
   sudo apt install libmysqlclient-dev python3-dev build-essential
   ```
2. Запуск mysql:
   ```shell
   sudo systemctl start mysql
   sudo systemctl enable mysql
   ```
3. Вход в cli:
   ```shell
   sudo mysql -u root -p
   ```
4. Создание базы данных:
   ```shell
   CREATE DATABASE name_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'projectuser'@'localhost' IDENTIFIED BY 'password';
   GRANT ALL PRIVILEGES ON name_db.* TO 'projectuser'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```
5. В settings.py указать:
   ```shell
   DATABASES['default'] = DATABASES['main']
   ```
6. Прописать креды для подключения к базе данных в `.env` (пример есть в `.env.example`).

### Инструкция по настройке проекта:
1. Установить необходимые пакеты в виртуальное окружение:
   ```shell
   pip install -r requirements.txt
   ```
2. Применить миграции к базе данных:
   ```shell
   python manage.py migrate
   ```
3. *Для заполнения базы данных рандомными данными выполнить команду:
   ```shell
   python manage.py fill_db [ratio]
   ```
   где `ratio` - числовой коэффициент, определяющий количество создаваемых объектов:
   - пользователей = ratio
   - вопросов = ratio * 10
   - ответов = ratio * 100
   - тэгов = ratio
   - лайков = ratio * 200
4. Запустить gunicorn (backend сервер):
   ```shell
   gunicorn -c gunicorn.conf.py
   ```
5. Запустить nginx (reverse proxy сервер):
   ```shell
   sudo systemctl start nginx
   ```
   Конфигурационный файл nginx находится в папке `nginx`.
   Его нужно скопировать в `/etc/nginx/sites-available/` и создать символическую ссылку в `/etc/nginx/sites-enabled/`.
   После этого, можно запускать nginx командой выше.
6. Выполнить сбор статических файлов:
   ```shell
    python manage.py collectstatic
   ```
7. Добавить задачу регулярного кэширования в cron:
   ```shell
   python manage.py crontab add
   ```


### Запуск centrifugo
1. Установка Centrifugo:
   ```shell
   cd dir/to/install/centrifugo
   wget https://github.com/centrifugal/centrifugo/releases/download/v5.0.0/centrifugo_5.0.0_linux_amd64.tar.gz
   tar -xzf centrifugo_5.0.0_linux_amd64.tar.gz
   sudo mv centrifugo /usr/local/bin/
   ```
2. Создание конфигурации:
   ```shell
   centrifugo genconfig
   cat config.json
   ```
3. В конфиге будут указаны токены, которые необходимо добавить в `.env`.
4. Желательно ещё добавить в конфиг строку `"port": "8001"`, чтобы centrifugo не конфликтовал с django.
5. Запуск centrifugo:
   ```shell
   centrifugo -c config.json
   ```
