import socket
import threading

HOST = "127.0.0.1"
PORT = 9999
FORMATO_CODIFICACAO = "utf-8"


def conectar_servidor():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        cliente.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("Não foi possível conectar com o servidor.")
    except Exception as e:
        print(f"Um erro ocorreu ao tentar conectar com o servidor: {e}")

    return cliente


def escolher_username(cliente):
    mensagem = ""
    while mensagem != "Conectado com sucesso.":
        username = input("Usuário: ")
        cliente.send(f"!username:{username}".encode(FORMATO_CODIFICACAO))
        mensagem = cliente.recv(2048).decode(FORMATO_CODIFICACAO)
        print(mensagem)


def enviar_mensagem(cliente):
    while True:
        mensagem = input()
        cliente.send(mensagem.encode(FORMATO_CODIFICACAO))


def receber_mensagem(cliente):
    while True:
        mensagem = cliente.recv(2048).decode(FORMATO_CODIFICACAO)
        print(mensagem)


def main():
    cliente = conectar_servidor()
    escolher_username(cliente)

    thread_receber_mensagem = threading.Thread(target=receber_mensagem, args=(cliente,))
    thread_enviar_mensagem = threading.Thread(target=enviar_mensagem, args=(cliente,))

    thread_receber_mensagem.start()
    thread_enviar_mensagem.start()


if __name__ == "__main__":
    main()
