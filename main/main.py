""" 
Aqui está o código completo, onde todas as funções e classes estão tudo em um mesmo arquivo .py

"""

import time
import keyring
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import pyautogui
import subprocess
from pywinauto import Desktop
import sv_ttk

# Configurações
class Config:
    APP_NAME = "GerenciadorRDP"
    ULTIMO_USUARIO_FILE = "ultimo_usuario.txt"
    ULTIMO_SERVIDOR_FILE = "ultimo_servidor.txt"
    ULTIMO_TEMA_FILE = "ultimo_tema.txt"
    SALVAR_LOGIN_FILE = "salvar_login.txt"
    IPS_FILE = "ips_servidor.txt"
    IP_SERVIDOR = ""
    TEMPO_ESPERA_PADRAO = 15
    TEMPO_VERIFICACAO = 0.5

# Cores corporativas e temas
CORES = {
    "light": {
        "bg": "#ffffff",
        "fg": "#000000",
        "highlight": "#e0e0e0"
    },
    "dark": {
        "bg": "#2e2e2e",
        "fg": "#ffffff",
        "highlight": "#3e3e3e"
    }
}

# --- Funções de gerenciamento de arquivos ---
def salvar_arquivo(nome_arquivo, conteudo):
    try:
        with open(nome_arquivo, 'w') as f:
            f.write(conteudo)
    except IOError as e:
        print(f"Erro ao salvar arquivo {nome_arquivo}: {e}")

def carregar_arquivo(nome_arquivo):
    try:
        if os.path.exists(nome_arquivo):
            with open(nome_arquivo, 'r') as f:
                return f.read().strip()
    except IOError as e:
        print(f"Erro ao carregar arquivo {nome_arquivo}: {e}")
    return None

def remover_arquivo(nome_arquivo):
    try:
        if os.path.exists(nome_arquivo):
            os.remove(nome_arquivo)
    except IOError as e:
        print(f"Erro ao remover arquivo {nome_arquivo}: {e}")

# --- Funções de gerenciamento de credenciais ---
def alterar_senha(usuario):
    nova_senha = simpledialog.askstring("Alterar Senha", f"Nova senha para {usuario}:", show='*')
    if nova_senha:
        keyring.set_password(Config.APP_NAME, usuario, nova_senha)
        messagebox.showinfo("Sucesso", "Senha atualizada com sucesso!")
    else:
        messagebox.showwarning("Aviso", "Operação cancelada.")

def excluir_senha(usuario):
    if messagebox.askyesno("Confirmar", f"Remover senha salva para {usuario}?"):
        try:
            keyring.delete_password(Config.APP_NAME, usuario)
            messagebox.showinfo("Sucesso", "Credenciais removidas com sucesso!")
        except keyring.errors.PasswordDeleteError:
            messagebox.showerror("Erro", "Credenciais não encontradas.")

# --- Funções de gerenciamento de IPs ---
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

def adicionar_ip(nome, ip):
    ips = carregar_ips()
    ips[nome] = ip
    salvar_ips(ips)

def remover_ip(nome):
    ips = carregar_ips()
    if nome in ips:
        del ips[nome]
        salvar_ips(ips)
        return True
    return False

# -- Funções da automação --

def acao_sim():
    pyautogui.press('left')
    pyautogui.press('enter')

def acao_nao():
    pyautogui.moveTo(400, 460)
    pyautogui.click()
    time.sleep(0.5)
    pyautogui.moveTo(700, 510)
    pyautogui.click()

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
    for _ in range(timeout * 2):
        time.sleep(0.5)
        try:
            for win in desktop.windows():
                titulo = win.window_text().strip()
                if titulo == "Conexão de Área de Trabalho Remota":
                    return True
        except Exception:
            continue
    return False

def conectar_servidor(ip, usuario, senha):
    try:
        subprocess.Popen('mstsc.exe', shell=True)
        time.sleep(0.5)
        
        # Minimiza a janela principal
        root.iconify()
               
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

        if not detectar_janela(titulos_seguranca, timeout=15):
            raise TimeoutError("Janela 'Segurança do Windows' não apareceu")

        time.sleep(1)
        pyautogui.write(senha, interval=0.01)
        time.sleep(0.5)
        pyautogui.press('enter')

        if detectar_janela_rdp():
            acao_sim()
            time.sleep(1)
         
    except Exception as e:
        time.sleep(2)
        raise

# -- Função para foco

def askstring_focus(title, prompt, parent=None):
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.grab_set()  # Faz a janela modal
    dialog.transient(parent)

    tk.Label(dialog, text=prompt, font=("Segoe UI", 10)).pack(padx=20, pady=(20, 10))

    entry = tk.Entry(dialog, font=("Segoe UI", 10), width=40)
    entry.pack(padx=20, pady=(0, 20))
    entry.focus_force()  # Força o foco no campo

    result = {"value": None}

    def on_ok():
        result["value"] = entry.get()
        dialog.destroy()

    def on_cancel():
        dialog.destroy()

    btn_frame = tk.Frame(dialog)
    btn_frame.pack(pady=(0, 15))

    tk.Button(btn_frame, text="OK", width=10, command=on_ok).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Cancelar", width=10, command=on_cancel).pack(side=tk.LEFT, padx=5)

    dialog.bind("<Return>", lambda e: on_ok())
    dialog.bind("<Escape>", lambda e: on_cancel())

    # Centraliza na tela
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_reqwidth() // 2)
    y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_reqheight() // 2)
    dialog.geometry(f"+{x}+{y}")

    parent.wait_window(dialog)  # Espera a janela ser fechada
    return result["value"]

# -- Menu Principal --
class ModernConnectionManager:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.tema_atual = self._carregar_tema() or "light"
        self._setup_basics()
        self._create_widgets()
        self._load_state()
        sv_ttk.set_theme(self.tema_atual)
        self.setup_keyboard_navigation()
    
    def handle_enter_press(self, event=None):
        if self.user_entry.get() and self.pass_entry.get():
            self._connect()

    def _setup_basics(self):
        self.root.title("Conexão Remota")
        self.root.geometry("500x450")
        self.root.resizable(True, True)
        self.center_window()

    def setup_keyboard_navigation(self):
        self.root.bind('<Down>', self.focus_next_widget)
        self.root.bind('<Up>', self.focus_prev_widget)
        self.root.bind('<Return>', self.handle_enter_press)
        self.root.bind('<Escape>', lambda e: self.root.quit())
    
    def focus_next_widget(self, event):
        event.widget.tk_focusNext().focus()
        return "break"
    
    def focus_prev_widget(self, event):
        event.widget.tk_focusPrev().focus()
        return "break"

    def _carregar_tema(self):
        return carregar_arquivo(Config.ULTIMO_TEMA_FILE)

    def _salvar_tema(self):
        salvar_arquivo(Config.ULTIMO_TEMA_FILE, self.tema_atual)

    def _carregar_salvar_login(self):
        return carregar_arquivo(Config.SALVAR_LOGIN_FILE) == "True"

    def _salvar_salvar_login(self, valor):
        salvar_arquivo(Config.SALVAR_LOGIN_FILE, str(valor))

    def _create_widgets(self):
        # Container Principal
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(expand=True, fill=tk.BOTH)
    
            # Cabeçalho
        self.header = ttk.Label(
            self.main_frame,
            text="CONEXÃO REMOTA",
            font=("Segoe UI", 16, "bold"),
            justify="center"
        )
        self.header.pack(pady=(0, 20))

        # Botão de Tema
        self.theme_btn = ttk.Button(
            self.main_frame,
            text="🌓 Alternar Tema",
            command=self._toggle_theme,
            style="Accent.TButton"
        )
        self.theme_btn.pack(anchor=tk.NE, pady=5)

        # Formulário
        self._create_form()
        self._create_action_buttons()
        self._create_status_bar()

    def _create_form(self):
        form_frame = ttk.Frame(self.main_frame)
        form_frame.pack(fill=tk.X, pady=10)

        # Entrada de Usuário
        ttk.Label(form_frame, text="Usuário:", font=("Segoe UI", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.user_entry = ttk.Entry(form_frame, font=("Segoe UI", 10))
        self.user_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)

        # Entrada de Senha
        ttk.Label(form_frame, text="Senha:", font=("Segoe UI", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.pass_entry = ttk.Entry(form_frame, show="•", font=("Segoe UI", 10))
        self.pass_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)

        # Checkbox para salvar login
        self.save_login_var = tk.BooleanVar(value=self._carregar_salvar_login())
        self.save_login_check = ttk.Checkbutton(
            form_frame, 
            text="Salvar usuário para próximos logins",
            variable=self.save_login_var,
            command=lambda: self._salvar_salvar_login(self.save_login_var.get())
        )
        self.save_login_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Seleção de Servidor
        ttk.Label(form_frame, text="Servidor:", font=("Segoe UI", 10)).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.server_combobox = ttk.Combobox(form_frame, state="readonly", font=("Segoe UI", 10))
        self.server_combobox.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        self.server_combobox.bind("<<ComboboxSelected>>", self._on_server_select)

        form_frame.columnconfigure(1, weight=1)
        self._load_servers()

    def _create_action_buttons(self):
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(pady=15)

        self.connect_btn = ttk.Button(
            btn_frame,
            text="Conectar",
            command=self._connect,
            style="Accent.TButton",
            width=15
        )
        self.connect_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Gerenciar IPs",
            command=self._manage_ips,
            width=15
        ).pack(side=tk.LEFT, padx=5)

    def _create_status_bar(self):
        self.status_bar = ttk.Label(
            self.root,
            text="Pronto para conectar",
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Segoe UI", 9)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _load_state(self):
        # Carrega o último usuário se a opção de salvar login estiver ativa
        if self._carregar_salvar_login():
            if (user := carregar_arquivo(Config.ULTIMO_USUARIO_FILE)):
                self.user_entry.insert(0, user)
                # Tenta carregar a senha salva para este usuário
                try:
                    password = keyring.get_password(Config.APP_NAME, user)
                    if password:
                        self.pass_entry.insert(0, password)
                except Exception:
                    pass
                self.status_bar.config(text=f"Usuário carregado: {user}")

        # Carrega o último servidor acessado
        if (ultimo_servidor := carregar_arquivo(Config.ULTIMO_SERVIDOR_FILE)):
            ips = carregar_ips()
            if ultimo_servidor in ips:
                Config.IP_SERVIDOR = ips[ultimo_servidor]
                # Atualiza o combobox para mostrar o último servidor
                valores = list(ips.keys())
                self.server_combobox["values"] = valores
                try:
                    idx = valores.index(ultimo_servidor)
                    self.server_combobox.current(idx)
                except ValueError:
                    self.server_combobox.current(0)
            else:
                self.server_combobox.current(0)
                Config.IP_SERVIDOR = list(ips.values())[0] if ips else ""
        else:
            self._load_servers()

    def _load_servers(self):
        ips = carregar_ips()
        if ips:
            self.server_combobox["values"] = list(ips.keys())
            self.server_combobox.current(0)
            Config.IP_SERVIDOR = list(ips.values())[0]

    def _toggle_theme(self):
        self.tema_atual = "dark" if self.tema_atual == "light" else "light"
        sv_ttk.set_theme(self.tema_atual)
        self._salvar_tema()
        self.root.update()

    def _on_server_select(self, event=None):
        selected = self.server_combobox.get()
        ips = carregar_ips()
        if selected in ips:
            Config.IP_SERVIDOR = ips[selected]
            salvar_arquivo(Config.ULTIMO_SERVIDOR_FILE, selected)
            self.status_bar.config(text=f"Servidor selecionado: {selected}")

    def _connect(self):
        servidor = self.server_combobox.get()
        usuario = self.user_entry.get()
        senha = self.pass_entry.get()
        lembrar_login = self.save_login_var.get()

        if not servidor or not usuario or not senha:
            self.status_bar["text"] = "Preencha todos os campos."
            return

        Config.USUARIO = usuario
        Config.SENHA = senha
        Config.ULTIMO_USUARIO = usuario
        Config.ULTIMO_SERVIDOR = servidor
        Config.IP_SERVIDOR = carregar_ips().get(servidor)

        if not Config.IP_SERVIDOR:
            self.status_bar["text"] = "IP do servidor não encontrado."
            return

        if lembrar_login:
            keyring.set_password(Config.APP_NAME, usuario, senha)
        else:
            try:
                keyring.delete_password(Config.APP_NAME, usuario)
            except keyring.errors.PasswordDeleteError:
                pass

        salvar_arquivo(Config.ULTIMO_USUARIO_FILE, usuario)
        salvar_arquivo(Config.ULTIMO_SERVIDOR_FILE, servidor)

        # Minimiza a janela principal
        self.root.iconify()

        # Chama a função de conexão e espera ela finalizar
        sucesso = conectar_servidor(Config.IP_SERVIDOR, usuario, senha)

        if sucesso:
            self.status_bar["text"] = "Conexão encerrada com sucesso."
        else:
            self.status_bar["text"] = "Falha ao conectar ou conexão encerrada."
    
    def _manage_ips(self):
        ip_win = tk.Toplevel(self.root)
        ip_win.title("Gerenciamento de IPs")
        ip_win.geometry("500x400")
        self.center_window(ip_win, 600, 500)

        main_frame = ttk.Frame(ip_win, padding=20)
        main_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(main_frame, text="Servidores Configurados", font=("Segoe UI", 14)).pack(pady=10)

        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        server_list = tk.Listbox(list_frame, font=("Segoe UI", 10))
        server_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll = ttk.Scrollbar(list_frame, command=server_list.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        server_list.config(yscrollcommand=scroll.set)

        ips = carregar_ips()
        for name, ip in ips.items():
            server_list.insert(tk.END, f"{name:20} | {ip}")

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)

        def adicionar_servidor():
            nome = askstring_focus("Adicionar Servidor", "Nome do servidor:", parent=ip_win)
            if nome:
                ip = askstring_focus("Adicionar Servidor", "IP do servidor:", parent=ip_win)
                if ip:
                    adicionar_ip(nome, ip)
                    server_list.insert(tk.END, f"{nome:20} | {ip}")
                    self._load_servers()                        

        def remover_servidor():
            selecionado = server_list.curselection()
            if selecionado:
                item = server_list.get(selecionado[0])
                nome = item.split("|")[0].strip()
                if remover_ip(nome):
                    server_list.delete(selecionado[0])
                    self._load_servers()

        ttk.Button(btn_frame, text="Adicionar", command=adicionar_servidor, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Remover", command=remover_servidor, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Fechar", command=ip_win.destroy, width=15).pack(side=tk.LEFT, padx=5)

    def center_window(self, window=None, width=500, height=450):
        window = window or self.root
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernConnectionManager(root)
    root.mainloop()
