import json


def pegar_path_banco(db):
    if db == 'clientes_conectados':
        db_path = 'db/clientes_conectados.json'
    elif db == 'salas':
        db_path = 'db/salas.json'
    elif db == 'moderadores':
        db_path = 'db/moreradores.json'
    return db_path


def salvar_dados_banco(db: str, dados):
    db_path = pegar_path_banco(db)
    #teste = pegar_dados_banco(db)    
    with open(db_path, mode='w', encoding='utf-8') as arquivo:
        json.dump(dados, arquivo)


def pegar_dados_banco(db: str):
    db_path = pegar_path_banco(db)
    try:
        with open(db_path, mode='r', encoding='utf-8') as arquivo:
            dados = json.load(arquivo)
            return dados
    except json.JSONDecodeError:
        return None


