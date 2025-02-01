"""Salva e Recupera informações sobre as conversas"""

import pathlib


def salvar_historico_chat(nome_chat: str, dados: str) -> None:
    """Salva as conversas publicas do chat em um arquivo txt

    Args:
        nome_chat (str): Nome da sala
        dados (str): mensagem enviada
    """
    with open(f"historico_chat/{nome_chat}.txt", "a", encoding="utf-8") as arquivo:
        arquivo.write(f"{dados}\n")


def pegar_historico_chat(nome_chat: str) -> list[str]:
    """Retorna o historico de conversas de uma determinada sala"""

    with open(f"historico_chat/{nome_chat}.txt", "r", encoding="utf-8") as arquivo:
        dados = arquivo.readlines()

    return dados


def limpar_historico() -> None:
    """Limpa o histório de conversas"""
    for arquivo in pathlib.Path("historico_chat").iterdir():
        arquivo.unlink(missing_ok=True)
