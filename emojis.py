# emojis.py

from PyQt6.QtGui import QIcon, QImage
import os
import sys

# --- Função "Mágica" para encontrar arquivos no .exe ---
# Movida para cá para que get_type_icon possa usá-la
def resource_path(relative_path):
    """ Retorna o caminho absoluto para o recurso, funcionando tanto em dev quanto no PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)# emojis.py

from PyQt6.QtGui import QIcon, QImage
import os
import sys

# --- Função "Mágica" para encontrar arquivos no .exe ---
# Movida para cá para que get_type_icon possa usá-la
def resource_path(relative_path):
    """ Retorna o caminho absoluto para o recurso, funcionando tanto em dev quanto no PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Ícones Gerais
LOGO = "Images/logo.png"
LOGO_PEQUENO = "Images/logo_pequeno.png"
CORACAO = "❤️"
ENERGIA = "⚡"
DEFESA = "🛡️"
EXPLOSÃO = "💥"
ATK_ESPECIAL = "🔮"
VELCIDADE = "🏃"
REGENERAR_HP = "❤️‍🔥"
REGENERAR_ENERGIA = "⚡‍🔥"
APOIO = "💖"
CONFIG = "⚙️"
EVOLUIR = "⏫"
LIXEIRA = "🗑️"
MITICO = "🌟"
ADICIONAR = "➕"
REMOVER = "➖"
ENVIAR = "📤"
BUSCAR = "🔍"
EDITAR = "✏️"
SALVAR = "💾"
AVISO = "⚠️"
ERRO = "❌"
SUCESSO = "✅"
AJUDA = "❓"
IVS = "🔢"
EVS = "📈"
LOCALIZAÇÃO = "📍"
MAPA = "🗺️"
SIMULADOR = "🎮"
INFO = "ℹ️"
FLECHA_DIREITA = "➡️"
FLECHA_ESQUERDA = "⬅️"
FLECHA_CIMA = "⬆️"
FLECHA_BAIXO = "⬇️"
FLECHA_DUPLA_DIREITA = "⏩"
FLECHA_DUPLA_ESQUERDA = "⏪"
FLECHA_DUPLA_CIMA = "⏫"
FLECHA_DUPLA_BAIXO = "⏬"
RELÓGIO = "⏰"
CALENDÁRIO = "📅"
CALIBRAR = "📏"
ALVO = "🎯"
LÍNGUA = "🗣️"
LÂMPADA = "💡"
VARRER = "🧹"
CAMERA = "📷"
HOTKEY = "⌨️"
# Emojis de Status
CARREGANDO = "⏳"
ERRO_CARREGAMENTO = "❗"
STATUS = "📊"
# Emojis de Ação
INICIAR = "▶️"
PAUSAR = "⏸️"
PARAR = "⏹️"
# Emojis de Navegação
NAVEGAR = "🌐"
# Emojis de Comunicação
CHAT = "💬"  
# Emojis de Mídia
IMAGEM = "🖼️"
AUDIO = "🎵"
VIDEO = "🎥"
# Emojis de Reações
GOSTEI = "👍"
TRISTE = "👎"
# Emojis de Emoções
FELIZ = "😊"
TRISTE = "😢"
# Emojis de Eventos
EVENTO = "🎉"
# Emojis de Status de Rede
REDE_ONLINE = "🌐"
REDE_OFFLINE = "🚫"
# Emojis de Pokémon
TYPE_ICONS = {
    "Fire": "Images/fogo.png",
    "Ground": "Images/terra.png",
    "Water": "Images/agua.png",
    "Poison": "Images/veneno.png",
    "Psychic": "Images/psiquico.png",
    "Electric": "Images/eletrico.png",
    "Ghost": "Images/fantasma.png",
    "Ice": "Images/gelo.png",
    "Grass": "Images/planta.png",
    "Dragon": "Images/dragao.png",
    "Dark": "Images/sombrio.png",
    "Flying": "Images/voador.png",
    "Rock": "Images/pedra.png",
    "Fairy": "Images/fada.png",
    "Bug": "Images/inseto.png",
    "Fighting": "Images/lutador.png",
    "Steel": "Images/metalico.png",
    "Normal": "Images/normal.png"
}
# --- CAMINHOS PARA SPRITESHEETS ---
# Presume que você tem pastas /Images/hearts e /Images/energy
# com arquivos numerados de 0 a 11 (ex: heart_0.png, heart_1.png, etc.)
HP_BASE = "Images/hp/hp_"
ENERGY_BASE = "Images/energy/energy_"
ATTACK_BASE = "Images/attack/attack_"
DEFENSE_BASE = "Images/defense/defense_"
SPECIAL_ATTACK_BASE = "Images/special_attack/special_attack_"
SPECIAL_DEFENSE_BASE = "Images/special_defense/special_defense_"
SPEED_BASE = "Images/speed/speed_"
HPREGEN_BASE = "Images/hp_regen/hp_regen_"
ENERGYREGEN_BASE = "Images/energy_regen/energy_regen_"

# Emojis de Status de Batalha
SHINY = "✨"
BOSS = "👑"
POKEBOLA = "Images/pokebola.png"
ESCUDO = "🛡️"
ESPADA = "⚔️"
PATAS = "🐾"
TROFÉU = "🏆"
TEMA = "🎨"
CERÉBRAL = "🧠"
VITÓRIA = "🏅"
COMEMORAÇÃO = "🎊"
DERROTA = "💔"
MUKI = "💪"
RESISTÊNCIA = "🛡️"
FRACO = "💢"
DOENTE = "🤒"
MACHUCADO = "🤕"
# Outros
DINHEIRO = "💰"


def get_type_icon(type_name: str) -> QImage | None:
    """
    Recebe o nome de um tipo e retorna o QIcon correspondente.
    """
    # 1. Pega o caminho relativo do dicionário
    relative_path = TYPE_ICONS.get(type_name)
    
    if relative_path:
        # 2. Usa a função resource_path para obter o caminho absoluto e correto
        absolute_path = resource_path(relative_path)

        # --- LINHA DE DEPURAÇÃO ---
        # Esta linha vai te dizer o que está acontecendo no terminal.
        print(f"Procurando por '{type_name}': Caminho = '{absolute_path}' | Arquivo existe? {os.path.exists(absolute_path)}")
        
        # 3. Verifica se o arquivo realmente existe nesse caminho final
        if os.path.exists(absolute_path):
            return QIcon(absolute_path)
            
    return None

# Ícones Gerais
LOGO = "Images/logo.png"
LOGO_PEQUENO = "Images/logo_pequeno.png"
CORACAO = "❤️"
ENERGIA = "⚡"
DEFESA = "🛡️"
EXPLOSÃO = "💥"
ATK_ESPECIAL = "🔮"
VELCIDADE = "🏃"
REGENERAR_HP = "❤️‍🔥"
REGENERAR_ENERGIA = "⚡‍🔥"
APOIO = "💖"
CONFIG = "⚙️"
EVOLUIR = "⏫"
LIXEIRA = "🗑️"
MITICO = "🌟"
ADICIONAR = "➕"
REMOVER = "➖"
ENVIAR = "📤"
BUSCAR = "🔍"
EDITAR = "✏️"
SALVAR = "💾"
AVISO = "⚠️"
ERRO = "❌"
SUCESSO = "✅"
AJUDA = "❓"
IVS = "🔢"
EVS = "📈"
LOCALIZAÇÃO = "📍"
MAPA = "🗺️"
SIMULADOR = "🎮"
INFO = "ℹ️"
FLECHA_DIREITA = "➡️"
FLECHA_ESQUERDA = "⬅️"
FLECHA_CIMA = "⬆️"
FLECHA_BAIXO = "⬇️"
FLECHA_DUPLA_DIREITA = "⏩"
FLECHA_DUPLA_ESQUERDA = "⏪"
FLECHA_DUPLA_CIMA = "⏫"
FLECHA_DUPLA_BAIXO = "⏬"
RELÓGIO = "⏰"
CALENDÁRIO = "📅"
CALIBRAR = "📏"
ALVO = "🎯"
LÍNGUA = "🗣️"
LÂMPADA = "💡"
VARRER = "🧹"
CAMERA = "📷"
HOTKEY = "⌨️"
# Emojis de Status
CARREGANDO = "⏳"
ERRO_CARREGAMENTO = "❗"
STATUS = "📊"
# Emojis de Ação
INICIAR = "▶️"
PAUSAR = "⏸️"
PARAR = "⏹️"
# Emojis de Navegação
NAVEGAR = "🌐"
# Emojis de Comunicação
CHAT = "💬"  
# Emojis de Mídia
IMAGEM = "🖼️"
AUDIO = "🎵"
VIDEO = "🎥"
# Emojis de Reações
GOSTEI = "👍"
TRISTE = "👎"
# Emojis de Emoções
FELIZ = "😊"
TRISTE = "😢"
# Emojis de Eventos
EVENTO = "🎉"
# Emojis de Status de Rede
REDE_ONLINE = "🌐"
REDE_OFFLINE = "🚫"
# Emojis de Pokémon
TYPE_ICONS = {
    "Fire": "Images/fogo.png",
    "Ground": "Images/terra.png",
    "Water": "Images/agua.png",
    "Poison": "Images/veneno.png",
    "Psychic": "Images/psiquico.png",
    "Electric": "Images/eletrico.png",
    "Ghost": "Images/fantasma.png",
    "Ice": "Images/gelo.png",
    "Grass": "Images/planta.png",
    "Dragon": "Images/dragao.png",
    "Dark": "Images/sombrio.png",
    "Flying": "Images/voador.png",
    "Rock": "Images/pedra.png",
    "Fairy": "Images/fada.png",
    "Bug": "Images/inseto.png",
    "Fighting": "Images/lutador.png",
    "Steel": "Images/metalico.png",
    "Normal": "Images/normal.png"
}
# --- CAMINHOS PARA SPRITESHEETS ---
# Presume que você tem pastas /Images/hearts e /Images/energy
# com arquivos numerados de 0 a 11 (ex: heart_0.png, heart_1.png, etc.)
HEARTS_BASE = "Images/hearts/hearts_"
ENERGY_BASE = "Images/energy/energy_"
ATTACK_BASE = "Images/attack/attack_"
DEFENSE_BASE = "Images/defense/defense_"
SPECIAL_ATTACK_BASE = "Images/special_attack/special_attack_"
SPECIAL_DEFENSE_BASE = "Images/special_defense/special_defense_"
SPEED_BASE = "Images/speed/speed_"
HPREGEN_BASE = "Images/hp_regen/hp_regen_"
ENERGYREGEN_BASE = "Images/energy_regen/energy_regen_"
# Emojis de Status de Batalha
SHINY = "✨"
BOSS = "👑"
POKEBOLA = "Images/pokebola.png"
ESCUDO = "🛡️"
ESPADA = "⚔️"
PATAS = "🐾"
TROFÉU = "🏆"
TEMA = "🎨"
CERÉBRAL = "🧠"
VITÓRIA = "🏅"
COMEMORAÇÃO = "🎊"
DERROTA = "💔"
MUKI = "💪"
RESISTÊNCIA = "🛡️"
FRACO = "💢"
DOENTE = "🤒"
MACHUCADO = "🤕"
# Outros
DINHEIRO = "💰"


def get_type_icon(type_name: str) -> QImage | None:
    """
    Recebe o nome de um tipo e retorna o QIcon correspondente.
    """
    # 1. Pega o caminho relativo do dicionário
    relative_path = TYPE_ICONS.get(type_name)
    
    if relative_path:
        # 2. Usa a função resource_path para obter o caminho absoluto e correto
        absolute_path = resource_path(relative_path)

        # --- LINHA DE DEPURAÇÃO ---
        # Esta linha vai te dizer o que está acontecendo no terminal.
        print(f"Procurando por '{type_name}': Caminho = '{absolute_path}' | Arquivo existe? {os.path.exists(absolute_path)}")
        
        # 3. Verifica se o arquivo realmente existe nesse caminho final
        if os.path.exists(absolute_path):
            return QIcon(absolute_path)
            
    return None