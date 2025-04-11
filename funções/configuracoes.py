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