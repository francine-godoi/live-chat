""" Servidor de chat em tempo real usando socket """

import socket
import threading
from collections import defaultdict


FORMATO_CODIFICACAO = "utf-8"
HOST = "127.0.0.1"
PORT = 9999

clientes_conectados = {}
moderadores = {}
salas = defaultdict(list)
salas["Geral"] = []


def enviar_notificacao_privada(mensagem: str, cliente: socket) -> None:
    """Notificação do sistema, enviados de forma privada"""

    cliente.send(mensagem.encode(FORMATO_CODIFICACAO))


def enviar_notificacao_publica(mensagem: str, nome_sala: str) -> None:
    """Notificação do sistema, enviados para os membros de uma determinada sala."""

    for username, cliente in clientes_conectados.items():
        if username in salas[nome_sala]:
            cliente.send(mensagem.encode(FORMATO_CODIFICACAO))


def pegar_username_escolhido(cliente: socket, mensagem: str) -> str | None:
    """Pega o username do cliente usando a mensagem recebida.
       Utilizado apenas durante a Conexão Inicial.

    Args:
        mensagem (str): '!username:nome_usuario'

    Returns:
        str: username, se tiver
    """
    username = mensagem.split(":")
    if not username[1]:
        enviar_notificacao_privada("Digite um usuário.", cliente)
        return None
    if username[1] in clientes_conectados:
        enviar_notificacao_privada("Usuário já existe.", cliente)
        return None
    return username[1]


def salvar_usuario_conectado(cliente: socket, mensagem: str) -> str | None:
    """Salva o usuário que acabou de conectar na lista de clientes conectados.

    Args:
        mensagem (str): '!username:nome_usuario', usada para pegar o usuário

    Returns:
        str: username
    """
    username = pegar_username_escolhido(cliente, mensagem)
    if not username:
        return None
    clientes_conectados[username] = cliente
    enviar_notificacao_privada("Conectado com sucesso.", cliente)
    return username


def enviar_salas_disponiveis(cliente: socket) -> None:
    """Envia para o cliente as salas disponíveis"""

    salas_disponiveis = "|".join(sala for sala in salas)
    cliente.send(salas_disponiveis.encode(FORMATO_CODIFICACAO))


def pegar_sala_escolhida(cliente: socket) -> str:
    """Pega sala escolhida

    Returns:
        str: nome da sala escolhida
    """
    enviar_salas_disponiveis(cliente)

    sala_escolhida = cliente.recv(25).decode(FORMATO_CODIFICACAO)
    return sala_escolhida


def adicionar_moderador(sala: str, username: str) -> None:
    """Caso a sala não exista, o usuário a criou e portanto será seu moderador"""

    if sala not in salas:
        moderadores[username] = sala


def vincular_cliente_e_sala_escolhida(cliente: socket, username: str) -> None:
    """Vincula o cliente a sala de conversas"""

    sala_escolhida = pegar_sala_escolhida(cliente)
    adicionar_moderador(sala_escolhida, username)
    salas[sala_escolhida].append(username)

    enviar_notificacao_publica(f"<{username}> entrou no chat.", sala_escolhida)


def pegar_username_do_cliente(cliente: socket) -> str:
    """Filtra os clientes conectados para pegar o username do cliente.

    Returns:
        str: username
    """
    username = next(
        filter(lambda key: clientes_conectados[key] == cliente, clientes_conectados)
    )
    return username


def pegar_sala_do_cliente(username: str) -> str | None:
    """Filtra as salas para achar em qual delas está o username do cliente

    Returns:
        str: nome da sala
    """
    for nome_sala in salas:
        if username in salas[nome_sala]:
            return nome_sala
    return None


def enviar_mensagem_publica(remetente: socket, mensagem: str) -> None:
    """Envia mensagem para todos os membros da sala do cliente"""

    username_remetente = pegar_username_do_cliente(remetente)
    sala_do_remetente = pegar_sala_do_cliente(username_remetente)

    for username, cliente in clientes_conectados.items():
        if username in salas[sala_do_remetente] and username != username_remetente:
            cliente.send(
                f"<{username_remetente}> disse: {mensagem}".encode(FORMATO_CODIFICACAO)
            )


def chamar_bot(cliente: socket, mensagem: str) -> None:
    """Envia a mensagem com o comando para o bot precessar"""
    enviar_notificacao_privada(mensagem, clientes_conectados["!bot!"])
    resposta = clientes_conectados["!bot!"].recv(1024).decode(FORMATO_CODIFICACAO)
    cliente.send(f"<bot> disse: {resposta}".encode(FORMATO_CODIFICACAO))


def receber_mensagens(cliente: socket) -> None:
    """Recebe e processa as mensagens dos clientes."""

    while True:
        mensagem = cliente.recv(2048).decode(FORMATO_CODIFICACAO)
        if mensagem.startswith("!username"):
            # Conexão inicial, salva username e sala do novo usuário
            username = salvar_usuario_conectado(cliente, mensagem)
            if username:
                vincular_cliente_e_sala_escolhida(cliente, username)
        elif mensagem == "!bot!":
            # Salva os dados de conexão do bot
            clientes_conectados["!bot!"] = cliente
        elif mensagem.startswith("/"):
            # Comandos especiais, responsabilidade do bot
            chamar_bot(cliente, mensagem)
        else:
            # Mensagens normais
            enviar_mensagem_publica(cliente, mensagem)


def iniciar_servidor() -> socket:
    """Setup inicial do servidor.

    Returns:
        socket: socket para comunicação com o servidor
    """
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        servidor.bind((HOST, PORT))
        print("Servidor iniciado.")
    except socket.gaierror:
        print("Não foi possivel iniciar o servidor.")
        exit()
    except Exception as e:
        print(f"Um erro ocorreu ao tentar iniciar o servidor: {e}")
        exit()

    return servidor


def aceitar_conexao_cliente(servidor: socket) -> None:
    """Escuta conexão com clientes e inicia as threads."""

    servidor.listen()
    while True:
        cliente, endereco = servidor.accept()
        print(f"Cliente conectado com sucesso. IP {endereco}")

        thread = threading.Thread(target=receber_mensagens, args=(cliente,))
        thread.start()


def main() -> None:
    """Inicia o programa"""

    servidor = iniciar_servidor()
    aceitar_conexao_cliente(servidor)


if __name__ == "__main__":
    main()
