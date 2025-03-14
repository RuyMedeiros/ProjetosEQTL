import pyautogui
import time
import keyring
import getpass

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

def alterar_senha(usuario):
    """Função para alterar a senha no Keyring."""
    nova_senha = getpass.getpass("Digite a nova senha de rede: ")
    keyring.set_password(servico, usuario, nova_senha)
    print("Senha alterada com sucesso!")

def excluir_senha(usuario):
    """Função para excluir a senha do Keyring."""
    keyring.delete_password(servico, usuario)
    print("Senha excluída com sucesso!")

def menu():
    """Menu principal para interação com o usuário."""
    print("\n--- Menu ---")
    print("1. Conectar ao servidor remoto")
    print("2. Alterar senha")
    print("3. Excluir senha")
    print("4. Sair")
    escolha = input("Escolha uma opção: ")
    return escolha

def main():
    # Solicitar o nome de usuário
    usuario = input("Digite seu nome de usuário de rede: ")

    while True:
        escolha = menu()

        if escolha == "1":  # Conectar ao servidor remoto
            senha = keyring.get_password(servico, usuario)
            if not senha:
                print("Senha não encontrada. Por favor, configure uma senha.")
                senha = getpass.getpass("Digite sua senha de rede: ")
                keyring.set_password(servico, usuario, senha)
            conectar_servidor(usuario, senha)

        elif escolha == "2":  # Alterar senha
            alterar_senha(usuario)

        elif escolha == "3":  # Excluir senha
            excluir_senha(usuario)

        elif escolha == "4":  # Sair
            print("Saindo...")
            break

        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()