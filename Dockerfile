FROM python:3.9-slim-buster


# Создание рабочей директории
WORKDIR /app

# Копирование файла зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование приложения
COPY . .

# Создание пользователя для безопасности
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Открытие порта
EXPOSE 5000

# Команда запуска с Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5050", "--workers", "1", "app:app"]
