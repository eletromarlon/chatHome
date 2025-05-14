from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Message, Specialist, Model
from forms import LoginForm, RegisterForm, EspecialistaForm, ModeloForm
from utils import enviar_mensagem_modelo, listar_especialistas, listar_messages
from forms import ModeloForm
from sqlalchemy.orm import aliased
import bcrypt, uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
# Coloca o banco dentro de var/app-instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///init_test.db'
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

@app.route("/chat", methods=["GET", "POST"])
@login_required
def chat():
    user_id = current_user.id

    print(f"ID do usuer {user_id}, da conversa {session.get('conversation_id')}")

    # Se for requisição GET com parâmetro nova=1 ou não tiver conversa ativa
    if request.args.get("nova") or "conversation_id" not in session:
        session["conversation_id"] = str(uuid.uuid4())

    conversation_id = session["conversation_id"]

    # ----- TRATAMENTO DE POST: CARREGAMENTO DE HISTÓRICO -----
    if request.method == "POST" and request.content_type != "application/json":
        conversa_id = request.form.get("carregar_conversa")
        print("tentou carregar conversa", conversa_id)
        if conversa_id:
            session["conversation_id"] = conversa_id
            return redirect(url_for("chat"))

    # ----- TRATAMENTO DE POST: ENVIO DE MENSAGEM JSON -----
    elif request.method == "POST" and request.content_type == "application/json":
        content = request.get_json()
        user_message = content.get("message")
        specialist_id = content.get("especialista_id")

        # Salvar mensagem do usuário
        user_msg = Message(
            user_id=user_id,
            specialist_id=specialist_id,
            content=user_message,
            role="user",
            conversation_id=conversation_id
        )
        db.session.add(user_msg)

        # Chamada simulada ao modelo (ou real via API)
        resposta = enviar_mensagem_modelo(user_message, specialist_id)

        # Salvar resposta
        ai_msg = Message(
            user_id=user_id,
            specialist_id=specialist_id,
            content=resposta,
            role="assistant",
            conversation_id=conversation_id
        )
        db.session.add(ai_msg)
        db.session.commit()

        return jsonify({"response": resposta})  # <- retorna resposta ao fetch()

    # Buscar especialistas
    especialistas = Specialist.query.all()

    # Buscar mensagens da conversa atual
    mensagens = Message.query.filter_by(
        conversation_id=session["conversation_id"]
    ).order_by(Message.timestamp).all()


    # Subquery para pegar a primeira mensagem de cada conversa
    first_messages = (
        db.session.query(
            Message.conversation_id,
            db.func.min(Message.timestamp).label("min_time")
        )
        .filter_by(user_id=user_id, role="user")
        .group_by(Message.conversation_id)
        .subquery()
    )

    # Alias da tabela Message para fazer join
    M1 = aliased(Message)

    # Join para pegar conteúdo da primeira mensagem
    historico = (
        db.session.query(
            M1.conversation_id,
            M1.timestamp,
            M1.content
        )
        .join(first_messages, db.and_(
            M1.conversation_id == first_messages.c.conversation_id,
            M1.timestamp == first_messages.c.min_time
        ))
        .order_by(M1.timestamp.desc())
        .all()
    )

    print(f"Historico: {historico}")

    return render_template(
        "chat.html",
        especialistas=especialistas,
        mensagens=mensagens,
        historico=historico
    )


@app.route('/api/send_message', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    user_message = data.get('message')
    especialista_id = data.get('especialista_id')

    print("veio para cá")

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
    print(f"Conteudo de get: {request.args}")
    mensagens = Message.query.filter_by(user_id=current_user.id).order_by(Message.timestamp.asc()).all()
    historico = [{'pergunta': m.user_message, 'resposta': m.model_response} for m in mensagens]
    return jsonify(historico)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
