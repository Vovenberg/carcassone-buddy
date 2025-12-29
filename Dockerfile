FROM python:3.13

# Копируем uv из официального образа
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Создание рабочей директории
WORKDIR /app

# Копируем файлы зависимостей для кэширования слоя
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости (без проекта для лучшего кэширования)
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_NO_DEV=1
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev

# Копирование приложения
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# Устанавливаем PATH **ДО** переключения пользователя
ENV PATH="/app/.venv/bin:$PATH"

# Создание пользователя для безопасности
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Открытие порта
EXPOSE 5000

# Команда запуска с Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5050", "--workers", "1", "app:app"]
