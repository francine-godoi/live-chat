# 🗫 Chat em tempo real com socket 🗫

## 📋 Descrição

Terceiro projeto (via terminal) aplicando conceitos vistos durante minha jornada para aprender Python:

    1. Lógica de programação
    2. Socket
    3. Threading
    4. Manipulação de arquivos    
---
## 📝 Requisitos do Sistema / Funcionalidades

### 🌐 Tarefas do Servidor:
- Criar um socket e fazer com que ele escute em uma porta.
- Aceitar conexões de clientes.
- Criar uma lista/dict de clientes conectados no servidor.
- Criar uma lista de salas disponíveis e seus respectivos moderadores/administradores 
- Mensagem publica: Receber e repassar as mensagens para todos os outros clientes da mesma sala.
- Mensagem privada: Identificar qual cliente deve receber a mensagem e garantir que apenas o destinatário a receba.
---
### 🖥️ Tarefas do Cliente:
- Criar um socket e conectar-se ao servidor.
- Enviar as mensagens que o usuário digitar.
- Ouvir as mensagens que o servidor enviar e exibi-las no terminal.
---
### 🤖 Tarefas do Bot:
- Processar as mensagens que o cliente envia e realizar os comandos solicitados, se tiver algum.
---
### ✅ Funcionalidades:
1. Identificação dos usuários: Cada cliente pode se identificar com um nome.
2. Criação de Salas de Chat: Permitir que os usuários entrem ou criem "salas" de conversa, onde apenas os usuários da sala podem ver as mensagens. 	
3. Notificações de Conexão e Desconexão: Avisar os usuários sempre que alguém entrar ou sair do chat.
4. Mensagens com Data e Hora: Adicionar a data e a hora às mensagens enviadas.
5. Mensagens Privadas: Permitir que os usuários enviem mensagens privadas apenas para o cliente específico.
6. Armazenamento de mensagens: O servidor pode manter um histórico de mensagens, e os clientes podem solicitar para ver as mensagens anteriores.
7. Bot do Chat: Adicionar um bot no chat que responda automaticamente a comandos que alteram o comportamento do chat.
    - Comandos Especiais:
      - /sair: Para desconectar do chat.
      - /help: Para listar os comandos disponíveis.
      - /usuarios: Para listar todos os usuários conectados.
      - /nome novo_nome: Para alterar o nome de exibição do usuário.
      - /privado nome_usuario mensagem: envia mensagem privada.
      - /historico: mostra histórico do chat.
      - /hora: mostra a hora atual.
      - /ping: o bot responde com "pong" para testar a conectividade.
      - /stats: Mostrar informações do chat: número total de mensagens enviadas, tempo total de atividade do chat, usuários mais ativos.
    - Comandos de Administrador/Moderador: 
      - /banir nome_usuario: Desconecta usuário e o adiciona a uma lista de clientes que não podem acessar a sala.
      - /expulsar nome_usuario: Desconecta usuário da sala, mas usuario pode voltar ao chat.
---

## ⚠️ Restrições, Tratamento de Erros e Fechamento das Conexões:
- O nome de usuário deve ser único.
- As mensagens são enviadas apenas para os membros da mesma sala.
- Desconexão: Quando desconectar o cliente deve ser removido da lista de clientes ativos e o servidor deve fechar a conexão.              
- Erros de comunicação: O servidor e o cliente devem verificar se as conexões falharam e tratar adequadamente.
- Fechamento de sockets: Após o fim da comunicação, tanto o servidor quanto o cliente devem fechar seus sockets.

-------
