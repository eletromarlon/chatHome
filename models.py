from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))  # Armazenar hash da senha

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_message = db.Column(db.Text)
    model_response = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Specialist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150))
    descricao = db.Column(db.String(300))
    prompt_base = db.Column(db.Text)  # few-shot ou instruções
    modelo_preferido = db.Column(db.String(50))

class Model(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    api_key = db.Column(db.String(300))
    endpoint = db.Column(db.String(300))
    tipo = db.Column(db.String(50))  # Ex: openai, huggingface
