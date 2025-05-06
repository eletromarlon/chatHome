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
        print(f"{modelo.endpoint} - {modelo.api_key}")

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

        '''response = requests.post(
            modelo.endpoint,
            headers={
                "Authorization": f"Bearer {modelo.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": modelo.nome,
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        resposta = response.json()["choices"][0]["message"]["content"]
        return resposta'''
    else:
        # Aqui você adicionaria outros tipos (Ex: huggingface, modelos locais)
        return "Modelo não suportado ainda."
