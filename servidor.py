""" Servidor de chat em tempo real usando socket """

import socket
import threading
from collections import defaultdict

FORMATO_CODIFICACAO = "utf-8"
HOST = "127.0.0.1"
PORT = 9999

clientes_conectados = {}
salas = defaultdict(list)
salas["Geral"] = []


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
    """Escuta conexão com clientes e inicia as threads.

    Args:
        servidor (socket): socket do servidor
    """
    servidor.listen()
    while True:
        cliente, endereco = servidor.accept()
        print(f"Cliente conectado com sucesso. IP {endereco}")

        thread = threading.Thread(target=receber_mensagens, args=(cliente,))
        thread.start()


def receber_mensagens(cliente: socket) -> None:
    """Recebe e processa as mensagens dos clientes.

    Args:
        cliente (socket): socket para comunicação com o cliente
    """

    while True:
        mensagem = cliente.recv(2048).decode(FORMATO_CODIFICACAO)
        if mensagem.startswith("!username"):
            # Conexão inicial, salva username e sala do novo usuário
            username = salvar_usuario_conectado(cliente, mensagem)
            if username:
                vincular_cliente_e_sala_escolhida(cliente, username)
        elif mensagem.startswith("/"):
            # comandos especiais, responsabilidade do bot
            chamar_bot(cliente, mensagem)
        else:
            # mensagens normais
            enviar_mensagem_publica(cliente, mensagem)


def salvar_usuario_conectado(cliente: socket, mensagem: str) -> str | None:
    """Salva o usuário que acabou de conectar na lista de clientes conectados.

    Args:
        cliente (socket): socket para comunicação com o cliente
        mensagem (str): mensagem = '!username:nome_usuario', usada para pegar o usuário

    Returns:
        str: username
    """
    username = pegar_username_escolhido(cliente, mensagem)
    if not username:
        return None
    clientes_conectados[username] = cliente
    enviar_alerta_do_servidor("Conectado com sucesso.", cliente=cliente)
    return username


def pegar_username_escolhido(cliente: socket, mensagem: str) -> str | None:
    """Pega o username do cliente usando a mensagem recebida. Conexão Inicial.

    Args:
        cliente (socket): socket para comunicação com o cliente
        mensagem (str): '!username:nome_usuario', usada para pegar o usuário

    Returns:
        str: username
    """
    username = mensagem.split(":")
    if not username[1]:
        enviar_alerta_do_servidor("Digite um usuário.", cliente=cliente)
        return None
    if username[1] in clientes_conectados:
        enviar_alerta_do_servidor("Usuário já existe.", cliente=cliente)
        return None
    return username[1]


def vincular_cliente_e_sala_escolhida(cliente: socket, username: str) -> None:
    """Vincula o cliente a sala de conversas

    Args:
        cliente (socket): socket para comunicação com o cliente
    """
    sala_escolhida = pegar_sala_escolhida(cliente)
    salas[sala_escolhida].append(username)

    enviar_alerta_do_servidor(
        f"<{username}> entrou no chat.", nome_sala=sala_escolhida, privado=False
    )
    print(salas)


def pegar_sala_escolhida(cliente: socket) -> str:
    """Envia para o cliente as salas disponíveis e pega sua escolha

    Args:
        cliente (socket): socket para comunicação com o cliente

    Returns:
        str: nome da sala escolhida
    """
    salas_disponiveis = "|".join(sala for sala in salas)
    cliente.send(salas_disponiveis.encode(FORMATO_CODIFICACAO))

    sala_escolhida = cliente.recv(25).decode(FORMATO_CODIFICACAO)
    return sala_escolhida


def enviar_mensagem_publica(remetente: socket, mensagem: str) -> None:
    """Envia mensagem para todos os membros da sala do cliente

    Args:
        cliente (socket): socket para comunicação com o cliente
        mensagem (str): mensagem a ser enviada
    """
    username_remetente = pegar_username_do_cliente(remetente)
    sala_do_remetente = pegar_sala_do_cliente(username_remetente)

    for username, cliente in clientes_conectados.items():
        if username in salas[sala_do_remetente] and username != username_remetente:
            cliente.send(
                f"<{username_remetente}> disse: {mensagem}".encode(FORMATO_CODIFICACAO)
            )


def pegar_username_do_cliente(cliente: socket) -> str:
    """Filtra os clientes conectados para pegar o username do cliente.

    Args:
        cliente (socket): socket para comunicação com o cliente

    Returns:
        str: username
    """
    username = next(
        filter(lambda key: clientes_conectados[key] == cliente, clientes_conectados)
    )
    return username


def pegar_sala_do_cliente(username: str) -> str | None:
    """Filtra as salas para achar em qual sala está o username do cliente

    Args:
        username (str): nome do usuario

    Returns:
        str: nome da sala
    """
    for nome_sala in salas:
        if username in salas[nome_sala]:
            return nome_sala
    return None


def enviar_alerta_do_servidor(
    mensagem: str, nome_sala: str = None, cliente: socket = None, privado: bool = True
) -> None:
    """Mensagens de alerta do sistema, enviados de forma privada
       ou publica para os membros de uma determinada sala.

    Args:
        mensagem (str): Mensagem a ser enviada
        nome_sala (str, optional): Nome da sala que receberá o alerta,
                                   caso mensagem publica. Defaults to None.
        cliente (socket, optional): socket do cliente caso mensagem privada. Defaults to None.
        privado (bool, optional): Decide se a mensagem será publica ou privada. Defaults to True.
    """
    if privado:
        cliente.send(mensagem.encode(FORMATO_CODIFICACAO))
    else:
        for username, cliente_conectado in clientes_conectados.items():
            if username in salas[nome_sala]:
                cliente_conectado.send(mensagem.encode(FORMATO_CODIFICACAO))


def chamar_bot(cliente, mensagem):
    print("bot aqui")


def main() -> None:
    """Inicia o programa"""
    servidor = iniciar_servidor()
    aceitar_conexao_cliente(servidor)


if __name__ == "__main__":
    main()
