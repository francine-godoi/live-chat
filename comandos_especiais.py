from datetime import datetime
from collections import defaultdict
import socket
from database import pegar_historico_chat


def ajuda() -> None:
    """Para listar os comandos disponíveis."""

    comandos = """
        Comandos Especiais:
        /ajuda: Para listar os comandos disponíveis.
        /historico: mostra histórico do chat.
        /hora: mostra a hora atual.
        /nome novo_nome: Para alterar o nome de exibição do usuário. 
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

def banir(banidos:defaultdict, destinatario_cmd: str, sala_remetente: str, remetente_cmd: str, moderadores: defaultdict, salas: defaultdict, clientes_conectados: dict):
    if destinatario_cmd == remetente_cmd:
        return 'Você não pode banir você mesmo'
    
    if remetente_cmd not in moderadores or destinatario_cmd not in salas[sala_remetente]:
        return 'Apenas moderadores podem banir usuários de sua sala'
    clientes_conectados[destinatario_cmd].send('<bot> disse: Você foi banido dessa sala.'.encode('utf-8'))
    clientes_conectados[destinatario_cmd].close()
    sair(destinatario_cmd, salas[sala_remetente], moderadores, clientes_conectados)
    banidos[sala_remetente] = destinatario_cmd
    return 'banido'


def expulsar(destinatario_cmd: str, sala_remetente: str, remetente_cmd: str, moderadores: defaultdict, salas: defaultdict, clientes_conectados: dict):
    if destinatario_cmd == remetente_cmd:
        return 'Você não pode expulsar você mesmo'
    
    if remetente_cmd not in moderadores or destinatario_cmd not in salas[sala_remetente]:
        return 'Apenas moderadores podem expulsar usuários de sua sala'
    clientes_conectados[destinatario_cmd].send('<bot> disse: Você foi expulso dessa sala.'.encode('utf-8'))
    sair(destinatario_cmd, salas[sala_remetente], moderadores, clientes_conectados)    
    return 'expulso'


def historico(sala):
    """mostra histórico do chat."""
    chat = pegar_historico_chat(sala)
    return chat


def hora():
    """mostra a hora atual."""
    horas = datetime.now().strftime("%H:%M")
    return horas


def nome(nome_atual: str, novo_nome: str, clientes_conectados: dict, sala: list, moderadores: dict):

    clientes_conectados[novo_nome] = clientes_conectados[nome_atual]
    del clientes_conectados[nome_atual]    
    sala.remove(nome_atual)
    sala.append(novo_nome)
    if nome_atual in moderadores:
        moderadores[novo_nome] = moderadores[nome_atual]
        del moderadores[nome_atual]
    return 'nome'


def ping():
    """o bot responde com "pong" para testar a conectividade."""
    return "pong"


def privado(
    remetente: str, destinatario: str, clientes_conectados: dict, mensagem: str, destinatario_cmd: str, sala_remetente
):
    """envia mensagem privada."""
    if destinatario_cmd not in sala_remetente:
        return "Remetente não se encontra na sala"
    clientes_conectados[destinatario_cmd].send(
        f"<{remetente}> disse: @{destinatario} {mensagem}".encode("utf-8")
    )
    return 'enviado'


def sair(
    username: str, sala: defaultdict, moderadores: dict, clientes_conectados: dict
):
    """Para desconectar do chat."""    
    clientes_conectados[username].close()
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
    return "\n".join(f'\t{usuario}' for usuario in sala)


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
