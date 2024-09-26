# models.py
from flask_sqlalchemy import SQLAlchemy
from app import app
from config import config

app.config.from_object(config)
db = SQLAlchemy(app)

class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    common_name = db.Column(db.String(100))
    scientific_name = db.Column(db.String(100))
    watering_frequency = db.Column(db.Integer)
    sunlight_requirements = db.Column(db.String(50))

    def __repr__(self):
        return f"<Plant {self.common_name}>"
