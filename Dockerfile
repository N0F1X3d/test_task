# 1. Используем официальный Python-образ
FROM python:3.12-slim

# 2. Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# 3. Копируем зависимости
COPY requirements.txt .

# 4. Устанавливаем зависимости
RUN pip install --upgrade pip && pip install -r requirements.txt

# 5. Копируем весь код проекта
COPY . .

# 6. Открываем порт (если используешь стандартный порт Django)
EXPOSE 8000

# 7. Команда по умолчанию (запуск сервера)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
