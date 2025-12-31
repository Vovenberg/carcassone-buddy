#!/bin/bash
set -e  # Остановить выполнение при ошибке

echo "🔄 Обновление репозитория..."
git fetch
git rebase origin/main

echo "🛑 Остановка контейнера..."
docker stop carcassone-buddy 2>/dev/null || true


echo "🏗️  Сборка образа..."
DOCKER_BUILDKIT=1 docker build -t carcassone-buddy .

echo "🚀 Запуск контейнера..."
docker run -d --rm -p 5050:5050 -v "$(pwd)/data/db.json:/app/db.json" --name carcassone-buddy carcassone-buddy

echo "✅ Готово!"