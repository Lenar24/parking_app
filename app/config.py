"""Конфигурация приложения"""

import os


class Config:
    """Базовые настройки приложения"""

    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///parking.db"


class DevelopmentConfig(Config):
    """Настройки для разработки"""

    DEBUG = True
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    """Настройки для тестирования"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    """Настройки для продакшена"""

    DEBUG = False

    @classmethod
    def init_app(cls, app):
        import logging  # Импорт логирования

        logging.basicConfig(level=logging.INFO)


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}  # Словарь конфигурации
