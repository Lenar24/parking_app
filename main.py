"""Точка входа"""

# !/usr/bin/env python3
import os

from app import create_app

config_name = os.environ.get("FLASK_CONFIG", "development")  # Получаем имя конфигурации
app = create_app(config_name)  # Создаем приложение

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
