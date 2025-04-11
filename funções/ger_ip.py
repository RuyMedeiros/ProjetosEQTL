from configuracoes import Config
import os

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