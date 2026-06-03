"""Фабрика приложения"""

from flask import Flask, jsonify, render_template

from app.config import config
from app.models import db


def create_app(config_name="default"):
    """Фабрика создания приложения Flask"""
    app = Flask(
        __name__, template_folder="templates"
    )  # Изменяем путь к папке templates

    app.config.from_object(config[config_name])  # Загружаем конфигурацию

    # Отложенная инициализация SQLAlchemy
    db.init_app(app)

    register_blueprints(app)  # Регистрируем BluePrint
    register_error_handlers(app)  # Создаем обработчики ошибок
    register_cli_commands(app)  # Добавим команды CLI
    register_template_routes(app)  # Добавляем маршруты для шаблонов

    return app  # Возвращение объекта класса Flask


def register_blueprints(app):
    """Регистрация blueprint'ов API"""
    from app.api.client_parkings import client_parkings_bp
    from app.api.clients import clients_bp
    from app.api.parkings import parkings_bp

    app.register_blueprint(clients_bp, url_prefix="/api")
    app.register_blueprint(parkings_bp, url_prefix="/api")
    app.register_blueprint(client_parkings_bp, url_prefix="/api")

    @app.route("/health")
    def health_check():
        return (
            jsonify({"status": "ok", "message": "Parking application is running"}),
            200,
        )


def register_error_handlers(app):
    """Регистрация обработчиков ошибок"""

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": "Bad request", "message": str(error)}),
            400,
        )

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": "Not found", "message": str(error)}),
            404,
        )

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({"success": False, "error": "Internal server error"}), 500


def register_cli_commands(app):
    """Регистрация CLI команд"""

    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        print("Database initialized successfully!")

    @app.cli.command("drop-db")
    def drop_db():
        db.drop_all()
        print("Database dropped!")


def register_template_routes(app):
    """Регистрация маршрутов для HTML шаблонов"""

    @app.route("/")
    def index():
        """Главная страница"""
        return render_template("index.html")

    @app.route("/clients")
    def clients_page():
        """Страница управления клиентами"""
        return render_template("clients.html")

    @app.route("/parkings")
    def parkings_page():
        """Страница управления парковками"""
        return render_template("parkings.html")

    @app.route("/operations")
    def operations_page():
        """Страница операций заезда/выезда"""
        return render_template("parking_operations.html")

    @app.route("/history")
    def history_page():
        """Страница истории парковок"""
        return render_template("client_history.html")
