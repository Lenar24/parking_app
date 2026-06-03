"""ORM-модели"""

from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # Инициализация БД


class Client(db.Model):
    """Модель клиента"""

    __tablename__ = "client"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    credit_card = db.Column(db.String(50), nullable=True)
    car_number = db.Column(db.String(10), nullable=True)

    parking_logs = db.relationship("ClientParking", backref="client", lazy="dynamic")

    def to_dict(self):
        """
        Конвертация модели в словарь для API
        (с маскированием карты, видны только 4 последние цифры)
        """
        masked_card = None
        if self.credit_card:
            card_length = len(self.credit_card)
            if card_length > 4:
                masked_card = "*" * (card_length - 4) + self.credit_card[-4:]
            else:
                masked_card = "*" * card_length

        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "credit_card": masked_card,
            "car_number": self.car_number,
        }


class Parking(db.Model):
    """Модель парковки"""

    __tablename__ = "parking"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    opened = db.Column(db.Boolean, default=True)
    count_places = db.Column(db.Integer, nullable=False)
    count_available_places = db.Column(db.Integer, nullable=False)

    parking_logs = db.relationship("ClientParking", backref="parking", lazy="dynamic")

    def to_dict(self):
        """Конвертация модели в словарь для API"""
        occupancy_rate = 0
        if self.count_places > 0:
            occupancy_rate = round(
                (1 - self.count_available_places / self.count_places) * 100, 2
            )

        return {
            "id": self.id,
            "address": self.address,
            "opened": self.opened,
            "count_places": self.count_places,
            "count_available_places": self.count_available_places,
            "occupancy_rate": occupancy_rate,
        }

    def has_available_spaces(self):
        """Проверка наличия свободных мест на парковке"""
        return self.opened and self.count_available_places > 0

    def occupy_space(self):
        """Занять место на парковке (уменьшить количество мест на 1)"""
        if self.has_available_spaces():
            self.count_available_places -= 1
            return True
        return False

    def free_space(self):
        """Выезд из места на парковке (увеличить количество мест на 1)"""
        if self.count_available_places < self.count_places:
            self.count_available_places += 1
            return True
        return False


class ClientParking(db.Model):
    """Модель лога въезда-выезда с парковки"""

    __tablename__ = "client_parking"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    parking_id = db.Column(db.Integer, db.ForeignKey("parking.id"), nullable=False)
    time_in = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    time_out = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        """Преобразование модели к словарю для API представления"""
        return {
            "id": self.id,
            "client_id": self.client_id,
            "parking_id": self.parking_id,
            "time_in": self.time_in.isoformat() if self.time_in else None,
            "time_out": self.time_out.isoformat() if self.time_out else None,
            "is_active": self.time_out is None,
            "parking_duration": self.get_duration(),
        }

    def get_duration(self):
        """Расчет времени парковки в минутах"""
        if not self.time_in:
            return None
        end_time = self.time_out or datetime.now(timezone.utc).replace(tzinfo=None)
        duration = (end_time - self.time_in).total_seconds() / 60
        return round(duration, 2)
