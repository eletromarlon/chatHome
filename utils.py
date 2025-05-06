from models import Specialist, Model
import requests, openai

def listar_especialistas():
    especialistas = Specialist.query.all()
    print(f"Lista de Especialistas: {[especialista.nome for especialista in especialistas]}")
    return especialistas

def enviar_mensagem_modelo(mensagem, especialista_id):
    especialista = Specialist.query.get(especialista_id)
    modelo = Model.query.filter_by(nome=especialista.modelo_preferido).first()

    # Se quiser fazer RAG, manipular aqui o contexto
    #prompt = especialista.prompt_base + "\nUsuário: " + mensagem + "\nModelo:"

    if modelo.tipo == 'openai':
    
        # Cria o cliente da OpenAI com a chave da API
        client = openai.OpenAI(api_key=modelo.api_key)

        # Envia a requisição para o modelo de chat
        response = client.chat.completions.create(
            model=modelo.nome,
            messages=[
                {"role": "system", "content": especialista.prompt_base},
                {"role": "user", "content": mensagem}
            ]
        )

        # Extrai e retorna o conteúdo da resposta
        resposta = response.choices[0].message.content
        return resposta
    elif modelo.tipo == 'anthropic':
        # Aqui você implementaria a chamada para o modelo da Anthropic
        # Exemplo fictício:
        headers = {
            'Authorization': f'Bearer {modelo.api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': modelo.nome,
            'messages': [
                {"role": "system", "content": especialista.prompt_base},
                {"role": "user", "content": mensagem}
            ]
        }
        response = requests.post(modelo.endpoint, headers=headers, json=data)
        if response.status_code == 200:
            resposta = response.json().get('choices')[0].get('message').get('content')
            return resposta
        else:
            return "Erro ao chamar o modelo da Anthropic."
    elif modelo.tipo == 'deepseaker':
        # Aqui você implementaria a chamada para o modelo da DeepSeaker
        # Exemplo fictício:
        headers = {
            'Authorization': f'Bearer {modelo.api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': modelo.nome,
            'messages': [
                {"role": "system", "content": especialista.prompt_base},
                {"role": "user", "content": mensagem}
            ]
        }
        response = requests.post(modelo.endpoint, headers=headers, json=data)
    else:
        # Aqui você adicionaria outros tipos (Ex: huggingface, modelos locais)
        return "Modelo não suportado ainda."
