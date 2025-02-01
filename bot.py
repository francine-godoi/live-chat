"""Bot que lida com comandos especiais do servidor"""

from datetime import datetime
from collections import defaultdict, Counter
from database import pegar_historico_chat


def ajuda() -> None:
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
    return comandos


def banir(
    banidos: defaultdict,
    destinatario_cmd: str,
    sala_remetente: str,
    remetente_cmd: str,
    moderadores: defaultdict,
    salas: defaultdict,
    clientes_conectados: dict,
) -> str:
    """Bani um usuário de uma determinada sala
       desde que quem usou o comando seja o moderador da sala

    Args:
        banidos (defaultdict): list de todos os usuários banidos
        destinatario_cmd (str): quem será afetado pelo comando
        sala_remetente (str): sala de quem usou o comando
        remetente_cmd (str): quem usou o comando
        moderadores (defaultdict): lista de todos os moderadores
        salas (defaultdict): lista de todas as salas disponíveis
        clientes_conectados (dict): lista de todos os cliente conectados

    Returns:
        str: resposta após a execução do comando
    """
    if destinatario_cmd == remetente_cmd:
        return "Você não pode banir você mesmo"

    if (
        remetente_cmd not in moderadores
        or destinatario_cmd not in salas[sala_remetente]
    ):
        return "Apenas moderadores podem banir usuários de sua sala"
    clientes_conectados[destinatario_cmd].send(
        "<bot> disse: Você foi banido dessa sala.".encode("utf-8")
    )
    clientes_conectados[destinatario_cmd].close()
    sair(destinatario_cmd, salas[sala_remetente], moderadores, clientes_conectados)
    banidos[sala_remetente] = destinatario_cmd
    return "banido"


def expulsar(
    destinatario_cmd: str,
    sala_remetente: str,
    remetente_cmd: str,
    moderadores: defaultdict,
    salas: defaultdict,
    clientes_conectados: dict,
) -> str:
    """Expulsa um usuário de uma determinada sala desde que
        quem usou o comando seja o moderador da sala

    Args:
        destinatario_cmd (str): quem será afetado pelo comando
        sala_remetente (str): sala de quem usou o comando
        remetente_cmd (str): quem usou o comando
        moderadores (defaultdict): lista de moderadores
        salas (defaultdict): lista de salas disponíveis
        clientes_conectados (dict): lista de clientes conectados

    Returns:
        str: resposta após a execução do comando
    """
    if destinatario_cmd == remetente_cmd:
        return "Você não pode expulsar você mesmo"

    if (
        remetente_cmd not in moderadores
        or destinatario_cmd not in salas[sala_remetente]
    ):
        return "Apenas moderadores podem expulsar usuários de sua sala"
    clientes_conectados[destinatario_cmd].send(
        "<bot> disse: Você foi expulso dessa sala.".encode("utf-8")
    )
    sair(destinatario_cmd, salas[sala_remetente], moderadores, clientes_conectados)
    return "expulso"


def historico(sala) -> str:
    """mostra histórico do chat."""
    chat = pegar_historico_chat(sala)
    return f'\n{"".join(f"\t{linha}" for linha in chat)}'


def hora() -> str:
    """mostra a hora atual."""
    horas = datetime.now().strftime("%H:%M")
    return horas


def nome(
    nome_atual: str,
    novo_nome: str,
    clientes_conectados: dict,
    sala: list,
    moderadores: dict,
) -> str:
    """Altera o nome de usuario"""
    clientes_conectados[novo_nome] = clientes_conectados[nome_atual]
    del clientes_conectados[nome_atual]
    sala.remove(nome_atual)
    sala.append(novo_nome)
    if nome_atual in moderadores:
        moderadores[novo_nome] = moderadores[nome_atual]
        del moderadores[nome_atual]
    return "nome"


def ping() -> str:
    """o bot responde com "pong" para testar a conectividade."""
    return "pong"


def privado(
    remetente: str,
    destinatario: str,
    clientes_conectados: dict,
    mensagem: str,
    destinatario_cmd: str,
    sala_remetente,
) -> str:
    """envia mensagem privada."""
    if destinatario_cmd not in sala_remetente:
        return "Remetente não se encontra na sala"
    clientes_conectados[destinatario_cmd].send(
        f"<{remetente}> disse: @{destinatario} {mensagem}".encode("utf-8")
    )
    return "enviado"


def sair(
    username: str, sala: defaultdict, moderadores: dict, clientes_conectados: dict
) -> str:
    """Para desconectar do chat."""
    clientes_conectados[username].close()
    del clientes_conectados[username]
    sala.remove(username)
    if username in moderadores:
        del moderadores[username]

    return f"{username} saiu da sala."


def stats(sala) -> str:
    """Mostrar informações do chat:
    número total de mensagens enviadas,
    tempo total de atividade do chat,
    usuários mais ativos."""

    conversa = pegar_historico_chat(sala)
    total_mensagens = len(conversa)

    # exemplo do timestamp = [31/01/2025 15:39]
    inicio = conversa[0][1:17]  # timestamp da primeira linha do chat
    fim = conversa[total_mensagens - 1][1:17]  # timestamp da ultima linha do chat

    horario_inicio = datetime.strptime(inicio, "%d/%m/%Y %H:%M")
    horario_fim = datetime.strptime(fim, "%d/%m/%Y %H:%M")

    lista_usuarios = []
    for linha in conversa:
        inicio_tag_usuario = linha.find("<")
        final_tag_usuario = linha.find(">")
        usuario = linha[inicio_tag_usuario + 1 : final_tag_usuario]
        lista_usuarios.append(usuario)

    contagem = Counter(lista_usuarios).most_common()
    atividade_usuarios = "\n".join(
        f"\t\t<{usuario}> mandou {qtde} mensagens" for usuario, qtde in contagem
    )

    mensagem = f"""Estatisticas da Conversa:\n
        Total de mensagens: {total_mensagens}\n
        Duração da conversa: {horario_fim - horario_inicio}\n
        Atividades dos usuários:\n{atividade_usuarios}\n
        Usuário mais ativo: <{contagem[0][0]}>
    """

    return mensagem


def usuarios(sala) -> str:
    """Para listar todos os usuários conectados."""
    return "\n".join(f"\t{usuario}" for usuario in sala)


def extrair_dados_da_mensagem(mensagem: str) -> tuple:
    """Separa as informações da mensagem

    Returns:
        tuple: cliente, sala, Comando, Usuário afetado pelo comando, Texto da mensagem(se tiver)
    """
    if mensagem.find(" ") == -1:
        # Se não tem espaço, a mensagem é o comando
        comando = mensagem
        nome_usuario = ""
        texto_da_mensagem = ""
    else:
        # Caso tenha espaço, o comando tem argumentos
        comando, nome_usuario, *texto_da_mensagem = mensagem.split(" ")
        texto_da_mensagem = " ".join(texto_da_mensagem)

    return (comando, nome_usuario, texto_da_mensagem)
