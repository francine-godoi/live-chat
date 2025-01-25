import socket
import threading

HOST = "127.0.0.1"
PORT = 9998

clientes_conectados = {'fran':(1,1)}

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
        print(f'Cliente conectado com sucesso. IP {endereco}')

        #clientes_conectados.append(cliente)

        thread = threading.Thread(target=receber_mensagens, args=(cliente,))
        thread.start()

def receber_mensagens(cliente):
    while True:
        mensagem = cliente.recv(2048).decode('utf-8')
        if mensagem.startswith('!username'):
            username = mensagem.split(':')
            if existe_usuario(username[1]):
                enviar_mensagem_privada(cliente,'Usuário já existe.')
            else:                           
                clientes_conectados = {username[1] : cliente}
                enviar_mensagem_privada(cliente, 'Conectado') 


def existe_usuario(username):
    return username in clientes_conectados
    

def enviar_mensagem_publica():
    pass


def enviar_mensagem_privada(cliente, mensagem):
    cliente.send(mensagem.encode('utf-8'))


def desconectar_cliente():
    pass


def chamar_bot():
    pass


def main():
    servidor = iniciar_servidor()
    aceitar_conexao_cliente(servidor)    


if __name__ == "__main__":
    main()
