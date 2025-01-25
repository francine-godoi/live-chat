import socket
import threading

HOST = '127.0.0.1'
PORT = 9998

def enviar_mensagem(cliente):
    while True:
        mensagem = input('Mensagem: ')
        cliente.send(mensagem.encode('utf-8'))


def receber_mensagem(cliente):
    while True:
        mensagem = cliente.recv(2048).decode('utf-8')
        print(mensagem)

def conectar_servidor():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        cliente.connect((HOST, PORT))
    except ConnectionRefusedError:
        print('Não foi possível conectar com o servidor')
    except Exception as e:
        print(f'Um erro ocorreu ao tentar conectar com o servidor: {e}')

    return cliente

def main():
    cliente = conectar_servidor()
    while True:
        username = input('Usuário: ')
        cliente.send(f'!username:{username}'.encode('utf-8'))
        msg = cliente.recv(2048).decode('utf-8')        
        if msg == 'Conectado':
            print('Conectado com sucesso.')
            break
        else:
            print(msg)
    
    thread_receber_mensagem = threading.Thread(target=receber_mensagem, args=(cliente,))
    thread_enviar_mensagem = threading.Thread(target=enviar_mensagem, args=(cliente,))

    thread_enviar_mensagem.start()
    thread_receber_mensagem.start()

if __name__ == '__main__':
    main()