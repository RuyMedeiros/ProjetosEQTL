import keyring
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from configuracoes import Config

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