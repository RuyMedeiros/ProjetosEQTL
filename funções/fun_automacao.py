import pyautogui
import time
import subprocess
from configuracoes import Config
from pywinauto import Desktop

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