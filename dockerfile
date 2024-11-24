# Используем базовый образ Python
FROM python:3.11

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN python manage.py migrate
RUN python manage.py shell < create_superuser.py

# Копируем все содержимое проекта
COPY . .

# Открываем порт для Django
EXPOSE 8000

# Команда запуска
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
