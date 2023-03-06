#Client

import tkinter, socket, threading, json
from tkinter import DISABLED, VERTICAL, END, NORMAL, StringVar

#Definir janela root

root = tkinter.Tk()
root.title("Client Chat")
root.iconbitmap('imagens/message_icon.ico')
root.geometry("600x600")
root.resizable(0,0)

#Definir cores e fonts

minha_fonte = ("SimSun", 14)
preto = "#010101"
verde_claro = "#1fc742"
branco = "#ffffff"
vermelho = "#ff3855"


root.config(bg=preto)


class Conexao():
    ''' Uma classe para segurar uma conexão - um server socket e uma informação pertinente '''
    def __init__(self):
        self.encodificador = 'utf-8'
        self.bytetam = 1024



# Definir funções
def conectar(conexao):
    ''' Inicie o server quando receber um IP e número de porta '''
    #Limpar o chat anterior
    minha_listbox.delete(0, END)

    #Pegue as informações para conexão
    conexao.nome = nome_entry.get()
    conexao.target_ip = ip_entry.get()
    conexao.port = port_entry.get()
    conexao.cor = cor.get()

    try:
        #Criar socket client
        conexao.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #IPv4 e TCP
        conexao.client_socket.connect((conexao.target_ip, int(conexao.port)))

        #Receber uma mensagem do server
        mensagem_json = conexao.client_socket.recv(conexao.bytetam)
        processar_mensagem(conexao, mensagem_json)
    except:
        minha_listbox.insert(END, "Conexão não estabelecida... Adeus!")



def desconectar(conexao):
    ''' Desconectar um client do servidor '''
    # Criar um pacote de mensagem para ser enviado
    mensagem_pacote = criar_mensagem("DESCONECTAR", conexao.nome, "Estou saindo...", conexao.cor)
    mensagem_json = json.dumps(mensagem_pacote)
    conexao.client_socket.send(mensagem_json.encode(conexao.encodificador))

    #Desabilitar o GUI
    encerrar_gui()


def iniciar_gui():
    ''' Iniciar conexao atualizando o GUI'''
    conectar_button.config(state = DISABLED)
    desconectar_button.config(state = NORMAL)
    enviar_button.config(state = NORMAL)
    nome_entry.config(state = DISABLED)
    ip_entry.config(state = DISABLED)
    port_entry.config(state = DISABLED)
    input_entry.config(state=NORMAL)

    for button in cores_buttons:
        button.config(state=DISABLED)


def encerrar_gui():
    ''' Encerrar conexão atualizando o GUI '''
    conectar_button.config(state = NORMAL)
    desconectar_button.config(state = DISABLED)
    enviar_button.config(state = DISABLED)
    nome_entry.config(state = NORMAL)
    ip_entry.config(state = NORMAL)
    port_entry.config(state = NORMAL)
    input_entry.config(state=DISABLED)

    for button in cores_buttons:
        button.config(state=NORMAL)

def criar_mensagem(flag, nome, mensagem, cor):
    ''' Retorna um pacote de mensagem para ser enviado ao server '''
    mensagem_pacote = {
        "flag": flag,
        "nome":nome,
        "mensagem":mensagem,
        "cor": cor,
    }
    return mensagem_pacote

def processar_mensagem(conexao, mensagem_json):
    ''' Atualiza o client baseado na flag do pacote de mensagem '''
    # Atualizar o historico do chat mas antes desempacotar o pacote json
    mensagem_pacote = json.loads(mensagem_json) #decodificar e tranforma em dicionario
    flag = mensagem_pacote["flag"]
    nome = mensagem_pacote["nome"]
    mensagem = mensagem_pacote["mensagem"]
    cor = mensagem_pacote["cor"]

    if flag == "INFO":
        # O servidor está pedindo por informações para verificar conexão, envie as informações
        mensagem_pacote = criar_mensagem("INFO", conexao.nome, "Entre no server!", conexao.cor)
        mensagem_json = json.dumps(mensagem_pacote)
        conexao.client_socket.send((mensagem_json).encode(conexao.encodificador))

        #Habilitar os botoes
        iniciar_gui()
        
        #Criar thread que recebe mensagem continuamente do server
        receber_thread = threading.Thread(target=receber_mensagem, args=(conexao, ))
        receber_thread.start()

    elif flag == "MENSAGEM":
        # Servidor enviou uma mensagem, então mostre
        minha_listbox.insert(END, f"{nome}: {mensagem}")
        minha_listbox.itemconfig(END, fg=cor)

    elif flag == "DESCONECTAR":
        #server está solicitanto para desligar
        minha_listbox.insert(END, f"{nome}: {mensagem}")
        minha_listbox.itemconfig(END, fg=cor)

        desconectar(conexao)

    else:
        #se der erro...
        minha_listbox.insert(0, "Erro ao processar a mensagem...")




def enviar_mensagem(conexao):
    ''' Envia mensagem ao server '''
    # Enviar mensagem ao server!
    mensagem_pacote = criar_mensagem("MENSAGEM", conexao.nome, input_entry.get(), conexao.cor)
    mensagem_json = json.dumps(mensagem_pacote)
    conexao.client_socket.send(mensagem_json.encode(conexao.encodificador))
    #Limpar o input entry
    input_entry.delete(0,END)



def receber_mensagem(conexao):
    ''' Receber mensagem do server '''
    while True:
        # receber um pacote de mensagem do server
        try:
            #Receber um pacote de mensagem
            mensagem_json = conexao.client_socket.recv(conexao.bytetam)
            processar_mensagem(conexao, mensagem_json)
        except:
            # Não posso receber mensagem, feche a conexão e pare
            minha_listbox.insert(END, "Conexão foi fechada... Adeus!")
            break


  

#Definir layout GUI
#Criando Frames
info_frame = tkinter.Frame(root, bg=preto)
cor_frame = tkinter.Frame(root, bg=preto)
output_frame = tkinter.Frame(root, bg=preto)
input_frame = tkinter.Frame(root, bg=preto)



info_frame.pack()
cor_frame.pack()
output_frame.pack(pady=10)
input_frame.pack()


#Info Frame layout
nome_label = tkinter.Label(info_frame, text="Nome do Cliente", font=minha_fonte, fg=verde_claro, bg=preto)
nome_entry = tkinter.Entry(info_frame, borderwidth=3, font=minha_fonte)
nome_entry.insert(0,"Marcelo")

ip_label = tkinter.Label(info_frame, text="Host IP:", font=minha_fonte, fg=verde_claro, bg=preto)
ip_entry = tkinter.Entry(info_frame, borderwidth=3, font=minha_fonte)
ip_entry.insert(0,"10.0.0.105")
port_label = tkinter.Label(info_frame, text="Porta:", font=minha_fonte, fg=verde_claro, bg=preto)
port_entry = tkinter.Entry(info_frame, borderwidth=3, font=minha_fonte, width=10)
port_entry.insert(0,"12345")


conectar_button = tkinter.Button(info_frame, text="Conectar", font=minha_fonte, bg=verde_claro, borderwidth=5, width=8, command=lambda:conectar(minha_conexao))
desconectar_button = tkinter.Button(info_frame, text="Desconectar", font=minha_fonte, bg="red", borderwidth=5, width=10, state=DISABLED, command=lambda:desconectar(minha_conexao))

nome_label.grid(row=0,column=0,padx=2,pady=10)
nome_entry.grid(row=0,column=1,padx=2,pady=10)
port_label.grid(row=0,column=2,padx=2,pady=10)
port_entry.grid(row=0,column=3,padx=2,pady=10)
ip_label.grid(row=1,column=0,padx=2,pady=5)
ip_entry.grid(row=1,column=1,padx=2,pady=5)
conectar_button.grid(row=1,column=2,padx=4,pady=5)
desconectar_button.grid(row=1,column=3,padx=4,pady=5)

#Cor Frame layout
cor = StringVar()
cor.set(branco)

branco_button = tkinter.Radiobutton(cor_frame, width=5, text="Branco", variable=cor, value=branco, bg=branco, fg=preto, font=minha_fonte)
vermelho_button = tkinter.Radiobutton(cor_frame, width=8, text="Vermelho", variable=cor, value=vermelho, bg=vermelho, fg=preto, font=minha_fonte)


cores_buttons = [branco_button, vermelho_button]

branco_button.grid(row=1, column=0, padx=2, pady=2)
vermelho_button.grid(row=1, column=1, padx=2, pady=2)




#Output frame Layout
minha_scrollbar = tkinter.Scrollbar(output_frame, orient=VERTICAL)
minha_listbox = tkinter.Listbox(output_frame, height=20, width=55, borderwidth=3, bg=preto, fg=verde_claro, font=minha_fonte, yscrollcommand=minha_scrollbar.set)
minha_scrollbar.config(command=minha_listbox.yview)

minha_listbox.grid(row=0, column=0)
minha_scrollbar.grid(row=0, column=1, sticky="NS")



#Input frame layout
input_entry = tkinter.Entry(input_frame, width=45, borderwidth=3, font=minha_fonte, state=DISABLED)
enviar_button = tkinter.Button(input_frame, text="Enviar", borderwidth=5, width=9, font=minha_fonte, bg=verde_claro, state=DISABLED, command=lambda:enviar_mensagem(minha_conexao))

input_entry.grid(row=0, column=0, padx=5)
enviar_button.grid(row=0, column=1, padx=5)










#Criar um objeto de Conexao e rodar o Main loop()
minha_conexao = Conexao()
root.mainloop()