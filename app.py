from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Message, Specialist, Model
from forms import LoginForm, RegisterForm, EspecialistaForm, ModeloForm
from utils import enviar_mensagem_modelo, listar_especialistas
import bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
# Coloca o banco dentro de var/app-instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///teste.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Para primeiro uso: cria o banco
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        usuario = User.query.filter_by(email=form.email.data).first()
        if usuario and bcrypt.checkpw(form.password.data.encode('utf-8'), usuario.password.encode('utf-8')):
            login_user(usuario)
            return redirect(url_for('chat'))
        else:
            flash('Email ou senha incorretos.')
    return render_template('login.html', form=form)

from forms import ModeloForm

@app.route('/cadastro_modelo', methods=['GET', 'POST'])
@login_required  # Se quiser restringir a usuários logados
def cadastro_modelo():
    form = ModeloForm()
    if form.validate_on_submit():
        novo_modelo = Model(
            nome=form.nome.data,
            tipo=form.tipo.data,
            api_key=form.chave_api.data,
            endpoint=form.endpoint.data
        )
        db.session.add(novo_modelo)
        db.session.commit()
        flash('Modelo cadastrado com sucesso!', 'success')
        return redirect(url_for('cadastro_especialista'))  # Redireciona para usar o modelo
    return render_template('cadastro_modelo.html', form=form)


@app.route('/cadastro_especialista', methods=['GET', 'POST'])
@login_required  # Opcional: restrinja a admins no futuro
def cadastro_especialista():
    form = EspecialistaForm()

    # Preenche o campo de modelo com os disponíveis no banco
    modelos = Model.query.all()
    form.modelo_preferido.choices = [(m.id, m.nome) for m in modelos]

    if form.validate_on_submit():
        modelo = Model.query.get(form.modelo_preferido.data)
        novo = Specialist(
            nome=form.nome.data,
            descricao=form.descricao.data,
            prompt_base=form.prompt_base.data,
            modelo_preferido=modelo.nome  # Nome, pois esse campo é texto
        )
        db.session.add(novo)
        db.session.commit()
        flash('Especialista cadastrado com sucesso!', 'success')
        return redirect(url_for('chat'))  # Ou outro destino
    return render_template('cadastro_especialista.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Verifica se já existe um usuário com o mesmo email
        if User.query.filter_by(email=form.email.data).first():
            flash("Já existe um usuário com este email.")
            return redirect(url_for('register'))

        # Cria hash da senha
        hashed = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())
        novo_usuario = User(
            nome=form.nome.data,
            email=form.email.data,
            password=hashed.decode('utf-8')
        )
        db.session.add(novo_usuario)
        db.session.commit()
        flash("Usuário registrado com sucesso! Faça login.")
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/chat')
@login_required
def chat():
    especialistas = listar_especialistas()
    return render_template('chat.html', especialistas=especialistas)

@app.route('/api/send_message', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    user_message = data.get('message')
    especialista_id = data.get('especialista_id')

    resposta = enviar_mensagem_modelo(user_message, especialista_id)

    # Salvar no histórico
    nova_msg = Message(
        user_id=current_user.id,
        user_message=user_message,
        model_response=resposta
    )
    db.session.add(nova_msg)
    db.session.commit()

    return jsonify({'response': resposta})

@app.route('/api/load_history', methods=['GET'])
@login_required
def load_history():
    mensagens = Message.query.filter_by(user_id=current_user.id).order_by(Message.timestamp.asc()).all()
    historico = [{'pergunta': m.user_message, 'resposta': m.model_response} for m in mensagens]
    return jsonify(historico)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
