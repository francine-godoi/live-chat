""" Servidor de chat em tempo real usando socket """

import socket
import threading
from collections import defaultdict
from datetime import datetime

import comandos_especiais as cmd_esp
from database import salvar_historico_chat, limpar_historico


FORMATO_CODIFICACAO = "utf-8"
HOST = "127.0.0.1"
PORT = 9999

clientes_conectados = {}
moderadores = {}
banidos = defaultdict(list)
salas = defaultdict(list)
salas["Geral"] = []


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
        enviar_mensagem_privada("Digite um usuário.", cliente)
        return None
    if username[1] in clientes_conectados:
        enviar_mensagem_privada("Usuário já existe.", cliente)
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
    enviar_mensagem_privada("Conectado com sucesso.", cliente)
    return username


def enviar_salas_disponiveis(cliente: socket, username: str) -> None:
    """Envia para o cliente as salas disponíveis"""

    salas_disponiveis = "|".join(sala for sala in salas if username not in banidos[sala])
    cliente.send(salas_disponiveis.encode(FORMATO_CODIFICACAO))


def pegar_sala_escolhida(cliente: socket, username: str) -> str:
    """Pega sala escolhida

    Returns:
        str: nome da sala escolhida
    """
    enviar_salas_disponiveis(cliente, username)

    sala_escolhida = cliente.recv(25).decode(FORMATO_CODIFICACAO)
    return sala_escolhida


def adicionar_moderador_sala(sala: str, username: str) -> None:
    """Caso a sala não exista, o usuário a criou e portanto será seu moderador"""

    if sala not in salas:
        moderadores[username] = sala


def vincular_cliente_e_sala_escolhida(cliente: socket, username: str) -> None:
    """Vincula o cliente a sala de conversas"""

    sala_escolhida = pegar_sala_escolhida(cliente, username)
    if username in banidos[sala_escolhida]:
        enviar_mensagem_privada('Você foir banido dessa sala.', cliente)
        clientes_conectados[username].close()
        return
    adicionar_moderador_sala(sala_escolhida, username)
    salas[sala_escolhida].append(username)

    enviar_mensagem_publica(
        f"<{username}> entrou no chat.", sala_escolhida, remetente="Servidor"
    )


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


def enviar_mensagem_publica(mensagem: str, sala_remetente: str, remetente: str) -> None:
    """Envia mensagem para todos os membros da sala do cliente"""

    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')
    mensagem_formatada = f"[{timestamp}] <{remetente}> disse: {mensagem}"

    for username, cliente in clientes_conectados.items():
        if username in salas[sala_remetente] and username != remetente:
            cliente.send(mensagem_formatada.encode(FORMATO_CODIFICACAO))

    salvar_historico_chat(sala_remetente, mensagem_formatada)


def enviar_mensagem_privada(mensagem: str, cliente: socket) -> None:
    """Mensagem enviados de forma privada"""

    cliente.send(mensagem.encode(FORMATO_CODIFICACAO))


def processar_comando_bot(
    comando: str,
    destinatario_cmd: str,
    texto_da_mensagem: str,
    sala_remetente: str,
    remetente_cmd: str,
) -> str:
    """Processa os comandos enviados pelo usuário e os envia para a função que o executará

    Args:
        comando (str): comando que o usuário enviou
        destinatario_cmd (str): usuário que será afetado pelo comando
        texto_da_mensagem (str): mensagem enviada pelo usuário
        sala_remetente (str): sala de quem enviou o comando
        remetente_cmd (str): quem enviou o comando

    Returns:
        str: mensagem do bot depois de processar o comando
    """

    match comando:
        case "/ajuda":
            resposta = cmd_esp.ajuda()
        case "/banir":
            resposta = cmd_esp.banir(banidos, destinatario_cmd, sala_remetente, remetente_cmd, moderadores, salas, clientes_conectados)
        case '/expulsar':
            resposta = cmd_esp.expulsar(destinatario_cmd, sala_remetente, remetente_cmd, moderadores, salas, clientes_conectados)        
        case "/historico":
            resposta = cmd_esp.historico(sala_remetente)
        case "/hora":
            resposta = cmd_esp.hora()
        case '/nome':
            if destinatario_cmd in clientes_conectados:
                return 'Usuário já existe'
            resposta = cmd_esp.nome(remetente_cmd, destinatario_cmd, clientes_conectados, salas[sala_remetente], moderadores)
        case "/ping":
            resposta = cmd_esp.ping()
        case "/privado":
            resposta = cmd_esp.privado(
                remetente_cmd,
                destinatario_cmd,
                clientes_conectados,
                texto_da_mensagem, 
                destinatario_cmd, 
                salas[sala_remetente]
            )            
        case "/sair":                        
            resposta = cmd_esp.sair(
                remetente_cmd, salas[sala_remetente], moderadores, clientes_conectados
            )
        case "/stats":
            resposta = cmd_esp.stats(sala_remetente)
        case "/usuarios":
            resposta = cmd_esp.usuarios(salas[sala_remetente])
        case _:
            resposta = "Comando inválido"

    return resposta


def processar_respostas_bot(resposta: str,  destinatario_cmd: str, remetente_cmd: str, sala: str, cliente: socket):
    if resposta == 'banido' :
        enviar_mensagem_publica(f'{destinatario_cmd} foi banido da sala', sala, 'bot')
    elif resposta == 'enviado':
        enviar_mensagem_privada(f'<bot> disse: Mensagem privada enviada com sucesso para {destinatario_cmd}.', cliente)
    elif resposta == 'expulso' :
        enviar_mensagem_publica(f'{destinatario_cmd} foi expulso da sala', sala, 'bot')
    elif resposta == 'nome':
        enviar_mensagem_publica(f'<bot> disse: {remetente_cmd} agora se chama {destinatario_cmd}.', sala, 'bot')
    elif resposta.find("saiu da sala") > 0:
        enviar_mensagem_publica(resposta, sala, "bot")
    else:
        enviar_mensagem_privada(f'<bot> disse: {resposta}', cliente)


def chamar_bot(cliente: socket, mensagem: str) -> None:
    """Envia a mensagem com o comando para o bot precessar"""

    comando, destinatario_cmd, texto_da_mensagem = cmd_esp.extrair_dados_da_mensagem(
        mensagem
    )
    remetente_cmd = pegar_username_do_cliente(cliente)
    sala_remetente = pegar_sala_do_cliente(remetente_cmd)

    resposta = processar_comando_bot(
        comando, destinatario_cmd, texto_da_mensagem, sala_remetente, remetente_cmd
    )
    processar_respostas_bot(resposta, destinatario_cmd, remetente_cmd, sala_remetente, cliente)



def processar_mensagens(mensagem: str, cliente: socket):
    """Envia a mensagem para a função adequada"""

    if mensagem.startswith("!username"):
        # Conexão inicial, salva username e sala do novo usuário
        username = salvar_usuario_conectado(cliente, mensagem)
        if username:
            vincular_cliente_e_sala_escolhida(cliente, username)
    elif mensagem == "!bot!":
        # Salva os dados de conexão do bot
        clientes_conectados[mensagem] = cliente
    elif mensagem.startswith("/"):
        # Comandos especiais, responsabilidade do bot
        chamar_bot(cliente, mensagem)
    else:
        # Mensagens normais
        remetente = pegar_username_do_cliente(cliente)
        sala_do_remetente = pegar_sala_do_cliente(remetente)
        enviar_mensagem_publica(mensagem, sala_do_remetente, remetente)


def receber_mensagens(cliente: socket) -> None:
    """Recebe e processa as mensagens dos clientes."""

    while True:
        try:
            mensagem = cliente.recv(2048).decode(FORMATO_CODIFICACAO)
        except Exception as e:
            cliente.close()    
            break    
        processar_mensagens(mensagem, cliente)


def aceitar_conexao_cliente(servidor: socket) -> None:
    """Escuta conexão com clientes e inicia as threads."""

    servidor.listen()
    while True:
        cliente, endereco = servidor.accept()
        print(f"Cliente conectado com sucesso. IP {endereco}")

        thread = threading.Thread(target=receber_mensagens, args=(cliente,))
        thread.start()


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
        exit(0)
    except Exception as e:
        print(f"Um erro ocorreu ao tentar iniciar o servidor: {e}")
        exit(0)

    return servidor


def main() -> None:
    """Inicia o programa"""

    servidor = iniciar_servidor()
    limpar_historico()
    aceitar_conexao_cliente(servidor)


if __name__ == "__main__":
    main()
