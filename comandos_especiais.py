from datetime import datetime
from collections import defaultdict
import socket

#TODO colocar /nome e comandos de moderador

def ajuda() -> None:
    """Para listar os comandos disponíveis."""

    comandos = """
        Comandos Especiais:
        /ajuda: Para listar os comandos disponíveis.
        /historico: mostra histórico do chat.
        /hora: mostra a hora atual.
        /ping: o bot responde com "pong" para testar a conectividade.
        /privado nome_usuario mensagem: envia mensagem privada.
        /sair: Para desconectar do chat.
        /stats: Mostrar estatisticas do chat
        /usuarios: Para listar todos os usuários conectados.

        Comandos de Administrador/Moderador:
        //banir nome_usuario: Usuários banidos não podem acessar a sala.
        //expulsar nome_usuario: Desconecta usuário da sala.
    """
    return comandos


def historico(sala):
    """mostra histórico do chat."""
    return 0


def hora():
    """mostra a hora atual."""
    horas = datetime.now().strftime("%H:%M")
    return horas


def ping():
    """o bot responde com "pong" para testar a conectividade."""
    return "pong"


def privado(
    remetente: str, destinatario: str, socket_destinatario: socket, mensagem: str
):
    """envia mensagem privada."""
    socket_destinatario.send(
        f"<{remetente}> disse: @{destinatario} {mensagem}".encode("utf-8")
    )



def sair(
    username: str, sala: defaultdict, moderadores: dict, clientes_conectados: dict
):
    """Para desconectar do chat."""
    del clientes_conectados[username]
    sala.remove(username)
    if username in moderadores:
        del moderadores[username]

    return f"{username} saiu da sala."


def stats(sala):
    """Mostrar informações do chat:
    número total de mensagens enviadas,
    tempo total de atividade do chat,
    usuários mais ativos."""
    return 0


def usuarios(sala):
    """Para listar todos os usuários conectados."""
    return "\n".join(usuario for usuario in sala)


def extrair_dados_da_mensagem(mensagem: str) -> tuple:
    """Separa as informações da mensagem

    Returns:
        tuple: cliente, sala, Comando, Usuário afetado pelo comando, Texto da mensagem(se tiver)
    """
    if mensagem.find(" ") == -1:
        # Se não tem espaço, a mensagem é o comando
        comando = mensagem
        nome_usuario = ""
        texto_da_mensagem = ""
    else:
        # Caso tenha espaço, o comando tem argumentos
        comando, nome_usuario, *texto_da_mensagem = mensagem.split(" ")
        texto_da_mensagem = " ".join(texto_da_mensagem)

    return (comando, nome_usuario, texto_da_mensagem)
