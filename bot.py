""" Bot para chat em tempo real usando socket """

import socket
import threading
from datetime import datetime

# Temporário, até implementar persistencia
from servidor import clientes_conectados, salas, moderadores

HOST = "127.0.0.1"
PORT = 9999
FORMATO_CODIFICACAO = "utf-8"


def enviar_resposta_servidor(mensagem, bot):
    """Envia mensagem do bot após processar o comando enviado pelo usuário"""
    bot.send(mensagem.encode(FORMATO_CODIFICACAO))


def ajuda(bot: socket) -> None:
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
    enviar_resposta_servidor(comandos, bot)


def historico(sala, bot):
    """mostra histórico do chat."""
    pass


def hora(bot):
    """mostra a hora atual."""
    horas = datetime.now().strftime("%H:%M")
    enviar_resposta_servidor(horas, bot)


def nome(nome_atual, novo_nome, sala, bot):
    """Para alterar o nome de exibição do usuário."""
    if novo_nome in clientes_conectados:
        enviar_resposta_servidor("Username já existe", bot)
        # TODO Testar com usernames que já existem

    clientes_conectados[novo_nome] = clientes_conectados[nome_atual]
    del clientes_conectados[nome_atual]

    salas[sala].remove(nome_atual)
    salas[sala].append(novo_nome)

    if nome_atual in moderadores:
        moderadores[novo_nome] = moderadores[nome_atual]
        del moderadores[nome_atual]

    enviar_resposta_servidor(f"{nome_atual} agora se chama {novo_nome}", bot)


def ping(bot):
    """o bot responde com "pong" para testar a conectividade."""
    enviar_resposta_servidor("pong", bot)


def privado(destinatario, mensagem, bot):
    """envia mensagem privada."""
    resposta = f"para:{destinatario}|{mensagem}"
    enviar_resposta_servidor(resposta, bot)


def sair(username, sala, bot):
    """Para desconectar do chat."""
    del clientes_conectados[username]
    salas[sala].remove(username)
    enviar_resposta_servidor(f"sair|{username} sai da sala.", bot)


def stats(username, sala, bot):
    """Mostrar informações do chat:
    número total de mensagens enviadas,
    tempo total de atividade do chat,
    usuários mais ativos."""
    pass


def usuarios(sala, bot):
    """Para listar todos os usuários conectados."""
    mensagem = "\n".join(usuario for usuario in salas[sala])
    enviar_resposta_servidor(mensagem, bot)


def banir(username, nome_usuario, sala, bot):
    """Desconecta usuário e o adiciona a uma lista de clientes que não podem acessar a sala."""
    pass


def expulsar(username, nome_usuario, sala, bot):
    """Desconecta usuário da sala, mas usuario pode voltar ao chat."""
    pass


def extrair_dados_da_mensagem(informacao: str) -> tuple:
    """Separa as informações da mensagem

    Returns:
        tuple: username, sala, Comando, Usuário afetado pelo comando, Texto da mensagem(se tiver)
    """
    info_usuario, mensagem = informacao.split("|")
    cliente, sala = info_usuario.split(":")

    if mensagem.find(" ") == -1:
        # Se não tem espaço, a mensagem é o comando
        comando = informacao
        nome_usuario = ""
        texto_da_mensagem = ""
    else:
        # Caso tenha espaço, o comando tem argumentos
        comando, nome_usuario, *texto_da_mensagem = informacao.split(" ")
        texto_da_mensagem = " ".join(texto_da_mensagem)

    return (cliente, sala, comando, nome_usuario, texto_da_mensagem)


def processar_comando(mensagem: str, bot: socket) -> None:
    """Envia o comando para a função responsável por sua execução"""
    cliente, sala, comando, nome_usuario, texto_da_mensagem = extrair_dados_da_mensagem(
        mensagem
    )

    match comando:
        case "/ajuda":
            ajuda(bot)
        case "/banir":
            banir(cliente, nome_usuario, sala, bot)
        case "/expulsar":
            expulsar(cliente, nome_usuario, sala, bot)
        case "/historico":
            historico(sala, bot)
        case "/hora":
            hora(bot)
        case "/nome":
            nome(cliente, nome_usuario, sala, bot)
        case "/ping":
            ping(bot)
        case "/privado":
            privado(nome_usuario, texto_da_mensagem, bot)
        case "/sair":
            sair(cliente, sala, bot)
        case "/stats":
            stats(cliente, sala, bot)
        case "/usuarios":
            usuarios(sala, bot)
        case _:
            enviar_resposta_servidor("Comando inválido", bot)


def receber_comando(bot: socket) -> None:
    """Recebe comando enviado pelo cliente"""

    while True:
        comando = bot.recv(1024).decode(FORMATO_CODIFICACAO)
        processar_comando(comando, bot)


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
    """Inicia o bot"""
    bot = conectar_servidor()

    thread_receber_comando = threading.Thread(target=receber_comando, args=(bot,))
    thread_receber_comando.start()


if __name__ == "__main__":
    main()
