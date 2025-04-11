import os

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