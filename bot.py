"""
Bot inicia com server
Verificar falta de conexão 
Server chama bot com cliente e msg
Server manda msg bot
Recebe msg server
Processa comando
Envia msg server
Server manda PM client
Verificar como faz !privado
"""

import socket
import threading

HOST = "127.0.0.1"
PORT = 9999
FORMATO_CODIFICACAO = "utf-8"


def sair():
    """Para desconectar do chat."""
    pass


def ajuda():
    """Para listar os comandos disponíveis."""
    pass


def usuarios():
    """Para listar todos os usuários conectados."""
    pass


def nome(novo_nome):
    """Para alterar o nome de exibição do usuário."""
    pass


def privado(nome_usuario, mensagem):
    """envia mensagem privada."""
    pass


def historico():
    """mostra histórico do chat."""
    pass


def hora():
    """mostra a hora atual."""
    pass


def ping():
    """o bot responde com "pong" para testar a conectividade."""
    pass


def stats():
    """Mostrar informações do chat:
    número total de mensagens enviadas,
    tempo total de atividade do chat,
    usuários mais ativos."""
    pass


def banir(nome_usuario):
    """Desconecta usuário e o adiciona a uma lista de clientes que não podem acessar a sala."""
    pass


def expulsar(nome_usuario):
    """Desconecta usuário da sala, mas usuario pode voltar ao chat."""
    pass


def extrair_dados_da_mensagem(mensagem: str) -> tuple:
    """Separa as informações da mensagem

    Returns:
        tuple: Comando, Usuário afetado pelo comando, Texto da mensagem(se tiver)
    """

    if mensagem.find(" ") == -1:
        # Se não tem espaço, a mensagem é o comando
        comando = mensagem
        usuario = ""
        texto_da_mensagem = ""
    else:
        # Caso tenha espaço, o comando tem argumentos
        comando, usuario, *texto_da_mensagem = mensagem.split(" ")
        texto_da_mensagem = " ".join(texto_da_mensagem)

    return (comando, usuario, texto_da_mensagem)


def processar_comando(mensagem: str) -> None:
    """Envia o comando para a função responsável por sua execução"""
    comando, usuario_afetado, texto_da_mensagem = extrair_dados_da_mensagem(mensagem)

    match comando:
        case "/ajuda":
            ajuda()
        case "/banir":
            banir(usuario_afetado)
        case "/expulsar":
            expulsar(usuario_afetado)
        case "/historico":
            historico()
        case "/hora":
            hora()
        case "/nome":
            nome(usuario_afetado)
        case "/ping":
            ping()
        case "/privado":
            privado(usuario_afetado, texto_da_mensagem) #TODO ver como mandar a mensagem privada
        case "/sair":
            sair() #TODO: ver como pega o usuario que quer sair
        case "/stats":
            stats() #TODO ver como pega a sala onde a conversa está acontecendo
        case "/usuarios":
            usuarios() #TODO ver como pega a sala onde a conversa está acontecendo
        case _:
            pass


def receber_comando(bot) -> None:
    """Recebe comando enviado pelo cliente"""

    while True:
        comando = bot.recv(1024).decode(FORMATO_CODIFICACAO)
        processar_comando(comando)


def conectar_servidor() -> socket:
    """Conexão com o servidor

    Returns:
        socket: socket de comunicação com o servidor
    """
    bot = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        bot.connect((HOST, PORT))
        bot.send("!bot!".encode(FORMATO_CODIFICACAO))
    except ConnectionRefusedError:
        print("Não foi possível conectar com o servidor.")
    except Exception as e:
        print(f"Um erro ocorreu ao tentar conectar com o servidor: {e}")

    return bot


def main():
    bot = conectar_servidor()

    thread_receber_comando = threading.Thread(target=receber_comando, args=(bot,))
    thread_receber_comando.start()


if __name__ == "__main__":
    main()
