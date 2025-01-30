""" Bot para chat em tempo real usando socket """

import socket
import threading
from datetime import datetime

import database

HOST = "127.0.0.1"
PORT = 9999
FORMATO_CODIFICACAO = "utf-8"


def enviar_resposta_servidor(mensagem: str, bot_socket: socket):
    """Envia mensagem do bot após processar o comando enviado pelo usuário"""
    bot_socket.send(mensagem.encode(FORMATO_CODIFICACAO))


def ajuda(cliente: str, bot_socket: socket) -> None:
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
        /banir nome_usuario: Usuários banidos não podem acessar a sala.
        /expulsar nome_usuario: Desconecta usuário da sala.
    """
    enviar_resposta_servidor(f'{cliente}|{comandos}', bot_socket)


def historico(cliente, sala, bot_socket):
    """mostra histórico do chat."""
    pass


def hora(cliente: str, bot_socket: socket):
    """mostra a hora atual."""
    horas = datetime.now().strftime("%H:%M")
    enviar_resposta_servidor(f'{cliente}|{horas}', bot_socket)


def nome(nome_atual, novo_nome, sala, bot_socket):
    """Para alterar o nome de exibição do usuário."""
    clientes_conectados = database.pegar_dados_banco('clientes_conectados')
    salas = database.pegar_dados_banco('salas')
    moderadores = database.pegar_dados_banco('moderadores')

    if novo_nome in clientes_conectados:
        enviar_resposta_servidor(f"{nome_atual}|Username já existe", bot_socket)
        # TODO Testar com usernames que já existem

    #TODO precisa atualizar no servidor também
    clientes_conectados.remove(nome_atual)
    clientes_conectados.append(novo_nome)

    salas[sala].remove(nome_atual)
    salas[sala].append(novo_nome)

    if moderadores and nome_atual in moderadores:
        moderadores[novo_nome] = moderadores[nome_atual]
        del moderadores[nome_atual]

    database.salvar_dados_banco('clientes_conectados', clientes_conectados)
    database.salvar_dados_banco('salas', salas)
    database.salvar_dados_banco('moderadores', moderadores)

    enviar_resposta_servidor(f"{novo_nome}|{nome_atual} agora se chama {novo_nome}", bot_socket)


def ping(cliente: str, bot_socket):
    """o bot responde com "pong" para testar a conectividade."""
    enviar_resposta_servidor(f'{cliente}|pong', bot_socket)


def privado(cliente:str, destinatario:str, mensagem:str, bot_socket:socket):
    """envia mensagem privada."""
    resposta = f"{cliente}|{destinatario}|{mensagem}"
    enviar_resposta_servidor(resposta, bot_socket)


def sair(username, sala, bot_socket):
    """Para desconectar do chat."""
    #TODO arrumar
    del clientes_conectados[username]
    salas[sala].remove(username)
    enviar_resposta_servidor(f"sair:{username}|{username} sai da sala.", bot_socket)


def stats(username, sala, bot_socket):
    """Mostrar informações do chat:
    número total de mensagens enviadas,
    tempo total de atividade do chat,
    usuários mais ativos."""
    pass


def usuarios(username, sala, bot_socket):
    """Para listar todos os usuários conectados."""
    #TODO arrumar
    mensagem = "\n".join(nome_usuario for nome_usuario in salas[sala])
    enviar_resposta_servidor(f'{username}|{mensagem}', bot_socket)


def banir(username, nome_usuario, sala, bot_socket):
    """Desconecta usuário e o adiciona a uma lista de clientes que não podem acessar a sala."""
    pass


def expulsar(username, nome_usuario, sala, bot_socket):
    """Desconecta usuário da sala, mas usuario pode voltar ao chat."""
    #TODO arrumar
    if moderadores[username] == sala:
        sair(nome_usuario, sala, bot_socket)
    else:
        enviar_resposta_servidor(f'{username}|"Apenas o moderador pode expulsar alguém da sala.', bot_socket)


def extrair_dados_da_mensagem(informacao: str) -> tuple:
    """Separa as informações da mensagem

    Returns:
        tuple: cliente, sala, Comando, Usuário afetado pelo comando, Texto da mensagem(se tiver)
    """
    info_usuario, mensagem = informacao.split("|")
    cliente, sala = info_usuario.split(":")

    if mensagem.find(" ") == -1:
        # Se não tem espaço, a mensagem é o comando
        comando = mensagem
        nome_usuario = ""
        texto_da_mensagem = ""
    else:
        # Caso tenha espaço, o comando tem argumentos
        comando, nome_usuario, *texto_da_mensagem = mensagem.split(" ")
        texto_da_mensagem = " ".join(texto_da_mensagem)

    return (cliente, sala, comando, nome_usuario, texto_da_mensagem)


def processar_comando(mensagem: str, bot_socket: socket) -> None:
    """Envia o comando para a função responsável por sua execução"""
    cliente, sala, comando, nome_usuario, texto_da_mensagem = extrair_dados_da_mensagem(
        mensagem
    )

    match comando:
        case "/ajuda":
            ajuda(cliente, bot_socket)
        case "/banir":
            banir(cliente, nome_usuario, sala, bot_socket)
        case "/expulsar":
            expulsar(cliente, nome_usuario, sala, bot_socket)
        case "/historico":
            historico(cliente, sala, bot_socket)
        case "/hora":
            hora(cliente, bot_socket)
        case "/nome":
            nome(cliente, nome_usuario, sala, bot_socket)
        case "/ping":
            ping(cliente, bot_socket)
        case "/privado":
            privado(cliente, nome_usuario, texto_da_mensagem, bot_socket)
        case "/sair":
            sair(cliente, sala, bot_socket)
        case "/stats":
            stats(cliente, sala, bot_socket)
        case "/usuarios":
            usuarios(cliente, sala, bot_socket)
        case _:
            enviar_resposta_servidor("Comando inválido", bot_socket)


def receber_comando(bot_socket: socket) -> None:
    """Recebe comando enviado pelo cliente"""

    while True:
        comando = bot_socket.recv(1024).decode(FORMATO_CODIFICACAO)
        processar_comando(comando, bot_socket)


def conectar_servidor() -> socket:
    """Conexão com o servidor

    Returns:
        socket: socket de comunicação com o servidor
    """
    bot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        bot_socket.connect((HOST, PORT))
        bot_socket.send("!bot!".encode(FORMATO_CODIFICACAO))
    except ConnectionRefusedError:
        print("Não foi possível conectar com o servidor.")
    except Exception as e:
        print(f"Um erro ocorreu ao tentar conectar com o servidor: {e}")

    return bot_socket


def main():
    """Inicia o bot"""
    bot_socket = conectar_servidor()

    thread_receber_comando = threading.Thread(target=receber_comando, args=(bot_socket,))
    thread_receber_comando.start()


if __name__ == "__main__":
    main()
