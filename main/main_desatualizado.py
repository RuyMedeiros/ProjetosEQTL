import time
import keyring
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import pyautogui
import subprocess
import base64
import pygetwindow as gw
import re
from pywinauto import Desktop
from pywinauto.application import Application
import sv_ttk

# Configurações
class Config:
    SERVICO = "sistema_remoto"
    ULTIMO_USUARIO_FILE = "ultimo_usuario.txt"
    ULTIMO_SERVIDOR_FILE = "ultimo_servidor.txt"  # Armazena o último servidor selecionado
    IPS_FILE = "ips_servidor.txt"  # Arquivo txt para salvar os servidores
    IP_SERVIDOR = ""   # Sem IP padrão; deve ser definido pelo usuário
    TEMPO_ESPERA_PADRAO = 15
    TEMPO_VERIFICACAO = 0.5

# Cores corporativas e temas
CORES = {
    'claro': {
        'fundo': '#f0f2f5',
        'fundo_frame': '#ffffff',
        'texto': '#333333',
        'destaque': '#0066cc',
        'botao': '#0066cc',
        'botao_texto': '#ffffff',
        'status': '#e0e0e0'
    },
    'escuro': {
        'fundo': '#1a1a1a',
        'fundo_frame': '#2d2d2d',
        'texto': '#e0e0e0',
        'destaque': '#0088ff',
        'botao': '#004080',
        'botao_texto': '#ffffff',
        'status': '#333333'
    }
}

# Dados base64 de um ícone de lua (16x16 PNG, exemplo simples)
moon_icon_data = """
iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAM1BMVEVHcEz///////////////////////////////////////////////////////////////////9FzZPRAAAAEXRSTlMAEBAgICQoKCxBQkC7AAAADUlEQVQY02NgYGBgAAAABAABJzQnCgAAAABJRU5ErkJggg==
"""

def get_moon_icon():
    # Cria a PhotoImage a partir do dado base64
    return tk.PhotoImage(data=moon_icon_data)

# --- Funções de gerenciamento de credenciais ---
def salvar_ultimo_usuario(usuario):
    try:
        with open(Config.ULTIMO_USUARIO_FILE, 'w') as f:
            f.write(usuario)
    except IOError as e:
        print(f"Erro ao salvar último usuário: {e}")

def carregar_ultimo_usuario():
    try:
        if os.path.exists(Config.ULTIMO_USUARIO_FILE):
            with open(Config.ULTIMO_USUARIO_FILE, 'r') as f:
                return f.read().strip()
    except IOError as e:
        print(f"Erro ao carregar último usuário: {e}")
    return None

def remover_ultimo_usuario():
    try:
        if os.path.exists(Config.ULTIMO_USUARIO_FILE):
            os.remove(Config.ULTIMO_USUARIO_FILE)
    except IOError as e:
        print(f"Erro ao remover arquivo de último usuário: {e}")

def alterar_senha(usuario):
    nova_senha = simpledialog.askstring("Alterar Senha", f"Nova senha para {usuario}:", show='*')
    if nova_senha:
        keyring.set_password(Config.SERVICO, usuario, nova_senha)
        messagebox.showinfo("Sucesso", "Senha atualizada com sucesso!")
    else:
        messagebox.showwarning("Aviso", "Operação cancelada.")

def excluir_senha(usuario):
    if messagebox.askyesno("Confirmar", f"Remover senha salva para {usuario}?"):
        try:
            keyring.delete_password(Config.SERVICO, usuario)
            if carregar_ultimo_usuario() == usuario:
                remover_ultimo_usuario()
            messagebox.showinfo("Sucesso", "Credenciais removidas com sucesso!")
        except keyring.errors.PasswordDeleteError:
            messagebox.showerror("Erro", "Credenciais não encontradas.")

# --- Funções de gerenciamento de IPs utilizando arquivo .txt ---
def carregar_ips():
    ips = {}
    if os.path.exists(Config.IPS_FILE):
        try:
            with open(Config.IPS_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and ':' in line:
                        nome, ip = line.split(":", 1)
                        ips[nome.strip()] = ip.strip()
        except Exception as e:
            print(f"Erro ao carregar IPs: {e}")
    return ips

def salvar_ips(ips):
    try:
        with open(Config.IPS_FILE, 'w') as f:
            for nome, ip in ips.items():
                f.write(f"{nome}: {ip}\n")
    except Exception as e:
        print(f"Erro ao salvar IPs: {e}")

# Funções para salvar/carregar o último servidor selecionado
def salvar_ultimo_servidor(nome):
    try:
        with open(Config.ULTIMO_SERVIDOR_FILE, 'w') as f:
            f.write(nome)
    except Exception as e:
        print(f"Erro ao salvar último servidor: {e}")

def carregar_ultimo_servidor():
    try:
        if os.path.exists(Config.ULTIMO_SERVIDOR_FILE):
            with open(Config.ULTIMO_SERVIDOR_FILE, 'r') as f:
                return f.read().strip()
    except Exception as e:
        print(f"Erro ao carregar último servidor: {e}")
    return None

# --- Funções para automação do aviso ---
def exibir_popup_aviso():
    popup = tk.Toplevel()
    popup.title("Aviso de Conexão")
    popup.geometry("300x150")
    popup.attributes("-topmost", True)
    popup.update_idletasks()
    width = 300
    height = 150
    x = (popup.winfo_screenwidth() // 2) - (width // 2)
    y = (popup.winfo_screenheight() // 2) - (height // 2)
    popup.geometry(f"{width}x{height}+{x}+{y}")

    label = ttk.Label(popup, text="Você gostaria de continuar recebendo essa janela de aviso?", wraplength=280)
    label.pack(pady=20, padx=10)
    
    answer = tk.StringVar(value="")

    def on_sim():
        answer.set("sim")
        popup.destroy()

    def on_nao():
        answer.set("nao")
        popup.destroy()

    btn_frame = ttk.Frame(popup)
    btn_frame.pack(pady=10)
    btn_sim = ttk.Button(btn_frame, text="Sim", command=on_sim)
    btn_sim.pack(side=tk.LEFT, padx=10)
    btn_nao = ttk.Button(btn_frame, text="Não", command=on_nao)
    btn_nao.pack(side=tk.LEFT, padx=10)

    popup.grab_set()
    popup.focus_force()
    popup.wait_window()
    return answer.get()

def acao_sim():
    pyautogui.press('left')
    pyautogui.press('enter')

def acao_nao():
    pyautogui.moveTo(400, 460)  # coordenada da checkbox (ajuste conforme necessário)
    pyautogui.click()
    time.sleep(0.5)
    pyautogui.moveTo(700, 510)  # coordenada do botão "Sim" (ajuste conforme necessário)
    pyautogui.click()

# --- Feedback Visual ---
class FeedbackWindow:
    def __init__(self):
        self.root = tk.Toplevel()
        self.root.title("Status da Conexão")
        self.root.geometry("400x150")
        self.root.resizable(False, False)
        
        style = ttk.Style()
        style.configure("Custom.Horizontal.TProgressbar",
                      thickness=20,
                      troughcolor='#e0e0e0',
                      background='#4CAF50',
                      troughrelief='flat',
                      relief='flat')
        
        self.progress = ttk.Progressbar(
            self.root,
            style="Custom.Horizontal.TProgressbar",
            mode='determinate',
            length=300,
            maximum=100
        )
        self.progress.pack(pady=(20, 10), padx=20, fill=tk.X)
        
        self.label = tk.Label(
            self.root,
            text="",
            font=('Segoe UI', 10),
            bg='#f0f2f5',
            fg='#333333'
        )
        self.label.pack(pady=(0, 10))
        
        self.btn_cancelar = ttk.Button(
            self.root,
            text="Cancelar",
            command=self.cancelar
        )
        self.btn_cancelar.pack(pady=(0, 10))
        
        self.operacao_cancelada = False
        self.atualizar_progresso(0, "Preparando conexão...")

    def atualizar_progresso(self, valor, mensagem):
        self.progress['value'] = valor
        self.label.config(text=mensagem)
        self.root.update()

    def cancelar(self):
        self.operacao_cancelada = True
        self.atualizar_progresso(0, "Operação cancelada pelo usuário")
        self.root.after(2000, self.close)

    def close(self):
        self.root.destroy()

def detectar_janela(titulos, timeout=15):
    start_time = time.time()
    while time.time() - start_time < timeout:
        for titulo in titulos:
            try:
                windows = pyautogui.getWindowsWithTitle(titulo)
                if windows:
                    windows[0].activate()
                    return True
            except Exception:
                pass
        time.sleep(0.5)
    return False

def detectar_janela_rdp(timeout=5):
    desktop = Desktop(backend="uia")
    for _ in range(timeout * 2):  # tenta a cada 0.5s
        time.sleep(0.5)
        try:
            for win in desktop.windows():
                titulo = win.window_text().strip()
                if titulo == "Conexão de Área de Trabalho Remota":
                    return True
        except Exception:
            continue
    return False

def conectar_servidor(usuario, senha):
    feedback = FeedbackWindow()
    
    try:
        feedback.atualizar_progresso(25, "Iniciando conexão remota...")
        subprocess.Popen('mstsc.exe', shell=True)
        time.sleep(0.5)

        feedback.atualizar_progresso(30, f"Conectando a {Config.IP_SERVIDOR}...")

        titulos_conexao = [
            "Conexão de Área de Trabalho Remota", 
            "Remote Desktop Connection",
            "Área de Trabalho Remota",
            "Conexão Remota",
            "mstsc",
            "Desktop Remoto"
        ]
        titulos_seguranca = [
            "Segurança do Windows", 
            "Windows Security",
            "Credenciais do Windows"
        ]

        if not detectar_janela(titulos_conexao):
            raise TimeoutError("Janela de Conexão Remota não encontrada")

        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.5)
        pyautogui.write(Config.IP_SERVIDOR, interval=0.01)
        time.sleep(0.5)
        pyautogui.press('enter')

        feedback.atualizar_progresso(40, "Aguardando credenciais...")

        if not detectar_janela(titulos_seguranca, timeout=15):
            raise TimeoutError("Janela 'Segurança do Windows' não apareceu")

        feedback.atualizar_progresso(55, "Inserindo credenciais...")
        time.sleep(1)
        pyautogui.write(senha, interval=0.01)
        time.sleep(0.5)
        pyautogui.press('enter')

        feedback.atualizar_progresso(70, "Autenticando...")

        if detectar_janela_rdp():
            feedback.atualizar_progresso(80, "Aviso detectado, processando resposta...")

            resposta = exibir_popup_aviso()
            if resposta == "sim":
                acao_sim()
            else:
                acao_nao()
        else:
            feedback.atualizar_progresso(80, "Autenticando...")
            feedback.atualizar_progresso(90, "Autenticando...")

        feedback.atualizar_progresso(100, "✅ Conexão estabelecida com sucesso!")
        salvar_ultimo_usuario(usuario)
        time.sleep(1)

    except Exception as e:
        feedback.atualizar_progresso(100, f"❌ Falha: {str(e)}")
        time.sleep(2)
        raise

    finally:
        feedback.close()

# --- Interface Principal ---
class MainApplication:
    def __init__(self, root):
        self.root = root
        self.tema_atual = 'claro'
        self.setup_ui()
        self.center_window()
        self.check_quick_connect()
        self.setup_keyboard_navigation()
        self.root.bind('<Return>', self.handle_enter_press)
    
    def handle_enter_press(self, event=None):
        if self.user_entry.get() and self.pass_entry.get():
            self.connect()
    
    def center_window(self, window=None, width=None, height=None):
        if window is None:
            window = self.root
            width = 600
            height = 500
        
        window.update_idletasks()
        if width is None:
            width = window.winfo_width()
        if height is None:
            height = window.winfo_height()
        
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_keyboard_navigation(self):
        self.root.bind('<Down>', self.focus_next_widget)
        self.root.bind('<Up>', self.focus_prev_widget)
        self.root.bind('<Escape>', lambda e: self.root.quit())
    
    def focus_next_widget(self, event):
        event.widget.tk_focusNext().focus()
        return "break"
    
    def focus_prev_widget(self, event):
        event.widget.tk_focusPrev().focus()
        return "break"
    
    def setup_ui(self):
        self.apply_theme()
        
        self.root.title("Gerenciador de Conexão Remota - Equatorial Energia")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        main_frame = ttk.Frame(self.root, padding="20", style='Main.TFrame')
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        header = ttk.Label(
            main_frame,
            text="CONEXÃO REMOTA",
            font=('Segoe UI', 16, 'bold'),
            style='Header.TLabel'
        )
        header.pack(pady=(0, 20))
        
        theme_btn = ttk.Button(
            main_frame,
            text="🌓",
            command=self.toggle_theme,
            style='Theme.TButton',
            width=3
        )
        theme_btn.pack(anchor=tk.NE)
        
        # Formulário com os campos: Usuário, Senha e Servidor
        form_frame = ttk.Frame(main_frame, style='Form.TFrame')
        form_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(form_frame, text="Usuário:", style='Label.TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.user_entry = ttk.Entry(form_frame, font=('Segoe UI', 10), style='Entry.TEntry')
        self.user_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Senha:", style='Label.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.pass_entry = ttk.Entry(form_frame, show="•", font=('Segoe UI', 10), style='Entry.TEntry')
        self.pass_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Servidor:", style='Label.TLabel').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.server_combobox = ttk.Combobox(form_frame, state="readonly", font=('Segoe UI', 10))
        self.server_combobox.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        self.server_combobox.bind("<<ComboboxSelected>>", self.selecionar_servidor)
        self.carregar_servidores_no_combobox()
        
        form_frame.columnconfigure(1, weight=1)
        
        btn_frame = ttk.Frame(main_frame, style='Btn.TFrame')
        btn_frame.pack(pady=20)
        
        self.connect_btn = ttk.Button(btn_frame, text="Conectar", command=self.connect, style='Accent.TButton')
        self.connect_btn.pack(side=tk.LEFT, padx=5, ipadx=20)
        
        ttk.Button(btn_frame, text="Gerenciar Credenciais", command=self.manage_credentials, style='Secondary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Gerenciar IPs", command=self.manage_ips, style='Secondary.TButton').pack(side=tk.LEFT, padx=5)
        
        self.status_bar = ttk.Label(self.root, text="Pronto para conectar", relief=tk.SUNKEN, anchor=tk.W, style='Status.TLabel')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.user_entry.focus_set()
    
    def apply_theme(self):
        tema = CORES[self.tema_atual]
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Main.TFrame', background=tema['fundo_frame'])
        style.configure('Form.TFrame', background=tema['fundo_frame'])
        style.configure('Btn.TFrame', background=tema['fundo_frame'])
        style.configure('Header.TLabel', foreground=tema['destaque'], background=tema['fundo_frame'])
        style.configure('Label.TLabel', foreground=tema['texto'], background=tema['fundo_frame'])
        style.configure('Entry.TEntry', foreground=tema['texto'], fieldbackground=tema['fundo_frame'])
        style.configure('Accent.TButton', foreground=tema['botao_texto'], background=tema['botao'])
        style.map('Accent.TButton', background=[('active', tema['destaque'])])
        style.configure('Secondary.TButton', foreground=tema['texto'], background=tema['fundo_frame'])
        style.configure('Status.TLabel', foreground=tema['texto'], background=tema['status'])
        style.configure('Theme.TButton', foreground=tema['texto'], background=tema['fundo_frame'])
        
        self.root.configure(bg=tema['fundo'])
    
    def toggle_theme(self):
        self.tema_atual = 'escuro' if self.tema_atual == 'claro' else 'claro'
        self.apply_theme()
    
    def aplicar_dados_servidor(self):
        """Ao selecionar um servidor, atualiza o IP e salva o último servidor selecionado."""
        selecionado = self.server_combobox.get()
        ips = carregar_ips()
        if selecionado in ips:
            Config.IP_SERVIDOR = ips[selecionado]
            salvar_ultimo_servidor(selecionado)
    
    def carregar_servidores_no_combobox(self):
        ips = carregar_ips()
        servidores = list(ips.keys())
        self.server_combobox['values'] = servidores
        ultimo = carregar_ultimo_servidor()
        if ultimo and ultimo in servidores:
            self.server_combobox.set(ultimo)
            self.aplicar_dados_servidor()
        elif servidores:
            self.server_combobox.current(0)
            self.aplicar_dados_servidor()
    
    def selecionar_servidor(self, event=None):
        """Atualiza o IP conforme o servidor selecionado."""
        self.aplicar_dados_servidor()
        messagebox.showinfo("Servidor Selecionado", f"Servidor '{self.server_combobox.get()}' selecionado.\nIP: {Config.IP_SERVIDOR}")
    
    def apply_theme(self):
        tema = CORES[self.tema_atual]
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Main.TFrame', background=tema['fundo_frame'])
        style.configure('Form.TFrame', background=tema['fundo_frame'])
        style.configure('Btn.TFrame', background=tema['fundo_frame'])
        style.configure('Header.TLabel', foreground=tema['destaque'], background=tema['fundo_frame'])
        style.configure('Label.TLabel', foreground=tema['texto'], background=tema['fundo_frame'])
        style.configure('Entry.TEntry', foreground=tema['texto'], fieldbackground=tema['fundo_frame'])
        style.configure('Accent.TButton', foreground=tema['botao_texto'], background=tema['botao'])
        style.map('Accent.TButton', background=[('active', tema['destaque'])])
        style.configure('Secondary.TButton', foreground=tema['texto'], background=tema['fundo_frame'])
        style.configure('Status.TLabel', foreground=tema['texto'], background=tema['status'])
        style.configure('Theme.TButton', foreground=tema['texto'], background=tema['fundo_frame'])
        
        self.root.configure(bg=tema['fundo'])
    
    def toggle_theme(self):
        self.tema_atual = 'escuro' if self.tema_atual == 'claro' else 'claro'
        self.apply_theme()
    
    def check_quick_connect(self):
        if (ultimo_usuario := carregar_ultimo_usuario()) and (senha := keyring.get_password(Config.SERVICO, ultimo_usuario)):
            self.user_entry.insert(0, ultimo_usuario)
            self.pass_entry.insert(0, senha)
            self.status_bar.config(text=f"Credenciais encontradas para {ultimo_usuario}")

    def connect(self):
        usuario = self.user_entry.get()
        senha = self.pass_entry.get()
        
        if not usuario or not senha:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos!")
            return
        if not Config.IP_SERVIDOR:
            messagebox.showwarning("Atenção", "Por favor, selecione um servidor!")
            return
        
        if not keyring.get_password(Config.SERVICO, usuario):
            keyring.set_password(Config.SERVICO, usuario, senha)
        
        self.status_bar.config(text=f"Conectando como {usuario}...")
        self.root.update()
        
        try:
            conectar_servidor(usuario, senha)
            self.status_bar.config(text=f"✅ Conectado como {usuario}")
        except Exception as e:
            self.status_bar.config(text=f"❌ Falha na conexão: {str(e)}")
            messagebox.showerror("Erro", f"Falha na conexão: {str(e)}")

    def manage_credentials(self):
        try:
            if not hasattr(self, 'user_entry'):
                messagebox.showwarning("Erro", "Componente user_entry não encontrado")
                return
            usuario = self.user_entry.get()
            if not usuario:
                messagebox.showwarning("Aviso", "Digite um usuário primeiro")
                return

            manage_win = tk.Toplevel(self.root)
            manage_win.title("Gerenciar Credenciais")
            manage_win.geometry("400x280")
            manage_win.resizable(False, False)
            main_frame = ttk.Frame(manage_win, style='Main.TFrame')
            main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
            ttk.Label(main_frame, text="GERENCIAR CREDENCIAIS", font=('Segoe UI', 12, 'bold'), style='Header.TLabel').pack(pady=(0, 20))
            ttk.Label(main_frame, text=f"Usuário: {usuario}", font=('Segoe UI', 10), style='Label.TLabel').pack(pady=5)
            btn_frame = ttk.Frame(main_frame, style='Btn.TFrame')
            btn_frame.pack(pady=20)
            ttk.Button(btn_frame, text="Alterar Senha", command=lambda: self.on_alterar_senha(usuario, manage_win), style='Accent.TButton', width=20).pack(pady=5, fill=tk.X)
            ttk.Button(btn_frame, text="Remover Credenciais", command=lambda: self.on_remover_credenciais(usuario, manage_win), style='Destructive.TButton', width=20).pack(pady=5, fill=tk.X)
            ttk.Button(btn_frame, text="Fechar", command=manage_win.destroy, style='Secondary.TButton', width=20).pack(pady=5, fill=tk.X)
            if hasattr(self, 'center_window'):
                self.center_window(manage_win)
            manage_win.transient(self.root)
            manage_win.grab_set()
            manage_win.focus_force()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao abrir gerenciador: {str(e)}")
            if 'manage_win' in locals():
                manage_win.destroy()

    def on_alterar_senha(self, usuario, janela):
        try:
            alterar_senha(usuario)
            janela.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao alterar senha: {str(e)}")
            janela.destroy()

    def on_remover_credenciais(self, usuario, janela):
        try:
            if messagebox.askyesno("Confirmar", f"Remover credenciais de {usuario}?"):
                excluir_senha(usuario)
                if hasattr(self, 'user_entry'):
                    self.user_entry.delete(0, tk.END)
                if hasattr(self, 'pass_entry'):
                    self.pass_entry.delete(0, tk.END)
                if hasattr(self, 'status_bar'):
                    self.status_bar.config(text="Credenciais removidas")
            janela.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao remover credenciais: {str(e)}")
            janela.destroy()

    def manage_ips(self):
        manage_ip_win = tk.Toplevel(self.root)
        manage_ip_win.title("Gerenciar IPs do Servidor")
        manage_ip_win.geometry("500x420")
        manage_ip_win.resizable(False, False)
        main_frame = ttk.Frame(manage_ip_win, padding="20", style='Main.TFrame')
        main_frame.pack(expand=True, fill=tk.BOTH)
        ttk.Label(main_frame, text="GERENCIAR IPs", font=('Segoe UI', 12, 'bold'), style='Header.TLabel').pack(pady=(0, 10))
        ips = carregar_ips()
        list_frame = ttk.Frame(main_frame, style='Main.TFrame')
        list_frame.pack(fill=tk.BOTH, expand=True)
        self.ips_listbox = tk.Listbox(list_frame, height=8)
        self.ips_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.ips_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ips_listbox.config(yscrollcommand=scrollbar.set)
        for nome, ip in ips.items():
            self.ips_listbox.insert(tk.END, f"{nome}: {ip}")
        btn_frame = ttk.Frame(main_frame, style='Btn.TFrame')
        btn_frame.pack(pady=10, fill=tk.X)
        ttk.Button(btn_frame, text="Adicionar/Alterar", command=self.adicionar_alterar_ip, style='Accent.TButton').pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(btn_frame, text="Selecionar", command=self.selecionar_ip, style='Secondary.TButton').pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(btn_frame, text="Excluir", command=self.excluir_ip, style='Destructive.TButton').pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(main_frame, text="Fechar", command=manage_ip_win.destroy, style='Secondary.TButton').pack(pady=5, fill=tk.X)
        self.center_window(manage_ip_win)
        manage_ip_win.transient(self.root)
        manage_ip_win.grab_set()
        manage_ip_win.focus_force()

    def adicionar_alterar_ip(self):
        nome = simpledialog.askstring(
            "Nome do Servidor",
            "Informe um nome para o servidor:",
            parent=self.root  
        )
        if not nome:
            messagebox.showwarning("Aviso", "Nome não informado!", parent=self.root)
            return
        ip = simpledialog.askstring(
            "Endereço IP",
            "Informe o endereço IP do servidor:",
            parent=self.root  
        )
        if not ip:
            messagebox.showwarning("Aviso", "IP não informado!", parent=self.root)
            return
    
    # Resto do seu código para salvar o IP...   
        ips = carregar_ips()
        ips[nome] = ip
        salvar_ips(ips)
        messagebox.showinfo("Sucesso", f"Servidor '{nome}' com IP {ip} salvo!")
        self.ips_listbox.delete(0, tk.END)
        for nome, ip in ips.items():
            self.ips_listbox.insert(tk.END, f"{nome}: {ip}")
        self.carregar_servidores_no_combobox()

    def selecionar_ip(self):
        try:
            selecionado = self.ips_listbox.get(self.ips_listbox.curselection())
            nome_ip, ip = selecionado.split(":", 1)
            Config.IP_SERVIDOR = ip.strip()
            messagebox.showinfo("Sucesso", f"IP do servidor alterado para {Config.IP_SERVIDOR}")
        except tk.TclError:
            messagebox.showwarning("Aviso", "Nenhum IP selecionado!")

    def excluir_ip(self):
        try:
            selecionado = self.ips_listbox.get(self.ips_listbox.curselection())
            nome_ip, ip = selecionado.split(":", 1)
            ips = carregar_ips()
            if nome_ip in ips:
                if messagebox.askyesno("Confirmar", f"Excluir o servidor '{nome_ip}'?"):
                    del ips[nome_ip]
                    salvar_ips(ips)
                    messagebox.showinfo("Sucesso", "Servidor excluído!")
                    self.ips_listbox.delete(0, tk.END)
                    for nome, ip in ips.items():
                        self.ips_listbox.insert(tk.END, f"{nome}: {ip}")
                    self.carregar_servidores_no_combobox()
            else:
                messagebox.showerror("Erro", "Servidor não encontrado na lista!")
        except tk.TclError:
            messagebox.showwarning("Aviso", "Nenhum IP selecionado!")

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()
