from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class RegisterForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Registrar')

class ModeloForm(FlaskForm):
    nome = StringField('Nome do Modelo', validators=[DataRequired()])
    tipo = SelectField('Tipo', choices=[
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('deepseaker', 'DeepSeaker'),
        ('meta', 'Meta'),
        ('google', 'Google'),
        ('huggingface', 'HuggingFace'),
        ('mistral', 'Mistral'),
        ('local', 'Local/Servidor Próprio'),
        ('outro', 'Outro')
    ], validators=[DataRequired()])
    chave_api = TextAreaField('Chave da API', validators=[DataRequired()])
    endpoint = StringField('Endpoint da API', validators=[DataRequired()])
    submit = SubmitField('Cadastrar Modelo')


class EspecialistaForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    descricao = StringField('Descrição', validators=[DataRequired()])
    prompt_base = TextAreaField('Prompt Base', validators=[DataRequired()])
    modelo_preferido = SelectField('Modelo Preferido', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Cadastrar Especialista')