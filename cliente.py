""" Client de chat em tempo real usando socket """

import socket
import threading

HOST = "127.0.0.1"
PORT = 9999
FORMATO_CODIFICACAO = "utf-8"


def conectar_servidor() -> socket:
    """Conexão com o servidor

    Returns:
        socket: socket de comunicação com o servidor
    """
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        cliente.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("Não foi possível conectar com o servidor.")
    except Exception as e:
        print(f"Um erro ocorreu ao tentar conectar com o servidor: {e}")

    return cliente


def escolher_username(cliente: socket) -> None:
    """Pede para o usuario escolher um username para usar no chat

    Args:
        cliente (socket): socket para comunicação com o servidor
    """
    mensagem = ""
    while mensagem != "Conectado com sucesso.":
        username = ""
        while not username:
            username = input("Usuário: ").strip()
        cliente.send(f"!username:{username}".encode(FORMATO_CODIFICACAO))
        mensagem = cliente.recv(22).decode(FORMATO_CODIFICACAO)
        print(mensagem)


def escolher_sala(cliente: socket, salas: str) -> None:
    """Pede para o usuário escolher ou criar uma sala

    Args:
        cliente (socket): socket para comunicação com o servidor
        salas (str): lista de salas disponíveis para escolha
    """
    print("Salas disponíveis:")
    salas_disponiveis = salas.split("|")
    for sala in salas_disponiveis:
        print(f"\t{sala}")

    while True:
        nome_sala = (
            input("Digite o nome da sala para entrar ou 'criar' para criar nova sala: ")
            .capitalize()
            .strip()
        )
        if nome_sala in salas_disponiveis:
            break
        if nome_sala == "Criar":
            nome_sala = ""
            while not nome_sala:
                nome_sala = input("Nome da nova sala: ").capitalize().strip()
            break
    cliente.send(nome_sala.encode(FORMATO_CODIFICACAO))


def enviar_mensagem(cliente: socket) -> None:
    """Envia as mensagens do cliente para o servidor

    Args:
        cliente (socket): socket para comunicação com o servidor
    """
    while True:
        mensagem = ""
        while not mensagem:
            # '!username:nome_usuario' é usado na conexão inicial com cliente
            mensagem = input().strip().replace("!username:", "")
        cliente.send(mensagem.encode(FORMATO_CODIFICACAO))


def receber_mensagem(cliente: socket) -> None:
    """Recebe mensagens do servidor e exibe no terminal

    Args:
        cliente (socket): socket para comunicação com o servidor
    """
    while True:
        mensagem = cliente.recv(2048).decode(FORMATO_CODIFICACAO)
        print(mensagem)


def main() -> None:
    """Inicia o programa"""

    cliente = conectar_servidor()
    escolher_username(cliente)
    salas = cliente.recv(2048).decode(FORMATO_CODIFICACAO)
    escolher_sala(cliente, salas)

    thread_receber_mensagem = threading.Thread(target=receber_mensagem, args=(cliente,))
    thread_enviar_mensagem = threading.Thread(target=enviar_mensagem, args=(cliente,))

    thread_receber_mensagem.start()
    thread_enviar_mensagem.start()


if __name__ == "__main__":
    main()
