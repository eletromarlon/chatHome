# Inserir os dados iniciais no banco de dados
from app import db, app, os
from models import Model, Specialist, User
from app import bcrypt
import especialistas

models = ["deepseek-r1-distill-llama-70b",
        "gemma2-9b-it",
        "llama-3.3-70b-versatile",
        "allam-2-7b",
        "compound-beta",
        "qwen-qwq-32b",   
        "llama3-8b-8192",
        "meta-llama/llama-4-maverick-17b-128e-instruct",
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "distil-whisper-large-v3-en"]

with app.app_context():
    for model in models:
        user_msg = Model(
            nome = model,
            api_key = os.getenv("GROQ_API_KEY"),
            endpoint = "http://groq.com",
            tipo = "outro"
            )
        db.session.add(user_msg)
        db.session.commit()

with app.app_context():
    vetor_especialistas = [
        especialistas.Pesquisa,
        especialistas.Matematica,
        especialistas.Criador_Perguntas,
        especialistas.Gerador_Codigo,
        especialistas.Resumo_Texto,
        especialistas.Conversacao_Ingles
    ]   

    for especialista in vetor_especialistas:
        specialist = Specialist(
            nome = especialista["nome"],
            descricao = especialista["descricao"],
            prompt_base = especialista["prompt_base"],
            modelo_preferido = especialista["modelo_preferido"]
        )
        db.session.add(specialist)
        db.session.commit()
