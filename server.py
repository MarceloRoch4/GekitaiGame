#Server

import tkinter, socket, threading, json
from tkinter import DISABLED, VERTICAL, END, NORMAL


#Definir uma janela

root = tkinter.Tk()
root.title("Chat Server")
root.iconbitmap("imagens/message_icon.ico")
root.geometry('600x600')
root.resizable(0,0)

#Definir fonts e cores

minha_fonte = ('SimSun', 14)
preto = "#010101"
verde_claro = "#1fc742"
root.config(bg=preto)



# Criar uma classe de conexão para segurar nosso server socket
class Conexao():
    ''' Uma classe para segurar uma conexão - um server socket e uma informação pertinente '''
    def __init__(self):
        self.host_ip = socket.gethostbyname(socket.gethostname())
        self.encodificador = 'utf-8'
        self.bytetam = 1024

        self.client_sockets = []  
        self.client_ips = []
        self.banidos_ip = []


#Definir funções
def iniciar_servidor(conexao):
    ''' Inicie o server quando receber um número de porta '''
    # Pegue o numero do porta para rodar o server
    conexao.port = int(port_entry.get())

    #Criar um server socket
    conexao.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #IPv4 e TCP
    conexao.server_socket.bind((conexao.host_ip, conexao.port))
    conexao.server_socket.listen()


    # Atualizar o GUI
    historico_listbox.delete(0, END)
    historico_listbox.insert(END, f"Servidor iniciou na porta {conexao.port}.")
    desconectar_button.config(state=NORMAL)
    input_entry.config(state=NORMAL)
    self_broadcast_button.config(state=NORMAL)
    pm_button.config(state=NORMAL)
    expulsar_button.config(state=NORMAL)
    banir_button.config(state=NORMAL)
    iniciar_button.config(state=DISABLED)

    #criar thread para continuar escutando
    conectar_thread = threading.Thread(target=conectar_client, args=(conexao, ))
    conectar_thread.start()




def encerrar_servidor(conexao):
    ''' Iniciar o processo de encerrar o servidor '''
    #enviar para todos q o servidor está fechando
    mensagem_pacote = criar_mensagem("DESCONECTAR", "Admin (transmitir)", "Servidor está fechando...", verde_claro)
    mensagem_json = json.dumps(mensagem_pacote)
    transmitir_mensagem(conexao, mensagem_json.encode(conexao.encodificador))


    # Atualizar o GUI
    historico_listbox.insert(END, f"Servidor fechou na porta {conexao.port}.")
    desconectar_button.config(state=DISABLED)
    input_entry.config(state=DISABLED)
    self_broadcast_button.config(state=DISABLED)
    pm_button.config(state=DISABLED)
    expulsar_button.config(state=DISABLED)
    banir_button.config(state=DISABLED)
    iniciar_button.config(state=NORMAL)

    #FECHE O SERVER SOCKET
    conexao.server_socket.close()


def conectar_client(conexao):
    ''' Conectar um client ao servidor '''
    while True:
        try:
            client_socket, client_address = conexao.server_socket.accept()
            # verificar se o IP está banido
            if client_address[0] in conexao.banidos_ip:
                mensagem_pacote = criar_mensagem("DESCONECTAR", "Admin (privado)", "Você foi banido... Adeus!", verde_claro)
                mensagem_json = json.dumps(mensagem_pacote)
                client_socket.send(mensagem_json.encode(conexao.encodificador))

                # Feche o socket client
                client_socket.close()
            else:
                # Envie o pacote mensagem para receber info do client
                mensagem_pacote = criar_mensagem("INFO", "Admin (privado)", "para confirmar conexão", verde_claro)
                mensagem_json = json.dumps(mensagem_pacote)
                client_socket.send(mensagem_json.encode(conexao.encodificador))

                # Espere que mensagem de confirmaçao seja enviada para verificar conexao
                mensagem_json = client_socket.recv(conexao.bytetam)
                processar_mensagem(conexao, mensagem_json, client_socket, client_address)
        except:
            break


def criar_mensagem(flag, nome, mensagem, cor):
    ''' Retorna um pacote de mensagem que irá ser enviado'''
    mensagem_pacote = {
        "flag": flag,
        "nome": nome,
        "mensagem": mensagem,
        "cor": cor,
    }

    return mensagem_pacote



def processar_mensagem(conexao, mensagem_json, client_socket, client_address=(0,0)):
    ''' Atualizar as informações do server baseado na flag do pacote '''
    mensagem_pacote = json.loads(mensagem_json) #decodificar e tranforma em dicionario
    flag = mensagem_pacote["flag"]
    nome = mensagem_pacote["nome"]
    mensagem = mensagem_pacote["mensagem"]
    cor = mensagem_pacote["cor"]

    if flag == "INFO":
        #Adc a nova informação do client nas listas criadas
        conexao.client_sockets.append(client_socket)
        conexao.client_ips.append(client_address[0])
        
        #Transmitir que o client entrou
        mensagem_pacote = criar_mensagem("MENSAGEM", "Admin (transmitir)", f"{nome} entrou no servidor!", verde_claro)
        mensagem_json = json.dumps(mensagem_pacote)
        transmitir_mensagem(conexao, mensagem_json.encode(conexao.encodificador))

        # Atualizar GUI do server
        client_listbox.insert(END, f"Nome: {nome}        IP: {client_address[0]}")

        # Agora que o client estabeleceu conexão, inicie uma thread pra esperar mensagens
        receber_thread = threading.Thread(target=receber_mensagem, args=(conexao, client_socket, ))
        receber_thread.start()
 
    elif flag == "MENSAGEM":
        #Transmitir a mensagem recebida p/ todos
        transmitir_mensagem(conexao, mensagem_json)

        #Atualizar o GUI
        historico_listbox.insert(END, f"{nome}: {mensagem}")
        historico_listbox.itemconfig(END, fg=cor)

    elif flag == "DESCONECTAR":
        # Fechar/remover o client socket
        index = conexao.client_sockets.index(client_socket)
        conexao.client_sockets.remove(client_socket)
        conexao.client_ips.pop(index) #remove um elemento especificado da lista
        client_listbox.delete(index)

        #fecher o client socket
        client_socket.close()

        #enviar para todos os clientes que alguem saiu
        mensagem_pacote = criar_mensagem("MENSAGEM", "Admim (transmitir)", f"{nome} saiu do chat...", verde_claro)
        mensagem_json = json.dumps(mensagem_pacote)
        transmitir_mensagem(conexao, mensagem_json.encode(conexao.encodificador))

        #atualizar o UI do server
        historico_listbox.insert(END, f"Admin(transmitir): {nome} saiu do chat...")

    else:
        # se der erro
        historico_listbox.insert(END, "Erro ao processar mensagem...")


def transmitir_mensagem(conexao, mensagem_json):
    ''' Envia uma mensagem a todos os clients conectados ao server...'''
    for client_socket in conexao.client_sockets:
        client_socket.send(mensagem_json)

def receber_mensagem(conexao, client_socket):
    ''' Receber uma mensagem de um client '''
    while True:
        # Pegue a mensagem_json do client 
        try:
            mensagem_json = client_socket.recv(conexao.bytetam)
            processar_mensagem(conexao, mensagem_json, client_socket)
        except:
            break


def self_broadcast(conexao):
    ''' Transmitir uma mensagem do admin aos clients '''
    # Criar uma mensagem_pacote
    mensagem_pacote = criar_mensagem("MENSAGEM", "Admin (transmitir)", input_entry.get(), verde_claro)
    mensagem_json = json.dumps(mensagem_pacote)
    transmitir_mensagem(conexao, mensagem_json.encode(conexao.encodificador))
    # limpar o input_entry
    input_entry.delete(0, END)


def pm_mensagem(conexao):
    ''' Envia uma mensagem privada a apenas um client '''
    # Selecione o client da client listbox e acesse o seu socket
    index = client_listbox.curselection()[0]
    client_socket = conexao.client_sockets[index]
    
    # Criar um pacote de mensagem e envie
    mensagem_pacote = criar_mensagem("MENSAGEM", "Admim (privado)", input_entry.get(), verde_claro)
    mensagem_json = json.dumps(mensagem_pacote)
    client_socket.send(mensagem_json.encode(conexao.encodificador))


    #limpar o input_entry
    input_entry.delete(0, END)

def expulsar_client(conexao):
    ''' Expulsa um client do server '''
    #selecionar o client da listbox
    index = client_listbox.curselection()[0]
    client_socket = conexao.client_sockets[index]

    mensagem_pacote = criar_mensagem("DESCONECTAR", "Admim (privado)", "Você foi expulso do chat!", verde_claro)
    mensagem_json = json.dumps(mensagem_pacote)
    client_socket.send(mensagem_json.encode(conexao.encodificador))

def banir_client (conexao):
    ''' Banir um client do server baseado no IP'''
    #selecionar o client da listbox
    index = client_listbox.curselection()[0]
    client_socket = conexao.client_sockets[index]

    mensagem_pacote = criar_mensagem("DESCONECTAR", "Admim (privado)", "Você foi BANIDO do chat!", verde_claro)
    mensagem_json = json.dumps(mensagem_pacote)
    client_socket.send(mensagem_json.encode(conexao.encodificador))

    #banir o IP
    conexao.banidos_ip.append(conexao.client_ips[index])








#Definir GUI layout
#Criar Frames

conexao_frame = tkinter.Frame(root, bg=preto)
historico_frame = tkinter.Frame(root, bg=preto)
client_frame = tkinter.Frame(root, bg=preto)
mensagem_frame = tkinter.Frame(root, bg=preto)
admin_frame = tkinter.Frame(root, bg=preto)


conexao_frame.pack(pady=5)
historico_frame.pack()
client_frame.pack(pady=5)
mensagem_frame.pack()
admin_frame.pack()

#Conexão frame layout
port_label = tkinter.Label(conexao_frame, text="Porta:", font=minha_fonte, bg=preto, fg=verde_claro)
port_entry = tkinter.Entry(conexao_frame, width=10, borderwidth=3, font=minha_fonte)
port_entry.insert(0, "12345")
iniciar_button = tkinter.Button(conexao_frame, text="Iniciar Servidor", borderwidth=3, width=17, font=minha_fonte, bg=verde_claro, command=lambda:iniciar_servidor(minha_conexao))
desconectar_button = tkinter.Button(conexao_frame, text="Encerrar Servidor", borderwidth=3, width=19, font=minha_fonte, bg="red", state=DISABLED, command=lambda:encerrar_servidor(minha_conexao))

port_label.grid(row=0, column=0, padx=2, pady=10)
port_entry.grid(row=0, column=1, padx=2, pady=10)
iniciar_button.grid(row=0, column=2, padx=5, pady=10)
desconectar_button.grid(row=0, column=3, padx=5, pady=10)


# Histórico frame layout
historico_scrollbar = tkinter.Scrollbar(historico_frame, orient=VERTICAL)
historico_listbox = tkinter.Listbox(historico_frame, height=10, width=55, borderwidth=3, font=minha_fonte, bg=preto, fg=verde_claro, yscrollcommand=historico_scrollbar.set)
historico_scrollbar.config(command=historico_listbox.yview)

historico_listbox.grid(row=0, column=0)
historico_scrollbar.grid(row=0, column=1, sticky="NS")

#client frame layout
client_scrollbar = tkinter.Scrollbar(client_frame, orient=VERTICAL)
client_listbox = tkinter.Listbox(client_frame, height=10, width=55, borderwidth=3, font=minha_fonte, bg=preto, fg=verde_claro, yscrollcommand=client_scrollbar.set)
client_scrollbar.config(command=client_listbox.yview)

client_listbox.grid(row=0, column=0)
client_scrollbar.grid(row=0, column=1, sticky="NS")

# Mensagem Frame
input_entry = tkinter.Entry(mensagem_frame, width=40, borderwidth=3, font=minha_fonte, state=DISABLED)
self_broadcast_button = tkinter.Button(mensagem_frame, text="Transmitir", width=13, borderwidth=5, font=minha_fonte, bg=verde_claro, state=DISABLED, command=lambda:self_broadcast(minha_conexao))

input_entry.grid(row=0, column=0, padx=5, pady=5)
self_broadcast_button.grid(row=0, column=1, padx=5, pady=5)


# Botões

pm_button = tkinter.Button(admin_frame, text="PM", borderwidth=5, width=15, font=minha_fonte, bg=verde_claro, state=DISABLED, command=lambda:pm_mensagem(minha_conexao))
expulsar_button = tkinter.Button(admin_frame, text="Expulsar", borderwidth=5, width=15, font=minha_fonte, bg="orange", state=DISABLED, command=lambda:expulsar_client(minha_conexao))
banir_button = tkinter.Button(admin_frame, text="Banir", borderwidth=5, width=15, font=minha_fonte, bg="red", state=DISABLED, command=lambda:banir_client(minha_conexao))


pm_button.grid(row=0, column=0, padx=5, pady=5)
expulsar_button.grid(row=0, column=1, padx=5, pady=5)
banir_button.grid(row=0, column=2, padx=5, pady=5)



#Criar um objeto de Conexao e rodar o Main loop()
minha_conexao = Conexao()
root.mainloop()