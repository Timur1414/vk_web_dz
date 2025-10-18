# Домашнее задание VK по web.

## Цель
Создать аналог Stack Overflow с возможностью задавать вопросы и отвечать на них.

### Технологический стек:
- Python
- Django
- Gunicorn
- Nginx
- PostgreSQL

### Инструкция по настройке проекта:
1. Установить необходимые пакеты в виртуальное окружение:
   ```bash
   pip install -r requirements.txt
   ```
2. Применить миграции к базе данных:
   ```bash
   python manage.py migrate
   ```
3. *Для заполнения базы данных рандомными данными выполнить команду:
   ```bash
   python manage.py fill_db [ratio]
   ```
    где `ratio` - числовой коэффициент, определяющий количество создаваемых объектов:
    - пользователей = ratio
    - вопросов = ratio * 10
    - ответов = ratio * 100
    - тэгов = ratio
    - лайков = ratio * 200
4. Запустить gunicorn (backend сервер):
   ```bash
   gunicorn -c gunicorn.conf.py
   ```
5. Запустить nginx (reverse proxy сервер):
   ```bash
   sudo systemctl start nginx
   ```
   Конфигурационный файл nginx находится в папке `nginx`.
   Его нужно скопировать в `/etc/nginx/sites-available/` и создать символическую ссылку в `/etc/nginx/sites-enabled/`.
   После этого, можно запускать nginx командой выше.
