import pathlib

def salvar_historico_chat(nome_chat: str, dados):

    with open(f'historico_chat/{nome_chat}.txt', 'a', encoding='utf-8') as arquivo:
        arquivo.write(f'{dados}\n')


def pegar_historico_chat(nome_chat: str):
    with open(f'historico_chat/{nome_chat}.txt', 'r', encoding='utf-8') as arquivo:
        dados = arquivo.readlines()
    
    return ''.join(f'\t{dado}' for dado in dados)

def limpar_historico():
    for arquivo in pathlib.Path('historico_chat').iterdir():
        arquivo.unlink(missing_ok=True)