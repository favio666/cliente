import tkinter as tk
import tkinter.ttk as ttk
from tkinter.scrolledtext import ScrolledText
import socket
import threading
import time
import ipaddress
from datetime import datetime
from ttkthemes import ThemedStyle

HEADER_SIZE = 10
EMOJIS = {
    ":)": u"\U0001F642",
    ":(": u"\U0001F641",
    ":D": u"\U0001F600",
    ":P": u"\U0001F61B",
    ":'(": u"\U0001F622",
    ":o": u"\U0001F62E",
    ";)": u"\U0001F609",
}

class ChatService(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Chat Service")
        self.geometry("+700+100")
        self.resizable(0, 0)

        self.client = None
        self.estilo = ThemedStyle(self)
        self.nombre_temas = self.estilo.theme_names()
        # ------------------------ FRAMES -----------------------------
        frm1 = tk.LabelFrame(self, text="Conexion")
        frm2 = tk.Frame(self)
        frm3 = tk.LabelFrame(self, text="Enviar mensaje")
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        frm1.pack(padx=5, pady=5,fill='both', anchor=tk.W)
        frm2.pack(padx=5, pady=5, fill='both', expand=True)
        frm3.pack(padx=5, pady=5, fill='both')
        # ------------------------ FRAME 1 ----------------------------
        self.lblName = tk.Label(frm1, text="Nombre:")
        self.entName = tk.Entry(frm1)
        self.lblHost = tk.Label(frm1, text="Host:")
        self.entHost = tk.Entry(frm1)
        self.lblPort = tk.Label(frm1, text="Puerto:")
        self.entPort = tk.Entry(frm1)
        self.btnConnect = ttk.Button(frm1, text="Conectar", width=16, command=self.altrnr_conex)
        self.lblTheme = tk.Label(frm1, text="Tema:")
        self.cbxTheme = ttk.Combobox(frm1, values=self.nombre_temas)
        self.cbxTheme.bind('<<ComboboxSelected>>', self.cambiar_tema)
        self.lblName.grid(row=0, column=0, padx=5, pady=5)
        self.entName.grid(row=0, column=1, padx=5, pady=5)
        self.lblHost.grid(row=1, column=0, padx=5, pady=5)
        self.entHost.grid(row=1, column=1, padx=5, pady=5)
        self.lblPort.grid(row=1, column=2, padx=5, pady=5)
        self.entPort.grid(row=1, column=3, padx=5, pady=5)
        self.btnConnect.grid(row=2, column=3, padx=5, pady=5)
        self.lblTheme.grid(row=0, column=2, padx=5, pady=5)
        self.cbxTheme.grid(row=0, column=3, padx=5, pady=5)
        
        self.entName.bind('<Return>', lambda event: self.altrnr_conex())
        self.entHost.bind('<Return>', lambda event: self.altrnr_conex())
        self.entPort.bind('<Return>', lambda event: self.altrnr_conex())
        # ------------------------ FRAME 2 ---------------------------
        self.txtChat = ScrolledText(frm2, height=25, width=50, wrap=tk.WORD, state='disable')
        self.txtChat.grid(row=0, column=0, columnspan=3, padx=5, pady=5)
        self.txtChat.tag_config('enviado', foreground='blue', justify='right')
        self.txtChat.tag_config('recibido', foreground='green', justify='left')
        # ------------------------ FRAME 3 --------------------------
        self.lblText = tk.Label(frm3, text="Texto:")
        self.inText = tk.Entry(frm3, width=45, state='disable')
        self.inText.bind('<Return>', lambda event: self.enviar_msj())
        self.btnSend = ttk.Button(frm3, text="Enviar", width=12, state='disable', command=self.enviar_msj)
        
        self.lblText.grid(row=0, column=0, padx=5, pady=5)
        self.inText.grid(row=0, column=1, padx=5, pady=5)
        self.btnSend.grid(row=0, column=2, padx=5, pady=5)

        # --------------------------- StatusBar -----------------------
        self.statusBar = tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.statusBar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # ------------- Control del boton "X" de la ventana -----------
        self.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
        
    def cambiar_tema(self, event):
        sele_tema = self.cbxTheme.get()
        self.estilo.theme_use(sele_tema)
        
    def altrnr_conex(self):
        if self.client is None:
            self.conex_sv()
        else:
            self.desconexion_sv()

    def conex_sv(self):
        try:
            nombre = self.entName.get()
            if not nombre:  
                self.statusBar.config(text="El nombre está vacío.")
                return
            host = self.entHost.get()
            if not host:  
                self.statusBar.config(text="El host está vacío.")
                return
            try: 
                ipaddress.ip_address(host) 
            except ValueError: 
                self.statusBar.config(text="El host debe ser una dirección IP válida.")
                return 
            port_entry = self.entPort.get()
            if not port_entry:  
                self.statusBar.config(text="El puerto está vacío.")
                return
            try:
                port = int(port_entry)
            except ValueError:  
                self.statusBar.config(text="El puerto debe ser un número.")
                return
            if port <= 1023:
                self.statusBar.config(text="El puerto debe ser mayor a 1023.")
                return
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.client.connect((host, port))
            except ConnectionRefusedError:  
                self.statusBar.config(text=f"Error al establecer conexión con {host} en el puerto {port}")
                return
    
            self.entName.config(state=tk.DISABLED)
            self.entHost.config(state=tk.DISABLED)
            self.entPort.config(state=tk.DISABLED)
            self.btnConnect.config(text='Desconectar')
            self.inText.config(state=tk.NORMAL)
            self.btnSend.config(state=tk.NORMAL)
    
            threading.Thread(target=self.recepcion_msj, args=(self.client,)).start()
            self.statusBar.config(text=f"Conectado a {host} en el puerto {port}")
        except Exception as e:
            self.statusBar.config(text="Error al conectarse al servidor")
            self.client = None

    def desconexion_sv(self):
        if self.client is not None:
            self.client.close()
            self.client = None
            self.entName.config(state=tk.NORMAL)
            self.entHost.config(state=tk.NORMAL)
            self.entPort.config(state=tk.NORMAL)
            self.btnConnect.config(text='Conectar')
            self.inText.config(state=tk.DISABLED)
            self.btnSend.config(state=tk.DISABLED)
            self.statusBar.config(text=f"Desconectado")

    def enviar_msj(self):
        if self.client is not None:
            try:
                nombre = self.entName.get()
                msj = self.inText.get()
                for k, v in EMOJIS.items():
                    msj = msj.replace(k, v)
                if msj:
                    self.inText.delete(0, tk.END)
                    full_msj = nombre + ': ' + msj
                    full_msj_encoded = full_msj.encode()
                    header = f"{len(full_msj_encoded):<{HEADER_SIZE}}".encode()
                    self.client.send(header + full_msj_encoded)
    
                    hora = datetime.now().strftime('%H:%M')
                    self.txtChat.config(state=tk.NORMAL)
                    self.txtChat.insert(tk.END, f"[{hora}] Tu: {msj}\n", ('enviado'))
                    self.txtChat.config(state=tk.DISABLED)
                    self.txtChat.see(tk.END)
                    self.msj_tempo(f"Enviando mensaje")
            except ConnectionAbortedError:
                self.desconexion_sv()
                self.conex_sv()


    def recepcion_msj(self, client):
        while True:
            try:
                msj_header = client.recv(HEADER_SIZE)
                self.msj_tempo(f"Recibiendo mensaje")
                if not msj_header:
                    break
                time.sleep(1)
                msj_length = int(msj_header.decode('utf-8').strip())
                msj = client.recv(msj_length).decode('utf-8')
    
                hora = datetime.now().strftime('%H:%M')
                self.txtChat.config(state=tk.NORMAL)
                self.txtChat.insert(tk.END, f"[{hora}] {msj}\n", ('recibido'))
                self.txtChat.config(state=tk.DISABLED)
                self.txtChat.see(tk.END)
            except Exception as e:
                break
            
    def msj_tempo(self, mensajet, time=1):
        self.statusBar.config(text=mensajet)
        threading.Timer(time, lambda: self.statusBar.config(text="")).start()
        
    def cerrar_aplicacion(self):
        self.desconexion_sv()
        self.destroy()



ChatService().mainloop()