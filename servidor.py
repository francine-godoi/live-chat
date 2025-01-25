import socket
import threading

HOST = "127.0.0.1"
PORT = 9999
FORMATO_CODIFICACAO = "utf-8"

clientes_conectados = {}


def iniciar_servidor():
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


def aceitar_conexao_cliente(servidor):
    servidor.listen()
    while True:
        cliente, endereco = servidor.accept()
        print(f"Cliente conectado com sucesso. IP {endereco}")

        thread = threading.Thread(target=receber_mensagens, args=(cliente,))
        thread.start()


def receber_mensagens(cliente):
    while True:
        mensagem = cliente.recv(2048).decode(FORMATO_CODIFICACAO)
        if mensagem.startswith("!username"):
            adicionar_usuario(cliente, mensagem)
        elif mensagem.startswith("/"):
            chamar_bot(cliente, mensagem)
        else:
            enviar_mensagem_publica(cliente, mensagem)


def adicionar_usuario(cliente, mensagem):
    username = mensagem.split(":")
    if existe_usuario(username[1]):
        enviar_alerta_do_servidor('Usuário já existe.', cliente)
        return

    clientes_conectados[username[1]] = cliente
    enviar_alerta_do_servidor('Conectado com sucesso.', cliente)
    enviar_alerta_do_servidor(f'<{username[1]}> entrou no chat.', privado=False)


def existe_usuario(username):
    return username in clientes_conectados


def enviar_mensagem_publica(remetente, mensagem):
    for usuario, cliente in clientes_conectados.items():
        if cliente != remetente:
            cliente.send(f"<{usuario}> disse: {mensagem}".encode(FORMATO_CODIFICACAO))


def enviar_alerta_do_servidor(mensagem, cliente=None, privado=True):
    if privado:
        cliente.send(mensagem.encode(FORMATO_CODIFICACAO))
    else:
        for cliente in clientes_conectados.values():
            cliente.send(mensagem.encode(FORMATO_CODIFICACAO))


def desconectar_cliente():
    pass


def chamar_bot(cliente, mensagem):
    print("bot aqui")


def main():
    servidor = iniciar_servidor()
    aceitar_conexao_cliente(servidor)


if __name__ == "__main__":
    main()
