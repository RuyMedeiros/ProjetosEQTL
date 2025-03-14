import pyautogui
import time
import keyring
import tkinter as tk
from tkinter import simpledialog, messagebox
import sys

# Definir o serviço
servico = "sistema_remoto"

def conectar_servidor(usuario, senha):
    """Função para conectar ao servidor remoto."""
    pyautogui.hotkey('winleft', 'r')
    pyautogui.write('mstsc')
    pyautogui.press('enter')
    time.sleep(1)

    pyautogui.write('10.17.107.150')
    pyautogui.press('enter')
    time.sleep(3)

    pyautogui.write(senha)  # Insere a senha
    pyautogui.press('enter')
    time.sleep(1)

    pyautogui.press('left')
    pyautogui.press('enter')

    # Fechar a interface após a conexão
    sys.exit()  # Encerra o script completamente

def alterar_senha(usuario):
    """Função para alterar a senha no Keyring."""
    nova_senha = simpledialog.askstring("Alterar Senha", "Digite a nova senha de rede:", show='*')
    if nova_senha:
        keyring.set_password(servico, usuario, nova_senha)
        messagebox.showinfo("Sucesso", "Senha alterada com sucesso!")

def excluir_senha(usuario):
    """Função para excluir a senha do Keyring."""
    keyring.delete_password(servico, usuario)
    messagebox.showinfo("Sucesso", "Senha excluída com sucesso!")

def menu():
    """Menu principal para interação com o usuário."""
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal do tkinter

    while True:
        escolha = simpledialog.askinteger(
            "Menu",
            "--- Menu ---\n"
            "1. Conectar ao servidor remoto\n"
            "2. Alterar senha\n"
            "3. Excluir senha\n"
            "4. Sair\n\n"
            "Escolha uma opção:",
            minvalue=1,
            maxvalue=4
        )

        if escolha == 1:  # Conectar ao servidor remoto
            usuario = simpledialog.askstring("Usuário", "Digite seu nome de usuário de rede:\n(Ex: U12345)")
            if not usuario:
                continue

            senha = keyring.get_password(servico, usuario)
            if not senha:
                senha = simpledialog.askstring("Senha", "Digite sua senha de rede:", show='*')
                if senha:
                    keyring.set_password(servico, usuario, senha)
                else:
                    continue

            conectar_servidor(usuario, senha)

        elif escolha == 2:  # Alterar senha
            usuario = simpledialog.askstring("Usuário", "Digite seu nome de usuário de rede:\n(Ex: U12345)")
            if usuario:
                alterar_senha(usuario)

        elif escolha == 3:  # Excluir senha
            usuario = simpledialog.askstring("Usuário", "Digite seu nome de usuário de rede:\n(Ex: U12345)")
            if usuario:
                excluir_senha(usuario)

        elif escolha == 4:  # Sair
            messagebox.showinfo("Saindo", "Até logo!")
            sys.exit()  # Encerra o script completamente

        else:
            messagebox.showerror("Erro", "Opção inválida. Tente novamente.")

if __name__ == "__main__":
    menu()