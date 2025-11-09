import sys
import json
import os
import re
import unicodedata
import traceback
import math
import emojis
import copy
import webbrowser
import sys
import threading
import requests
import base64
import platform
import sound_manager
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QSpinBox, QFormLayout, QMessageBox, QHeaderView, QTextEdit, QFrame, QCompleter,
    QScrollArea, QDialog, QGridLayout, QToolButton, QSizePolicy, QStackedWidget, QListWidget, QListWidgetItem, QScrollArea
)
from PyQt6.QtGui import QIcon, QPixmap, QImage, QColor, QResizeEvent, QPainter, QFont, QCursor
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize, QRect, QBuffer, QByteArray, QEvent, QPoint,QEasingCurve, QPropertyAnimation, QUrl
from animations.factory import get_animation_class, get_available_animations
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

class HorizontalLine(QFrame):
    """Uma linha divisória horizontal simples."""
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setStyleSheet("color: #555;") # Cor cinza

# --- Bloco de Dependências e Configuração ---
try:
    from PIL import Image, ImageGrab
    import pytesseract
    import cv2
    import numpy as np
    from pynput import keyboard
    # --- CONFIGURAÇÃO DO CAMINHO DO TESSERACT ---
    # Se o sistema for Windows, define o caminho manualmente.
    if platform.system() == "Windows":
        # ---> MUDE O CAMINHO ABAIXO PARA O CAMINHO CORRETO NO SEU PC <---
        # Use o caminho que você copiou no Passo 1 e adicione \\tesseract.exe no final.
        # O 'r' antes da string é importante, não o apague!
        caminho_tesseract = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        # Verifica se o arquivo realmente existe antes de definir o caminho
        if os.path.exists(caminho_tesseract):
            pytesseract.pytesseract.tesseract_cmd = caminho_tesseract
        else:
            # Se você errar o caminho, esta mensagem aparecerá no terminal para te ajudar
            print(f"AVISO: O caminho para o Tesseract '{caminho_tesseract}' não foi encontrado!")
            # Tenta um caminho alternativo comum
            caminho_alternativo = r'C:\Users\sergi\AppData\Local\Tesseract-OCR\tesseract.exe'
            if os.path.exists(caminho_alternativo):
                pytesseract.pytesseract.tesseract_cmd = caminho_alternativo
            else:
                print(f"AVISO: O caminho alternativo '{caminho_alternativo}' também não foi encontrado!")
    OCR_ENABLED = True
except ImportError:
    OCR_ENABLED = False
    print("AVISO: Dependências de OCR não encontradas. A 'Calculadora de Stats' será desativada.")
    print("Instale com: pip install Pillow opencv-python pytesseract pynput")

    def close_and_restore(self):
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.close()
        self.parent_window.show()
        self.calibration_done.emit()

# --- Importação da Lógica de Batalha ---
try:
    from battle_logic import BattleLogic, NATURES
except ImportError:
    print("ERRO CRÍTICO: O arquivo 'battle_logic.py' não foi encontrado. A aba de Batalhas não funcionará.")
    BattleLogic = None
    NATURES = {}


# --- Função "Mágica" para encontrar arquivos no .exe ---
def resource_path(relative_path):
    """ Retorna o caminho absoluto para o recurso, funcionando tanto em dev quanto no PyInstaller """
    try:
        # PyInstaller cria uma pasta temporária e a armazena em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # --- A CORREÇÃO ESTÁ AQUI ---
        # Usamos o caminho do ARQUIVO .py, não o diretório de trabalho atual
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# --- DADOS DE EVOLUÇÃO ---
EVOLUTIONS = {
    "Bulbasaur": "Ivysaur", "Ivysaur": "Venusaur", "Charmander": "Charmeleon", "Charmeleon": "Charizard",
    "Squirtle": "Wartortle", "Wartortle": "Blastoise", "Caterpie": "Metapod", "Metapod": "Butterfree",
    "Weedle": "Kakuna", "Kakuna": "Beedrill", "Pidgey": "Pidgeotto", "Pidgeotto": "Pidgeot",
    "Rattata": "Raticate", "Spearow": "Fearow", "Ekans": "Arbok", "Pikachu": "Raichu",
    "Sandshrew": "Sandslash", "NidoranF": "Nidorina", "Nidorina": "Nidoqueen", "NidoranM": "Nidorino",
    "Nidorino": "Nidoking", "Clefairy": "Clefable", "Vulpix": "Ninetales", "Jigglypuff": "Wigglytuff",
    "Zubat": "Golbat", "Golbat": "Crobat", "Oddish": "Gloom", "Paras": "Parasect",
    "Venonat": "Venomoth", "Diglett": "Dugtrio", "Meowth": "Persian", "Psyduck": "Golduck",
    "Mankey": "Primeape", "Growlithe": "Arcanine", "Poliwag": "Poliwhirl",
    "Abra": "Kadabra", "Kadabra": "Alakazam", "Machop": "Machoke", "Machoke": "Machamp",
    "Bellsprout": "Weepinbell", "Weepinbell": "Victreebel", "Tentacool": "Tentacruel", "Geodude": "Graveler",
    "Graveler": "Golem", "Ponyta": "Rapidash", "Magnemite": "Magneton",
    "Doduo": "Dodrio", "Seel": "Dewgong", "Grimer": "Muk", "Shellder": "Cloyster", "Gastly": "Haunter",
    "Haunter": "Gengar", "Onix": "Steelix", "Drowzee": "Hypno", "Krabby": "Kingler", "Voltorb": "Electrode",
    "Exeggcute": "Exeggutor", "Cubone": "Marowak", "Koffing": "Weezing", "Rhyhorn": "Rhydon",
    "Chansey": "Blissey", "Horsea": "Seadra", "Seadra": "Kingdra", "Goldeen": "Seaking",
    "Staryu": "Starmie", "Scyther": "Scizor", "Magikarp": "Gyarados",
    "Omanyte": "Omastar", "Kabuto": "Kabutops", "Dratini": "Dragonair", "Dragonair": "Dragonite",
    "Chikorita": "Bayleef", "Bayleef": "Meganium", "Cyndaquil": "Quilava", "Quilava": "Typhlosion",
    "Totodile": "Croconaw", "Croconaw": "Feraligatr", "Sentret": "Furret", "Hoothoot": "Noctowl",
    "Ledyba": "Ledian", "Spinarak": "Ariados", "Chinchou": "Lanturn", "Pichu": "Pikachu",
    "Cleffa": "Clefairy", "Igglybuff": "Jigglypuff", "Natu": "Xatu", "Mareep": "Flaaffy",
    "Flaaffy": "Ampharos", "Marill": "Azumarill", "Hoppip": "Skiploom", "Skiploom": "Jumpluff",
    "Sunkern": "Sunflora", "Wooper": "Quagsire", "Pineco": "Forretress", "Snubbull": "Granbull",
    "Teddiursa": "Ursaring", "Slugma": "Magcargo", "Swinub": "Piloswine", "Remoraid": "Octillery",
    "Houndour": "Houndoom", "Phanpy": "Donphan", "Smoochum": "Jynx", "Elekid": "Electabuzz", "Electabuzz": "Electivire",
    "Magby": "Magmar", "Larvitar": "Pupitar", "Pupitar": "Tyranitar", "Mudkip": "Marshtomp", "Marshtomp": "Swampert", "Treecko": "Grovyle", "Grovyle": "Sceptile", "Torchic": "Combusken", "Combusken": "Blaziken",
    # Exemplo de multi-evolução
    "Tyrogue": ["Hitmonlee", "Hitmonchan", "Hitmontop"],
    "Eevee": ["Vaporeon", "Jolteon", "Flareon", "Espeon", "Umbreon",],
    "Gloom": ["Vileplume", "Bellossom"],
    "Poliwhirl": ["Poliwrath", "Politoed"],
    "Slowpoke": ["Slowbro", "Slowking"],
}

# --- Funções Auxiliares ---
def get_user_data_path(filename):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".") 
    data_folder_path = os.path.join(base_path, 'data')
    os.makedirs(data_folder_path, exist_ok=True)
    return os.path.join(data_folder_path, filename)

def load_json(filename, default_data=None, is_user_data=False):
    if is_user_data:
        filepath = get_user_data_path(filename)
        if not os.path.exists(filepath):
            if default_data is not None:
                save_json(filename, default_data, is_user_data=True)
                return copy.deepcopy(default_data)
            return {} if 'teams' in filename else []
    else:
        filepath = resource_path(filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f: return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError): 
        return copy.deepcopy(default_data) if default_data is not None else {}

def save_json(filename, data, is_user_data=True):
    filepath = get_user_data_path(filename)
    with open(filepath, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4, ensure_ascii=False)

def normalize_name(name):
    if not name: return ""
    name = re.sub(r'\.png$', '', name, flags=re.IGNORECASE)
    nfkd_form = unicodedata.normalize('NFD', name)
    only_ascii = nfkd_form.encode('ASCII', 'ignore').decode('utf-8')
    alphanumeric_only = re.sub(r'[^a-zA-Z0-9]', '', only_ascii)
    return alphanumeric_only.lower()

def get_pokemon_image_path(pokemon_name):
    if not pokemon_name: return None
    image_folder = resource_path('Images')
    if not os.path.isdir(image_folder): return None
    normalized_search_name = normalize_name(pokemon_name)
    if not normalized_search_name: return None
    try:
        for filename in os.listdir(image_folder):
            if filename.lower().endswith('.png'):
                file_base_name = os.path.splitext(filename)[0]
                if normalized_search_name == normalize_name(file_base_name):
                    return os.path.join(image_folder, filename)
    except FileNotFoundError: return None
    return None

def get_map_image_path(location_name):
    if not location_name: return None
    map_folder = resource_path('Maps')
    if not os.path.isdir(map_folder): return None
    filename = location_name.replace(' ', '_') + '_Map.png'
    filepath = os.path.join(map_folder, filename)
    return filepath if os.path.exists(filepath) else None

def load_pixmap_robustly(image_path, target_size_w, target_size_h=None):
    if target_size_h is None: target_size_h = target_size_w
    if not image_path or not os.path.exists(image_path) or target_size_w <= 0 or target_size_h <= 0: return None
    try:
        normalized_path = image_path.replace('\\', '/')
        with Image.open(normalized_path) as img:
            img = img.convert("RGBA")
            qimage = QImage(img.tobytes("raw", "RGBA"), img.width, img.height, QImage.Format.Format_RGBA8888)
            if qimage.isNull(): return None
            pixmap = QPixmap.fromImage(qimage)
            return pixmap.scaled(target_size_w, target_size_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    except Exception:
        traceback.print_exc()
        return None

# --- FUNÇÃO CENTRALIZADA E ROBUSTA PARA CARREGAR ÍCONES ---
def get_icon_from_path(relative_path: str) -> QIcon | None:
    """
    Carrega um QIcon de um caminho relativo, usando o método robusto de Pillow para evitar problemas de plugin do Qt.
    """
    if not relative_path:
        return None
        
    absolute_path = resource_path(relative_path)
    if not os.path.exists(absolute_path):
        return None

    pixmap = load_pixmap_robustly(absolute_path, 64, 64)
    
    if not pixmap or pixmap.isNull():
        print(f"AVISO: Falha ao carregar pixmap (via PIL) de '{absolute_path}'.")
        return None
    
    icon = QIcon(pixmap)
    if icon.isNull():
        print(f"AVISO: Falha ao criar QIcon a partir de pixmap para '{absolute_path}'.")
        return None
        
    return icon
    
# --- NOVA FUNÇÃO PARA BARRA DE STATS DINÂMICA ---
def get_dynamic_stat_bar(parent_window, stat_name: str, current_value: int, context: str = 'final') -> QPixmap | None:
    """
    Retorna o QPixmap da barra de status.
    Versão corrigida para lidar com todos os 9 stats.
    """
    num_frames = 13 # 0 a 12

    if context == 'base':
        # Sua lógica de escala dinâmica (agora funciona para todos os stats da lista)
        if stat_name in parent_window.stat_ranges['base']:
            ranges = parent_window.stat_ranges['base'][stat_name]
            min_val, max_val = ranges['min'], ranges['max']
            
            if max_val == min_val: percentage = 1.0
            else: percentage = (current_value - min_val) / (max_val - min_val)
        else:
            return None
    
    else: # context == 'final'
        # AGORA USA A RÉGUA DINÂMICA CALCULADA!
        if stat_name in parent_window.stat_ranges['final']:
            max_val = parent_window.stat_ranges['final'][stat_name]['max']
            if max_val == 0: percentage = 1.0
            else: percentage = current_value / max_val
        else: # Fallback para o valor antigo se algo der errado
            max_possible_value = 600
            if stat_name == 'hp': max_possible_value = 2000
            percentage = current_value / max_possible_value

    percentage = min(max(percentage, 0), 1)
    frame_index = min(int(percentage * (num_frames -1)) + 1, num_frames -1) if percentage > 0 else 0
    if percentage > 0.99: frame_index = num_frames -1

    # CORREÇÃO: Adicionamos os paths para hp_reg e en_reg
    path_map = {
        'hp': emojis.HP_BASE, 'energy': emojis.ENERGY_BASE,
        'attack': emojis.ATTACK_BASE, 'defense': emojis.DEFENSE_BASE,
        'special-attack': emojis.SPECIAL_ATTACK_BASE,
        'special-defense': emojis.SPECIAL_DEFENSE_BASE, 'speed': emojis.SPEED_BASE,
        'hp_reg': emojis.HPREGEN_BASE, 'en_reg': emojis.ENERGYREGEN_BASE
    }
    base_path = path_map.get(stat_name)
    if not base_path: return None

    image_path = resource_path(f"{base_path}{frame_index:02d}.png")
    if not os.path.exists(image_path):
        return None

    return load_pixmap_robustly(image_path, 64, 16)


def format_time(seconds):
    if seconds is None or seconds < 0 or math.isinf(seconds) or math.isnan(seconds): return "N/A"
    if seconds > 3600 * 24: return "Infinito"
    minutes, sec = divmod(seconds, 60)
    if minutes > 0: return f"{int(minutes)}m {int(sec)}s"
    return f"{sec:.2f}s"

def format_timedelta(td):
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f'{hours:02}:{minutes:02}:{seconds:02}'

# --- Classes das Abas ---
class CalibrationWindow(QWidget):
    calibration_done = pyqtSignal()

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.start_point = None
        self.instruction_label = QLabel(self)
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instruction_label.setStyleSheet(
            "background-color: rgba(0, 0, 0, 0.75); color: white; font-size: 24px; font-weight: bold; padding: 20px; border-radius: 15px;")
        self.instruction_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        self.steps = [
            ("nickname", self.parent_window.get_string("calibration.area_nickname", "o Apelido do Pokémon")),
            ("species", self.parent_window.get_string("calibration.area_species", "a Espécie do Pokémon")),
            ("level", self.parent_window.get_string("calibration.area_level", "o Nível do Pokémon")),
            ("nature", self.parent_window.get_string("calibration.area_nature", "a Natureza do Pokémon")),
            ("hp_iv", self.parent_window.get_string("calibration.area_hp_iv", "o número do IV HP")),
            ("energy_iv", self.parent_window.get_string("calibration.area_energy_iv", "o número do IV Energy")),
            ("attack_iv", self.parent_window.get_string("calibration.area_attack_iv", "o número do IV Attack")),
            ("defense_iv", self.parent_window.get_string("calibration.area_defense_iv", "o número do IV Defense")),
            ("special-attack_iv", self.parent_window.get_string("calibration.area_special_attack_iv", "o número do IV Sp. Atk")),
            ("special-defense_iv", self.parent_window.get_string("calibration.area_special_defense_iv", "o número do IV Sp. Def")),
            ("speed_iv", self.parent_window.get_string("calibration.area_speed_iv", "o número do IV Speed")),
            ("hp_reg_iv", self.parent_window.get_string("calibration.area_hp_reg_iv", "o número do IV HP Reg")),
            ("en_reg_iv", self.parent_window.get_string("calibration.area_en_reg_iv", "o número do IV EN Reg")),
            ("hp_ev", self.parent_window.get_string("calibration.area_hp_ev", "o número do EV HP")),
            ("energy_ev", self.parent_window.get_string("calibration.area_energy_ev", "o número do EV Energy")),
            ("attack_ev", self.parent_window.get_string("calibration.area_attack_ev", "o número do EV Attack")),
            ("defense_ev", self.parent_window.get_string("calibration.area_defense_ev", "o número do EV Defense")),
            ("special-attack_ev", self.parent_window.get_string("calibration.area_special_attack_ev", "o número do EV Sp. Atk")),
            ("special-defense_ev", self.parent_window.get_string("calibration.area_special_defense_ev", "o número do EV Sp. Def")),
            ("speed_ev", self.parent_window.get_string("calibration.area_speed_ev", "o número do EV Speed")),
            ("hp_reg_ev", self.parent_window.get_string("calibration.area_hp_reg_ev", "o número do EV HP Reg")),
            ("en_reg_ev", self.parent_window.get_string("calibration.area_en_reg_ev", "o número do EV EN Reg")),
        ]
        self.current_step = 0
        self.coordinates = {}

    def start(self):
        self.parent_window.hide()
        self.showFullScreen()
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.update_instruction()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 70))
        super().paintEvent(event)

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        screen_rect = self.rect()
        label_size_hint = self.instruction_label.sizeHint()
        x = (screen_rect.width() - label_size_hint.width()) / 2
        y = (screen_rect.height() - label_size_hint.height()) / 2
        self.instruction_label.setGeometry(int(x), int(y), label_size_hint.width(), label_size_hint.height())

    def update_instruction(self):
        if self.current_step < len(self.steps):
            _, stat_name_desc = self.steps[self.current_step]
            self.instruction_label.setText(
                self.parent_window.get_string("calibration.instruction").format(area=stat_name_desc))
        else:
            self.finish_calibration()
        self.instruction_label.adjustSize()
        self.resizeEvent(QResizeEvent(self.size(), self.size()))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.start_point:
            end_point = event.globalPosition().toPoint()
            left = min(self.start_point.x(), end_point.x())
            top = min(self.start_point.y(), end_point.y())
            right = max(self.start_point.x(), end_point.x())
            bottom = max(self.start_point.y(), end_point.y())
            
            if (right - left) > 0 and (bottom - top) > 0:
                stat_key, _ = self.steps[self.current_step]
                self.coordinates[stat_key] = (left, top, right, bottom)
                self.current_step += 1

            self.start_point = None
            self.update_instruction()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.cancel_calibration()

    def finish_calibration(self):
        save_json("ocr_config.json", self.coordinates)
        QMessageBox.information(self.parent_window, self.parent_window.get_string("globals.success"), self.parent_window.get_string("calibration.success_message"))
        self.close_and_restore()

    def cancel_calibration(self):
        self.close_and_restore()

    def close_and_restore(self):
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.close()
        self.parent_window.show()
        self.calibration_done.emit()

# --- NOVA CLASSE: EvolutionDialog ---
class EvolutionDialog(QDialog):
    """
    Uma janela de diálogo para o usuário atualizar os dados de um Pokémon ao evoluir.
    """
    def __init__(self, current_pokemon, next_evolution_name, pokemon_data, parent_window):
        super().__init__(parent_window)
        self.parent_window = parent_window
        self.current_pokemon = current_pokemon
        self.next_evolution_name = next_evolution_name
        self.pokemon_data = pokemon_data
        self.stats = list(current_pokemon.get("ivs", {}).keys())
        self.stat_labels = parent_window.collection_tab.stat_labels
        
        self.setWindowTitle(self.parent_window.get_string("evolution.window_title").format(name=(current_pokemon.get('nickname') or current_pokemon['species'])))
        self.setMinimumWidth(400)

        # Dados do Pokémon evoluído que serão retornados
        self.evolved_pokemon_data = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # --- Display Visual da Evolução ---
        evo_display_layout = QHBoxLayout()
        evo_display_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Imagem do Pokémon Atual
        self.img_before = QLabel()
        self.img_before.setFixedSize(80, 80)
        path_before = get_pokemon_image_path(self.current_pokemon['species'])
        if pixmap := load_pixmap_robustly(path_before, 80):
            self.img_before.setPixmap(pixmap)
            
        # Seta
        arrow = QLabel(emojis.FLECHA_DIREITA)
        arrow.setStyleSheet("font-size: 24px;")
        
        # Imagem da Evolução
        self.img_after = QLabel()
        self.img_after.setFixedSize(80, 80)
        path_after = get_pokemon_image_path(self.next_evolution_name)
        if pixmap := load_pixmap_robustly(path_after, 80):
            self.img_after.setPixmap(pixmap)
            
        evo_display_layout.addWidget(self.img_before)
        evo_display_layout.addWidget(arrow)
        evo_display_layout.addWidget(self.img_after)
        layout.addLayout(evo_display_layout)
        
        title = QLabel(f"<b>{self.current_pokemon['species']}</b> {emojis.FLECHA_DIREITA} <b>{self.next_evolution_name}</b>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # --- Formulário de Atualização ---
        form_layout = QFormLayout()
        
        self.level_input = QSpinBox()
        self.level_input.setRange(self.current_pokemon['level'], 200)
        self.level_input.setValue(self.current_pokemon['level'])
        form_layout.addRow(self.parent_window.get_string("globals.level"), self.level_input)
        
        form_layout.addRow(QLabel(f"--- <b>{self.parent_window.get_string('evolution.ivs_label')}</b> ---"))
        for stat in self.stats:
            iv_value = self.current_pokemon.get("ivs", {}).get(stat, 0)
            form_layout.addRow(f"IV {self.stat_labels[stat]}:", QLabel(f"<b>{iv_value}</b>"))
            
        form_layout.addRow(QLabel(f"--- <b>{self.parent_window.get_string('evolution.evs_label')}</b> ---"))
        self.ev_inputs = {}
        for stat in self.stats:
            self.ev_inputs[stat] = QSpinBox()
            self.ev_inputs[stat].setRange(0, 5000)
            self.ev_inputs[stat].setValue(self.current_pokemon.get("evs", {}).get(stat, 0))
            form_layout.addRow(f"EV {self.stat_labels[stat]}:", self.ev_inputs[stat])
            
        layout.addLayout(form_layout)
        
        # --- Botões de Ação ---
        button_box = QHBoxLayout()
        self.cancel_btn = QPushButton(self.parent_window.get_string("globals.cancel"))
        self.confirm_btn = QPushButton(f"{emojis.SUCESSO} {self.parent_window.get_string('evolution.confirm_button')}")
        self.cancel_btn.clicked.connect(self.reject)
        self.confirm_btn.clicked.connect(self.confirm_evolution)
        button_box.addWidget(self.cancel_btn)
        button_box.addWidget(self.confirm_btn)
        layout.addLayout(button_box)

    def confirm_evolution(self):
        # Monta o dicionário do novo Pokémon
        self.evolved_pokemon_data = {
            "nickname": self.current_pokemon.get("nickname", ""),
            "species": self.next_evolution_name,
            "level": self.level_input.value(),
            "nature": self.current_pokemon.get("nature", "Hardy"),
            "ivs": self.current_pokemon.get("ivs", {}), # IVs não mudam
            "evs": {name: widget.value() for name, widget in self.ev_inputs.items()},
            "notes": self.current_pokemon.get("notes", "")
        }
        self.accept()

# --- FIM DA NOVA CLASSE ---

# --- NOVA CLASSE: MultipleEvolutionChoiceDialog ---
class MultipleEvolutionChoiceDialog(QDialog):
    """
    Um diálogo para o usuário escolher para qual Pokémon evoluir quando há múltiplas opções.
    """
    def __init__(self, evolution_options, parent=None):
        super().__init__(parent)
        self.selected_evolution = None
        self.setWindowTitle(parent.get_string("evolution.choice_title"))
        
        layout = QVBoxLayout(self)
        label = QLabel(parent.get_string("evolution.choice_label"))
        layout.addWidget(label)
        
        buttons_layout = QGridLayout()
        for i, name in enumerate(evolution_options):
            btn = QPushButton(name)
            
            icon = get_icon_from_path(get_pokemon_image_path(name))
            if icon:
                btn.setIcon(icon)
                btn.setIconSize(QSize(48, 48))
                
            btn.clicked.connect(lambda _, n=name: self.select_option(n))
            row, col = divmod(i, 3) # Organiza em até 3 colunas
            buttons_layout.addWidget(btn, row, col)
            
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def select_option(self, name):
        self.selected_evolution = name
        self.accept()

class CollectionTab(QWidget):
    collection_updated = pyqtSignal()

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.parent_window.pokemon_data = load_json("pokemon_data.json") #muda aqui
        self.natures = sorted(NATURES.keys()) if NATURES else []
        self.stats = ["hp", "energy", "attack", "defense", "special-attack", "special-defense", "speed", "hp_reg", "en_reg"]
        self.stat_labels = {
            "hp": "HP", "energy": "EN", "attack": "Attack", "defense": "Defense",
            "special-attack": "Sp. Atk", "special-defense": "Sp. Def", "speed": "Speed",
            "hp_reg": "HP Reg", "en_reg": "EN Reg"
        }
        self.pokedex_order = {name: i for i, name in enumerate(self.parent_window.pokemon_data.keys())} #muda aqui
        self.animation_widget = None 
        
        self.init_ui()
        self.load_collection()

    def retranslate_ui(self):
        """Atualiza todos os textos da aba para o idioma selecionado, sem recriar a UI."""
        self.image_display.setText(self.parent_window.get_string("collection.select_to_see_image"))
        
        # Atualiza os labels do formulário (agora com referências salvas)
        self.nickname_label.setText(self.parent_window.get_string("globals.nickname"))
        self.species_label.setText(self.parent_window.get_string("globals.species"))
        self.level_label.setText(self.parent_window.get_string("globals.level"))
        self.nature_label.setText(self.parent_window.get_string("globals.nature"))
        self.notes_label.setText(self.parent_window.get_string("globals.notes"))

        # Atualiza os botões
        self.add_btn.setText(f"{emojis.ADICIONAR} {self.parent_window.get_string('collection.add_button')}")
        self.save_btn.setText(f"{emojis.SALVAR} {self.parent_window.get_string('collection.save_button')}")
        self.clear_btn.setText(f"{emojis.VARRER} {self.parent_window.get_string('collection.clear_button')}")
        
        # Atualiza os cabeçalhos da tabela
        headers = [
            "", "ID_Original", self.parent_window.get_string("globals.nickname"), self.parent_window.get_string("globals.species"),
            self.parent_window.get_string("globals.level"), self.parent_window.get_string("globals.nature"), "IVs", "EVs",
            self.parent_window.get_string("globals.edit"), self.parent_window.get_string("collection.evolve_tooltip"),
            self.parent_window.get_string("globals.remove"), self.parent_window.get_string("globals.notes_header")
        ]
        self.table.setHorizontalHeaderLabels(headers)
        
        # Atualiza o seletor de ordenação
        self.sort_label.setText(self.parent_window.get_string("collection.sort_by_label"))
        current_sort_index = self.sort_combo.currentIndex()
        self.sort_combo.setItemText(0, self.parent_window.get_string("collection.sort_alpha"))
        self.sort_combo.setItemText(1, self.parent_window.get_string("collection.sort_pokedex"))
        self.sort_combo.setCurrentIndex(current_sort_index)

        # Atualiza o cabeçalho do painel de stats finais
        self.final_stats_title_label.setText(f"<b>{self.parent_window.get_string('ocr.final_stats_header', 'Stats Finais')}</b>")

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        left_vbox = QVBoxLayout()
        
        self.image_display = QLabel(self.parent_window.get_string("collection.select_to_see_image"))
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_display.setFixedSize(128, 128)
        self.image_display.setFrameShape(QFrame.Shape.StyledPanel)
        self.image_display.setWordWrap(True)
        
        form_container = QWidget()
        form_layout = QFormLayout(form_container)
        form_layout.setContentsMargins(10, 10, 10, 10)
        
        self.nickname_input = QLineEdit()
        self.species_input = QComboBox()
        self.species_input.setEditable(True)
        pokemon_list = self.parent_window.get_sorted_pokemon_list()
        self.species_input.addItems([""] + pokemon_list)
        self.completer = QCompleter(pokemon_list, self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.species_input.setCompleter(self.completer)
        
        self.level_input = QSpinBox()
        self.level_input.setRange(1, 200)
        self.level_input.setValue(1) # Garante que o valor inicial seja 1
        self.nature_input = QComboBox()
        self.nature_input.addItems(self.natures)

        self.nickname_label = QLabel(self.parent_window.get_string("globals.nickname"))
        self.species_label = QLabel(self.parent_window.get_string("globals.species"))
        self.level_label = QLabel(self.parent_window.get_string("globals.level"))
        self.nature_label = QLabel(self.parent_window.get_string("globals.nature"))
        
        form_layout.addRow(self.nickname_label, self.nickname_input)
        form_layout.addRow(self.species_label, self.species_input)
        form_layout.addRow(self.level_label, self.level_input)
        form_layout.addRow(self.nature_label, self.nature_input)

        stats_layout = QHBoxLayout()
        
        iv_group = QFrame()
        iv_form = QFormLayout(iv_group)
        iv_form.addRow(QLabel(f"<b>{self.parent_window.get_string('globals.ivs')}</b>"))
        self.iv_inputs = {}
        for stat_key in self.stats:
            self.iv_inputs[stat_key] = QSpinBox()
            self.iv_inputs[stat_key].setRange(0, 31)
            iv_form.addRow(f"IV {self.stat_labels[stat_key]}:", self.iv_inputs[stat_key])
        stats_layout.addWidget(iv_group)
        
        ev_group = QFrame()
        ev_form = QFormLayout(ev_group)
        ev_form.addRow(QLabel(f"<b>{self.parent_window.get_string('globals.evs')}</b>"))
        self.ev_inputs = {}
        for stat_key in self.stats:
            self.ev_inputs[stat_key] = QSpinBox()
            self.ev_inputs[stat_key].setRange(0, 5000)
            ev_form.addRow(f"EV {self.stat_labels[stat_key]}:", self.ev_inputs[stat_key])
        stats_layout.addWidget(ev_group)
        
        self.final_stats_frame = QFrame()
        self.final_stats_frame.setFrameShape(QFrame.Shape.StyledPanel)
        final_stats_layout = QFormLayout(self.final_stats_frame)
        self.final_stats_title_label = QLabel(f"<b>{self.parent_window.get_string('ocr.final_stats_header', 'Stats Finais')}</b>")
        final_stats_layout.addRow(self.final_stats_title_label)
        self.final_stat_labels = {}
        self.stat_bar_labels = {}
        for stat in self.stats:
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            self.final_stat_labels[stat] = QLabel("?")
            row_layout.addWidget(self.final_stat_labels[stat])
            self.stat_bar_labels[stat] = QLabel()
            self.stat_bar_labels[stat].setFixedSize(64, 16)
            row_layout.addWidget(self.stat_bar_labels[stat])
            row_layout.addStretch()
            final_stats_layout.addRow(f"{self.stat_labels[stat]}:", row_widget)
        stats_layout.addWidget(self.final_stats_frame)
        
        form_layout.addRow(stats_layout)
        
        self.notes_input = QTextEdit()
        self.notes_input.setFixedHeight(60)
        self.notes_label = QLabel(self.parent_window.get_string("globals.notes"))
        form_layout.addRow(self.notes_label, self.notes_input)
        
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton(f"{emojis.ADICIONAR} {self.parent_window.get_string('collection.add_button')}")
        self.save_btn = QPushButton(f"{emojis.SALVAR} {self.parent_window.get_string('collection.save_button')}")
        self.clear_btn = QPushButton(f"{emojis.VARRER} {self.parent_window.get_string('collection.clear_button')}")
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.clear_btn)
        
        left_vbox.addWidget(self.image_display, alignment=Qt.AlignmentFlag.AlignCenter)
        left_vbox.addWidget(form_container)
        left_vbox.addLayout(button_layout)
        left_vbox.addStretch()
        
        table_container = QWidget()
        right_vbox = QVBoxLayout(table_container)
        
        sort_layout = QHBoxLayout()
        self.sort_label = QLabel(self.parent_window.get_string("collection.sort_by_label"))
        sort_layout.addWidget(self.sort_label)
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            self.parent_window.get_string("collection.sort_alpha"),
            self.parent_window.get_string("collection.sort_pokedex")
        ])
        sort_layout.addStretch()
        sort_layout.addWidget(self.sort_combo)
        right_vbox.addLayout(sort_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(13)
        headers = [
             "", "ID_Original", self.parent_window.get_string("globals.nickname"), self.parent_window.get_string("globals.species"),
            self.parent_window.get_string("globals.level"), self.parent_window.get_string("globals.nature"), "IVs", "EVs",
            self.parent_window.get_string("ocr.final_stats_header", "Stats Finais"), # <-- NOVA COLUNA AQUI
            self.parent_window.get_string("globals.edit"), self.parent_window.get_string("collection.evolve_tooltip"),
            self.parent_window.get_string("globals.remove"), self.parent_window.get_string("globals.notes_header")
        ]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setColumnHidden(1, True)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 64)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        right_vbox.addWidget(self.table)
        
        main_layout.addLayout(left_vbox, 1)
        main_layout.addWidget(table_container, 2)
        self.final_stats_frame.hide()

        # CONEXÕES DE SINAIS
        self.add_btn.clicked.connect(self.add_pokemon)
        self.save_btn.clicked.connect(self.save_pokemon)
        self.clear_btn.clicked.connect(self.clear_form)
        self.sort_combo.currentIndexChanged.connect(self.reload_and_sort_collection)
        self.species_input.currentTextChanged.connect(self.update_form_image)
        self.species_input.currentTextChanged.connect(self.update_stats_from_form)
        self.level_input.valueChanged.connect(self.update_stats_from_form)
        self.nature_input.currentTextChanged.connect(self.update_stats_from_form)
        for widget in self.iv_inputs.values():
            widget.valueChanged.connect(self.update_stats_from_form)
        for widget in self.ev_inputs.values():
            widget.valueChanged.connect(self.update_stats_from_form)
    
    def update_stats_from_form(self, _=None):
        """Pega os dados atuais do formulário e atualiza o display de stats finais."""
        species = self.species_input.currentText()
        if not species or species not in self.parent_window.pokemon_data: #muda aqui
            self.final_stats_frame.hide()
            return

        level = self.level_input.value()
        ivs = {name: widget.value() for name, widget in self.iv_inputs.items()}
        evs = {name: widget.value() for name, widget in self.ev_inputs.items()}
        
        mock_pokemon_data = { "species": species, "level": level, "ivs": ivs, "evs": evs }
        self.update_final_stats_display(mock_pokemon_data)

    def update_pokemon_list(self):
        current_selection = self.species_input.currentText()
        pokemon_list = self.parent_window.get_sorted_pokemon_list()
        self.species_input.blockSignals(True)
        self.species_input.clear()
        self.species_input.addItems([""] + pokemon_list)
        if current_selection in pokemon_list:
            self.species_input.setCurrentText(current_selection)
        self.completer.setModel(self.species_input.model())
        self.species_input.blockSignals(False)

    def update_form_image(self, species_name):
        self.image_display.setPixmap(QPixmap())
        if not species_name:
            self.image_display.setText(self.parent_window.get_string("collection.select_to_see_image"))
            return
        image_path = get_pokemon_image_path(species_name)
        if image_path:
            pixmap = load_pixmap_robustly(image_path, 128)
            if pixmap:
                self.image_display.setText("")
                self.image_display.setPixmap(pixmap)
            else:
                self.image_display.setText(f"Erro ao carregar:\n{os.path.basename(image_path)}")
        else:
            self.image_display.setText(self.parent_window.get_string("globals.image_not_found"))
    
    def load_collection(self):
        self.collection = load_json("my_pokemon.json", [], is_user_data=True)
        self.reload_and_sort_collection()
        self.collection_updated.emit()

    def reload_and_sort_collection(self):
        sort_mode_text = self.sort_combo.currentText()
        sort_alpha_text = self.parent_window.get_string("collection.sort_alpha")
        sort_pokedex_text = self.parent_window.get_string("collection.sort_pokedex")

        sort_key = "Ordem Alfabética"
        if sort_mode_text == sort_pokedex_text:
            sort_key = "Ordem da Pokédex"
        
        if sort_key == "Ordem da Pokédex":
            sorted_collection = sorted(self.collection, key=lambda p: self.pokedex_order.get(p["species"], 9999))
        else:
            sorted_collection = sorted(self.collection, key=lambda p: (p.get("nickname") or p["species"]).lower())

        self.table.setRowCount(0)
        for p in sorted_collection:
            original_idx = self.collection.index(p)
            self.add_pokemon_to_table(self.table.rowCount(), p, original_idx)

    def add_pokemon_to_table(self, row_idx, pokemon_data, original_idx):
        self.table.insertRow(row_idx)
        self.table.setRowHeight(row_idx, 64)

        # ... (código do image_label e das strings iv/ev continua igual) ...
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if image_path := get_pokemon_image_path(pokemon_data.get("species", "")):
            if pixmap := load_pixmap_robustly(image_path, 60):
                image_label.setPixmap(pixmap)
        self.table.setCellWidget(row_idx, 0, image_label)

        iv_str = ", ".join(f"{pokemon_data.get('ivs', {}).get(stat, 0)}" for stat in self.stats)
        ev_str = ", ".join(f"{pokemon_data.get('evs', {}).get(stat, 0)}" for stat in self.ev_inputs.keys())


        final_stats_values = []
        tooltip_html = "<div style='background-color:#3c3c3c; color:white; padding:5px; border-radius:4px;'><table>"

        # Corrigido: usa self.parent_window.pokemon_data
        base_stats = self.parent_window.pokemon_data.get(pokemon_data.get("species"), {}).get("base_stats", {})
        if base_stats:
            for stat_name in self.stats:
                base_value = base_stats.get(stat_name, 0)
                level = pokemon_data.get("level", 1)
                iv = pokemon_data.get("ivs", {}).get(stat_name, 0)
                ev = pokemon_data.get("evs", {}).get(stat_name, 0)
                final_stat = self.parent_window._calculate_final_stat(stat_name, base_value, level, iv, ev, pokemon_data.get("nature", "Hardy"))
                final_stats_values.append(str(final_stat))

                # CORREÇÃO DA CHAMADA DA FUNÇÃO
                pixmap = get_dynamic_stat_bar(self.parent_window, stat_name, final_stat, context='final')

                img_tag = ""
                if pixmap:
                    buffer = QBuffer()
                    buffer.open(QBuffer.OpenModeFlag.ReadWrite)
                    pixmap.save(buffer, "PNG")
                    base64_data = base64.b64encode(buffer.data().data()).decode('utf-8')
                    img_tag = f"<img src='data:image/png;base64,{base64_data}'>"

                stat_label = self.stat_labels.get(stat_name, stat_name.capitalize())
                tooltip_html += f"<tr><td align='right' style='padding-right:5px;'><b>{stat_label}:</b></td><td>{final_stat}</td><td>{img_tag}</td></tr>"

        tooltip_html += "</table></div>"
        final_stats_str = ", ".join(final_stats_values)

        # ... (o resto da função, com os self.table.setItem e botões, continua igual)
        self.table.setItem(row_idx, 1, QTableWidgetItem(str(original_idx)))
        self.table.setItem(row_idx, 2, QTableWidgetItem(pokemon_data.get("nickname", "")))
        self.table.setItem(row_idx, 3, QTableWidgetItem(pokemon_data.get("species", "")))
        self.table.setItem(row_idx, 4, QTableWidgetItem(str(pokemon_data.get("level", 1))))
        self.table.setItem(row_idx, 5, QTableWidgetItem(pokemon_data.get("nature", "")))
        self.table.setItem(row_idx, 6, QTableWidgetItem(iv_str))
        self.table.setItem(row_idx, 7, QTableWidgetItem(ev_str))
        stats_item = QTableWidgetItem(final_stats_str)
        stats_item.setToolTip(tooltip_html)
        self.table.setItem(row_idx, 8, stats_item)
        self.table.setItem(row_idx, 12, QTableWidgetItem(pokemon_data.get("notes", "")))
        edit_btn = QPushButton(emojis.EDITAR)
        edit_btn.setToolTip(self.parent_window.get_string("collection.edit_tooltip"))
        edit_btn.clicked.connect(lambda _, r=row_idx: self.load_pokemon_to_form(r))
        self.table.setCellWidget(row_idx, 9, edit_btn)
        evolve_btn = QPushButton(emojis.EVOLUIR)
        evolve_btn.setToolTip(self.parent_window.get_string("collection.evolve_tooltip"))
        species_name = pokemon_data.get("species", "")
        if species_name in EVOLUTIONS:
            evolve_btn.setEnabled(True)
            evolve_btn.clicked.connect(lambda _, r=row_idx: self.initiate_evolution(r))
        else:
            evolve_btn.setEnabled(False)
        self.table.setCellWidget(row_idx, 10, evolve_btn)
        remove_btn = QPushButton(emojis.LIXEIRA)
        remove_btn.setToolTip(self.parent_window.get_string("collection.remove_tooltip"))
        remove_btn.clicked.connect(lambda _, r=row_idx: self.remove_pokemon(r))
        self.table.setCellWidget(row_idx, 11, remove_btn)

    # --- NOVO: Função para iniciar o processo de evolução ---
    def initiate_evolution(self, row_idx):
        original_idx = int(self.table.item(row_idx, 1).text())
        current_pokemon = self.collection[original_idx]
        species_name = current_pokemon["species"]
        
        evolution_target = EVOLUTIONS.get(species_name)

        if not evolution_target:
            return

        next_evolution_name = ""
        # Verifica se o alvo é uma lista (multi-evolução)
        if isinstance(evolution_target, list):
            choice_dialog = MultipleEvolutionChoiceDialog(evolution_target, self.parent_window)
            if choice_dialog.exec() == QDialog.DialogCode.Accepted:
                next_evolution_name = choice_dialog.selected_evolution
            else:
                return  # O usuário cancelou
        else:
            # É uma evolução simples (string)
            next_evolution_name = evolution_target

        if not next_evolution_name:
            return

        # O resto do fluxo continua normalmente com o nome escolhido
        dialog = EvolutionDialog(current_pokemon, next_evolution_name, self.parent_window.pokemon_data, self.parent_window) #muda aqui
        if dialog.exec() == QDialog.DialogCode.Accepted:
            evolved_data = dialog.evolved_pokemon_data
            if evolved_data:
                self.handle_evolution_confirmed(original_idx, current_pokemon, evolved_data)

    # --- 4. ADICIONAR os novos métodos para a animação ---
    def handle_evolution_confirmed(self, original_idx, pre_evo_pokemon, post_evo_data):
        """ Inicia a animação de evolução. """
        pre_evo_name = pre_evo_pokemon['species']
        post_evo_name = post_evo_data['species']

        pre_evo_path = get_pokemon_image_path(pre_evo_name)
        post_evo_path = get_pokemon_image_path(post_evo_name)

        pre_evo_pixmap = load_pixmap_robustly(pre_evo_path, 128)
        post_evo_pixmap = load_pixmap_robustly(post_evo_path, 128)

        if not pre_evo_pixmap or not post_evo_pixmap:
            print("AVISO: Imagem de evolução não encontrada. Pulando animação.")
            self.finalize_evolution_and_refresh(original_idx, post_evo_data)
            return

        # Pega a escolha do usuário do arquivo de config
        animation_name = self.parent_window.config.get("evolution_animation", "Flash Clássico")
        
        # Pede para a fábrica a classe de animação correta
        AnimationClass = get_animation_class(animation_name)
        
        # Cria a instância da animação
        self.animation_widget = AnimationClass(pre_evo_pixmap, post_evo_pixmap, parent=self.parent_window)
        
        # Conecta o sinal 'animationFinished' para quando a animação terminar,
        # e usa uma lambda para passar os dados que precisaremos depois.
        self.animation_widget.animationFinished.connect(
            lambda: self.finalize_evolution_and_refresh(original_idx, post_evo_data)
        )
        
        # Inicia a animação!
        self.animation_widget.start_animation()

    def finalize_evolution_and_refresh(self, original_idx, evolved_data):
        """ Executado SOMENTE APÓS a animação terminar. """
        print("Animação finalizada. Atualizando o banco de dados e a tabela.")
        
        self.collection[original_idx] = evolved_data
        save_json("my_pokemon.json", self.collection, is_user_data=True)
        self.load_collection() # Recarrega e reordena a coleção

    def add_pokemon(self):
        if new_pokemon := self.get_pokemon_from_form():
            self.collection.append(new_pokemon)
            save_json("my_pokemon.json", self.collection, is_user_data=True)
            self.load_collection()
            self.clear_form()
            QMessageBox.information(self, self.parent_window.get_string("globals.success"),
                                     f"{emojis.SUCESSO} {self.parent_window.get_string('collection.pokemon_added').format(name=new_pokemon['species'])}")

    def save_pokemon(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, self.parent_window.get_string("globals.error"), f"{emojis.AVISO} {self.parent_window.get_string('collection.select_to_save')}")
            return
        row_idx = selected_items[0].row()
        original_idx = int(self.table.item(row_idx, 1).text())
        if updated_pokemon := self.get_pokemon_from_form():
            self.collection[original_idx] = updated_pokemon
            save_json("my_pokemon.json", self.collection, is_user_data=True)
            self.load_collection()
            QMessageBox.information(self, self.parent_window.get_string("globals.success"), f"{emojis.SUCESSO} {self.parent_window.get_string('collection.pokemon_updated')}")

    def remove_pokemon(self, row_idx):
        original_idx = int(self.table.item(row_idx, 1).text())
        pokemon = self.collection[original_idx]
        reply = QMessageBox.question(self, self.parent_window.get_string("collection.confirm_remove_title"),
                                       f"{emojis.LIXEIRA} {self.parent_window.get_string('collection.confirm_remove_text').format(name=(pokemon.get('nickname') or pokemon['species']))}",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.collection.pop(original_idx)
            save_json("my_pokemon.json", self.collection, is_user_data=True)
            self.load_collection()

    def load_pokemon_to_form(self, row_idx):
        original_idx = int(self.table.item(row_idx, 1).text())
        pokemon = self.collection[original_idx]
        self.nickname_input.setText(pokemon.get("nickname", ""))
        self.species_input.setCurrentText(pokemon["species"])
        self.level_input.setValue(pokemon["level"])
        self.nature_input.setCurrentText(pokemon["nature"])
        for name, input_widget in self.iv_inputs.items():
            input_widget.setValue(pokemon.get("ivs", {}).get(name, 0))
        for name, input_widget in self.ev_inputs.items():
            input_widget.setValue(pokemon.get("evs", {}).get(name, 0))
        self.table.selectRow(row_idx)
        self.notes_input.setText(pokemon.get("notes", ""))
        self.update_final_stats_display(pokemon)

    # CÓDIGO CORRIGIDO E PRONTO PARA O FUTURO
    def update_final_stats_display(self, pokemon_data):
        species = pokemon_data.get("species")
        level = pokemon_data.get("level")
        ivs = pokemon_data.get("ivs", {})
        evs = pokemon_data.get("evs", {})

        # Corrigido: usa self.parent_window.pokemon_data
        base_stats = self.parent_window.pokemon_data.get(species, {}).get("base_stats", {})
        if not base_stats:
            self.final_stats_frame.hide()
            return

        for stat_name in self.stats:
            base_value = base_stats.get(stat_name, 0)
            iv = ivs.get(stat_name, 0)
            ev = evs.get(stat_name, 0)
            final_stat = self.parent_window._calculate_final_stat(stat_name, base_value, level, iv, ev, self.nature_input.currentText())

            self.final_stat_labels[stat_name].setText(f"<b>{final_stat}</b>")

            # CORREÇÃO DA CHAMADA DA FUNÇÃO
            pixmap = get_dynamic_stat_bar(self.parent_window, stat_name, final_stat, context='final')

            if pixmap:
                self.stat_bar_labels[stat_name].setPixmap(pixmap)
            else:
                self.stat_bar_labels[stat_name].clear()

        self.final_stats_frame.show()

    def get_pokemon_from_form(self):
        species = self.species_input.currentText()
        if not species or species not in self.parent_window.pokemon_data: #muda aqui
            QMessageBox.warning(self, self.parent_window.get_string("globals.error"), f"{emojis.ERRO} {self.parent_window.get_string('collection.invalid_species')}")
            return None
        return {
            "nickname": self.nickname_input.text().strip(), 
            "species": species, 
            "level": self.level_input.value(),
            "nature": self.nature_input.currentText(),
            "ivs": {name: widget.value() for name, widget in self.iv_inputs.items()},
            "evs": {name: widget.value() for name, widget in self.ev_inputs.items()},
            "notes": self.notes_input.toPlainText()
        }

    def clear_form(self):
        self.nickname_input.clear()
        self.species_input.setCurrentIndex(0)
        self.level_input.setValue(1)
        self.nature_input.setCurrentIndex(0)
        for widget in self.iv_inputs.values(): widget.setValue(0)
        for widget in self.ev_inputs.values(): widget.setValue(0)
        self.table.clearSelection()
        self.notes_input.clear()
        self.final_stats_frame.hide()

    def add_pokemon_directly(self, data):
        species = data.get("species")
        if not species or species not in self.parent_window.pokemon_data: #muda aqui
            QMessageBox.warning(self, self.parent_window.get_string("globals.error", "Erro"), f"{emojis.ERRO} {self.parent_window.get_string('collection.invalid_species', 'Espécie de Pokémon inválida.')}")
            return

        nickname = data.get("nickname", "").strip()
        if not nickname:
            nickname = species

        new_pokemon = {
            "nickname": nickname, "species": species,
            "level": data.get("level", 1), "nature": data.get("nature", "Hardy"),
            "ivs": data.get("ivs", {}), "evs": data.get("evs", {}),
            "notes": self.parent_window.get_string("collection.note_from_ocr", "Adicionado via Calculadora de Stats")
        }

        self.collection.append(new_pokemon)
        save_json("my_pokemon.json", self.collection, is_user_data=True)
        self.load_collection()
        QMessageBox.information(self, self.parent_window.get_string("globals.success", "Sucesso"),
                                 f"{emojis.SUCESSO} {self.parent_window.get_string('collection.pokemon_added_from_ocr').format(name=species)}")

class StatsCalculatorTab(QWidget):
    send_to_collection = pyqtSignal(dict)
    f10_pressed = pyqtSignal()

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        if not OCR_ENABLED:
            self.setup_disabled_ui()
        else:
            self.parent_window.pokemon_data = load_json("pokemon_data.json") #muda aqui
            self.stats = ["hp", "energy", "attack", "defense", "special-attack", "special-defense", "speed", "hp_reg", "en_reg"]
            self.stat_labels = {
                "hp": f"{emojis.CORACAO} HP", "energy": f"{emojis.ENERGIA} EN", "attack": f"{emojis.ESPADA} Attack", 
                "defense": f"{emojis.DEFESA} Defense", "special-attack": f"{emojis.ATK_ESPECIAL} Sp. Atk", 
                "special-defense": f"{emojis.ESCUDO} Sp. Def", "speed": f"{emojis.VELCIDADE} Speed", 
                "hp_reg": f"{emojis.REGENERAR_HP} HP Reg", "en_reg": f"{emojis.REGENERAR_ENERGIA} EN Reg"
            }
            self.init_ui()
            self.hotkey_listener = None
            self.calculated_data = {}

    def retranslate_ui(self):

        def setup_disabled_ui(self):
            layout = QVBoxLayout(self)
            label = QLabel(self.parent_window.get_string("ocr.disabled_text"))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.title = QLabel(self.parent_window.get_string("tabs.ocr"))
        self.title.setStyleSheet("font-size: 18px; font-weight: bold;")
        h_layout = QHBoxLayout()
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        self.nickname_input = QLineEdit()
        self.species_input = QComboBox() # <--- CRIADO AQUI
        self.species_input.setEditable(True)

        # Agora sim, usamos a função para popular a lista
        pokemon_list = self.parent_window.get_sorted_pokemon_list()
        self.species_input.addItems([""] + pokemon_list)
        self.completer = QCompleter(pokemon_list, self)
        self.species_input.setCompleter(self.completer)

        self.species_input.currentTextChanged.connect(self.update_ocr_image)
        self.level_input = QSpinBox()
        self.level_input.setRange(1, 200)
        self.nature_input = QComboBox()
        self.nature_input.addItems(sorted(NATURES.keys()) if NATURES else [])
        form_layout.addRow(self.parent_window.get_string("globals.nickname"), self.nickname_input)
        form_layout.addRow(self.parent_window.get_string("globals.species"), self.species_input)
        form_layout.addRow(self.parent_window.get_string("globals.level"), self.level_input)
        form_layout.addRow(self.parent_window.get_string("globals.nature"), self.nature_input)
        self.ocr_image_display = QLabel("?")
        self.ocr_image_display.setFixedSize(96, 96)
        self.ocr_image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        h_layout.addWidget(form_widget)
        h_layout.addWidget(self.ocr_image_display)
        layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(h_layout)
        control_layout = QHBoxLayout()
        self.hotkey_btn = QPushButton(f"{emojis.HOTKEY} {self.parent_window.get_string('ocr.activate_hotkey_button')}")
        self.hotkey_btn.setCheckable(True)
        self.hotkey_btn.clicked.connect(self.toggle_hotkey_listener)
        self.calibrate_btn = QPushButton(f"{emojis.CALIBRAR} {self.parent_window.get_string('ocr.calibrate_button')}")
        self.calibrate_btn.clicked.connect(self.start_calibration)
        control_layout.addWidget(self.hotkey_btn)
        control_layout.addWidget(self.calibrate_btn)
        layout.addLayout(control_layout)
        self.status_label = QLabel(f"{emojis.CARREGANDO} {self.parent_window.get_string('ocr.status_waiting')}")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # --- NOVO LAYOUT DE RESULTADOS ---
        results_container = QFrame()
        results_container.setFrameShape(QFrame.Shape.StyledPanel)
        results_h_layout = QHBoxLayout(results_container)
        results_h_layout.setContentsMargins(10, 10, 10, 10) # Adiciona margem interna

        iv_results_layout = QFormLayout()
        final_stats_layout = QFormLayout()
        ev_results_layout = QFormLayout()
        
        self.iv_labels = {}
        self.ev_labels = {}
        self.final_stat_labels = {}
        self.stat_bar_labels = {}

        iv_results_layout.addRow(QLabel(f"<b>{self.parent_window.get_string('ocr.ivs_header')}</b>"))
        final_stats_layout.addRow(QLabel(f"<b>{self.parent_window.get_string('ocr.final_stats_header', 'Stats Finais')}</b>"))
        ev_results_layout.addRow(QLabel(f"<b>{self.parent_window.get_string('ocr.evs_header')}</b>"))

        for stat in self.stats:
            self.iv_labels[stat] = QLabel("?")
            iv_results_layout.addRow(f"{self.stat_labels[stat]}:", self.iv_labels[stat])
            
            self.ev_labels[stat] = QLabel("?")
            ev_results_layout.addRow(f"{self.stat_labels[stat]}:", self.ev_labels[stat])

            if stat in ['hp', 'energy']:
                self.final_stat_labels[stat] = QLabel("?")
                self.stat_bar_labels[stat] = QLabel()
                self.stat_bar_labels[stat].setFixedSize(64, 16)

                stat_row_widget = QWidget()
                stat_row_layout = QHBoxLayout(stat_row_widget)
                stat_row_layout.setContentsMargins(0, 0, 0, 0)
                stat_row_layout.addWidget(self.final_stat_labels[stat])
                stat_row_layout.addWidget(self.stat_bar_labels[stat])
                stat_row_layout.addStretch()
                final_stats_layout.addRow(f"{self.stat_labels[stat]}:", stat_row_widget)

        results_h_layout.addLayout(iv_results_layout, 1)
        results_h_layout.addLayout(final_stats_layout, 1)
        results_h_layout.addLayout(ev_results_layout, 1)
        layout.addWidget(results_container)
        
        self.send_btn = QPushButton(f"{emojis.ENVIAR} {self.parent_window.get_string('ocr.send_to_collection_button')}")
        self.send_btn.setEnabled(False)
        self.send_btn.clicked.connect(self.send_data)
        layout.addWidget(self.send_btn)
        layout.addStretch()
        
        self.f10_pressed.connect(self._start_ocr_processing)
        self.update_ocr_image(self.species_input.currentText())

    def update_pokemon_list(self):
        """Atualiza o conteúdo do ComboBox de espécies."""
        current_selection = self.species_input.currentText()
        pokemon_list = self.parent_window.get_sorted_pokemon_list()

        self.species_input.blockSignals(True)
        self.species_input.clear()
        self.species_input.addItems([""] + pokemon_list)

        if current_selection in pokemon_list:
            self.species_input.setCurrentText(current_selection)

        self.completer.setModel(self.species_input.model())
        self.species_input.blockSignals(False)

    def update_ocr_image(self, species_name):
        self.ocr_image_display.setPixmap(QPixmap())
        if not species_name:
            self.ocr_image_display.setText("?")
            return
            
        image_path = get_pokemon_image_path(species_name)
        if image_path:
            pixmap = load_pixmap_robustly(image_path, 96)
            if pixmap:
                self.ocr_image_display.setText("")
                self.ocr_image_display.setPixmap(pixmap)
            else:
                self.ocr_image_display.setText("Erro")
        else:
            self.ocr_image_display.setText("?")

    def start_calibration(self):
        self.calibration_window = CalibrationWindow(self.parent_window)
        self.calibration_window.start()

    def toggle_hotkey_listener(self):
        if self.hotkey_btn.isChecked(): self.start_listener()
        else: self.stop_listener()

    def start_listener(self):
        if self.hotkey_listener is None:
            try:
                self.hotkey_listener = keyboard.Listener(on_press=self.on_hotkey_press)
                self.hotkey_listener.start()
                self.hotkey_btn.setText(self.parent_window.get_string("ocr.deactivate_hotkey_button"))
                self.status_label.setText(self.parent_window.get_string("ocr.status_active"))
                self.status_label.setStyleSheet("color: #4CAF50;")
            except Exception as e:
                self.status_label.setText(f"Erro ao iniciar listener: {e}")

    def stop_listener(self):
        if self.hotkey_listener is not None:
            self.hotkey_listener.stop()
            self.hotkey_listener = None
            self.hotkey_btn.setText(self.parent_window.get_string("ocr.activate_hotkey_button"))
            self.status_label.setText(self.parent_window.get_string("ocr.status_inactive"))
            self.status_label.setStyleSheet("color: #F44336;")

    def on_hotkey_press(self, key):
        try:
            if key == keyboard.Key.f10:
                # Apenas emite o sinal. Não toca na interface!
                self.f10_pressed.emit()
        except Exception as e:
            # É uma boa prática imprimir o erro no terminal para debug
            print(f"Erro no listener da hotkey: {e}")

    def _start_ocr_processing(self):
        """ Este método é executado na thread principal em resposta ao sinal f10_pressed. """
        self.status_label.setText(self.parent_window.get_string("ocr.status_processing"))
        self.status_label.setStyleSheet("color: #FFA500;") # Laranja para "processando"
        
        # Força a interface a se atualizar ANTES de começar o trabalho pesado
        QApplication.processEvents()
        
        # Agora, com segurança, chama a função de processamento
        self.process_screenshot()

    def process_screenshot(self):
        try:
            ROI_STATS = load_json('ocr_config.json', is_user_data=True)
            if not ROI_STATS:
                self.status_label.setText(self.parent_window.get_string("ocr.error_not_calibrated"))
                return
        except FileNotFoundError:
            self.status_label.setText(self.parent_window.get_string("ocr.error_not_calibrated"))
            return
        try:
            screenshot = ImageGrab.grab()
            ocr_results = {}
            for stat_name, roi in ROI_STATS.items():
                crop = screenshot.crop(tuple(roi))
                img_np = np.array(crop)
                gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
                resized = cv2.resize(gray, (int(gray.shape[1] * 4), int(gray.shape[0] * 4)), interpolation=cv2.INTER_CUBIC)

                if stat_name in ["nickname", "species", "nature"]:
                    config = r'--oem 3 --psm 7'
                    text = pytesseract.image_to_string(resized, config=config).strip()
                    text = re.sub(r'[^a-zA-Z-]', '', text)
                    ocr_results[stat_name] = text
                else:
                    _, thresh = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                    config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
                    text = pytesseract.image_to_string(thresh, config=config).strip()
                    try:
                        ocr_results[stat_name] = int(text)
                    except ValueError:
                        self.status_label.setText(self.parent_window.get_string("ocr.error_read_stat").format(stat=stat_name))
                        self.clear_results()
                        return
                
            self.update_ui_with_ocr_data(ocr_results)

        except Exception as e:
            error_str = str(e)
            if "tesseract" in error_str.lower():
                QMessageBox.warning(self, 
                                    self.parent_window.get_string("globals.error"), 
                                    self.parent_window.get_string("ocr.error_tesseract_readme"))
                self.status_label.setText(self.parent_window.get_string("ocr.status_inactive"))
            else:
                self.status_label.setText(self.parent_window.get_string("ocr.error_screenshot").format(error=error_str))
            self.clear_results()

    def update_ui_with_ocr_data(self, ocr_data):
        species = ocr_data.get("species", "")
        level = ocr_data.get("level", 1)
        
        self.nickname_input.setText(ocr_data.get("nickname", ""))
        self.species_input.setCurrentText(species)
        self.level_input.setValue(level)
        self.nature_input.setCurrentText(ocr_data.get("nature", "Hardy"))

        ivs = {}
        evs = {}
        
        base_stats = self.parent_window.pokemon_data.get(species, {}).get("base_stats", {}) #muda aqui
        for stat_name in self.stats:
            iv_key = f"{stat_name}_iv"
            read_iv = ocr_data.get(iv_key, 0)
            ivs[stat_name] = read_iv
            self.iv_labels[stat_name].setText(f"<b>{read_iv}</b>")

            ev_key = f"{stat_name}_ev"
            read_ev = ocr_data.get(ev_key, 0)
            evs[stat_name] = read_ev
            self.ev_labels[stat_name].setText(f"<b>{read_ev}</b>")
            
            # ATUALIZAÇÃO: Calcula o stat final e atualiza a barra
            if stat_name in self.stats: # Vamos fazer isso para todos os stats, não só hp e energy
                base_value = base_stats.get(stat_name, 0)

                # --- LINHA CORRIGIDA ---
                # Chama a função mestre na MainWindow, passando todos os parâmetros
                final_stat = self.parent_window._calculate_final_stat(
                    stat_name, base_value, level, read_iv, read_ev, self.nature_input.currentText()
                )
                # --- FIM DA CORREÇÃO ---

                if stat_name in self.final_stat_labels:
                    self.final_stat_labels[stat_name].setText(f"<b>{final_stat}</b>")

                if stat_name in self.stat_bar_labels:
                    pixmap = get_dynamic_stat_bar(self.parent_window, stat_name, final_stat, context='final')
                    if pixmap:
                        self.stat_bar_labels[stat_name].setPixmap(pixmap)
                    else:
                        self.stat_bar_labels[stat_name].clear()

            
        self.status_label.setText(self.parent_window.get_string("ocr.status_success"))
        
        self.calculated_data = {
            "nickname": ocr_data.get("nickname", ""),
            "species": species,
            "level": level,
            "nature": ocr_data.get("nature", "Hardy"),
            "ivs": ivs,
            "evs": evs
        }
        self.send_btn.setEnabled(True)

    def clear_results(self):
        for label in self.iv_labels.values(): label.setText("?")
        for label in self.ev_labels.values(): label.setText("?")
        for label in self.stat_bar_labels.values(): label.clear()
        for label in self.final_stat_labels.values(): label.setText("?")
        self.send_btn.setEnabled(False)
        self.calculated_data = {}
        self.nickname_input.clear()
        self.species_input.setCurrentIndex(0)
        self.level_input.setValue(1)
        self.nature_input.setCurrentIndex(0)

    def send_data(self):
        if not self.calculated_data:
            QMessageBox.warning(self, self.parent_window.get_string("globals.error"), self.parent_window.get_string("ocr.error_no_data_to_send"))
            return

        final_data = {
            "nickname": self.nickname_input.text().strip(),
            "species": self.species_input.currentText(),
            "level": self.level_input.value(),
            "nature": self.nature_input.currentText(),
            "ivs": self.calculated_data.get('ivs', {}),
            "evs": self.calculated_data.get('evs', {})
        }
        
        if not final_data["species"] or final_data["species"] not in self.parent_window.pokemon_data: #muda aqui
            QMessageBox.warning(self, self.parent_window.get_string("globals.error"), self.parent_window.get_string("collection.invalid_species"))
            return

        self.send_to_collection.emit(final_data)
        self.clear_results()
        self.status_label.setText(self.parent_window.get_string("ocr.status_sent"))

    def closeEvent(self, event):
        self.stop_listener()
        super().closeEvent(event)

class EVTrainingTab(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.parent_window.pokemon_data = load_json("pokemon_data.json") #muda aqui
        self.collection = []
        self.init_ui()

    
    def retranslate_ui(self):
        # Guarda o estado atual se necessário
        # (Ex: qual item está selecionado em um ComboBox)

        # Cria um novo widget central para a aba
        new_central_widget = QWidget()
        # O truque: Nós aplicamos o novo layout A ESTE NOVO WIDGET, não ao 'self'
        self.init_ui(parent_widget=new_central_widget)

        # Define o novo widget como o conteúdo da aba
        # Primeiro, remove o antigo
        old_widget = self.findChild(QWidget)
        if old_widget:
            old_widget.deleteLater()

        # Adiciona o novo
        main_layout = QVBoxLayout()
        main_layout.addWidget(new_central_widget)
        self.setLayout(main_layout)

        # Recarrega os dados
        if hasattr(self, 'update_collection'): self.update_collection()
        if hasattr(self, 'update_team_list'): self.update_team_list()
        if hasattr(self, 'update_my_pokemon_list'): self.update_my_pokemon_list()
        if hasattr(self, 'load_hunts_list'): self.load_hunts_list()
        if hasattr(self, 'populate_history_table'): self.populate_history_table()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        title = QLabel(self.parent_window.get_string("tabs.ev_yield"))
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        left_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        controls_layout = QFormLayout()
        
        self.search_mode_select = QComboBox()
        self.search_mode_select.addItems([
            self.parent_window.get_string("ev_yield.search_by_stat"),
            self.parent_window.get_string("ev_yield.search_by_pokemon"),
            self.parent_window.get_string("ev_yield.suggest_for_my_pokemon")
        ])
        self.search_mode_select.currentTextChanged.connect(self.update_search_mode)
        controls_layout.addRow(self.parent_window.get_string("ev_yield.search_mode"), self.search_mode_select)
        
        self.search_widget_stack = QWidget()
        self.search_stack_layout = QVBoxLayout(self.search_widget_stack)
        self.search_stack_layout.setContentsMargins(0,0,0,0)

        self.default_search_combo = QComboBox()
        self.default_search_combo.currentTextChanged.connect(self.update_results)
        self.search_stack_layout.addWidget(self.default_search_combo)

        self.my_pokemon_search_widget = QWidget()
        my_poke_layout = QHBoxLayout(self.my_pokemon_search_widget)
        my_poke_layout.setContentsMargins(0,0,0,0)
        self.my_pokemon_select = QComboBox()
        self.suggest_btn = QPushButton(f"{emojis.LÂMPADA} {self.parent_window.get_string('ev_yield.suggest_button')}")
        self.suggest_btn.clicked.connect(self.suggest_ev_training)
        my_poke_layout.addWidget(self.my_pokemon_select)
        my_poke_layout.addWidget(self.suggest_btn)
        self.search_stack_layout.addWidget(self.my_pokemon_search_widget)

        controls_layout.addRow(self.parent_window.get_string("ev_yield.search_label"), self.search_widget_stack)
        left_layout.addLayout(controls_layout)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels([
             "",
             f"{emojis.PATAS} {self.parent_window.get_string('globals.pokemon')}",
             f"{emojis.EVS} {self.parent_window.get_string('ev_yield.header_ev_gain')}",
             f"{emojis.LOCALIZAÇÃO} {self.parent_window.get_string('globals.location')}"
        ])
        self.results_table.setSortingEnabled(True)
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.resizeSection(0, 64)
        self.results_table.verticalHeader().setDefaultSectionSize(64)
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.itemSelectionChanged.connect(self.display_selected_map)
        left_layout.addWidget(self.results_table)
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_container.setFixedWidth(350)
        map_title = QLabel(f"{emojis.MAPA} {self.parent_window.get_string('ev_yield.map_title')}")
        map_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        right_layout.addWidget(map_title, alignment=Qt.AlignmentFlag.AlignCenter)
        self.map_scroll_area = QScrollArea()
        self.map_scroll_area.setWidgetResizable(True)
        self.map_scroll_area.setFrameShape(QFrame.Shape.StyledPanel)
        self.map_container = QWidget()
        self.map_layout = QVBoxLayout(self.map_container)
        self.map_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.map_scroll_area.setWidget(self.map_container)
        right_layout.addWidget(self.map_scroll_area)
        main_layout.addWidget(left_container, stretch=2)
        main_layout.addWidget(right_container, stretch=1)
        self.update_search_mode(self.parent_window.get_string("ev_yield.search_by_stat"))
        self.display_selected_map()

    def update_pokemon_list(self):
        """Atualiza o ComboBox de busca por Pokémon."""
        # Apenas atualiza se o modo de busca for por Pokémon
        if self.search_mode_select.currentText() == self.parent_window.get_string("ev_yield.search_by_pokemon"):
            current_selection = self.default_search_combo.currentText()
            pokemon_list = self.parent_window.get_sorted_pokemon_list()

            self.default_search_combo.blockSignals(True)
            self.default_search_combo.clear()
            self.default_search_combo.addItems([""] + pokemon_list)

            if current_selection in pokemon_list:
                self.default_search_combo.setCurrentText(current_selection)
            self.default_search_combo.blockSignals(False)

    def update_my_pokemon_list(self):
        self.collection = load_json("my_pokemon.json", [], is_user_data=True)

        # --- CORREÇÃO: Centralizar a lógica de ordenação lendo do config ---
        sort_mode = self.parent_window.config.get("sort_order", "Ordem Alfabética")
        if sort_mode == "Ordem da Pokédex":
            sorted_collection = sorted(self.collection, key=lambda p: self.parent_window.pokedex_order.get(p["species"], 9999))
        else: # Alfabética como padrão
            sorted_collection = sorted(self.collection, key=lambda p: (p.get("nickname") or p["species"]).lower())

        pokemon_names = [(p.get("nickname") or p["species"]) for p in sorted_collection]
        self.my_pokemon_select.clear()
        self.my_pokemon_select.addItems([self.parent_window.get_string("ev_yield.select_pokemon")] + pokemon_names)

    def update_search_mode(self, mode):
        self.default_search_combo.blockSignals(True)
        self.default_search_combo.clear()
        
        if mode == self.parent_window.get_string("ev_yield.suggest_for_my_pokemon"):
            self.default_search_combo.hide()
            self.my_pokemon_search_widget.show()
            self.results_table.setRowCount(0)
        else:
            self.default_search_combo.show()
            self.my_pokemon_search_widget.hide()
            if mode == self.parent_window.get_string("ev_yield.search_by_stat"):
                self.default_search_combo.addItems([
                    self.parent_window.get_string('stats.hp'), self.parent_window.get_string('stats.attack'),
                    self.parent_window.get_string('stats.defense'), self.parent_window.get_string('stats.special-attack'),
                    self.parent_window.get_string('stats.special-defense'), self.parent_window.get_string('stats.speed')
                ])
            elif mode == self.parent_window.get_string("ev_yield.search_by_pokemon"):
                all_pokemon = self.parent_window.get_sorted_pokemon_list()
                self.default_search_combo.addItems([""] + all_pokemon)
            self.update_results()
        self.default_search_combo.blockSignals(False)

    def suggest_ev_training(self):
        selected_name = self.my_pokemon_select.currentText()
        if selected_name == self.parent_window.get_string("ev_yield.select_pokemon"): return
        pokemon_info = next((p for p in self.collection if (p.get("nickname") or p["species"]) == selected_name), None)
        if not pokemon_info: return
        base_stats = self.parent_window.pokemon_data.get(pokemon_info['species'], {}).get('base_stats', {}) #muda aqui
        if not base_stats:
            QMessageBox.warning(self, self.parent_window.get_string("globals.error"), self.parent_window.get_string("ev_yield.error_base_stats_not_found"))
            return
        trainable_stats = {
            self.parent_window.get_string('stats.attack'): base_stats.get("attack", 0), 
            self.parent_window.get_string('stats.defense'): base_stats.get("defense", 0),
            self.parent_window.get_string('stats.special-attack'): base_stats.get("special-attack", 0), 
            self.parent_window.get_string('stats.special-defense'): base_stats.get("special-defense", 0),
            self.parent_window.get_string('stats.speed'): base_stats.get("speed", 0)
        }
        sorted_stats = sorted(trainable_stats.items(), key=lambda item: item[1], reverse=True)
        top_two_stats = [stat[0] for stat in sorted_stats[:2]]
        pokemon_to_display = []
        for pokemon, data in self.parent_window.ev_data.items():
            if data.get("ev_stat") in top_two_stats and data.get("ev_value", 0) > 0:
                pokemon_to_display.append((pokemon, data))
        pokemon_to_display.sort(key=lambda x: (x[1]['ev_stat'], x[0]))
        self.add_pokemon_to_ev_table(pokemon_to_display)
        
    def update_results(self):
        selection = self.default_search_combo.currentText()
        mode = self.search_mode_select.currentText()
        if not selection: 
            self.results_table.setRowCount(0)
            return
        pokemon_to_display = []
        if mode == self.parent_window.get_string("ev_yield.search_by_stat"):
            for pokemon, data in self.parent_window.ev_data.items():
                if data.get("ev_stat") == selection and data.get("ev_value", 0) > 0:
                    pokemon_to_display.append((pokemon, data))
            pokemon_to_display.sort(key=lambda x: x[0])
        elif mode == self.parent_window.get_string("ev_yield.search_by_pokemon"):
            if data := self.parent_window.ev_data.get(selection):
                pokemon_to_display.append((selection, data))
        self.add_pokemon_to_ev_table(pokemon_to_display)

    def add_pokemon_to_ev_table(self, pokemon_list):
        self.results_table.setRowCount(0)
        for pokemon, data in pokemon_list:
            row_pos = self.results_table.rowCount()
            self.results_table.insertRow(row_pos)
            
            image_label = QLabel()
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if image_path := get_pokemon_image_path(pokemon):
                if pixmap := load_pixmap_robustly(image_path, 60):
                    image_label.setPixmap(pixmap)
                else:
                    image_label.setText("Erro")
            else:
                image_label.setText("?")
            self.results_table.setCellWidget(row_pos, 0, image_label)
            
            self.results_table.setItem(row_pos, 1, QTableWidgetItem(pokemon))
            
            ev_value = data.get('ev_value', 0)
            ev_stat = data.get('ev_stat', '')
            ev_text = f"{ev_value:02d} {ev_stat}" 
            self.results_table.setItem(row_pos, 2, QTableWidgetItem(ev_text))

            self.results_table.setItem(row_pos, 3, QTableWidgetItem(data.get("location", "N/A")))

    def display_selected_map(self):
        while self.map_layout.count():
            if child := self.map_layout.takeAt(0):
                if child.widget(): child.widget().deleteLater()
        selected_items = self.results_table.selectedItems()
        if not selected_items:
            self.map_layout.addWidget(QLabel(self.parent_window.get_string("ev_yield.select_to_see_map")))
            return
        location_item = self.results_table.item(selected_items[0].row(), 3)
        if not location_item: return
        location_name = location_item.text().strip()
        if location_name.lower() == 'anywhere':
            self.map_layout.addWidget(QLabel(self.parent_window.get_string("ev_yield.anywhere")))
            return
        if any(term in location_name.lower() for term in ["evolução", "especial", "evolution", "special"]):
            self.map_layout.addWidget(QLabel(self.parent_window.get_string("ev_yield.special_evolution")))
            return
        locations = [loc.strip() for loc in location_name.split(',')]
        found_map = False
        for loc in locations:
            if map_path := get_map_image_path(loc):
                if pixmap := load_pixmap_robustly(map_path, 320, 240):
                    map_label = QLabel()
                    map_label.setPixmap(pixmap)
                    self.map_layout.addWidget(map_label)
                    found_map = True
        if not found_map:
            self.map_layout.addWidget(QLabel(self.parent_window.get_string("ev_yield.map_not_found").format(loc=location_name)))

# -----------------------------------------------------------------
# --- CLASSE CORRIGIDA: TeamAnalyzerTab ---
# -----------------------------------------------------------------
class TeamAnalyzerTab(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.parent_window.pokemon_data = load_json("pokemon_data.json") #muda aqui
        self.collection = []
        self.teams = load_json("teams.json", {}, is_user_data=True)
        self.init_ui()
        self.update_collection()
        self.update_team_list()

    
    def retranslate_ui(self):
        # Guarda o estado atual se necessário
        # (Ex: qual item está selecionado em um ComboBox)

        # Cria um novo widget central para a aba
        new_central_widget = QWidget()
        # O truque: Nós aplicamos o novo layout A ESTE NOVO WIDGET, não ao 'self'
        self.init_ui(parent_widget=new_central_widget)

        # Define o novo widget como o conteúdo da aba
        # Primeiro, remove o antigo
        old_widget = self.findChild(QWidget)
        if old_widget:
            old_widget.deleteLater()

        # Adiciona o novo
        main_layout = QVBoxLayout()
        main_layout.addWidget(new_central_widget)
        self.setLayout(main_layout)

        # Recarrega os dados
        if hasattr(self, 'update_collection'): self.update_collection()
        if hasattr(self, 'update_team_list'): self.update_team_list()
        if hasattr(self, 'update_my_pokemon_list'): self.update_my_pokemon_list()
        if hasattr(self, 'load_hunts_list'): self.load_hunts_list()
        if hasattr(self, 'populate_history_table'): self.populate_history_table()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        title = QLabel(self.parent_window.get_string("tabs.teams"))
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        team_management_layout = QHBoxLayout()
        self.team_name_input = QLineEdit()
        self.team_name_input.setPlaceholderText(self.parent_window.get_string("teams.team_name_placeholder"))
        
        self.save_team_btn = QPushButton(f"{emojis.SALVAR} {self.parent_window.get_string('teams.save_button')}")
        self.save_team_btn.clicked.connect(self.save_team)
        
        self.load_team_combo = QComboBox()
        self.load_team_combo.currentTextChanged.connect(self.load_team)
        
        self.delete_team_btn = QPushButton(f"{emojis.LIXEIRA} {self.parent_window.get_string('teams.delete_button')}")
        self.delete_team_btn.clicked.connect(self.delete_team)
        
        team_management_layout.addWidget(self.team_name_input)
        team_management_layout.addWidget(self.save_team_btn)
        team_management_layout.addWidget(self.load_team_combo)
        team_management_layout.addWidget(self.delete_team_btn)
        layout.addLayout(team_management_layout)
        
        team_selection_layout = QHBoxLayout()
        self.team_selectors = []
        self.team_image_labels = []
        for i in range(6):
            member_layout = QVBoxLayout()
            image_label = QLabel()
            image_label.setFixedSize(80, 80)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            selector = QComboBox()
            selector.setMinimumWidth(120)
            selector.currentIndexChanged.connect(self.analyze_team)
            member_layout.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignCenter)
            member_layout.addWidget(selector)
            self.team_selectors.append(selector)
            self.team_image_labels.append(image_label)
            team_selection_layout.addLayout(member_layout)
        layout.addLayout(team_selection_layout)
        
        analysis_layout = QHBoxLayout()
        self.results_table = QTableWidget()
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels(["Tipo", "x4", "x2", "x1", "x0.5", "x0.25", "x0"])

        if self.parent_window.type_chart:
            self.all_types = sorted(self.parent_window.type_chart.keys())
            self.results_table.setRowCount(len(self.all_types))
            for row, type_name in enumerate(self.all_types):
                translated_name = self.parent_window.get_string(f"types.{type_name}", type_name)
                
                relative_path = emojis.TYPE_ICONS.get(type_name)
                icon = get_icon_from_path(relative_path)
                
                cell_widget = QWidget()
                cell_layout = QHBoxLayout(cell_widget)
                cell_layout.setContentsMargins(5, 0, 5, 0)
                cell_layout.setSpacing(5)
                
                icon_label = QLabel()
                icon_label.setFixedSize(24, 24)
                if icon:
                    pixmap = icon.pixmap(QSize(24, 24))
                    icon_label.setPixmap(pixmap)
                
                text_label = QLabel(translated_name)
                
                cell_layout.addWidget(icon_label)
                cell_layout.addWidget(text_label)
                cell_layout.addStretch()
                
                self.results_table.setCellWidget(row, 0, cell_widget)
                self.results_table.setRowHeight(row, 30)

        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.results_table.setColumnWidth(0, 150)
        
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        analysis_layout.addWidget(self.results_table)

        self.strategic_summary_output = QTextEdit()
        self.strategic_summary_output.setReadOnly(True)
        self.strategic_summary_output.setFixedWidth(250)
        analysis_layout.addWidget(self.strategic_summary_output)

        layout.addLayout(analysis_layout)

    def update_collection(self):
        self.collection = load_json("my_pokemon.json", [], is_user_data=True)
        
        # --- CORREÇÃO: Usar a mesma lógica de ordenação do config ---
        sort_mode = self.parent_window.config.get("sort_order", "Ordem Alfabética")
        if sort_mode == "Ordem da Pokédex":
            sorted_collection = sorted(self.collection, key=lambda p: self.parent_window.pokedex_order.get(p["species"], 9999))
        else:
            sorted_collection = sorted(self.collection, key=lambda p: (p.get("nickname") or p["species"]).lower())
        
        pokemon_options = [self.parent_window.get_string("globals.none")] + [(p.get("nickname") or p["species"]) for p in sorted_collection]
        
        current_selections = [s.currentText() for s in self.team_selectors]
        
        for i, selector in enumerate(self.team_selectors):
            selector.blockSignals(True)
            selector.clear()
            selector.addItems(pokemon_options)
            
            try:
                if current_selections[i] in pokemon_options:
                    selector.setCurrentText(current_selections[i])
                else:
                    selector.setCurrentIndex(0)
            except IndexError:
                selector.setCurrentIndex(0)
            
            selector.blockSignals(False)
        
        self.analyze_team()

    def analyze_team(self, _=None):
        for row in range(self.results_table.rowCount()):
            for col in range(1, self.results_table.columnCount()):
                self.results_table.setItem(row, col, None)

        self.strategic_summary_output.clear()
        
        team_members = []
        for i, selector in enumerate(self.team_selectors):
            name = selector.currentText()
            image_label = self.team_image_labels[i]
            image_label.setPixmap(QPixmap())
            image_label.setText("")
            if name != self.parent_window.get_string("globals.none"):
                found_pokemon = next((p for p in self.collection if (p.get("nickname") or p["species"]) == name), None)
                if found_pokemon:
                    team_members.append(found_pokemon)
                    if image_path := get_pokemon_image_path(found_pokemon['species']):
                        if pixmap := load_pixmap_robustly(image_path, 80): 
                            image_label.setPixmap(pixmap)
                        else: 
                            image_label.setText("Erro")
                    else: 
                        image_label.setText("?")
        
        if not team_members: 
            self.strategic_summary_output.setPlaceholderText(self.parent_window.get_string("teams.summary_placeholder"))
            for row in range(self.results_table.rowCount()):
                for col in range(1, self.results_table.columnCount()):
                    self.results_table.setItem(row, col, None)
            return

        analysis = {attacking_type: {4: 0, 2: 0, 1: 0, 0.5: 0, 0.25: 0, 0: 0} for attacking_type in self.all_types}

        for p_user in team_members:
            species_data = self.parent_window.pokemon_data.get(p_user["species"]) #muda aqui
            if not species_data: continue
            
            p_types = [species_data["type1"]]
            if species_data.get("type2"): p_types.append(species_data["type2"])

            for attacking_type in self.all_types:
                multiplier = 1.0
                for p_type in p_types:
                    multiplier *= self.parent_window.type_chart.get(attacking_type, {}).get(p_type, 1.0)
                
                key = 1
                if multiplier >= 4: key = 4
                elif multiplier >= 2: key = 2
                elif multiplier < 1 and multiplier >= 0.5: key = 0.5
                elif multiplier < 0.5 and multiplier > 0: key = 0.25
                elif multiplier == 0: key = 0
                analysis[attacking_type][key] += 1

        multiplier_map = {4: 1, 2: 2, 1: 3, 0.5: 4, 0.25: 5, 0: 6}
        for row, type_name in enumerate(self.all_types):
            for multiplier, count in analysis[type_name].items():
                if count > 0:
                    col = multiplier_map.get(multiplier)
                    if col is not None:
                        item = QTableWidgetItem(str(count))
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        # --- MUDANÇA AQUI ---
                        text_color = QColor("black") # Define a cor do texto como preto

                        if multiplier >= 2:
                            item.setBackground(QColor(255, 200, 200)) # Fundo vermelho claro
                            item.setForeground(text_color) # Aplica o texto preto
                        elif multiplier < 1 and multiplier > 0:
                            item.setBackground(QColor(200, 255, 200)) # Fundo verde claro
                            item.setForeground(text_color) # Aplica o texto preto
                        # --- FIM DA MUDANÇA ---

                        elif multiplier == 0:
                            item.setBackground(QColor(220, 220, 220))
                        self.results_table.setItem(row, col, item)
        
        self.generate_strategic_summary(analysis, len(team_members))

    def generate_strategic_summary(self, analysis, team_size):
        weaknesses = {}
        resistances = {}
        for type_name, counts in analysis.items():
            weak_count = counts[4] + counts[2]
            if weak_count > 0:
                weaknesses[type_name] = weak_count
            
            resist_count = counts[0.5] + counts[0.25] + counts[0]
            if resist_count > 0:
                resistances[type_name] = resist_count

        sorted_weak = sorted(weaknesses.items(), key=lambda item: item[1], reverse=True)
        sorted_resist = sorted(resistances.items(), key=lambda item: item[1], reverse=True)

        summary_html = f"<h4>{self.parent_window.get_string('teams.summary_title')}</h4>"
        
        if not sorted_weak and not sorted_resist:
            summary_html += f"<p>{self.parent_window.get_string('teams.summary_no_data')}</p>"
            self.strategic_summary_output.setHtml(summary_html)
            return

        if sorted_weak:
            max_weak_count = sorted_weak[0][1]
            if max_weak_count >= team_size / 2:
                major_weaknesses = [self.parent_window.get_string(f"types.{t}", t) for t, c in sorted_weak if c == max_weak_count]
                summary_html += f"<p><b><font color='red'>{self.parent_window.get_string('teams.summary_major_weakness')}:</font></b> {', '.join(major_weaknesses)} ({max_weak_count} Pokémon).</p>"
            else:
                summary_html += f"<p><b><font color='orange'>{self.parent_window.get_string('teams.summary_balanced_weakness')}</font></b></p>"
        
        if sorted_resist:
            max_resist_count = sorted_resist[0][1]
            if max_resist_count >= team_size / 2:
                major_resistances = [self.parent_window.get_string(f"types.{t}", t) for t, c in sorted_resist if c == max_resist_count]
                summary_html += f"<p><b><font color='green'>{self.parent_window.get_string('teams.summary_major_resistance')}:</font></b> {', '.join(major_resistances)} ({max_resist_count} Pokémon).</p>"

        self.strategic_summary_output.setHtml(summary_html)

    def save_team(self):
        team_name = self.team_name_input.text().strip()
        if not team_name:
            QMessageBox.warning(self, self.parent_window.get_string("globals.error"), f"{emojis.AVISO} {self.parent_window.get_string('teams.error_enter_name')}")
            return
        current_team = [s.currentText() for s in self.team_selectors]
        if all(member == self.parent_window.get_string("globals.none") for member in current_team):
            QMessageBox.warning(self, self.parent_window.get_string("globals.error"), f"{emojis.AVISO} {self.parent_window.get_string('teams.error_select_pokemon')}")
            return
        self.teams[team_name] = current_team
        save_json("teams.json", self.teams, is_user_data=True)
        QMessageBox.information(self, self.parent_window.get_string("globals.success"), f"{emojis.SUCESSO} {self.parent_window.get_string('teams.success_saved').format(name=team_name)}")
        self.update_team_list()
        self.load_team_combo.setCurrentText(team_name)

    def load_team(self, team_name):
        if not team_name or team_name == self.parent_window.get_string("teams.load_placeholder"): 
            self.team_name_input.clear()
            for selector in self.team_selectors:
                selector.setCurrentIndex(0)
            return

        if team_to_load := self.teams.get(team_name):
            for i, member_name in enumerate(team_to_load):
                if i < len(self.team_selectors):
                    selector = self.team_selectors[i]
                    index = selector.findText(member_name)
                    if index != -1:
                        selector.setCurrentIndex(index)
                    else:
                        selector.setCurrentIndex(0)
            self.team_name_input.setText(team_name)
            self.analyze_team()

    def delete_team(self):
        team_name = self.load_team_combo.currentText()
        if not team_name or team_name == self.parent_window.get_string("teams.load_placeholder"):
            QMessageBox.warning(self, self.parent_window.get_string("globals.error"), f"{emojis.AVISO} {self.parent_window.get_string('teams.error_select_to_delete')}")
            return
        reply = QMessageBox.question(self, self.parent_window.get_string("globals.confirm"), f"{emojis.LIXEIRA} {self.parent_window.get_string('teams.confirm_delete').format(name=team_name)}",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if team_name in self.teams:
                del self.teams[team_name]
                save_json("teams.json", self.teams, is_user_data=True)
                QMessageBox.information(self, self.parent_window.get_string("globals.success"), f"{emojis.SUCESSO} {self.parent_window.get_string('teams.success_deleted').format(name=team_name)}")
                self.team_name_input.clear()
                self.update_team_list()
                self.load_team(self.load_team_combo.currentText())

    def update_team_list(self):
        self.load_team_combo.blockSignals(True)
        current_selection = self.load_team_combo.currentText()
        self.load_team_combo.clear()
        self.load_team_combo.addItem(self.parent_window.get_string("teams.load_placeholder"))
        self.teams = load_json("teams.json", {}, is_user_data=True)
        self.load_team_combo.addItems(sorted(self.teams.keys()))
        if current_selection in self.teams: self.load_team_combo.setCurrentText(current_selection)
        else: self.load_team_combo.setCurrentIndex(0)
        self.load_team_combo.blockSignals(False)

class BattlePlannerTab(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        if BattleLogic:
            self.battle_logic = BattleLogic(
                pokemon_data=self.parent_window.pokemon_data,
                boss_data=self.parent_window.boss_data,
                type_chart=self.parent_window.type_chart,
                moves_data=self.parent_window.moves_data,
                learnsets_data=self.parent_window.learnsets_data
            )
        else:
            self.battle_logic = None
        self.collection = []
        self.init_ui()

    def _get_battle_score(self, result):
        """
        Calcula um "score" para a V4, já que 'battle_index' não existe mais.
        Vitórias rápidas = score alto. Derrotas = score baixo.
        """
        if result.get('winner') == 'player':
            # Score alto, mas subtrai o tempo (vitórias rápidas são melhores)
            return (1000 - result.get('time_elapsed', 300))
        elif result.get('winner') == 'timeout':
            # Empate
            return 0
        else:
            # Derrota (boss venceu)
            # Score negativo, baseado em quanto HP o boss sobrou
            return -1000 - result.get('boss_final_hp_percent', 100)

    def retranslate_ui(self):
        # Guarda o estado atual se necessário
        # (Ex: qual item está selecionado em um ComboBox)

        # Cria um novo widget central para a aba
        new_central_widget = QWidget()
        # O truque: Nós aplicamos o novo layout A ESTE NOVO WIDGET, não ao 'self'
        self.init_ui(parent_widget=new_central_widget)

        # Define o novo widget como o conteúdo da aba
        # Primeiro, remove o antigo
        old_widget = self.findChild(QWidget)
        if old_widget:
            old_widget.deleteLater()

        # Adiciona o novo
        main_layout = QVBoxLayout()
        main_layout.addWidget(new_central_widget)
        self.setLayout(main_layout)

        # Recarrega os dados
        if hasattr(self, 'update_collection'): self.update_collection()
        if hasattr(self, 'update_team_list'): self.update_team_list()
        if hasattr(self, 'update_my_pokemon_list'): self.update_my_pokemon_list()
        if hasattr(self, 'load_hunts_list'): self.load_hunts_list()
        if hasattr(self, 'populate_history_table'): self.populate_history_table()

    def init_ui(self):
        layout = QVBoxLayout(self)
        if not self.battle_logic:
            layout.addWidget(QLabel("Erro: Lógica de batalha não pôde ser carregada."), alignment=Qt.AlignmentFlag.AlignCenter)
            return

        layout.setContentsMargins(20, 20, 20, 20)
        title = QLabel(self.parent_window.get_string("tabs.bosses"))
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        top_controls_layout = QVBoxLayout()
        boss_selection_layout = QHBoxLayout()
        boss_label = QLabel(self.parent_window.get_string("bosses.select_boss"))
        self.boss_select = QComboBox()
        if self.battle_logic.boss_data:
            self.boss_select.addItems(sorted(self.battle_logic.boss_data.keys()))
        self.boss_select.currentTextChanged.connect(self.plan_battle)
        self.boss_select.setFixedWidth(400)
        
        boss_selection_layout.addStretch()
        boss_selection_layout.addWidget(boss_label)
        boss_selection_layout.addWidget(self.boss_select)
        boss_selection_layout.addStretch()

        buttons_container = QWidget()
        buttons_layout = QGridLayout(buttons_container)
        self.suggest_ideal_team_btn = QPushButton(f"{emojis.LÂMPADA} {self.parent_window.get_string('bosses.suggest_ideal_teams_button')}")
        self.simulation_btn = QPushButton(f"{emojis.SIMULADOR} {self.parent_window.get_string('bosses.simulation_button')}")
        self.suggest_ideal_team_btn.clicked.connect(self.show_ideal_teams_dialog)
        self.simulation_btn.clicked.connect(self.show_simulation_dialog)
        
        buttons_layout.addWidget(self.suggest_ideal_team_btn, 0, 0)
        buttons_layout.addWidget(self.simulation_btn, 0, 1)

        centering_buttons_layout = QHBoxLayout()
        centering_buttons_layout.addStretch()
        centering_buttons_layout.addWidget(buttons_container)
        centering_buttons_layout.addStretch()

        top_controls_layout.addLayout(boss_selection_layout)
        top_controls_layout.addLayout(centering_buttons_layout)
        layout.addLayout(top_controls_layout)
        
        details_layout = QHBoxLayout()
        self.boss_image_label = QLabel("?")
        self.boss_image_label.setFixedSize(150, 150)
        self.boss_image_label.setFrameShape(QFrame.Shape.StyledPanel)
        self.boss_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        details_layout.addWidget(self.boss_image_label)
        
        self.boss_info_label = QTextEdit()
        self.boss_info_label.setReadOnly(True)
        self.boss_info_label.setMaximumWidth(400)
        details_layout.addWidget(self.boss_info_label)
        
        self.map_image_label = QLabel(self.parent_window.get_string("bosses.select_to_see_map"))
        self.map_image_label.setFrameShape(QFrame.Shape.StyledPanel)
        self.map_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.map_image_label.setMinimumSize(400, 300)
        self.map_image_label.setWordWrap(True)
        details_layout.addWidget(self.map_image_label)
        layout.addLayout(details_layout)
        
        self.team_sim_results_widget = QFrame()
        self.team_sim_results_widget.setFrameShape(QFrame.Shape.StyledPanel)
        results_layout = QVBoxLayout(self.team_sim_results_widget)
        
        results_title = QLabel(f"<b>{self.parent_window.get_string('bosses.team_analysis_title')}</b>")
        results_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.team_sim_results_label = QLabel()
        self.team_sim_results_label.setText(self.parent_window.get_string("bosses.select_to_see_results"))
        self.team_sim_results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.team_sim_results_label.setWordWrap(True)

        results_layout.addWidget(results_title)
        results_layout.addWidget(self.team_sim_results_label)
        
        layout.insertWidget(3, self.team_sim_results_widget)
        self.team_sim_results_widget.hide()
        
        self.recommendation_container = QWidget()
        self.team_display_layout = QVBoxLayout(self.recommendation_container)
        
        self.recommendations_scroll_area = QScrollArea()
        self.recommendations_scroll_area.setWidgetResizable(True)
        self.recommendations_scroll_area.setWidget(self.recommendation_container)
        self.recommendations_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        layout.addWidget(self.recommendations_scroll_area)
        
        if self.boss_select.count() > 0:
            self.plan_battle()
        
    def update_collection(self):
        self.collection = load_json("my_pokemon.json", [], is_user_data=True)
        if self.battle_logic:
            self.plan_battle()

    def plan_battle(self):
        while self.team_display_layout.count():
            if child := self.team_display_layout.takeAt(0):
                if child.widget(): child.widget().deleteLater()

        boss_name = self.boss_select.currentText()
        self.boss_image_label.setPixmap(QPixmap())
        self.map_image_label.setPixmap(QPixmap())
        self.boss_info_label.clear()
        
        self.team_sim_results_widget.hide()

        if not boss_name:
            self.boss_image_label.setText("?")
            self.map_image_label.setText(self.parent_window.get_string("bosses.select_to_see_map"))
            self.suggest_ideal_team_btn.setEnabled(False)
            self.simulation_btn.setEnabled(False)
            return
            
        self.suggest_ideal_team_btn.setEnabled(True)
        self.simulation_btn.setEnabled(True)
        if image_path := get_pokemon_image_path(boss_name):
            if pixmap := load_pixmap_robustly(image_path, 150): self.boss_image_label.setPixmap(pixmap)
            else: self.boss_image_label.setText(self.parent_window.get_string("globals.image_error"))
        else: self.boss_image_label.setText("?")
        
        boss = self.battle_logic.boss_data.get(boss_name, {})
        
        type1_key = boss.get("type1")
        type2_key = boss.get("type2")
        type1_trans = self.parent_window.get_string(f"types.{type1_key}", type1_key) if type1_key else None
        type2_trans = self.parent_window.get_string(f"types.{type2_key}", type2_key) if type2_key else None
        boss_types_trans = ', '.join(filter(None, [type1_trans, type2_trans]))

        level_str = self.parent_window.get_string('bosses.level_label')
        types_str = self.parent_window.get_string('bosses.types_label')
        rank_str = self.parent_window.get_string('bosses.rank_label')
        location_str = self.parent_window.get_string('bosses.location_label')
        attacks_str = self.parent_window.get_string('bosses.attacks_label')
        
        if boss_name in ["Mew", "Celebi"]:
            info_text = f"<b>{boss_name}</b>{emojis.MITICO}<br>"
        else: info_text = f"<b>{boss_name}</b>{emojis.BOSS}<br>"
        if 'rank' in boss:
             info_text += f"<i>{rank_str}: {boss.get('rank')}</i><br>"
        info_text += f"""<p>{level_str}: {boss.get('level', 'N/A')}<br>
                             {types_str}: {boss_types_trans}<br>
                             {location_str}: {boss.get('location', 'N/A')}<br>
                             <b>{attacks_str}:</b> {', '.join(boss.get('moveset', []))}</p>"""
        self.boss_info_label.setHtml(info_text)
        
        location_name = boss.get('location', '')
        self.map_image_label.setPixmap(QPixmap())
        self.map_image_label.setText("") 

        if boss_name in ["Mew", "Celebi"]:
            self.map_image_label.setText(self.parent_window.get_string("bosses.mythical_location_text"))
        elif location_name and (map_path := get_map_image_path(location_name)):
            if pixmap := load_pixmap_robustly(map_path, self.map_image_label.width(), self.map_image_label.height()):
                self.map_image_label.setPixmap(pixmap)
            else:
                self.map_image_label.setText(self.parent_window.get_string("ev_yield.map_not_found").format(loc=location_name))
        else:
            self.map_image_label.setText(self.parent_window.get_string("bosses.map_not_found_generic", "Mapa não disponível."))
        
        # --- AQUI COMEÇA A LÓGICA V4 CORRIGIDA ---
        if self.collection:
            battle_results = []
            for p_user in self.collection:
                # 1. Roda a simulação V4 (modo Estrategista)
                result = self.battle_logic.run_simulation(p_user, boss_name, use_potions=False, manual_moveset=None)
                if result:
                    # 2. Anexa o Pokémon ao resultado, para não perdê-lo
                    result['pokemon'] = p_user 
                    battle_results.append(result)
            
            if battle_results:
                # 3. Ordena os resultados usando a nova função de score
                battle_results.sort(key=self._get_battle_score, reverse=True)
                
                # 4. Pega os 6 melhores
                recommended_team_results = battle_results[:6]
                
                # 5. Calcula a nova "win_prob" (não existe mais 'calculate_team_win_probability')
                total_wins = 0
                for res in recommended_team_results:
                    if res.get('winner') == 'player':
                        total_wins += 1
                
                win_prob = (total_wins / 6) * 100 # Simples % de vitórias do time

                # 6. Exibe o sumário (o código antigo aqui estava certo)
                if win_prob >= 50:
                    outcome = self.parent_window.get_string("bosses.outcome_victory")
                    color = "green"
                    advice = self.parent_window.get_string("bosses.advice_good")
                else:
                    outcome = self.parent_window.get_string("bosses.outcome_defeat")
                    color = "red"
                    if win_prob > 30:
                        advice = self.parent_window.get_string("bosses.advice_medium")
                    else:
                        advice = self.parent_window.get_string("bosses.advice_bad")

                resultado_texto = f"""
                {self.parent_window.get_string('bosses.simulation_result_label')}: <b style='color:{color};'>{outcome}</b><br>
                {self.parent_window.get_string('bosses.simulation_victory_prob')}: <b>{win_prob:.1f}%</b> ({total_wins}/6 vitórias)<br> 
                <i>{advice}</i>
                """
                self.team_sim_results_label.setText(resultado_texto)
                self.team_sim_results_widget.show()
                
                # 7. Chama a função de exibição V4
                self.update_user_recommendations(boss_name, recommended_team_results)
        
        else: # Se não tem coleção
            self.team_display_layout.addWidget(QLabel(self.parent_window.get_string("bosses.no_suitable_pokemon")))

    def update_user_recommendations(self, boss_name, recommended_team_results):
        # Esta função agora é mais "burra". Ela só exibe os resultados
        # que o plan_battle já calculou.
        if not recommended_team_results:
            self.team_display_layout.addWidget(QLabel(self.parent_window.get_string("bosses.no_suitable_pokemon")))
            return

        self.team_display_layout.addWidget(QLabel(f"<b>{self.parent_window.get_string('bosses.recommended_team_title')}</b>"))

        # Re-calcula a win_prob só para a mensagem
        total_wins = sum(1 for res in recommended_team_results if res.get('winner') == 'player')
        win_prob = (total_wins / 6) * 100

        if win_prob >= 50:
            message = self.parent_window.get_string("bosses.recommendation_strong_team").format(boss=boss_name)
        else:
            message = self.parent_window.get_string("bosses.recommendation_weak_team").format(boss=boss_name)
        
        self.team_display_layout.addWidget(QLabel(message))
        for result in recommended_team_results:
            self.add_pokemon_to_recommendation_ui(result) # Chama a V4
        
        disclaimer = QLabel(f"<i>{self.parent_window.get_string('bosses.disclaimer')}</i>")
        disclaimer.setWordWrap(True)
        self.team_display_layout.addWidget(disclaimer)

    def add_pokemon_to_recommendation_ui(self, result):
        p = result['pokemon'] 
        
        # --- O "CARD" DO POKÉMON ---
        card_frame = QFrame()
        card_frame.setFrameShape(QFrame.Shape.StyledPanel)
        card_layout = QVBoxLayout(card_frame)
        card_layout.setSpacing(6)

        # --- Topo do Card (Info) ---
        top_layout = QHBoxLayout()
        
        image_label = QLabel("?")
        image_label.setFixedSize(64, 64)
        if image_path := get_pokemon_image_path(p['species']):
            if pixmap := load_pixmap_robustly(image_path, 64):
                image_label.setPixmap(pixmap)
                image_label.setText("")
        
        level_str = self.parent_window.get_string('bosses.level_label')
        score_str = self.parent_window.get_string('bosses.battle_index_label', 'Score')
        time_str = self.parent_window.get_string('bosses.survival_time', 'Tempo')
        score = int(self._get_battle_score(result))
        tempo = format_time(result.get('time_elapsed', 0))

        info_label = QLabel(f"<b>{p.get('nickname') or p['species']}</b> ({level_str} {p['level']})<br>"
                            f"<b>{score_str}: {score}</b> | {time_str}: {tempo}")
        info_label.setWordWrap(True)

        top_layout.addWidget(image_label)
        top_layout.addWidget(info_label, 1) # Adiciona stretch=1
        
        # --- Base do Card (Golpes) ---
        moves_layout = QHBoxLayout()
        moveset = result.get('used_moveset', ['?']*6)
        
        # Coluna de Golpes 1-3
        moves_str_1 = "<b>Golpes:</b><br>" + "<br>".join([f"• {m}" for m in moveset[:3]])
        moves_label_1 = QLabel(moves_str_1)
        moves_label_1.setWordWrap(True)
        moves_label_1.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Coluna de Golpes 4-6
        moves_str_2 = "<br>" + "<br>".join([f"• {m}" for m in moveset[3:6] if m])
        moves_label_2 = QLabel(moves_str_2)
        moves_label_2.setWordWrap(True)
        moves_label_2.setAlignment(Qt.AlignmentFlag.AlignTop)

        moves_layout.addWidget(moves_label_1)
        moves_layout.addWidget(moves_label_2)
        moves_layout.addStretch()

        # Adiciona tudo ao card
        card_layout.addLayout(top_layout)
        card_layout.addWidget(HorizontalLine()) # Linha divisória
        card_layout.addLayout(moves_layout)
        
        # Adiciona o card ao layout vertical
        self.team_display_layout.addWidget(card_frame)

    def show_ideal_teams_dialog(self):
        boss_name = self.boss_select.currentText()
        if not boss_name: return

        # --- LÓGICA V4.1: CALCULANDO "MEU MELHOR TIME" (DA COLEÇÃO) ---
        my_best_team_results = []
        if self.collection:
            battle_results = []
            for p_user in self.collection:
                # Simula o Pokémon real no nível máximo para comparação justa
                sim_pokemon = p_user.copy()
                sim_pokemon['level'] = 125 
                
                result = self.battle_logic.run_simulation(sim_pokemon, boss_name, use_potions=False, manual_moveset=None)
                if result:
                    result['pokemon'] = p_user # Anexa o pokemon original
                    battle_results.append(result)
            
            battle_results.sort(key=self._get_battle_score, reverse=True)
            my_best_team_results = battle_results[:6]

        # --- LÓGICA V4.1: CALCULANDO O "TIME PERFEITO" (DO JOGO TODO) ---
        # (A lógica que eu tinha esquecido de adicionar de volta)
        perfect_team_results = []
        all_pokemon_data = self.parent_window.pokemon_data
        
        # Filtra a lista para tirar pré-evoluções (qualquer poke que exista em EVOLUTIONS)
        # e bosses (qualquer poke que exista em boss_data)
        final_forms = [name for name, data in all_pokemon_data.items() 
                       if name not in EVOLUTIONS and name not in self.battle_logic.boss_data]

        perfect_battle_results = []
        for species_name in final_forms:
            # Cria um Pokémon "perfeito" para simulação
            p_data = all_pokemon_data[species_name]
            base_stats = p_data.get("base_stats", {})
            
            # Pula pokes fracos que não são forma final (ex: Unown)
            if sum(base_stats.values()) < 480: # Chute de "Stats Totais"
                continue

            mock_pokemon = {
                "species": species_name,
                "level": 125,
                "nature": "Hardy", # Nature neutra para a simulação
                "ivs": {stat: 31 for stat in base_stats},
                "evs": {stat: 2500 for stat in base_stats}, # EV máximo (chute)
                "nickname": species_name # Usa o nome da espécie
            }
            
            result = self.battle_logic.run_simulation(mock_pokemon, boss_name, use_potions=False, manual_moveset=None)
            if result:
                result['pokemon'] = mock_pokemon # Anexa o mock
                perfect_battle_results.append(result)

        perfect_battle_results.sort(key=self._get_battle_score, reverse=True)
        perfect_team_results = perfect_battle_results[:6]
        # --- FIM DA LÓGICA V4.1 ---

        # Agora passamos os DOIS times para o Dialog
        dialog = IdealTeamsDialog(boss_name, self, perfect_team_results, my_best_team_results)
        dialog.exec()

    def show_simulation_dialog(self):
        boss_name = self.boss_select.currentText()
        if not boss_name: return

        if not self.collection:
            QMessageBox.warning(self, self.parent_window.get_string("globals.error"), self.parent_window.get_string("bosses.simulation_no_pokemon_error"))
            return

        dialog = SimulationDialog(boss_name, self.collection, self)
        dialog.exec()

class IdealTeamsDialog(QDialog):
    def __init__(self, boss_name, battle_planner_tab, perfect_team, my_best_team):
        super().__init__(battle_planner_tab.parent_window)
        self.parent_window = battle_planner_tab.parent_window
        self.battle_planner = battle_planner_tab
        self.battle_logic = battle_planner_tab.battle_logic
        self.boss_name = boss_name
        self.perfect_team = perfect_team # Lista de Resultados do Time Perfeito
        self.my_best_team = my_best_team # Lista de Resultados do Meu Time

        self.setWindowTitle(self.parent_window.get_string("bosses.ideal_teams_title").format(boss=boss_name))
        # Aumentei o tamanho para caber os cards
        self.setMinimumSize(1200, 800) 
        
        self.layout = QVBoxLayout(self)
        
        main_hbox = QHBoxLayout()

        # --- Coluna 1: Time Perfeito (do Jogo) ---
        team1_vbox = QVBoxLayout()
        team1_vbox.addWidget(QLabel(f"<b>{self.parent_window.get_string('bosses.perfect_team_title')}</b>"))
        
        # Área de Rolagem para o Time 1
        scroll1 = QScrollArea()
        scroll1.setWidgetResizable(True)
        scroll1.setFrameShape(QFrame.Shape.StyledPanel)
        team1_widget = self.create_team_widget(self.perfect_team) # Chama o novo layout de "Card"
        scroll1.setWidget(team1_widget)
        team1_vbox.addWidget(scroll1)
        
        if self.perfect_team:
            # Chama a análise de performance V3
            team1_vbox.addWidget(self.create_team_analysis_widget(self.perfect_team, is_perfect_team=True))

        # --- Coluna 2: Seu Melhor Time (da Coleção) ---
        team2_vbox = QVBoxLayout()
        team2_vbox.addWidget(QLabel(f"<b>{self.parent_window.get_string('bosses.your_best_team_title')}</b>"))

        # Área de Rolagem para o Time 2
        scroll2 = QScrollArea()
        scroll2.setWidgetResizable(True)
        scroll2.setFrameShape(QFrame.Shape.StyledPanel)
        team2_widget = self.create_team_widget(self.my_best_team) # Chama o novo layout de "Card"
        scroll2.setWidget(team2_widget)
        team2_vbox.addWidget(scroll2)

        if self.my_best_team:
            # Chama a análise de performance V3
            team2_vbox.addWidget(self.create_team_analysis_widget(self.my_best_team, is_perfect_team=False))

        main_hbox.addLayout(team1_vbox, 1) # stretch 1
        main_hbox.addLayout(team2_vbox, 1) # stretch 1
        self.layout.addLayout(main_hbox)

    def _show_pokedex(self, pokemon_name):
        self.parent_window.show_pokedex_for(pokemon_name)

    def create_team_widget(self, team_results):
        # O container principal é vertical (QVBoxLayout)
        container_widget = QWidget()
        team_layout = QVBoxLayout(container_widget)
        team_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        team_layout.setSpacing(10) # Espaço entre os "cards"

        if not team_results:
            team_layout.addWidget(QLabel(self.parent_window.get_string('globals.not_available', 'N/A')))
        else:
            for i, result in enumerate(team_results):
                p_info = result['pokemon'] # Pega o dict do Pokémon
                species_name = p_info['species']
                
                # --- O "CARD" DO POKÉMON ---
                card_frame = QFrame()
                card_frame.setFrameShape(QFrame.Shape.StyledPanel)
                card_layout = QVBoxLayout(card_frame)
                card_layout.setSpacing(6)

                # --- Topo do Card (Info) ---
                top_layout = QHBoxLayout()
                
                member_button = QToolButton()
                member_button.setCursor(Qt.CursorShape.PointingHandCursor)
                member_button.setFixedSize(100, 100)
                member_button.setStyleSheet("QToolButton { border: none; }")
                member_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

                if img_path := get_pokemon_image_path(species_name):
                    if pixmap := load_pixmap_robustly(img_path, 64):
                        member_button.setIcon(QIcon(pixmap))
                        member_button.setIconSize(QSize(64, 64))

                name_label_text = p_info.get('nickname') or species_name
                member_button.setText(f"{name_label_text}\n(Lvl {p_info.get('level', '?')})") # Mostra o nível
                font = member_button.font()
                font.setBold(True)
                member_button.setFont(font)
                member_button.clicked.connect(lambda _, name=species_name: self._show_pokedex(name))

                # Info de Score/Tempo
                score_str = self.parent_window.get_string('bosses.battle_index_label', 'Score')
                time_str = self.parent_window.get_string('bosses.survival_time', 'Tempo')
                score = int(self.battle_planner._get_battle_score(result))
                tempo = format_time(result.get('time_elapsed', 0))
                
                score_label = QLabel(f"<b>{score_str}: {score}</b><br>{time_str}: {tempo}")
                score_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

                top_layout.addWidget(member_button)
                top_layout.addStretch()
                top_layout.addWidget(score_label)
                
                # --- Base do Card (Golpes) ---
                moves_layout = QHBoxLayout()
                moveset = result.get('used_moveset', ['?']*6)
                
                # Coluna de Golpes 1-3
                moves_str_1 = "<b>Golpes:</b><br>" + "<br>".join([f"• {m}" for m in moveset[:3]])
                moves_label_1 = QLabel(moves_str_1)
                moves_label_1.setWordWrap(True)
                moves_label_1.setAlignment(Qt.AlignmentFlag.AlignTop)
                
                # Coluna de Golpes 4-6 (com padding para alinhar)
                moves_str_2 = "<br>" + "<br>".join([f"• {m}" for m in moveset[3:6] if m])
                moves_label_2 = QLabel(moves_str_2)
                moves_label_2.setWordWrap(True)
                moves_label_2.setAlignment(Qt.AlignmentFlag.AlignTop)

                moves_layout.addWidget(moves_label_1)
                moves_layout.addWidget(moves_label_2)
                moves_layout.addStretch() # Empurra os golpes para a esquerda

                # Adiciona tudo ao card
                card_layout.addLayout(top_layout)
                card_layout.addWidget(HorizontalLine()) # Linha divisória
                card_layout.addLayout(moves_layout)
                
                # Adiciona o card ao layout vertical
                team_layout.addWidget(card_frame)

        return container_widget

    def create_team_analysis_widget(self, team_results, is_perfect_team):
        analysis_box = QFrame()
        analysis_box.setFrameShape(QFrame.Shape.StyledPanel)
        analysis_layout = QVBoxLayout(analysis_box)
        
        title = QLabel(f"<b>{self.parent_window.get_string('bosses.team_performance_analysis')}</b>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        analysis_layout.addWidget(title)
        
        results_text = ""
        
        # --- LÓGICA DE NÍVEL V3 (Corrigido) ---
        # "tem que mostrar desde o lvl 100"
        if is_perfect_team:
            level_benchmarks = [100, 105, 110, 115, 120, 125]
        else: # Seu time (usa os níveis da sua coleção)
            level_benchmarks = [105, 110, 115, 120, 125] # (O benchmark antigo)
        # --- FIM DA LÓGICA V3 ---
        
        team = [res['pokemon'] for res in team_results] # Extrai os pokes

        for level in level_benchmarks:
            team_wins = 0
            total_time = 0
            
            for member in team:
                sim_pokemon = member.copy()
                sim_pokemon['level'] = level
                
                result = self.battle_logic.run_simulation(
                    sim_pokemon, self.boss_name, use_potions=False, manual_moveset=None
                )
                
                if result.get('winner') == 'player':
                    team_wins += 1
                    total_time += result.get('time_elapsed', 0)
            
            avg_time = (total_time / team_wins) if team_wins > 0 else 0
            
            level_str = self.parent_window.get_string('bosses.team_level_analysis')
            results_text += f"<li><b>{level_str.format(level=level)}:</b> {team_wins} / {len(team)} vitórias (Média: {avg_time:.1f}s)</li>"

        results_label = QLabel(f"<ul>{results_text}</ul>")
        results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        analysis_layout.addWidget(results_label)
        
        return analysis_box

    def get_recommended_nature(self, pokemon_name):
        base_stats = self.battle_logic.pokemon_data.get(pokemon_name, {}).get("base_stats", {})
        attack = base_stats.get("attack", 0)
        sp_attack = base_stats.get("special-attack", 0)
        
        if attack > sp_attack + 10: return self.parent_window.get_string('natures.Adamant', "Adamant")
        if sp_attack > attack + 10: return self.parent_window.get_string('natures.Modest', "Modest")
        return self.parent_window.get_string('natures.Hardy', "Hardy")

    def get_iv_recommendation(self, pokemon_name):
        base_stats = self.battle_logic.pokemon_data.get(pokemon_name, {}).get("base_stats", {})
        if not base_stats:
            return "IVs: 25+ em HP e Ataques"

        stat_map = {
            "attack": "Attack", "defense": "Defense", 
            "special-attack": "Sp. Atk", "special-defense": "Sp. Def", "speed": "Speed"
        }
        
        sorted_stats = sorted(stat_map.keys(), key=lambda k: base_stats.get(k, 0), reverse=True)
        
        top_stat1 = stat_map.get(sorted_stats[0])
        top_stat2 = stat_map.get(sorted_stats[1])

        return self.parent_window.get_string("bosses.iv_recommendation_text").format(stat1=top_stat1, stat2=top_stat2)

    def find_min_level(self, pokemon_name):
        boss_level = self.battle_logic.boss_data.get(self.boss_name, {}).get("level", 100)
        mock_pokemon = {"species": pokemon_name}
        
        ivs = {stat: 31 for stat in self.battle_logic.pokemon_data[pokemon_name]["base_stats"]}
        evs = {stat: 2500 for stat in self.battle_logic.pokemon_data[pokemon_name]["base_stats"]}
        nature = self.get_recommended_nature(pokemon_name)

        for level in range(boss_level, 126):
            result = self.battle_logic.run_simulation(mock_pokemon, self.boss_name, p_level=level, p_ivs=ivs, p_evs=evs, p_nature=nature)
            if result and result['battle_index'] >= 1.0:
                return level
        
        return f"125{self.parent_window.get_string('bosses.level_hard')}"

    def calculate_ideal_score(self, pokemon_name):
        p_data = self.battle_logic.pokemon_data.get(pokemon_name)
        boss_pokemon_data = self.battle_logic.pokemon_data.get(self.boss_name)
        if not p_data or not boss_pokemon_data: return 0

        base_stats = p_data.get("base_stats", {})
        
        p_types = [p_data["type1"]] + ([p_data.get("type2")] if p_data.get("type2") else [])
        boss_types = [boss_pokemon_data["type1"]] + ([boss_pokemon_data.get("type2")] if boss_pokemon_data.get("type2") else [])
        
        def_type_score = 1
        num_moves = 0
        for move_name in self.battle_logic.boss_data.get(self.boss_name, {}).get("moveset", []):
            move_info = self.battle_logic.moves_data.get(move_name)
            if not move_info or move_info.get("category") == "Status": continue
            num_moves += 1
            multiplier = 1.0
            for p_type in p_types:
                if not p_type: continue
                multiplier *= self.battle_logic.type_chart.get(move_info["type"], {}).get(p_type, 1.0)
            def_type_score += (1 - multiplier)
        
        if num_moves > 0: def_type_score /= num_moves

        off_type_score = 1
        for user_type in p_types:
            if not user_type: continue
            type_mult = 1.0
            for boss_type in boss_types:
                type_mult *= self.battle_logic.type_chart.get(user_type, {}).get(boss_type, 1.0)
            off_type_score = max(off_type_score, type_mult)
        
        stat_score = sum(base_stats.values()) / 720
        
        return (off_type_score * 3.0) + (def_type_score * 2.0) + (stat_score * 1.0)
    
    def generate_perfect_team(self):
        scores = []
        boss_list = self.battle_logic.boss_data.keys()
        for name, data in self.battle_logic.pokemon_data.items():
            if name in EVOLUTIONS:
                continue
            
            if name in boss_list:
                continue
            if sum(data.get("base_stats", {}).values()) < 480:
                continue
            
            scores.append((self.calculate_ideal_score(name), name))
        
        ranked_pokemon = sorted(scores, key=lambda x: x[0], reverse=True)
        
        perfect_team = []
        for _, p_name in ranked_pokemon[:6]:
            perfect_team.append({
                "name": p_name,
                "level": self.find_min_level(p_name),
                "nature": self.get_recommended_nature(p_name),
                "ivs": self.get_iv_recommendation(p_name)
            })

        return perfect_team

class SimulationDialog(QDialog):
    def __init__(self, boss_name, collection, battle_planner_tab):
        super().__init__(battle_planner_tab.parent_window)
        self.parent_window = battle_planner_tab.parent_window
        self.battle_logic = battle_planner_tab.battle_logic
        self.boss_name = boss_name
        self.collection = collection

        self.setWindowTitle(self.parent_window.get_string("bosses.simulation_title").format(boss=boss_name))
        self.setMinimumSize(800, 600) # Aumenta a altura para caber os golpes

        self.layout = QVBoxLayout(self)
        self.team_selectors = []
        self.team_image_labels = []
        
        # --- NOVO (V4): Lista para guardar os 6 QComboBox de golpes ---
        self.team_move_selectors = []

        controls_layout = QHBoxLayout()
        self.saved_teams_combo = QComboBox()
        self.load_saved_teams()
        self.saved_teams_combo.currentTextChanged.connect(self.load_selected_team)
        
        self.level_spinbox = QSpinBox()
        self.level_spinbox.setRange(1, 125)
        self.level_spinbox.setValue(100)
        self.level_spinbox.setPrefix(self.parent_window.get_string("bosses.simulation_level_prefix"))

        controls_layout.addWidget(QLabel(self.parent_window.get_string("teams.load_placeholder")))
        controls_layout.addWidget(self.saved_teams_combo)
        controls_layout.addWidget(self.level_spinbox)
        self.layout.addLayout(controls_layout)

        team_selection_layout = QHBoxLayout()

        sort_mode = self.parent_window.config.get("sort_order", "Ordem Alfabética")
        if sort_mode == "Ordem da Pokédex":
            sorted_collection = sorted(self.collection, key=lambda p: self.parent_window.pokedex_order.get(p["species"], 9999))
        else:
            sorted_collection = sorted(self.collection, key=lambda p: (p.get("nickname") or p["species"]).lower())
        pokemon_options = [self.parent_window.get_string("globals.none")] + [(p.get("nickname") or p["species"]) for p in sorted_collection]
        
        for i in range(6):
            member_layout = QVBoxLayout()
            image_label = QLabel("?")
            image_label.setFixedSize(80, 80)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # 1. Seletor de Pokémon
            selector = QComboBox()
            selector.addItems(pokemon_options)
            # --- MUDANÇA (V4): Conecta ao novo slot ---
            selector.currentIndexChanged.connect(lambda _, index=i: self.update_member_info(index))
            
            member_layout.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignCenter)
            member_layout.addWidget(selector)
            
            # --- NOVO (V4): Adiciona os 6 seletores de golpe ---
            move_selector_group = QWidget()
            move_layout = QVBoxLayout(move_selector_group)
            move_layout.setContentsMargins(0, 0, 0, 0)
            
            # Criamos 6 caixas por Pokémon, mas só mostraremos as necessárias
            poke_move_selectors = []
            for j in range(6):
                move_selector = QComboBox()
                move_selector.setEnabled(False)
                move_layout.addWidget(move_selector)
                poke_move_selectors.append(move_selector)
            
            self.team_move_selectors.append(poke_move_selectors) # Lista de listas
            member_layout.addWidget(move_selector_group)
            # --- FIM DA MUDANÇA ---
            
            self.team_selectors.append(selector)
            self.team_image_labels.append(image_label)
            team_selection_layout.addLayout(member_layout)
            
        self.layout.addLayout(team_selection_layout)

        self.simulate_btn = QPushButton(self.parent_window.get_string("bosses.simulation_run_button"))
        self.simulate_btn.clicked.connect(self.run_simulation)
        self.layout.addWidget(self.simulate_btn)

        # --- NOVO (V4): Área de Log ---
        self.results_log = QTextEdit()
        self.results_log.setReadOnly(True)
        self.results_log.setPlaceholderText(self.parent_window.get_string("bosses.simulation_waiting"))
        self.results_log.setFixedHeight(200) # Altura fixa para o log
        self.layout.addWidget(self.results_log)
        # --- FIM DA MUDANÇA ---

        disclaimer = QLabel(f"<i>{self.parent_window.get_string('bosses.disclaimer')}</i>")
        disclaimer.setWordWrap(True)
        self.layout.addWidget(disclaimer)

        self.layout.addStretch()

    def load_saved_teams(self):
        self.teams_data = load_json("teams.json", {}, is_user_data=True)
        self.saved_teams_combo.addItem(self.parent_window.get_string("globals.none"))
        self.saved_teams_combo.addItems(sorted(self.teams_data.keys()))

    def load_selected_team(self, team_name):
        if team_name and team_name != self.parent_window.get_string("globals.none"):
            team_members = self.teams_data.get(team_name, [])
            for i, selector in enumerate(self.team_selectors):
                if i < len(team_members):
                    index = selector.findText(team_members[i])
                    if index != -1:
                        selector.setCurrentIndex(index)
                    else:
                        selector.setCurrentIndex(0)
                else:
                    selector.setCurrentIndex(0)
        else:
             for i, selector in enumerate(self.team_selectors):
                 selector.setCurrentIndex(0)

    # --- FUNÇÃO ATUALIZADA (V4) ---
    def update_member_info(self, selector_index):
        """
        Esta função agora atualiza a IMAGEM e os GOLPES
        baseado no Pokémon selecionado e seu nível.
        """
        selector = self.team_selectors[selector_index]
        image_label = self.team_image_labels[selector_index]
        move_selectors = self.team_move_selectors[selector_index] # Pega a *lista* de 6 QComboBox
        
        pokemon_name = selector.currentText()

        # 1. Limpa tudo
        image_label.setPixmap(QPixmap())
        image_label.setText("?")
        for move_selector in move_selectors:
            move_selector.clear()
            move_selector.setEnabled(False)

        if pokemon_name == self.parent_window.get_string("globals.none"):
            return

        # 2. Encontra o Pokémon na coleção
        found_pokemon = next((p for p in self.collection if (p.get("nickname") or p["species"]) == pokemon_name), None)
        if not found_pokemon:
            return

        # 3. Atualiza a Imagem
        if image_path := get_pokemon_image_path(found_pokemon['species']):
            if pixmap := load_pixmap_robustly(image_path, 80):
                image_label.setPixmap(pixmap)
                image_label.setText("")

        # 4. Filtra o "Grimório" (pokemon_learnsets.json)
        level = found_pokemon['level']
        species = found_pokemon['species']
        
        learnset_data = self.battle_logic.learnsets_data.get(species, [])
        
        # Pega todos os golpes que ele aprende ATÉ o nível dele
        available_moves = [
            move_dict["move"] for move_dict in learnset_data 
            if move_dict["level"] <= level
        ]
        
        # Filtra duplicatas e ordena
        available_moves = sorted(list(set(available_moves)))

        # 5. Popula as 6 caixas de golpe
        if available_moves:
            for i in range(6):
                move_selector = move_selectors[i]
                move_selector.setEnabled(True)
                move_selector.addItems([self.parent_window.get_string("globals.none")] + available_moves)
        else:
            # Se o poke não tiver golpes no Grimório
            move_selectors[0].setEnabled(True)
            move_selectors[0].addItem("ERRO: Grimório vazio")

    # --- FUNÇÃO ATUALIZADA (V4) ---
    def run_simulation(self):
        """
        Roda a simulação V4 usando o moveset manual
        e exibe os resultados no log.
        """
        self.results_log.clear()
        
        team_to_simulate = []
        manual_movesets = []
        
        # 1. Monta os times e os movesets manuais
        for i in range(6):
            poke_name = self.team_selectors[i].currentText()
            if poke_name == self.parent_window.get_string("globals.none"):
                continue
                
            found_pokemon = next((p for p in self.collection if (p.get("nickname") or p["species"]) == poke_name), None)
            if found_pokemon:
                # Pega os 6 golpes que o usuário selecionou para este Pokémon
                selected_moves = []
                for move_selector in self.team_move_selectors[i]:
                    move = move_selector.currentText()
                    if move != self.parent_window.get_string("globals.none"):
                        selected_moves.append(move)
                
                # Remove duplicatas se o usuário selecionar o mesmo golpe 6x
                selected_moves = list(set(selected_moves)) 
                
                if not selected_moves:
                    QMessageBox.warning(self, "Erro", f"Selecione pelo menos um golpe para {poke_name}.")
                    return

                team_to_simulate.append(found_pokemon)
                manual_movesets.append(selected_moves)

        if not team_to_simulate:
            QMessageBox.warning(self, self.parent_window.get_string("globals.error"), self.parent_window.get_string("teams.error_select_pokemon"))
            return

        simulation_level = self.level_spinbox.value()
        
        full_log = ""
        total_wins = 0
        
        # 2. Roda a simulação 1-vs-1 para cada Pokémon
        for i, p_user in enumerate(team_to_simulate):
            # Cria uma cópia para simular no nível escolhido
            sim_pokemon = p_user.copy()
            sim_pokemon['level'] = simulation_level
            
            p_moveset = manual_movesets[i]
            
            result = self.battle_logic.run_simulation(
                sim_pokemon, 
                self.boss_name, 
                use_potions=False, # (Podemos adicionar uma checkbox para isso depois)
                manual_moveset=p_moveset
            )
            
            # 3. Exibe o resultado
            winner = result.get('winner', 'error')
            time_str = f"{result.get('time_elapsed', 0):.1f}s"
            
            if winner == 'player':
                total_wins += 1
                full_log += f"--- {sim_pokemon['nickname'] or sim_pokemon['species']} (Lvl {simulation_level}) vs {self.boss_name} ---\n"
                full_log += f"Resultado: VITÓRIA ({time_str})\n"
                full_log += "\n".join(result.get('log', []))
                full_log += "\n\n"
            else:
                full_log += f"--- {sim_pokemon['nickname'] or sim_pokemon['species']} (Lvl {simulation_level}) vs {self.boss_name} ---\n"
                full_log += f"Resultado: DERROTA ({time_str})\n\n"

        self.results_log.setText(f"### RESULTADO DA SIMULAÇÃO: {total_wins} / {len(team_to_simulate)} VITÓRIAS ###\n\n{full_log}")

class PokedexDialog(QDialog):
    """
    Janela que exibe informações de um Pokémon.
    Versão refinada com barras de stats base e nomes de tipos.
    """
    def __init__(self, pokedex_data, parent_window):
        super().__init__(parent_window)
        self.parent_window = parent_window
        self.data = pokedex_data
        
        species_name = self.data.get("species", "Pokémon")
        self.setWindowTitle(self.parent_window.get_string("pokedex.window_title", "Pokédex - {species_name}").format(species_name=species_name))
        self.setMinimumWidth(600)
        self.init_ui()

    def _load_pokemon_data(self, pokemon_name):
        # Limpa a janela antiga se estiver recarregando
        if hasattr(self, 'main_layout'):
            while self.main_layout.count():
                item = self.main_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        self.data = self.parent_window.ideal_teams_dialog._get_pokedex_data(pokemon_name) # Reutiliza a função que já criamos!

        species_name = self.data.get("species", "Pokémon")
        self.setWindowTitle(f"Pokédex - {species_name}")
        self.setMinimumWidth(600)

        self.init_ui()

    def _create_type_widget(self, type_key, size="normal"):
        if not type_key: return None
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Define tamanhos com base no parâmetro
        icon_size = 16 if size == "small" else 24
        font_size = 7 if size == "small" else 9
        
        if (icon := get_icon_from_path(emojis.TYPE_ICONS.get(type_key))):
            icon_label = QLabel()
            icon_label.setPixmap(icon.pixmap(icon_size, icon_size))
            layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
            
        type_name = self.parent_window.get_string(f"types.{type_key}", type_key)
        name_label = QLabel(type_name)
        name_label.setStyleSheet(f"font-size: {font_size}px; color: white; font-weight: bold;")
        layout.addWidget(name_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        return container

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        
        # --- Painel Superior (Com Nomes dos Tipos) ---
        top_layout = QHBoxLayout()
        self.pokemon_image = QLabel("?"); self.pokemon_image.setFixedSize(128, 128); self.pokemon_image.setFrameShape(QFrame.Shape.StyledPanel); self.pokemon_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if pixmap := load_pixmap_robustly(self.data.get("image_path"), 120): self.pokemon_image.setPixmap(pixmap)
        
        info_layout = QVBoxLayout()
        name_label = QLabel(f"<b><font size='+2'>{self.data.get('species')}</font></b>")
        
        types_container = QWidget()
        types_layout = QHBoxLayout(types_container)
        
        type1_widget = self._create_type_widget(self.data.get("type1"))
        if type1_widget: types_layout.addWidget(type1_widget)
            
        type2_widget = self._create_type_widget(self.data.get("type2"))
        if type2_widget: types_layout.addWidget(type2_widget)
        
        types_layout.addStretch()
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(types_container)
        top_layout.addWidget(self.pokemon_image); top_layout.addLayout(info_layout)
        self.main_layout.addLayout(top_layout)

        # --- Painel de Stats (Com Barras de Stats Base) ---
        stats_frame = QFrame(); stats_frame.setFrameShape(QFrame.Shape.StyledPanel)
        stats_layout = QFormLayout(stats_frame)
        stats_layout.addRow(QLabel(f"<b>{self.parent_window.get_string('base_stats_header', 'Stats Base')}</b>"))
        
        base_stats = self.data.get("base_stats", {})
        stat_labels_map = self.parent_window.collection_tab.stat_labels
        
        for stat_key, stat_value in base_stats.items():
            label_text = stat_labels_map.get(stat_key, stat_key.capitalize())
            
            # Container para o valor e a barra de stat
            stat_widget = QWidget()
            row_layout = QHBoxLayout(stat_widget)
            row_layout.setContentsMargins(0,0,0,0)
            
            value_label = QLabel(f"<b>{stat_value}</b>")
            row_layout.addWidget(value_label)
            
            # Chamando a função com o novo contexto!
            if bar_pixmap := get_dynamic_stat_bar(self.parent_window, stat_key, stat_value, context='base'):
                bar_label = QLabel()
                bar_label.setPixmap(bar_pixmap)
                row_layout.addWidget(bar_label)
            
            row_layout.addStretch()
            stats_layout.addRow(f"{label_text}:", stat_widget)
            
        self.main_layout.addWidget(stats_frame)

        # O resto da classe (Família Evolutiva, Mapa) continua igual ao que já fizemos...
        # ...
        family = self.data.get("family", [])
        if len(family) > 1:
            family_frame = QFrame(); family_frame.setFrameShape(QFrame.Shape.StyledPanel)
            family_layout = QVBoxLayout(family_frame)
            family_label = QLabel(f"<b>{self.parent_window.get_string('pokedex.evolutionary_family', 'Família Evolutiva')}</b>"); 
            family_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            family_buttons_layout = QHBoxLayout()
            
            for member_name in family:
                member_button = QToolButton()
                member_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
                member_button.setCursor(Qt.CursorShape.PointingHandCursor)
                member_button.setFixedSize(80, 80)
                member_button.setStyleSheet("QToolButton { border: none; }")
                if img_path := get_pokemon_image_path(member_name):
                    member_button.setIcon(QIcon(load_pixmap_robustly(img_path, 48)))
                    member_button.setIconSize(QSize(48, 48))
                member_button.setText(member_name)
                
                if member_name == self.data.get("species"):
                    member_button.setEnabled(False) 
                else:
                    member_button.clicked.connect(lambda _, name=member_name: self.parent_window.show_pokedex_for(name))
                
                family_buttons_layout.addWidget(member_button)

            family_layout.addWidget(family_label)
            family_layout.addLayout(family_buttons_layout)
            self.main_layout.addWidget(family_frame)

        map_title_text = self.data.get("location_name", "Localização")
        map_label_title = QLabel(f"<b>{map_title_text}</b>") # map_title_text já é traduzido pelo get_pokedex_data; 
        map_label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(map_label_title)
        scroll_area = QScrollArea(); scroll_area.setWidgetResizable(True); scroll_area.setFixedHeight(220)
        map_container = QWidget(); maps_layout = QHBoxLayout(map_container)
        locations = self.data.get("locations", [])
        if locations:
            for loc in locations:
                if pixmap := load_pixmap_robustly(loc["path"], 550, 200):
                    map_widget = QLabel(); map_widget.setPixmap(pixmap); maps_layout.addWidget(map_widget)
        else:
            no_map_label = QLabel(self.parent_window.get_string("bosses.map_not_found_generic", "Mapa não disponível")); 
            no_map_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            maps_layout.addWidget(no_map_label)
        scroll_area.setWidget(map_container)
        self.main_layout.addWidget(scroll_area)

    # Reutiliza a mesma lógica de busca recursiva aqui dentro
    def _find_base_spawn_info_recursive(self, pokemon_name):
        spawn_info = self.parent_window.spawn_rates.get(pokemon_name)
        if spawn_info: return pokemon_name, spawn_info
        pre_evo = self.parent_window.reverse_evolutions.get(pokemon_name)
        if pre_evo: return self._find_base_spawn_info_recursive(pre_evo)
        return None, None
    
class PokedexTab(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window

        self.POKEDEX_BASE_WIDTH = 1131
        self.POKEDEX_BASE_HEIGHT = 758
        self.overlay_widgets_rects = {}
        self.overlay_widget = None
        
        self.MODO_DEBUG = True
        self.power_state = "DESLIGADA"
        self.pokedex_list = self.parent_window.get_pokedex_list()
        self.current_pokemon_index = 0
        
        self.menu_keys = [
            "pokedex.menu_pokemon", "pokedex.menu_quests", "pokedex.menu_types", 
            "pokedex.menu_maps", "pokedex.menu_comparative", "pokedex.menu_topics", 
            "pokedex.menu_ev_hotspots"
        ]
        self.menu_buttons = []
        self.current_menu_index = 0

        self.selected_comparison_pokemon_data = []
        self.active_pokemon_for_removal = None
        self.comparative_is_showing_results = False

        self.types_submenu_keys = [
            "pokedex.types_explorer", "pokedex.types_boss_analysis", "pokedex.types_defensive_analysis"
        ]
        self.current_types_mode_index = 0
        self.types_submenu_buttons = []

        self.topic_keys = [
            "pokedex.topic_max_hp", "pokedex.topic_max_atk", "pokedex.topic_max_def", 
            "pokedex.topic_max_sp_atk", "pokedex.topic_max_sp_def", "pokedex.topic_max_speed",
            "pokedex.topic_richest_quest", "pokedex.topic_best_xp_quest", "pokedex.topic_best_ratio_quest",
            "pokedex.topic_priciest_candy", "pokedex.topic_most_common", "pokedex.topic_most_rare"
        ]
        self.ev_stat_keys = ['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed']

        self.pokemon_list_widget = None
        self.pokemon_detail_image = QLabel()
        self.quests_list_widget = None
        self.maps_list_widget = None
        
        self.animation_timer = QTimer(self); self.animation_timer.timeout.connect(self._update_pokedex_animation)
        self.pokedex_frames = []
        self.current_frame = 0
        self.animation_direction = 1
        
        self.player = QMediaPlayer(); self.audio_output = QAudioOutput(); self.player.setAudioOutput(self.audio_output)
        
        self.init_ui()
        self._load_animation_frames()

    def resizeEvent(self, event: QResizeEvent):
        """
        Este método é chamado automaticamente sempre que a janela é redimensionada.
        Ele garante que a posição dos botões e telas seja recalculada.
        """
        super().resizeEvent(event)
        
        if self.overlay_widget:
            self.overlay_widget.resize(self.pokedex_bg.size())

        self._update_overlay_positions()

    def _update_overlay_positions(self):
        """
        Calcula a nova posição de todos os elementos da interface com base na
        posição atual da imagem de fundo da Pokédex.
        """
        if not hasattr(self, 'pokedex_bg') or not self.pokedex_bg.pixmap() or self.pokedex_bg.pixmap().isNull():
            return

        label_size = self.pokedex_bg.size()
        pixmap_size = self.pokedex_bg.pixmap().size()
        
        offset_x = (label_size.width() - pixmap_size.width()) // 2
        offset_y = (label_size.height() - pixmap_size.height()) // 2

        for widget, original_rect in self.overlay_widgets_rects.items():
            if widget:
                new_rect = original_rect.translated(offset_x, offset_y)
                widget.setGeometry(new_rect)

    def init_ui(self):
        # --- SUBSTITUA O CONTEÚDO DESTE MÉTODO PELO CÓDIGO ABAIXO ---
        main_layout = QHBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.pokedex_bg = QLabel()
        self.pokedex_bg.setScaledContents(False)
        self.pokedex_bg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.pokedex_bg)
        
        self.overlay_widget = QWidget(self.pokedex_bg)
        self.overlay_widget.setStyleSheet("background-color: transparent;")
        self.overlay_widget.setGeometry(self.pokedex_bg.rect())

        self.base_list_style = """ QListWidget { border: none; background-color: transparent; color: #3c3c3c; font-weight: bold; } QListWidget::item { padding: 1px; } QListWidget::item:selected { background-color: #3c3c3c; color: white; border-radius: 3px; } """

        self.power_button = QPushButton(self.pokedex_bg)

        self.main_screen = QStackedWidget(self.overlay_widget)
        self.main_screen.setStyleSheet("background-color: transparent; border: none; color: #3c3c3c; font-weight: bold;")

        self.info_screen_container = QFrame(self.overlay_widget)
        self.info_screen_container.setStyleSheet("QFrame { background-color: transparent; border: 2px solid #3c3c3c; border-radius: 5px; }")

        self.info_screen = QStackedWidget(self.info_screen_container)
        self.info_screen.setStyleSheet("QStackedWidget { background-color: transparent; border: none; padding: 5px; color: white; font-weight: bold; }")
        
        container_layout = QVBoxLayout(self.info_screen_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(self.info_screen)
        
        self.aux_screen_1 = QLabel("N/A", self.overlay_widget); self.aux_screen_1.setAlignment(Qt.AlignmentFlag.AlignCenter); self.aux_screen_1.setStyleSheet("background-color: transparent; padding: 5px; color: white; font-weight: bold;")
        self.aux_screen_2 = QLabel("N/A", self.overlay_widget); self.aux_screen_2.setAlignment(Qt.AlignmentFlag.AlignCenter); self.aux_screen_2.setStyleSheet("background-color: transparent; padding: 5px; color: white; font-weight: bold;")
        self.aux_screen_3 = QWidget(self.overlay_widget); self.aux_screen_3_layout = QHBoxLayout(self.aux_screen_3); self.aux_screen_3.setStyleSheet("background-color: transparent; padding: 5px; color: white; font-weight: bold;")
        
        self.dpad_up = QPushButton(self.overlay_widget)
        self.dpad_down = QPushButton(self.overlay_widget)
        self.dpad_left = QPushButton(self.overlay_widget)
        self.dpad_right = QPushButton(self.overlay_widget)
        self.enter_button = QPushButton(self.overlay_widget)
        self.back_button = QPushButton(self.overlay_widget)

        self.overlay_widgets_rects = {
            self.main_screen: QRect(160, 275, 290, 148), # x = posição canto superior esquerdo, y = extremidade de cima, width, height / (170, 275, 270, 148) original
            self.info_screen_container: QRect(664, 225, 352, 99),
            self.aux_screen_1: QRect(208, 616, 108, 50),
            self.aux_screen_2: QRect(665, 620, 155, 52),
            self.aux_screen_3: QRect(862, 620, 155, 52),
            self.power_button: QRect(115, 508, 56, 50),
            self.dpad_up: QRect(413, 577, 40, 35),
            self.dpad_down: QRect(413, 652, 40, 35),
            self.dpad_left: QRect(376, 615, 40, 35),
            self.dpad_right: QRect(452, 615, 40, 35),
            self.enter_button: QRect(275, 509, 55, 18), # (265, 502, 55, 18) original
            self.back_button: QRect(195, 509, 55, 18), # = (185, 502, 55, 18) original
        }

        release_style = "QPushButton { background-color: rgba(255, 255, 255, 0.05); border: 1px solid rgba(200, 200, 200, 0.3); border-radius: 8px; } QPushButton:hover { background-color: rgba(255, 255, 255, 0.15); border: 1px solid rgba(255, 255, 255, 0.7); } QPushButton:pressed { background-color: rgba(200, 200, 200, 0.2); }"
        self.power_button.setStyleSheet("background-color: transparent; border: 1px solid rgba(200, 200, 200, 0.3); border-radius: 25px;"); self.power_button.setCursor(Qt.CursorShape.PointingHandCursor)
        for btn in [self.dpad_up, self.dpad_down, self.dpad_left, self.dpad_right, self.enter_button, self.back_button]: btn.setStyleSheet(release_style); btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.page_menu = QWidget(); self.page_menu_layout = QVBoxLayout(self.page_menu)
        self.page_pokemon_list = QWidget(); self.page_pokemon_list_layout = QVBoxLayout(self.page_pokemon_list)
        self.page_pokemon_detail = QWidget(); detail_layout = QVBoxLayout(self.page_pokemon_detail); self.pokemon_detail_image.setAlignment(Qt.AlignmentFlag.AlignCenter); detail_layout.addWidget(self.pokemon_detail_image)
        self.page_quests_list = QWidget(); self.page_quests_list_layout = QVBoxLayout(self.page_quests_list)
        self.page_types_submenu = QWidget(); self.page_types_submenu_layout = QVBoxLayout(self.page_types_submenu)
        self.page_types_explorer_list = QWidget(); self.page_types_explorer_list_layout = QVBoxLayout(self.page_types_explorer_list)
        self.page_types_boss_list = QWidget(); self.page_types_boss_list_layout = QVBoxLayout(self.page_types_boss_list)
        self.page_types_defense_list = QWidget(); self.page_types_defense_list_layout = QVBoxLayout(self.page_types_defense_list)
        self.page_maps_list = QWidget(); self.page_maps_list_layout = QVBoxLayout(self.page_maps_list)
        self.page_comparative = QWidget(); self.page_comparative_layout = QVBoxLayout(self.page_comparative)
        self.page_topics_records = QWidget(); self.page_topics_records_layout = QVBoxLayout(self.page_topics_records)
        self.page_ev_hotspots = QWidget(); self.page_ev_hotspots_layout = QVBoxLayout(self.page_ev_hotspots)
        self.page_placeholder = QLabel(self.parent_window.get_string("globals.wip")); self.page_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_map_detail = QLabel(); self.page_map_detail.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for page in [self.page_menu, self.page_pokemon_list, self.page_pokemon_detail, self.page_quests_list, self.page_types_submenu, self.page_types_explorer_list, self.page_types_boss_list, self.page_types_defense_list, self.page_maps_list, self.page_map_detail, self.page_comparative, self.page_topics_records, self.page_ev_hotspots, self.page_placeholder]:
            page.setStyleSheet("border: none; background-color: transparent;")
            self.main_screen.addWidget(page)
        
        self.info_page_menu = QLabel(); self.info_page_menu.setWordWrap(True); self.info_page_menu.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.info_page_pokemon_preview = QScrollArea(); self.info_page_pokemon_preview.setWidgetResizable(True); self.info_page_pokemon_preview.setFrameShape(QFrame.Shape.NoFrame); self.info_page_pokemon_preview.setStyleSheet("background-color: transparent;")
        self.info_page_pokemon_detail = QScrollArea(); self.info_page_pokemon_detail.setWidgetResizable(True); self.info_page_pokemon_detail.setFrameShape(QFrame.Shape.NoFrame); self.info_page_pokemon_detail.setStyleSheet("background-color: transparent;")
        self.info_page_quests_detail = QScrollArea(); self.info_page_quests_detail.setWidgetResizable(True); self.info_page_quests_detail.setFrameShape(QFrame.Shape.NoFrame); self.info_page_quests_detail.setStyleSheet("background-color: transparent;")
        self.info_page_types_detail_explorer = QScrollArea(); self.info_page_types_detail_explorer.setWidgetResizable(True); self.info_page_types_detail_explorer.setFrameShape(QFrame.Shape.NoFrame); self.info_page_types_detail_explorer.setStyleSheet("background-color: transparent;")
        self.info_page_types_detail_boss = QScrollArea(); self.info_page_types_detail_boss.setWidgetResizable(True); self.info_page_types_detail_boss.setFrameShape(QFrame.Shape.NoFrame); self.info_page_types_detail_boss.setStyleSheet("background-color: transparent;")
        self.info_page_types_detail_defense = QScrollArea(); self.info_page_types_detail_defense.setWidgetResizable(True); self.info_page_types_detail_defense.setFrameShape(QFrame.Shape.NoFrame); self.info_page_types_detail_defense.setStyleSheet("background-color: transparent;")
        self.info_page_maps_detail = QScrollArea(); self.info_page_maps_detail.setWidgetResizable(True); self.info_page_maps_detail.setFrameShape(QFrame.Shape.NoFrame); self.info_page_maps_detail.setStyleSheet("background-color: transparent;")
        self.info_page_comparative_detail = QWidget(); self.info_page_comparative_detail_layout = QVBoxLayout(self.info_page_comparative_detail)
        self.info_page_topics_records_detail = QScrollArea(); self.info_page_topics_records_detail.setWidgetResizable(True); self.info_page_topics_records_detail.setFrameShape(QFrame.Shape.NoFrame); self.info_page_topics_records_detail.setStyleSheet("background-color: transparent;")
        self.info_page_ev_hotspots_detail = QScrollArea(); self.info_page_ev_hotspots_detail.setWidgetResizable(True); self.info_page_ev_hotspots_detail.setFrameShape(QFrame.Shape.NoFrame); self.info_page_ev_hotspots_detail.setStyleSheet("background-color: transparent;")

        for page in [self.info_page_menu, self.info_page_pokemon_preview, self.info_page_pokemon_detail, self.info_page_quests_detail, self.info_page_types_detail_explorer, self.info_page_types_detail_boss, self.info_page_types_detail_defense, self.info_page_maps_detail, self.info_page_comparative_detail, self.info_page_topics_records_detail, self.info_page_ev_hotspots_detail]:
            self.info_screen.addWidget(page)
        
        self.power_button.clicked.connect(self._toggle_power); self.dpad_up.clicked.connect(lambda: self._navigate_content("up")); self.dpad_down.clicked.connect(lambda: self._navigate_content("down")); self.dpad_left.clicked.connect(lambda: self._navigate_content("left")); self.dpad_right.clicked.connect(lambda: self._navigate_content("right")); self.enter_button.clicked.connect(self._select_item); self.back_button.clicked.connect(self._go_back)
        
        self._set_ui_visibility(False)

    def _load_animation_frames(self):
        self.pokedex_frames = []
        i = 1
        while True:
            frame_path = resource_path(f"Images/Pokedex/{i:04d}.png")
            if os.path.exists(frame_path): 
                pixmap = QPixmap(frame_path)
                if not pixmap.isNull():
                    self.pokedex_frames.append(pixmap)
                i += 1
            else: break
        if self.pokedex_frames: 
            first_frame = self.pokedex_frames[0]
            self.pokedex_bg.setPixmap(first_frame.scaled(
                self.POKEDEX_BASE_WIDTH, self.POKEDEX_BASE_HEIGHT,
                Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            ))
        else: print("AVISO: Sequência de animação da Pokédex não encontrada em 'Images/Pokedex/'.")

    def _set_ui_visibility(self, is_visible):
        if self.overlay_widget:
            self.overlay_widget.setVisible(is_visible)

    def _play_sound(self, sound_name, volume=1.0):
        sound_path = resource_path(f"Images/Pokedex/sounds/{sound_name}")
        if os.path.exists(sound_path): self.player.setSource(QUrl.fromLocalFile(sound_path)); self.audio_output.setVolume(volume); self.player.play()
        else: print(f"AVISO de som: Arquivo '{sound_name}' não encontrado.")

    def _toggle_power(self):
        if self.power_state in ["LIGANDO", "DESLIGANDO"] or not self.pokedex_frames: return
        if self.power_state == "LIGADA": self.power_state = "DESLIGANDO"; self.animation_direction = -1; self._set_ui_visibility(False); self._play_sound("desligar.ogg"); self.animation_timer.start(30)
        elif self.power_state == "DESLIGADA": self.power_state = "LIGANDO"; self.animation_direction = 1; self.current_frame = 1; self._play_sound("ligar.mp3"); self.animation_timer.start(40)

    def _update_pokedex_animation(self):
        if 0 <= self.current_frame < len(self.pokedex_frames):
            scaled_frame = self.pokedex_frames[self.current_frame].scaled(
                self.POKEDEX_BASE_WIDTH, self.POKEDEX_BASE_HEIGHT,
                Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            self.pokedex_bg.setPixmap(scaled_frame)
        
        self.current_frame += self.animation_direction

        if self.animation_direction == 1 and self.current_frame >= len(self.pokedex_frames):
            self.animation_timer.stop()
            self.power_state = "LIGADA"
            self.current_frame = len(self.pokedex_frames) - 1
            scaled_frame = self.pokedex_frames[self.current_frame].scaled(
                self.POKEDEX_BASE_WIDTH, self.POKEDEX_BASE_HEIGHT,
                Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            self.pokedex_bg.setPixmap(scaled_frame)
            self._set_ui_visibility(True)
            self._populate_menu_page(reset_index=True)
            self._update_overlay_positions()
        elif self.animation_direction == -1 and self.current_frame < 0:
            self.animation_timer.stop()
            self.power_state = "DESLIGADA"
            self.current_frame = 0
            scaled_frame = self.pokedex_frames[self.current_frame].scaled(
                self.POKEDEX_BASE_WIDTH, self.POKEDEX_BASE_HEIGHT,
                Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            self.pokedex_bg.setPixmap(scaled_frame)
            
    def _clear_layout(self, layout):
        if layout is None: return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None: widget.deleteLater()
            else:
                nested_layout = item.layout()
                if nested_layout is not None: self._clear_layout(nested_layout)

    def _go_back(self):
        if self.power_state != "LIGADA": return
        if self.main_screen.currentWidget() == self.page_comparative and self.comparative_is_showing_results:
            self._play_sound("B.wav"); self._populate_comparative_page(); return
        self._play_sound("B.wav")
        current_page = self.main_screen.currentWidget()
        if current_page in [self.page_types_explorer_list, self.page_types_boss_list, self.page_types_defense_list]: self._populate_types_submenu()
        elif current_page == self.page_types_submenu: self._populate_menu_page()
        elif current_page == self.page_map_detail: self.main_screen.setCurrentWidget(self.page_maps_list)
        elif current_page == self.page_pokemon_detail: self._populate_pokemon_list_page()
        elif current_page is not self.page_menu: self._populate_menu_page()

    def _navigate_content(self, direction):
        if self.power_state != "LIGADA": return
        self._play_sound("click.ogg", volume=0.2)
        current_page = self.main_screen.currentWidget()
        
        if current_page == self.page_menu:
            if direction == "up": self.current_menu_index = (self.current_menu_index - 1) % len(self.menu_buttons)
            elif direction == "down": self.current_menu_index = (self.current_menu_index + 1) % len(self.menu_buttons)
            self._update_menu_selection()
        elif current_page == self.page_types_submenu:
            if direction == "up": self.current_types_mode_index = (self.current_types_mode_index - 1) % len(self.types_submenu_buttons)
            elif direction == "down": self.current_types_mode_index = (self.current_types_mode_index + 1) % len(self.types_submenu_buttons)
            self._update_types_submenu_selection()
        elif current_page == self.page_pokemon_detail:
            if direction in ["left", "right"]:
                if direction == "left": self.current_pokemon_index = (self.current_pokemon_index - 1) % len(self.pokedex_list)
                else: self.current_pokemon_index = (self.current_pokemon_index + 1) % len(self.pokedex_list)
                self._show_pokemon_detail(self.pokedex_list[self.current_pokemon_index], direction)
            else: 
                scroll_bar = self.info_page_pokemon_detail.verticalScrollBar()
                step = scroll_bar.pageStep() / 4
                if direction == "up": scroll_bar.setValue(scroll_bar.value() - int(step))
                elif direction == "down": scroll_bar.setValue(scroll_bar.value() + int(step))
        else:
            active_list_widget = None
            if current_page == self.page_pokemon_list: active_list_widget = self.pokemon_list_widget
            elif current_page == self.page_quests_list: active_list_widget = self.quests_list_widget
            elif current_page == self.page_types_explorer_list: active_list_widget = self.types_explorer_list_widget
            elif current_page == self.page_types_boss_list: active_list_widget = self.types_boss_list_widget
            elif current_page == self.page_types_defense_list: active_list_widget = self.types_defense_list_widget
            elif current_page == self.page_maps_list: active_list_widget = self.maps_list_widget
            elif current_page == self.page_topics_records: active_list_widget = self.topics_list_widget
            elif current_page == self.page_ev_hotspots: active_list_widget = self.ev_stats_list_widget
            elif current_page == self.page_comparative: active_list_widget = self.pokemon_selection_list
            if active_list_widget and active_list_widget.count() > 0:
                current_row = active_list_widget.currentRow() if active_list_widget.currentRow() != -1 else 0
                if direction == "up": next_row = (current_row - 1) % active_list_widget.count()
                elif direction == "down": next_row = (current_row + 1) % active_list_widget.count()
                else: return
                active_list_widget.setCurrentRow(next_row)

    def _select_item(self):
        if self.power_state != "LIGADA": return
        current_page = self.main_screen.currentWidget()
        if current_page == self.page_comparative:
            if self.comparative_is_showing_results: return
            if item := self.pokemon_selection_list.currentItem(): self._comparative_select_pokemon(item)
            return

        self._play_sound("click.ogg", volume=0.2)
        if current_page == self.page_menu:
            selected_key = self.menu_keys[self.current_menu_index]
            if selected_key == "pokedex.menu_pokemon": self._populate_pokemon_list_page()
            elif selected_key == "pokedex.menu_quests": self._populate_quests_list_page()
            elif selected_key == "pokedex.menu_types": self._populate_types_submenu(reset_index=True)
            elif selected_key == "pokedex.menu_maps": self._populate_maps_list_page()
            elif selected_key == "pokedex.menu_comparative": self._populate_comparative_page()
            elif selected_key == "pokedex.menu_topics": self._populate_topics_records_page()
            elif selected_key == "pokedex.menu_ev_hotspots": self._populate_ev_hotspots_page()
        elif current_page == self.page_types_submenu:
            selected_key = self.types_submenu_keys[self.current_types_mode_index]
            if selected_key == "pokedex.types_explorer": self._populate_types_explorer_list()
            elif selected_key == "pokedex.types_boss_analysis": self._populate_types_boss_list()
            elif selected_key == "pokedex.types_defensive_analysis": self._populate_types_defense_list()
        elif current_page == self.page_pokemon_list:
            if item := self.pokemon_list_widget.currentItem():
                pokemon_name = item.text().split(" - ")[1]; self.current_pokemon_index = self.pokedex_list.index(pokemon_name); self._show_pokemon_detail(pokemon_name)
        elif current_page == self.page_maps_list:
            if item := self.maps_list_widget.currentItem(): self._show_map_detail_on_main_screen(item.text())
        elif current_page == self.page_quests_list:
            if self.quests_list_widget and self.quests_list_widget.currentItem():
                self._show_quest_detail(self.quests_list_widget.currentItem().data(Qt.ItemDataRole.UserRole))

    def _populate_menu_page(self, reset_index=False):
        self._clear_layout(self.page_menu_layout); self.menu_buttons.clear()
        for index, key in enumerate(self.menu_keys):
            btn = QPushButton(self.parent_window.get_string(key)); btn.setFlat(True); btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("padding: 1px; font-size: 12px; border-radius: 5px; text-align: center; color: #3c3c3c; font-weight: bold;")
            btn.clicked.connect(lambda _, idx=index: self._menu_item_clicked(idx)); self.menu_buttons.append(btn); self.page_menu_layout.addWidget(btn)
        self.main_screen.setCurrentWidget(self.page_menu); self.info_screen.setCurrentWidget(self.info_page_menu)
        if reset_index: self.current_menu_index = 0
        self._update_menu_selection()

    def _menu_item_clicked(self, index):
        self.current_menu_index = index; self._update_menu_selection(); self._select_item()

    def _update_menu_selection(self):
        descriptions = { self.parent_window.get_string(k): self.parent_window.get_string(f"pokedex.desc_{k.split('.')[-1]}") for k in self.menu_keys }
        for index, btn in enumerate(self.menu_buttons):
            if index == self.current_menu_index:
                btn.setStyleSheet("padding: 1px; font-size: 12px; border-radius: 5px; background-color: #3c3c3c; color: white; text-align: center; font-weight: bold;")
                self.info_page_menu.setText(f"<b>{btn.text()}</b><br>{descriptions.get(btn.text(), '')}")
            else: btn.setStyleSheet("padding: 1px; font-size: 12px; border-radius: 5px; background-color: transparent; color: #3c3c3c; text-align: center; font-weight: bold;")
        self.aux_screen_1.setText(self.parent_window.get_string("pokedex.menu")); self.aux_screen_2.setText(self.menu_buttons[self.current_menu_index].text()); self._clear_layout(self.aux_screen_3_layout)

    def _populate_pokemon_list_page(self):
        self._clear_layout(self.page_pokemon_list_layout); self.pokemon_list_widget = QListWidget()
        for i, name in enumerate(self.pokedex_list): self.pokemon_list_widget.addItem(f"{i+1:04d} - {name}")
        self.pokemon_list_widget.setStyleSheet(self.base_list_style); self.pokemon_list_widget.currentItemChanged.connect(self._update_pokemon_preview)
        self.page_pokemon_list_layout.addWidget(self.pokemon_list_widget); self.main_screen.setCurrentWidget(self.page_pokemon_list); self.pokemon_list_widget.setCurrentRow(self.current_pokemon_index)

    def _update_pokemon_preview(self, current_item, previous_item):
        if not current_item: return
        pokemon_name = current_item.text().split(" - ")[1]; p_data = self.parent_window.get_pokedex_data(pokemon_name)
        if not p_data: return
        
        content_widget = QWidget(); content_layout = QFormLayout(content_widget)
        if base_stats := p_data.get("base_stats"):
            for stat_key, stat_value in base_stats.items(): content_layout.addRow(f"<b>{self.parent_window.get_string(f'stats.{stat_key.lower()}', stat_key.capitalize())}:</b>", QLabel(str(stat_value)))
        self.info_page_pokemon_preview.setWidget(content_widget); self.info_screen.setCurrentWidget(self.info_page_pokemon_preview)

        self.current_pokemon_index = self.pokedex_list.index(pokemon_name)
        self.aux_screen_1.setText(f"No. {self.current_pokemon_index + 1:04d}"); self.aux_screen_2.setText(pokemon_name); self._clear_layout(self.aux_screen_3_layout)
        if type1_widget := self._create_type_widget(p_data.get("type1"), size="small", show_name=False): self.aux_screen_3_layout.addWidget(type1_widget)
        if type2_widget := self._create_type_widget(p_data.get("type2"), size="small", show_name=False): self.aux_screen_3_layout.addWidget(type2_widget)

    def _show_pokemon_detail(self, pokemon_name, direction=None):
        p_data = self.parent_window.get_pokedex_data(pokemon_name);
        if not p_data: return
        if direction:
            start_x = self.main_screen.width() if direction == 'right' else -self.main_screen.width()
            self.page_pokemon_detail.setGeometry(start_x, 0, self.main_screen.width(), self.main_screen.height())
        pixmap = load_pixmap_robustly(p_data.get("image_path"), self.main_screen.height() - 10, self.main_screen.height() - 10)
        self.pokemon_detail_image.setPixmap(pixmap)

        content_widget = QWidget(); layout = QVBoxLayout(content_widget); form_layout = QFormLayout()
        if base_stats := p_data.get("base_stats"):
            stats_frame = QFrame(); stats_frame_layout = QFormLayout(stats_frame); stats_frame_layout.addRow(QLabel(f"<b>{self.parent_window.get_string('ocr.base_stats_header')}</b>"))
            for stat_key, stat_value in base_stats.items():
                row_widget = QWidget(); row_layout = QHBoxLayout(row_widget); row_layout.setContentsMargins(0,0,0,0)
                row_layout.addWidget(QLabel(f"<b>{stat_value}</b>"))
                if bar_pixmap := get_dynamic_stat_bar(self.parent_window, stat_key, stat_value, context='base'):
                    bar_label = QLabel(); bar_label.setPixmap(bar_pixmap); row_layout.addWidget(bar_label)
                row_layout.addStretch(); stats_frame_layout.addRow(f"<b>{self.parent_window.get_string(f'stats.{stat_key.lower()}', stat_key.title())}:</b>", row_widget)
            layout.addWidget(stats_frame)
        
        def add_wrapped_row(target_layout, label_key, value_list): target_layout.addRow(f"<b>{self.parent_window.get_string(label_key)}:</b>", QLabel(", ".join(value_list))); 
        matchups = self.parent_window._get_type_matchups(pokemon_name=pokemon_name); add_wrapped_row(form_layout, 'pokedex.advantages_atk', matchups.get('advantages', [])); add_wrapped_row(form_layout, 'pokedex.weaknesses_def', matchups.get('weaknesses', [])); add_wrapped_row(form_layout, 'pokedex.resistances_def', matchups.get('resistances', [])); add_wrapped_row(form_layout, 'pokedex.immunities_def', matchups.get('immunities', []))
        if ev_yield_str := self.parent_window._get_ev_yield_string(pokemon_name):
            add_wrapped_row(form_layout, 'pokedex.ev_yield', [ev_yield_str])
        if loot := self.parent_window.loots_data.get(pokemon_name): add_wrapped_row(form_layout, 'pokedex.drop', [f"{loot.get('item')} (${loot.get('price')})"])
        layout.addLayout(form_layout)

        if quests := self.parent_window.quests_data.get(pokemon_name):
            if isinstance(quests, list):
                quests_html = "".join([f"<li><b>{q['npc']}</b> @ {q['location']}<br><small>💰${q['money']} | ⭐{q['happiness']} | 🎓{q['trainer_xp']} XP</small></li>" for q in quests])
                label = QLabel(f"<b>{self.parent_window.get_string('pokedex.quests_title')}</b><ul>{quests_html}</ul>"); label.setWordWrap(True); layout.addWidget(label)
        
        self.info_page_pokemon_detail.setWidget(content_widget)
        self.aux_screen_1.setText(f"No. {self.current_pokemon_index + 1:04d}"); self.aux_screen_2.setText(pokemon_name); self._clear_layout(self.aux_screen_3_layout)
        if type1_widget := self._create_type_widget(p_data.get("type1"), size="small", show_name=False): self.aux_screen_3_layout.addWidget(type1_widget)
        if type2_widget := self._create_type_widget(p_data.get("type2"), size="small", show_name=False): self.aux_screen_3_layout.addWidget(type2_widget)
        self.main_screen.setCurrentWidget(self.page_pokemon_detail); self.info_screen.setCurrentWidget(self.info_page_pokemon_detail)
        if direction:
            anim = QPropertyAnimation(self.page_pokemon_detail, b"geometry"); anim.setDuration(250); anim.setStartValue(self.page_pokemon_detail.geometry()); anim.setEndValue(QRect(0, 0, self.main_screen.width(), self.main_screen.height())); anim.setEasingCurve(QEasingCurve.Type.OutCubic); anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def _populate_quests_list_page(self):
        self._clear_layout(self.page_quests_list_layout); self.quests_list_widget = QListWidget(); self.quests_list_widget.setStyleSheet(self.base_list_style)
        self.quests_list_widget.currentItemChanged.connect(self._update_quest_preview)
        all_quests_flat = []
        for pokemon_name, quests in self.parent_window.quests_data.items():
            for i, quest in enumerate(quests):
                item = QListWidgetItem(f"{pokemon_name} - {quest.get('npc')} ({quest.get('location')})"); item.setData(Qt.ItemDataRole.UserRole, (pokemon_name, i)); all_quests_flat.append(item)
        for item in sorted(all_quests_flat, key=lambda x: x.text()): self.quests_list_widget.addItem(item)
        self.page_quests_list_layout.addWidget(self.quests_list_widget); self.main_screen.setCurrentWidget(self.page_quests_list)
        if self.quests_list_widget.count() > 0: self.quests_list_widget.setCurrentRow(0)
        else: self._update_quest_preview(None, None)

    def _update_quest_preview(self, current_item, previous_item):
        if not current_item: self.info_screen.setCurrentWidget(self.info_page_menu); return
        if quest_id := current_item.data(Qt.ItemDataRole.UserRole): self._show_quest_detail(quest_id)

    def _show_quest_detail(self, quest_id):
        pokemon_name, quest_index = quest_id; quest = self.parent_window.quests_data.get(pokemon_name, [])[quest_index]
        content_widget = QWidget(); content_layout = QFormLayout(content_widget)
        content_layout.addRow(f"<b>{self.parent_window.get_string('globals.pokemon')}:</b>", QLabel(pokemon_name)); content_layout.addRow(f"<b>{self.parent_window.get_string('globals.npc')}:</b>", QLabel(quest.get('npc', 'N/A'))); content_layout.addRow(f"<b>{self.parent_window.get_string('globals.location')}:</b>", QLabel(quest.get('location', 'N/A')))
        content_layout.addRow(f"<b>{self.parent_window.get_string('globals.reward')}:</b>", QLabel(f"💰${quest.get('money')} | ⭐{quest.get('happiness')} | 🎓{quest.get('trainer_xp')} XP"))
        self.info_page_quests_detail.setWidget(content_widget); self.info_screen.setCurrentWidget(self.info_page_quests_detail)
        self.aux_screen_1.setText(self.parent_window.get_string('tabs.pokedex')); self.aux_screen_2.setText(pokemon_name); self._clear_layout(self.aux_screen_3_layout)
        self.aux_screen_3_layout.addWidget(QLabel(f"XP: {quest.get('trainer_xp')}")); self.aux_screen_3_layout.addWidget(QLabel(f"$: {quest.get('money')}"))

    def _populate_types_submenu(self, reset_index=False):
        self._clear_layout(self.page_types_submenu_layout); self.types_submenu_buttons.clear()
        title = QLabel(f"<b>{self.parent_window.get_string('pokedex.types_analysis_title')}</b>"); title.setAlignment(Qt.AlignmentFlag.AlignCenter); self.page_types_submenu_layout.addWidget(title)
        for index, key in enumerate(self.types_submenu_keys):
            btn = QPushButton(self.parent_window.get_string(key)); btn.setFlat(True); btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("padding: 1px; font-size: 12px; border-radius: 5px; text-align: center; color: #3c3c3c; font-weight: bold;")
            btn.clicked.connect(lambda _, idx=index: self._types_submenu_item_clicked(idx)); self.types_submenu_buttons.append(btn); self.page_types_submenu_layout.addWidget(btn)
        self.main_screen.setCurrentWidget(self.page_types_submenu); self.info_screen.setCurrentWidget(self.info_page_menu)
        if reset_index: self.current_types_mode_index = 0
        self._update_types_submenu_selection()

    def _types_submenu_item_clicked(self, index):
        self.current_types_mode_index = index; self._update_types_submenu_selection(); self._select_item()

    def _update_types_submenu_selection(self):
        descriptions = {self.parent_window.get_string(k): self.parent_window.get_string(f"pokedex.desc_{k.split('.')[-1]}") for k in self.types_submenu_keys}
        for index, btn in enumerate(self.types_submenu_buttons):
            if index == self.current_types_mode_index:
                btn.setStyleSheet("padding: 1px; font-size: 12px; border-radius: 5px; background-color: #3c3c3c; color: white; text-align: center; font-weight: bold;")
                self.info_page_menu.setText(f"<b>{btn.text()}</b><br>{descriptions.get(btn.text(), '')}")
            else: btn.setStyleSheet("padding: 1px; font-size: 12px; border-radius: 5px; background-color: transparent; color: #3c3c3c; text-align: center; font-weight: bold;")
        self.aux_screen_1.setText(self.parent_window.get_string("pokedex.menu_types")); self.aux_screen_2.setText(self.parent_window.get_string("pokedex.mode"))

    def _populate_types_explorer_list(self):
        self._clear_layout(self.page_types_explorer_list_layout); self.types_explorer_list_widget = QListWidget()
        for type_key in sorted(self.parent_window.type_chart.keys()):
            item_widget = QWidget(); item_layout = QHBoxLayout(item_widget); item_layout.setContentsMargins(5, 0, 5, 0)
            if icon := get_icon_from_path(emojis.TYPE_ICONS.get(type_key)): icon_label = QLabel(); icon_label.setPixmap(icon.pixmap(24, 24)); item_layout.addWidget(icon_label)
            item_layout.addWidget(QLabel(self.parent_window.get_string(f"types.{type_key}", type_key))); item_layout.addStretch()
            item = QListWidgetItem(self.types_explorer_list_widget); item.setData(Qt.ItemDataRole.UserRole, type_key); item.setSizeHint(item_widget.sizeHint()); self.types_explorer_list_widget.setItemWidget(item, item_widget)
        self.types_explorer_list_widget.setStyleSheet("QListWidget { border: none; background-color: transparent; } QListWidget::item:selected { background-color: #3c3c3c; }")
        self.types_explorer_list_widget.currentItemChanged.connect(self._update_types_explorer_detail)
        self.page_types_explorer_list_layout.addWidget(self.types_explorer_list_widget); self.main_screen.setCurrentWidget(self.page_types_explorer_list)
        if self.types_explorer_list_widget.count() > 0: self.types_explorer_list_widget.setCurrentRow(0)

    def _update_types_explorer_detail(self, current_item, previous_item):
        if not current_item: return
        original_type_key = current_item.data(Qt.ItemDataRole.UserRole); content = QWidget(); layout = QVBoxLayout(content)
        matchups = self.parent_window._get_type_matchups(p_types=[original_type_key])
        for key in ['advantages_atk', 'weaknesses_def', 'resistances_def', 'immunities_def']:
            label = QLabel(f"<b>{self.parent_window.get_string(f'pokedex.{key}')}:</b><br>{', '.join(matchups.get(key.split('_')[0], ['N/A']))}"); label.setWordWrap(True); layout.addWidget(label)
        layout.addSpacing(10)
        pokemon_of_type = sorted([name for name, data in self.parent_window.pokemon_data.items() if data.get("type1") == original_type_key or data.get("type2") == original_type_key])
        if pokemon_of_type:
            layout.addWidget(QLabel(f"<b>{self.parent_window.get_string('globals.pokemon')} do tipo {self.parent_window.get_string(f'types.{original_type_key}')}:</b>"))
            poke_list_label = QLabel(", ".join(pokemon_of_type)); poke_list_label.setWordWrap(True); layout.addWidget(poke_list_label)
        self.info_page_types_detail_explorer.setWidget(content); self.info_screen.setCurrentWidget(self.info_page_types_detail_explorer)
        self.aux_screen_2.setText(self.parent_window.get_string(f"types.{original_type_key}", original_type_key))

    def _populate_types_boss_list(self):
        self._clear_layout(self.page_types_boss_list_layout); self.types_boss_list_widget = QListWidget()
        for name in sorted(self.parent_window.boss_data.keys()): self.types_boss_list_widget.addItem(name)
        self.types_boss_list_widget.setStyleSheet(self.base_list_style); self.types_boss_list_widget.currentItemChanged.connect(self._update_types_boss_detail)
        self.page_types_boss_list_layout.addWidget(self.types_boss_list_widget); self.main_screen.setCurrentWidget(self.page_types_boss_list)
        if self.types_boss_list_widget.count() > 0: self.types_boss_list_widget.setCurrentRow(0)

    def _update_types_boss_detail(self, current_item, previous_item):
        if not current_item: return
        boss_name = current_item.text(); boss_info = self.parent_window.boss_data.get(boss_name)
        if not boss_info: return
        boss_types = list(filter(None, [boss_info.get("type1"), boss_info.get("type2")]))
        effectiveness = {}
        for attacking_type in self.parent_window.type_chart.keys():
            multiplier = 1.0
            for boss_def_type in boss_types: multiplier *= self.parent_window.type_chart[attacking_type].get(boss_def_type, 1.0)
            if multiplier != 1.0: effectiveness[attacking_type] = multiplier
        sorted_effectiveness = sorted(effectiveness.items(), key=lambda item: item[1], reverse=True)
        content = QWidget(); results_layout = QFormLayout(content)
        for type_key, mult in sorted_effectiveness: results_layout.addRow(f"{self.parent_window.get_string(f'types.{type_key}', type_key)}:", QLabel(f"<b>x{mult}</b>"))
        self.info_page_types_detail_boss.setWidget(content); self.info_screen.setCurrentWidget(self.info_page_types_detail_boss); self.aux_screen_2.setText(boss_name)

    def _populate_types_defense_list(self):
        self._populate_types_explorer_list(); self.main_screen.setCurrentWidget(self.page_types_explorer_list); self.types_explorer_list_widget.currentItemChanged.disconnect(); self.types_explorer_list_widget.currentItemChanged.connect(self._update_types_defense_detail)
        if self.types_explorer_list_widget.count() > 0: self._update_types_defense_detail(self.types_explorer_list_widget.item(0), None)

    def _update_types_defense_detail(self, current_item, previous_item):
        if not current_item: return
        attacking_type = current_item.data(Qt.ItemDataRole.UserRole); content = QWidget(); layout = QVBoxLayout(content)
        collection = load_json("my_pokemon.json", [], is_user_data=True)
        if not collection: layout.addWidget(QLabel(self.parent_window.get_string('pokedex.empty_collection'))); return
        weak, resistant, immune = [], [], []
        for p_user in collection:
            p_data = self.parent_window.pokemon_data.get(p_user['species']);
            if not p_data: continue
            p_types = list(filter(None, [p_data.get("type1"), p_data.get("type2")])); multiplier = 1.0
            for p_type in p_types: multiplier *= self.parent_window.type_chart[attacking_type].get(p_type, 1.0)
            p_name = p_user.get('nickname') or p_user['species']
            if multiplier > 1: weak.append(f"{p_name} (x{multiplier})")
            elif 0 < multiplier < 1: resistant.append(f"{p_name} (x{multiplier})")
            elif multiplier == 0: immune.append(p_name)
        
        for key, data_list in [('weak', weak), ('resistant', resistant), ('immune', immune)]:
            label = QLabel(f"<font color='{'red' if key=='weak' else 'green' if key=='resistant' else 'gray'}'><b>{self.parent_window.get_string(f'pokedex.{key}')} ({len(data_list)}):</b></font> {', '.join(data_list)}"); label.setWordWrap(True); layout.addWidget(label)
        
        self.info_page_types_detail_defense.setWidget(content); self.info_screen.setCurrentWidget(self.info_page_types_detail_defense)
        self.aux_screen_2.setText(f"{self.parent_window.get_string('pokedex.versus')} {self.parent_window.get_string(f'types.{attacking_type}')}")

    def _populate_maps_list_page(self):
        self._clear_layout(self.page_maps_list_layout); self.maps_list_widget = QListWidget()
        all_map_names = set()
        for pokemon_spawn_list in self.parent_window.spawn_rates.values():
            for spawn_info in pokemon_spawn_list: all_map_names.add(spawn_info['map'])
        for map_name in sorted(list(all_map_names)): self.maps_list_widget.addItem(map_name)
        self.maps_list_widget.setStyleSheet(self.base_list_style); self.maps_list_widget.currentItemChanged.connect(self._update_map_selection)
        self.page_maps_list_layout.addWidget(self.maps_list_widget); self.main_screen.setCurrentWidget(self.page_maps_list)
        if self.maps_list_widget.count() > 0: self.maps_list_widget.setCurrentRow(0)

    def _update_map_selection(self, current_item=None, previous_item=None):
        if not self.maps_list_widget or self.maps_list_widget.currentRow() == -1: return
        map_name = self.maps_list_widget.currentItem().text(); pokemon_in_map = []
        for poke_name, spawn_list in self.parent_window.spawn_rates.items():
            if any(spawn_info['map'] == map_name for spawn_info in spawn_list): pokemon_in_map.append(poke_name)
        content_label = QLabel(f"<b>{self.parent_window.get_string('pokedex.pokemon_found')}</b><br>{', '.join(sorted(pokemon_in_map))}" if pokemon_in_map else self.parent_window.get_string('pokedex.no_specific_pokemon'))
        content_label.setWordWrap(True); self.info_page_maps_detail.setWidget(content_label)
        self.info_screen.setCurrentWidget(self.info_page_maps_detail); self.aux_screen_1.setText(self.parent_window.get_string("pokedex.menu_maps")); self.aux_screen_2.setText(map_name); self._clear_layout(self.aux_screen_3_layout)
        map_icon_label = QLabel(emojis.MAPA); map_icon_label.setStyleSheet("font-size: 20px;"); self.aux_screen_3_layout.addWidget(map_icon_label, alignment=Qt.AlignmentFlag.AlignCenter)

    def _show_map_detail_on_main_screen(self, map_name):
        self.page_map_detail.setPixmap(QPixmap())
        if map_path := get_map_image_path(map_name):
            if pixmap := load_pixmap_robustly(map_path, self.main_screen.width() - 10, self.main_screen.height() - 10): self.page_map_detail.setPixmap(pixmap)
            else: self.page_map_detail.setText(self.parent_window.get_string('pokedex.error_loading_map').format(map_name=map_name))
        else: self.page_map_detail.setText(self.parent_window.get_string('pokedex.map_not_found').format(map_name=map_name))
        self.main_screen.setCurrentWidget(self.page_map_detail)

    def _populate_comparative_page(self):
        self._clear_layout(self.page_comparative_layout); self._clear_layout(self.info_page_comparative_detail_layout)
        self.selected_comparison_pokemon_data = []; self.active_pokemon_for_removal = None; self.comparative_is_showing_results = False
        self.page_comparative_layout.addWidget(QLabel(f"<b>{self.parent_window.get_string('pokedex.comparative_title')}</b>")); self.pokemon_selection_list = QListWidget(); self.pokemon_selection_list.setStyleSheet(self.base_list_style)
        collection = load_json("my_pokemon.json", [], is_user_data=True)
        for p in collection: item = QListWidgetItem(f"{(p.get('nickname') or p['species'])} (Lv.{p['level']})"); item.setData(Qt.ItemDataRole.UserRole, p); self.pokemon_selection_list.addItem(item)
        self.pokemon_selection_list.itemActivated.connect(self._comparative_select_pokemon)
        self.page_comparative_layout.addWidget(self.pokemon_selection_list); self.main_screen.setCurrentWidget(self.page_comparative)
        explanation_label = QLabel(self.parent_window.get_string('pokedex.comparative_explanation')); explanation_label.setWordWrap(True); explanation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_page_comparative_detail_layout.addWidget(explanation_label); self.info_screen.setCurrentWidget(self.info_page_comparative_detail); self._update_aux_screen_comparison()

    def _comparative_select_pokemon(self, item):
        if not item: return
        pokemon_data = item.data(Qt.ItemDataRole.UserRole)
        if pokemon_data in self.selected_comparison_pokemon_data: return
        self.selected_comparison_pokemon_data.append(pokemon_data); item.setHidden(True); custom_message = None
        if len(self.selected_comparison_pokemon_data) == 1:
            family = self.parent_window.get_evolution_family(pokemon_data['species'])
            for i in range(self.pokemon_selection_list.count()):
                list_item = self.pokemon_selection_list.item(i); item_data = list_item.data(Qt.ItemDataRole.UserRole)
                if item_data['species'] not in family: list_item.setHidden(True)
            if not any(not self.pokemon_selection_list.item(i).isHidden() for i in range(self.pokemon_selection_list.count())): custom_message = self.parent_window.get_string("pokedex.comparative_no_other_family_members")
        self._play_sound("click.ogg", volume=0.2); self._comparative_update_info_screen(custom_message=custom_message)

    def _comparative_update_info_screen(self, custom_message=None):
        self._clear_layout(self.info_page_comparative_detail_layout)
        self.active_pokemon_for_removal = None
        if not self.selected_comparison_pokemon_data:
            expl_label = QLabel(self.parent_window.get_string('pokedex.comparative_explanation'))
            expl_label.setWordWrap(True)
            self.info_page_comparative_detail_layout.addWidget(expl_label)
            return
            
        # CORREÇÃO VISUAL: Adiciona uma área de rolagem para as imagens
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(120) # Define uma altura fixa para a área de rolagem
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        images_container = QWidget()
        images_layout = QHBoxLayout(images_container)
        for p_data in self.selected_comparison_pokemon_data:
            member_button = QToolButton()
            member_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            member_button.setCursor(Qt.CursorShape.PointingHandCursor)
            member_button.setCheckable(True)
            member_button.setFixedSize(100, 100) # Tamanho total do botão
            
            # CORREÇÃO VISUAL: Tamanho do ícone ajustado para caber no botão
            icon_size = 80 
            if img_path := get_pokemon_image_path(p_data['species']):
                member_button.setIcon(QIcon(load_pixmap_robustly(img_path, icon_size, icon_size)))
                member_button.setIconSize(QSize(icon_size, icon_size))
            member_button.setText(p_data.get('nickname') or p_data['species'])
            member_button.clicked.connect(lambda _, p=p_data, btn=member_button: self._comparative_image_clicked(p, btn))
            images_layout.addWidget(member_button)

        scroll_area.setWidget(images_container)
        self.info_page_comparative_detail_layout.addWidget(scroll_area)

        if custom_message:
            msg_label = QLabel(custom_message)
            msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.info_page_comparative_detail_layout.addWidget(msg_label)

        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if len(self.selected_comparison_pokemon_data) >= 1:
            remove_btn = QPushButton(self.parent_window.get_string('globals.remove'))
            # CORREÇÃO VISUAL: Tamanho do botão ajustado
            remove_btn.setMinimumSize(130, 30)
            remove_btn.clicked.connect(self._comparative_remove_pokemon)
            buttons_layout.addWidget(remove_btn)
        if len(self.selected_comparison_pokemon_data) >= 2:
            compare_btn = QPushButton(self.parent_window.get_string('pokedex.comparative_button'))
            # CORREÇÃO VISUAL: Tamanho do botão ajustado
            compare_btn.setMinimumSize(130, 30)
            compare_btn.clicked.connect(self._comparative_run_comparison)
            buttons_layout.addWidget(compare_btn)
        self.info_page_comparative_detail_layout.addWidget(buttons_container)
        self._update_aux_screen_comparison()

    def _update_aux_screen_comparison(self):
        self._clear_layout(self.aux_screen_3_layout)
        if self.selected_comparison_pokemon_data: self.aux_screen_3_layout.addWidget(QLabel(self.parent_window.get_string('pokedex.comparative_selected_count', "Selecionados: {count}/6").format(count=len(self.selected_comparison_pokemon_data))))
        else: self.aux_screen_3_layout.addWidget(QLabel(self.parent_window.get_string('pokedex.comparative_none_selected', "Nenhum selecionado")))

    def _comparative_image_clicked(self, pokemon_data, button_clicked):
        for btn in self.info_page_comparative_detail_layout.findChildren(QToolButton):
            if btn is not button_clicked: btn.setChecked(False)
        self.active_pokemon_for_removal = pokemon_data if button_clicked.isChecked() else None
        if button_clicked.isChecked(): self._play_sound("click.ogg", volume=0.2)

    def _comparative_remove_pokemon(self):
        if not self.active_pokemon_for_removal: return
        for i in range(self.pokemon_selection_list.count()):
            list_item = self.pokemon_selection_list.item(i)
            if list_item.data(Qt.ItemDataRole.UserRole) == self.active_pokemon_for_removal: list_item.setHidden(False); break
        self.selected_comparison_pokemon_data.remove(self.active_pokemon_for_removal); self._play_sound("B.wav")
        if not self.selected_comparison_pokemon_data:
            for i in range(self.pokemon_selection_list.count()): self.pokemon_selection_list.item(i).setHidden(False)
        self._comparative_update_info_screen()

    def _comparative_run_comparison(self):
        if len(self.selected_comparison_pokemon_data) < 2: return
        self._play_sound("click.ogg", volume=0.2); self._comparative_display_results(self.parent_window.run_comparison(self.selected_comparison_pokemon_data))

    def _comparative_display_results(self, results):
        self._clear_layout(self.info_page_comparative_detail_layout); self.comparative_is_showing_results = True
        if not results: self.info_page_comparative_detail_layout.addWidget(QLabel(self.parent_window.get_string('pokedex.comparative_no_results'))); return
        results_layout = QFormLayout()
        for category, winner_data in results: results_layout.addRow(f"<b>{category}:</b>", QLabel(f"<b>{winner_data['name']}</b> (Score: {winner_data['score']})"))
        self.info_page_comparative_detail_layout.addLayout(results_layout)
        self.aux_screen_1.setText(self.parent_window.get_string('pokedex.comparative_title')); self.aux_screen_2.setText(self.parent_window.get_string('pokedex.comparative_final_analysis')); self._clear_layout(self.aux_screen_3_layout)

    def _populate_topics_records_page(self):
        self._clear_layout(self.page_topics_records_layout)
        self.page_topics_records_layout.addWidget(QLabel(f"<b>{self.parent_window.get_string('pokedex.topics_title')}</b>"))
        description = QLabel(self.parent_window.get_string('pokedex.topics_description')); description.setWordWrap(True); self.page_topics_records_layout.addWidget(description)
        self.topics_list_widget = QListWidget()
        for key in self.topic_keys: item = QListWidgetItem(self.parent_window.get_string(key)); item.setData(Qt.ItemDataRole.UserRole, key); self.topics_list_widget.addItem(item)
        self.topics_list_widget.setStyleSheet(self.base_list_style); self.topics_list_widget.currentItemChanged.connect(self._update_topic_detail)
        self.page_topics_records_layout.addWidget(self.topics_list_widget); self.main_screen.setCurrentWidget(self.page_topics_records); self.info_screen.setCurrentWidget(self.info_page_topics_records_detail)
        if self.topics_list_widget.count() > 0: self.topics_list_widget.setCurrentRow(0)

    def _update_topic_detail(self, current_item, previous_item):
        if not current_item: return
        key = current_item.data(Qt.ItemDataRole.UserRole)
        content = QWidget(); layout = QFormLayout(content)
        rankings = self.parent_window.rankings
        if not rankings:
            layout.addRow(QLabel(self.parent_window.get_string('pokedex.ranking_data_unavailable')))
            self.info_page_topics_records_detail.setWidget(content)
            return

        def add_line(label_key, value):
            layout.addRow(f"<b>{self.parent_window.get_string(label_key)}:</b>", QLabel(str(value)))
        
        # CORREÇÃO DO BUG: Lógica de busca de stat simplificada e corrigida para funcionar com traduções
        if key.startswith("pokedex.topic_max_"):
            stat_key_map = {
                "pokedex.topic_max_hp": "hp",
                "pokedex.topic_max_atk": "attack",
                "pokedex.topic_max_def": "defense",
                "pokedex.topic_max_sp_atk": "special-attack",
                "pokedex.topic_max_sp_def": "special-defense",
                "pokedex.topic_max_speed": "speed"
            }
            stat_key = stat_key_map.get(key)
            if stat_key:
                poke, value = rankings.get(f'stat_{stat_key}', ('N/A', 0))
                add_line('pokedex.topics_pokemon_label', poke)
                add_line('pokedex.topics_value_label', value)
        elif "quest" in key:
            quest_key_map = {"pokedex.topic_richest_quest": "quest_money", "pokedex.topic_best_xp_quest": "quest_xp", "pokedex.topic_best_ratio_quest": "quest_combo"}
            quest_data = rankings.get(quest_key_map.get(key), {})
            add_line('pokedex.topics_pokemon_label', quest_data.get('pokemon', 'N/A'))
            add_line('pokedex.topics_npc_label', quest_data.get('npc', 'N/A'))
            add_line('pokedex.topics_reward_label', f"💰${quest_data.get('money', 0)} | 🎓{quest_data.get('trainer_xp', 0)} XP")
        elif key == "pokedex.topic_priciest_candy":
            item, data = rankings.get('candy_price', ('N/A', {'price': 0}))
            add_line('pokedex.topics_item_label', item)
            add_line('pokedex.topics_price_label', f"${data.get('price', 0)}")
        elif key == "pokedex.topic_most_common":
            poke, data = rankings.get('most_common', ('N/A', {}))
            add_line('pokedex.topics_pokemon_label', poke)
            add_line('pokedex.topics_maps_label', data.get('maps', 0))
            add_line('pokedex.topics_avg_rate_label', f"1 / {data.get('rate', 0):.2f}")
        elif key == "pokedex.topic_most_rare":
            poke, data = rankings.get('most_rare', ('N/A', {}))
            add_line('pokedex.topics_pokemon_label', poke)
            add_line('pokedex.topics_maps_label', data.get('maps', 0))
            add_line('pokedex.topics_avg_rate_label', f"1 / {data.get('rate', 0):.2f}")
        
        self.info_page_topics_records_detail.setWidget(content)
        self.aux_screen_2.setText(current_item.text())
        self._clear_layout(self.aux_screen_3_layout)
        icon_label = QLabel(emojis.TROFÉU); icon_label.setStyleSheet("font-size: 20px;"); self.aux_screen_3_layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)

    def _populate_ev_hotspots_page(self):
        self._clear_layout(self.page_ev_hotspots_layout); self.page_ev_hotspots_layout.addWidget(QLabel(f"<b>{self.parent_window.get_string('pokedex.ev_hotspots_title')}</b>"))
        self.ev_stats_list_widget = QListWidget()
        for key in self.ev_stat_keys:
            item = QListWidgetItem(self.parent_window.get_string(f'stats.{key}')); item.setData(Qt.ItemDataRole.UserRole, key); self.ev_stats_list_widget.addItem(item)
        self.ev_stats_list_widget.setStyleSheet(self.base_list_style); self.ev_stats_list_widget.currentItemChanged.connect(self._update_ev_hotspot_detail)
        self.page_ev_hotspots_layout.addWidget(self.ev_stats_list_widget); self.main_screen.setCurrentWidget(self.page_ev_hotspots); self.info_screen.setCurrentWidget(self.info_page_ev_hotspots_detail)
        if self.ev_stats_list_widget.count() > 0: self.ev_stats_list_widget.setCurrentRow(0)

    def _update_ev_hotspot_detail(self, current_item, previous_item):
        if not current_item: return
        stat_key = current_item.data(Qt.ItemDataRole.UserRole)
        content = QWidget(); layout = QVBoxLayout(content)
        rankings = self.parent_window.ev_hotspots_ranking.get(stat_key, [])
        if not rankings:
            layout.addWidget(QLabel(self.parent_window.get_string('pokedex.no_hotspot_found').format(stat=current_item.text())))
        else:
            for i, spot in enumerate(rankings):
                rate_text = f"~1/{int(spot['rate'])}" if spot['rate'] != float('inf') else "N/A"
                item_widget = QWidget(); item_layout = QHBoxLayout(item_widget); item_layout.setContentsMargins(0, 5, 0, 5)
                if icon := get_icon_from_path(get_pokemon_image_path(spot['pokemon'])):
                    icon_label = QLabel(); icon_label.setPixmap(icon.pixmap(32, 32)); item_layout.addWidget(icon_label)
                info_label = QLabel(f"<b>{i+1}. {spot['pokemon']}</b> ({spot['ev_yield']})<br><i>{spot['map']} ({rate_text})</i>"); info_label.setWordWrap(True); item_layout.addWidget(info_label, 1)
                layout.addWidget(item_widget)
        self.info_page_ev_hotspots_detail.setWidget(content); self.aux_screen_1.setText(self.parent_window.get_string('pokedex.ev_hotspots_title')); self.aux_screen_2.setText(current_item.text())

    def _create_type_widget(self, type_key, size="normal", show_name=True):
        if not type_key: return None
        container = QWidget(); layout = QVBoxLayout(container); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(0)
        icon_size, font_size = (16, 7) if size == "small" else (24, 9)
        if (icon := get_icon_from_path(emojis.TYPE_ICONS.get(type_key))):
            icon_label = QLabel(); icon_label.setPixmap(icon.pixmap(icon_size, icon_size)); layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        if show_name:
            name_label = QLabel(self.parent_window.get_string(f"types.{type_key}", type_key)); name_label.setStyleSheet(f"font-size: {font_size}px; color: white; font-weight: bold;"); layout.addWidget(name_label, alignment=Qt.AlignmentFlag.AlignCenter)
        return container

class SettingsTab(QWidget):
    theme_changed = pyqtSignal(str)
    language_changed = pyqtSignal()
    sort_preference_changed = pyqtSignal()

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        # Precisamos importar aqui para ter acesso aos nomes dos sons
        from sound_manager import get_available_sounds
        self.available_sounds = get_available_sounds()
        self.init_ui()

    
    
    def retranslate_ui(self):
        self.title_label.setText(self.parent_window.get_string("tabs.settings"))
        self.theme_label.setText(self.parent_window.get_string("settings.theme"))
        self.lang_label.setText(self.parent_window.get_string("settings.language"))
        self.sort_label.setText(self.parent_window.get_string("collection.sort_by_label"))
        self.animation_label.setText(self.parent_window.get_string("settings.animation_style"))
        self.sound_label.setText(self.parent_window.get_string("settings.sound_style"))
        self.save_btn.setText(f"{emojis.SALVAR} {self.parent_window.get_string('settings.save_button')}")

        # Salva as seleções atuais para restaurá-las
        current_theme = self.theme_selector.currentText()
        current_sort = self.sort_selector.currentText()
        current_anim = self.animation_selector.currentText()
        current_sound = self.sound_selector.currentText()

        # Atualiza os textos das opções nos ComboBoxes
        self.update_theme_options()
        self.update_sort_options()
        self.update_animation_options()
        self.update_sound_options()

        # Restaura as seleções
        if current_theme in [self.theme_selector.itemText(i) for i in range(self.theme_selector.count())]: self.theme_selector.setCurrentText(current_theme)
        if current_sort in [self.sort_selector.itemText(i) for i in range(self.sort_selector.count())]: self.sort_selector.setCurrentText(current_sort)
        if current_anim in [self.animation_selector.itemText(i) for i in range(self.animation_selector.count())]: self.animation_selector.setCurrentText(current_anim)
        if current_sound in [self.sound_selector.itemText(i) for i in range(self.sound_selector.count())]: self.sound_selector.setCurrentText(current_sound)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.title_label = QLabel(self.parent_window.get_string("tabs.settings"))
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        form_layout = QFormLayout()

        self.themes = { "dark": "themes.dark", "light": "themes.light", "pokemon": "themes.pokemon" }
        self.theme_selector = QComboBox()
        self.update_theme_options()
        self.theme_selector.currentTextChanged.connect(self.on_theme_change)
        self.theme_label = QLabel(self.parent_window.get_string("settings.theme"))
        form_layout.addRow(self.theme_label, self.theme_selector)

        self.lang_selector = QComboBox()
        self.lang_selector.addItems(["pt-br", "en-us"])
        self.lang_label = QLabel(self.parent_window.get_string("settings.language"))
        form_layout.addRow(self.lang_label, self.lang_selector)

        self.sort_orders = { "Ordem Alfabética": "collection.sort_alpha", "Ordem da Pokédex": "collection.sort_pokedex" }
        self.sort_selector = QComboBox()
        self.update_sort_options()
        self.sort_label = QLabel(self.parent_window.get_string("collection.sort_by_label"))
        form_layout.addRow(self.sort_label, self.sort_selector)

        # --- SELETOR DE ANIMAÇÃO E SOM (COM TRADUÇÃO) ---
        self.animation_selector = QComboBox()
        self.raw_animation_names = get_available_animations()
        self.update_animation_options()
        self.animation_label = QLabel(self.parent_window.get_string("settings.animation_style"))
        form_layout.addRow(self.animation_label, self.animation_selector)

        self.sound_selector = QComboBox()
        from sound_manager import get_available_sounds 
        self.raw_sound_names = get_available_sounds()
        self.update_sound_options()
        self.sound_label = QLabel(self.parent_window.get_string("settings.sound_style"))
        form_layout.addRow(self.sound_label, self.sound_selector)

        layout.addLayout(form_layout)

        self.save_btn = QPushButton(f"{emojis.SALVAR} {self.parent_window.get_string('settings.save_button')}")
        self.save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()

    def update_animation_options(self):
        self.animation_selector.blockSignals(True)
        self.animation_selector.clear()
        translated_names = [self.parent_window.get_string(f"animations.{name}", name) for name in self.raw_animation_names]
        self.animation_selector.addItems(translated_names)
        self.animation_selector.blockSignals(False)

    def update_sound_options(self):
        self.sound_selector.blockSignals(True)
        self.sound_selector.clear()
        translated_names = [self.parent_window.get_string(f"sounds.{name}", name) for name in self.raw_sound_names]
        self.sound_selector.addItems(translated_names)
        self.sound_selector.blockSignals(False)

    def update_theme_options(self):
        self.theme_selector.blockSignals(True)
        self.theme_selector.clear()
        self.theme_selector.addItems([self.parent_window.get_string(v) for v in self.themes.values()])
        self.theme_selector.blockSignals(False)

    def update_sort_options(self):
        self.sort_selector.blockSignals(True)
        self.sort_selector.clear()
        self.sort_selector.addItems([self.parent_window.get_string(v) for v in self.sort_orders.values()])
        self.sort_selector.blockSignals(False)

    def on_theme_change(self, theme_text):
        theme_key = next((key for key, value in self.themes.items() if self.parent_window.get_string(value) == theme_text), "dark")
        self.theme_changed.emit(theme_key)

    # DENTRO da classe SettingsTab, substitua o método save_settings
    def save_settings(self):
        config = self.parent_window.config
        previous_lang = config.get('language', 'pt-br')

        theme_text = self.theme_selector.currentText()
        config['theme'] = next((key for key, value in self.themes.items() if self.parent_window.get_string(value) == theme_text), "dark")

        config['language'] = self.lang_selector.currentText()

        sort_text = self.sort_selector.currentText()
        config['sort_order'] = next((k for k, v in self.sort_orders.items() if self.parent_window.get_string(v) == sort_text), "Ordem Alfabética")

        # --- LÓGICA DE SALVAMENTO CORRIGIDA PARA TRADUÇÃO ---
        selected_anim_index = self.animation_selector.currentIndex()
        if selected_anim_index != -1:
            config['evolution_animation'] = self.raw_animation_names[selected_anim_index]

        selected_sound_index = self.sound_selector.currentIndex()
        if selected_sound_index != -1:
            config['evolution_sound'] = self.raw_sound_names[selected_sound_index]

        save_json("config.json", config, is_user_data=True)

        if previous_lang != config['language']:
            self.language_changed.emit()
        else:
            QMessageBox.information(self, 
                self.parent_window.get_string("settings.saved_title"), 
                self.parent_window.get_string("settings.saved_text_generic")
            )

        self.sort_preference_changed.emit()

    def set_current_settings(self, config):
        self.update_theme_options()
        self.theme_selector.blockSignals(True)
        theme_key = config.get("theme", "dark")
        theme_text = self.parent_window.get_string(self.themes.get(theme_key, "themes.dark"))
        self.theme_selector.setCurrentText(theme_text)
        self.theme_selector.blockSignals(False)
        
        self.lang_selector.blockSignals(True)
        self.lang_selector.setCurrentText(config.get("language", "pt-br"))
        self.lang_selector.blockSignals(False)

        self.update_sort_options()
        sort_key = config.get("sort_order", "Ordem Alfabética")
        sort_text = self.parent_window.get_string(self.sort_orders.get(sort_key, "collection.sort_alpha"))
        self.sort_selector.setCurrentText(sort_text)

        # --- Carregar as configurações de animação e som salvas ---
        animation_name = config.get("evolution_animation", "Flash Clássico")
        self.animation_selector.setCurrentText(animation_name)
        
        sound_name = config.get("evolution_sound", "Clássico (Game Boy)")
        self.sound_selector.setCurrentText(sound_name)

class SupportTab(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(20)
        
        self.title_label = QLabel(self.parent_window.get_string("support.title"))
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.message_label = QLabel(self.parent_window.get_string("support.message"))
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("font-size: 16px; padding-left: 20px; padding-right: 20px;")

        main_layout.addWidget(self.title_label)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.message_label)
        main_layout.addSpacing(30)
        
        content_layout = QHBoxLayout()
        
        kofi_container_wrapper = QHBoxLayout()
        kofi_content_layout = QVBoxLayout()
        self.kofi_title = QLabel(self.parent_window.get_string("support.kofi_title"))
        self.kofi_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.kofi_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        kofi_button_group_layout = QVBoxLayout()
        kofi_button_group_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.kofi_button = QPushButton("")
        kofi_icon_path = resource_path("Images/kofi_logo.png")
        if os.path.exists(kofi_icon_path):
            self.kofi_button.setIcon(QIcon(kofi_icon_path))
            self.kofi_button.setIconSize(QSize(200, 45))
        else:
            self.kofi_button.setText("[Imagem Ko-fi]")
            self.kofi_button.setStyleSheet("color: black;")
        self.kofi_button.setFixedSize(220, 60)
        self.kofi_button.setStyleSheet("background-color: transparent; border: none;")       
        self.kofi_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.kofi_button.clicked.connect(self.open_kofi_page)
        self.kofi_button_label = QLabel(self.parent_window.get_string("support.kofi_button"))
        self.kofi_button_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.kofi_button_label.setStyleSheet("font-size: 18px;")
        kofi_button_group_layout.addWidget(self.kofi_button)
        kofi_button_group_layout.addSpacing(10)
        kofi_button_group_layout.addWidget(self.kofi_button_label)
        kofi_content_layout.addWidget(self.kofi_title)
        kofi_content_layout.addStretch(1)
        kofi_content_layout.addLayout(kofi_button_group_layout)
        kofi_content_layout.addStretch(1)
        kofi_container_wrapper.addSpacing(90)
        kofi_container_wrapper.addLayout(kofi_content_layout)
        kofi_container_wrapper.addStretch()
        
        pix_container = QVBoxLayout()
        pix_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pix_title = QLabel(self.parent_window.get_string("support.pix_title"))
        self.pix_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.pix_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.pix_qrcode_label = QLabel(self.parent_window.get_string("support.pix_qrcode_not_found"))
        pix_qrcode_path = resource_path("qrcode.png")
        if os.path.exists(pix_qrcode_path):
             pixmap = QPixmap(pix_qrcode_path)
             self.pix_qrcode_label.setPixmap(pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            self.pix_qrcode_label.setFixedSize(250, 250)
            self.pix_qrcode_label.setStyleSheet("background-color: #CCCCCC; border-radius: 8px;")
        
        qrcode_hbox = QHBoxLayout()
        qrcode_hbox.addStretch()
        qrcode_hbox.addWidget(self.pix_qrcode_label)
        qrcode_hbox.addStretch()

        self.pix_key_label = QLabel(self.parent_window.get_string("support.pix_key_label"))
        self.pix_key_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        button_block_layout = QVBoxLayout()
        self.pix_key_line_edit = QLineEdit("c8e3b1f2-a4d5-4c6e-8b0f-9d1a2c3b4e5f")
        self.pix_key_line_edit.setReadOnly(True)
        self.pix_key_line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pix_key_line_edit.setFixedWidth(300)
        self.copy_pix_key_button = QPushButton(self.parent_window.get_string("support.pix_copy_button"))
        self.copy_pix_key_button.clicked.connect(self.copy_pix_key)
        self.copy_pix_key_button.setFixedWidth(300)
        button_block_layout.addWidget(self.pix_key_line_edit)
        button_block_layout.addWidget(self.copy_pix_key_button)
        centering_layout = QHBoxLayout()
        centering_layout.addStretch()
        centering_layout.addLayout(button_block_layout)
        centering_layout.addStretch()

        pix_container.addWidget(self.pix_title)
        pix_container.addSpacing(10)
        pix_container.addLayout(qrcode_hbox)
        pix_container.addSpacing(8)
        pix_container.addWidget(self.pix_key_label) 
        pix_container.addSpacing(8)
        pix_container.addStretch()
        pix_container.addLayout(centering_layout)
        pix_container.addStretch()

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.VLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        
        content_layout.addLayout(kofi_container_wrapper, 1)
        content_layout.addWidget(divider)
        content_layout.addLayout(pix_container, 1)

        main_layout.addLayout(content_layout)
        main_layout.addStretch()

    def open_kofi_page(self):
        webbrowser.open("https://ko-fi.com/G2G81J7HHW")

    def copy_pix_key(self):
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(self.pix_key_line_edit.text())
            QMessageBox.information(self, self.parent_window.get_string("support.pix_copied_title"), self.parent_window.get_string("support.pix_copied_text"))

    def retranslate_ui(self):
        self.title_label.setText(self.parent_window.get_string("support.title"))
        self.message_label.setText(self.parent_window.get_string("support.message"))
        self.kofi_title.setText(self.parent_window.get_string("support.kofi_title"))
        self.kofi_button_label.setText(self.parent_window.get_string("support.kofi_button"))
        self.pix_title.setText(self.parent_window.get_string("support.pix_title"))
        self.pix_key_label.setText(self.parent_window.get_string("support.pix_key_label"))
        self.copy_pix_key_button.setText(self.parent_window.get_string("support.pix_copy_button"))

# --- NOVA ABA: ShinyHuntTab ---
class ShinyHuntTab(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.parent_window.pokemon_data = load_json("pokemon_data.json") # mudar aqui
        self.hunts = load_json("shiny_hunts.json", {"active": {}, "history": []}, is_user_data=True)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        
        self.current_hunt_key = None
        self.is_running = False
        self.time_elapsed = timedelta(seconds=0)

        self.init_ui()
        self.load_hunts_list()
        self.populate_history_table()

    def retranslate_ui(self):
        # Guarda o estado atual se necessário
        # (Ex: qual item está selecionado em um ComboBox)

        # Cria um novo widget central para a aba
        new_central_widget = QWidget()
        # O truque: Nós aplicamos o novo layout A ESTE NOVO WIDGET, não ao 'self'
        self.init_ui(parent_widget=new_central_widget)

        # Define o novo widget como o conteúdo da aba
        # Primeiro, remove o antigo
        old_widget = self.findChild(QWidget)
        if old_widget:
            old_widget.deleteLater()

        # Adiciona o novo
        main_layout = QVBoxLayout()
        main_layout.addWidget(new_central_widget)
        self.setLayout(main_layout)

        # Recarrega os dados
        if hasattr(self, 'update_collection'): self.update_collection()
        if hasattr(self, 'update_team_list'): self.update_team_list()
        if hasattr(self, 'update_my_pokemon_list'): self.update_my_pokemon_list()
        if hasattr(self, 'load_hunts_list'): self.load_hunts_list()
        if hasattr(self, 'populate_history_table'): self.populate_history_table()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        left_panel = QVBoxLayout()
        right_panel = QVBoxLayout()

        # --- PAINEL ESQUERDO: CAÇADA ATIVA ---
        title = QLabel(self.parent_window.get_string("tabs.shiny_hunt"))
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel.addWidget(title)

        # AVISO BETA
        warning_label = QLabel(self.parent_window.get_string("shiny_hunt.beta_warning"))
        warning_label.setWordWrap(True)
        warning_label.setStyleSheet("background-color: #444; color: #ffc107; padding: 5px; border-radius: 3px; border: 1px solid #ffc107;")
        warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel.addWidget(warning_label)

        # --- NOVO AVISO DE DADOS SHINY ---
        shiny_data_warning = QLabel(self.parent_window.get_string("shiny_hunt.shiny_data_warning"))
        shiny_data_warning.setWordWrap(True)
        # Estilo para chamar a atenção, mas diferente do outro aviso
        shiny_data_warning.setStyleSheet(
            "background-color: #402E3D; color: #E89AF3; padding: 5px; "
            "border-radius: 3px; border: 1px solid #E89AF3;"
        )
        shiny_data_warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel.addWidget(shiny_data_warning)
        # --- FIM DO NOVO AVISO ---

        
        # Gerenciamento de Caçadas
        hunt_management_layout = QHBoxLayout()
        self.hunts_combo = QComboBox()
        self.hunts_combo.setPlaceholderText(self.parent_window.get_string("shiny_hunt.hunts_placeholder"))
        self.load_btn = QPushButton(self.parent_window.get_string("shiny_hunt.load_hunt"))
        self.save_btn = QPushButton(self.parent_window.get_string("shiny_hunt.save_hunt"))
        self.delete_btn = QPushButton(self.parent_window.get_string("shiny_hunt.delete_hunt"))
        
        self.hunts_combo.currentTextChanged.connect(self.load_selected_hunt)
        self.load_btn.clicked.connect(self.load_selected_hunt)
        self.save_btn.clicked.connect(self.save_current_hunt)
        self.delete_btn.clicked.connect(self.delete_selected_hunt)

        hunt_management_layout.addWidget(self.hunts_combo, 1)
        hunt_management_layout.addWidget(self.load_btn)
        hunt_management_layout.addWidget(self.save_btn)
        hunt_management_layout.addWidget(self.delete_btn)
        left_panel.addLayout(hunt_management_layout)

        # Seleção do Pokémon
        selection_layout = QHBoxLayout()
        self.pokemon_image_label = QLabel("?")
        self.pokemon_image_label.setFixedSize(96, 96)
        self.pokemon_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pokemon_image_label.setFrameShape(QFrame.Shape.StyledPanel)
        
        form_layout = QFormLayout()
        self.pokemon_select = QComboBox()
        self.pokemon_select.setEditable(True)
        pokemon_list = self.parent_window.get_sorted_pokemon_list()
        self.pokemon_select.addItems([""] + pokemon_list)
        self.pokemon_select.setCompleter(QCompleter(pokemon_list, self))
        self.pokemon_select.currentTextChanged.connect(self.update_pokemon_info)
        
        # Novos widgets de mapa e respawn
        self.map_select = QComboBox()
        self.respawn_input = QSpinBox()
        self.respawn_input.setRange(1, 999999)
        self.respawn_input.setPrefix("1 / ")
        
        self.map_select.currentIndexChanged.connect(self.update_respawn_display)

        form_layout.addRow(self.parent_window.get_string("shiny_hunt.select_pokemon"), self.pokemon_select)
        form_layout.addRow(self.parent_window.get_string("shiny_hunt.map_selector"), self.map_select)
        form_layout.addRow(self.parent_window.get_string("shiny_hunt.respawn_rate"), self.respawn_input)
        
        self.odds_label = QLabel(f"{self.parent_window.get_string('shiny_hunt.odds')} 1 / 8192")
        form_layout.addRow(self.odds_label)

        selection_layout.addWidget(self.pokemon_image_label)
        selection_layout.addLayout(form_layout)
        left_panel.addLayout(selection_layout)

        # Displays de tempo e encontros
        display_layout = QHBoxLayout()
        self.encounters_label = QLabel(f"<b>{self.parent_window.get_string('shiny_hunt.encounters')}</b> 0")
        self.timer_label = QLabel(f"<b>{self.parent_window.get_string('shiny_hunt.time')}</b> 00:00:00")
        display_layout.addWidget(self.encounters_label)
        display_layout.addWidget(self.timer_label)
        left_panel.addLayout(display_layout)

        # Botões de controle da caçada
        controls_layout = QGridLayout()
        self.start_btn = QPushButton(f"{emojis.INICIAR} {self.parent_window.get_string('shiny_hunt.start_button')}")
        self.stop_btn = QPushButton(f"{emojis.PARAR} {self.parent_window.get_string('shiny_hunt.stop_button')}")
        self.increment_btn = QPushButton(f"{emojis.ADICIONAR} {self.parent_window.get_string('shiny_hunt.increment_button')}")
        self.reset_btn = QPushButton(f"{emojis.LIXEIRA} {self.parent_window.get_string('shiny_hunt.reset_button')}")

        self.start_btn.clicked.connect(self.start_hunt)
        self.stop_btn.clicked.connect(self.stop_hunt)
        self.increment_btn.clicked.connect(self.increment_encounter)
        self.reset_btn.clicked.connect(self.reset_hunt)

        controls_layout.addWidget(self.start_btn, 0, 0)
        controls_layout.addWidget(self.stop_btn, 0, 1)
        controls_layout.addWidget(self.increment_btn, 1, 0)
        controls_layout.addWidget(self.reset_btn, 1, 1)
        left_panel.addLayout(controls_layout)
        left_panel.addStretch()

        # --- PAINEL DIREITO: HISTÓRICO ---
        history_title = QLabel(self.parent_window.get_string("shiny_hunt.history"))
        history_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        history_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels([
            self.parent_window.get_string("shiny_hunt.pokemon_header"),
            self.parent_window.get_string("shiny_hunt.encounters_header"),
            self.parent_window.get_string("shiny_hunt.time_header"),
            self.parent_window.get_string("shiny_hunt.date_header")
        ])
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        right_panel.addWidget(history_title)
        right_panel.addWidget(self.history_table)

        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_panel, 1)
        
        self.update_button_states()

    def update_pokemon_list(self):
        """Atualiza o conteúdo do ComboBox de Pokémon."""
        current_selection = self.pokemon_select.currentText()
        pokemon_list = self.parent_window.get_sorted_pokemon_list()

        self.pokemon_select.blockSignals(True)
        self.pokemon_select.clear()
        self.pokemon_select.addItems([""] + pokemon_list)

        if current_selection in pokemon_list:
            self.pokemon_select.setCurrentText(current_selection)

        self.pokemon_select.completer().setModel(self.pokemon_select.model())
        self.pokemon_select.blockSignals(False)

    def update_pokemon_info(self, species_name):
        self.pokemon_image_label.setPixmap(QPixmap())
        default_shiny_rate = 8192
        
        # Limpar e desabilitar seletor de mapa
        self.map_select.blockSignals(True)
        self.map_select.clear()
        self.map_select.setEnabled(False)
        self.respawn_input.setValue(0)
        self.map_select.blockSignals(False)

        if not species_name:
            self.pokemon_image_label.setText("?")
            self.odds_label.setText(f"{self.parent_window.get_string('shiny_hunt.odds')} 1 / {default_shiny_rate}")
            return

        # Atualizar imagem
        image_path = get_pokemon_image_path(species_name)
        if image_path:
            pixmap = load_pixmap_robustly(image_path, 96)
            if pixmap:
                self.pokemon_image_label.setText("")
                self.pokemon_image_label.setPixmap(pixmap)
            else:
                self.pokemon_image_label.setText("Erro")
        else:
            self.pokemon_image_label.setText("?")

        # Atualizar odds
        pokemon_info = self.parent_window.pokemon_data.get(species_name) # mudar aqui
        rate = pokemon_info.get('shiny_rate', default_shiny_rate) if pokemon_info else default_shiny_rate
        self.odds_label.setText(f"{self.parent_window.get_string('shiny_hunt.odds')} 1 / {rate}")

        # Popular seletor de mapa
        if spawn_locations := self.parent_window.spawn_rates.get(species_name):
            self.map_select.blockSignals(True)
            for loc in spawn_locations:
                self.map_select.addItem(loc["map"])
            self.map_select.setEnabled(True)
            self.map_select.blockSignals(False)
            self.update_respawn_display() # Chamar para o primeiro item

    def update_respawn_display(self):
        species_name = self.pokemon_select.currentText()
        map_name = self.map_select.currentText()
        
        if not species_name or not map_name:
            self.respawn_input.setValue(0)
            return
            
        if spawn_locations := self.parent_window.spawn_rates.get(species_name):
            for loc in spawn_locations:
                if loc["map"] == map_name:
                    self.respawn_input.setValue(loc.get("rate", 0))
                    break

    def start_hunt(self):
        pokemon_name = self.pokemon_select.currentText()
        if not pokemon_name:
            QMessageBox.warning(self, self.parent_window.get_string("globals.warning"), self.parent_window.get_string("shiny_hunt.select_pokemon_to_start"))
            return

        if self.is_running:
            QMessageBox.information(self, "Info", self.parent_window.get_string("shiny_hunt.hunt_in_progress").format(pokemon=self.current_hunt_key))
            return
        
        self.current_hunt_key = pokemon_name
        if self.current_hunt_key not in self.hunts["active"]:
            self.hunts["active"][self.current_hunt_key] = {"encounters": 0, "time": 0}
        
        self.time_elapsed = timedelta(seconds=self.hunts["active"][self.current_hunt_key].get("time", 0))
        self.timer.start(1000)
        self.is_running = True
        self.update_displays()
        self.update_button_states()

    def stop_hunt(self):
        if not self.is_running:
            QMessageBox.information(self, "Info", self.parent_window.get_string("shiny_hunt.no_hunt_active"))
            return

        self.timer.stop()
        self.is_running = False
        
        self.hunts["active"][self.current_hunt_key]["time"] = self.time_elapsed.total_seconds()
        self.save_hunts()
        
        reply = QMessageBox.question(self, self.parent_window.get_string("shiny_hunt.hunt_finished"),
                                     self.parent_window.get_string("shiny_hunt.hunt_finished_text"),
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            hunt_data = self.hunts["active"].pop(self.current_hunt_key)
            hunt_data["pokemon"] = self.current_hunt_key
            hunt_data["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.hunts["history"].append(hunt_data)
            self.save_hunts()
            self.reset_current_hunt_ui(clear_pokemon=True)
            self.populate_history_table()
        
        self.update_button_states()

    def increment_encounter(self):
        if self.is_running and self.current_hunt_key:
            self.hunts["active"][self.current_hunt_key]["encounters"] += 1
            self.update_displays()

    def reset_hunt(self):
        if not self.current_hunt_key: return

        reply = QMessageBox.question(self, self.parent_window.get_string("shiny_hunt.confirm_reset_title"),
                                     self.parent_window.get_string("shiny_hunt.confirm_reset_text"),
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.timer.stop()
            self.is_running = False
            if self.current_hunt_key in self.hunts["active"]:
                self.hunts["active"][self.current_hunt_key] = {"encounters": 0, "time": 0}
            self.save_hunts()
            self.reset_current_hunt_ui()

    def save_current_hunt(self):
        if self.current_hunt_key and self.current_hunt_key in self.hunts["active"]:
            self.hunts["active"][self.current_hunt_key]["time"] = self.time_elapsed.total_seconds()
            self.save_hunts()
            QMessageBox.information(self, self.parent_window.get_string("globals.success"), self.parent_window.get_string("shiny_hunt.hunt_saved"))
            self.load_hunts_list()

    def load_hunts_list(self):
        self.hunts_combo.blockSignals(True)
        self.hunts_combo.clear()
        self.hunts_combo.addItem(self.parent_window.get_string("shiny_hunt.hunts_placeholder"))
        self.hunts_combo.addItems(sorted(self.hunts["active"].keys()))
        self.hunts_combo.blockSignals(False)

    def load_selected_hunt(self):
        hunt_key = self.hunts_combo.currentText()
        if hunt_key == self.parent_window.get_string("shiny_hunt.hunts_placeholder"):
            return

        if self.is_running:
            self.timer.stop()
            self.is_running = False
            self.update_button_states()

        self.current_hunt_key = hunt_key
        self.pokemon_select.setCurrentText(self.current_hunt_key)
        self.time_elapsed = timedelta(seconds=self.hunts["active"].get(self.current_hunt_key, {}).get("time", 0))
        self.update_displays()

    def delete_selected_hunt(self):
        hunt_key = self.hunts_combo.currentText()
        if hunt_key == self.parent_window.get_string("shiny_hunt.hunts_placeholder"):
            return

        reply = QMessageBox.question(self, self.parent_window.get_string("shiny_hunt.confirm_delete_title"),
                                     self.parent_window.get_string("shiny_hunt.confirm_delete_text").format(pokemon=hunt_key),
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if hunt_key in self.hunts["active"]:
                del self.hunts["active"][hunt_key]
                self.save_hunts()
                self.load_hunts_list()
                if self.current_hunt_key == hunt_key:
                    self.reset_current_hunt_ui(clear_pokemon=True)

    def populate_history_table(self):
        self.history_table.setRowCount(0)
        for hunt in reversed(self.hunts.get("history", [])):
            row_pos = self.history_table.rowCount()
            self.history_table.insertRow(row_pos)
            self.history_table.setItem(row_pos, 0, QTableWidgetItem(hunt.get("pokemon", "?")))
            self.history_table.setItem(row_pos, 1, QTableWidgetItem(str(hunt.get("encounters", 0))))
            time_spent = format_timedelta(timedelta(seconds=hunt.get("time", 0)))
            self.history_table.setItem(row_pos, 2, QTableWidgetItem(time_spent))
            self.history_table.setItem(row_pos, 3, QTableWidgetItem(hunt.get("date", "")))

    def update_displays(self):
        if self.current_hunt_key and self.current_hunt_key in self.hunts["active"]:
            encounters = self.hunts["active"][self.current_hunt_key].get("encounters", 0)
            self.encounters_label.setText(f"<b>{self.parent_window.get_string('shiny_hunt.encounters')}</b> {encounters}")
        self.timer_label.setText(f"<b>{self.parent_window.get_string('shiny_hunt.time')}</b> {format_timedelta(self.time_elapsed)}")

    def update_timer(self):
        self.time_elapsed += timedelta(seconds=1)
        self.update_displays()

    def update_button_states(self):
        self.start_btn.setEnabled(not self.is_running)
        self.stop_btn.setEnabled(self.is_running)
        self.increment_btn.setEnabled(self.is_running)
        self.reset_btn.setEnabled(bool(self.current_hunt_key))

    def reset_current_hunt_ui(self, clear_pokemon=False):
        self.time_elapsed = timedelta(seconds=0)
        self.is_running = False
        self.timer.stop()
        if clear_pokemon:
            self.current_hunt_key = None
            self.pokemon_select.setCurrentIndex(0)
        self.update_displays()
        self.update_button_states()

    def save_hunts(self):
        save_json("shiny_hunts.json", self.hunts, is_user_data=True)

# --- Janela Principal ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- CONTROLE DE VERSÃO E UPDATER ---
        self.__version__ = "2.0.1" # <<-- MUDE AQUI A CADA NOVA VERSÃO
        self.github_repo = "VegaPunkSquer/PMMO-Helper-Suite" # <<-- MUDE PARA O SEU REPOSITÓRIO REAL
        # ------------------------------------

        self.config = load_json("config.json", {"theme": "dark", "language": "pt-br", "sort_order": "Ordem Alfabética"}, is_user_data=True)
        self.translations = load_json("translations.json")

        # --- FONTE ÚNICA DA VERDADE (COM CARREGAMENTO REMOTO) ---
        # Carregamos todos os dados principais aqui, uma única vez.
        self.pokemon_data = self._load_app_data_from_remote("pokemon_data.json")
        self.spawn_rates = self._load_app_data_from_remote("spawn_rates.json")
        self.ev_data = self._load_app_data_from_remote("ev_yield_data.json")
        self.type_chart = self._load_app_data_from_remote("type_chart.json")
        self.boss_data = self._load_app_data_from_remote("boss_data.json")
        self.moves_data = self._load_app_data_from_remote("moves_data.json")
        self.loots_data = self._load_app_data_from_remote("loots_and_drops.json")
        self.quests_data = self._load_app_data_from_remote("quests.json")
        self.shiny_data = self._load_app_data_from_remote("shiny_variants.json")
        self.learnsets_data = self._load_app_data_from_remote("pokemon_learnsets.json")
        # battle_logic.py e outros JSONs que você usa também podem ser carregados aqui
        # --- FIM DA CENTRALIZAÇÃO ---

        # NOVO: Pré-cálculo dos rankings para a seção "Tópicos"
        self._calculate_rankings()

        # --- INÍCIO DO CÁLCULO DE ESCALA DINÂMICA ---
        self.stat_ranges = {'base': {}}
        stats_to_calculate = ["hp", "attack", "defense", "special-attack", "special-defense", "speed", "energy", "hp_reg", "en_reg"]

        # Inicializa o dicionário com valores "impossíveis"
        for stat in stats_to_calculate:
            self.stat_ranges['base'][stat] = {'min': 999, 'max': 0}

        # Itera por todos os Pokémon para encontrar os verdadeiros min/max
        for poke_data in self.pokemon_data.values():
            if base_stats := poke_data.get("base_stats"):
                for stat in stats_to_calculate:
                    if stat_value := base_stats.get(stat):
                        if stat_value < self.stat_ranges['base'][stat]['min']:
                            self.stat_ranges['base'][stat]['min'] = stat_value
                        if stat_value > self.stat_ranges['base'][stat]['max']:
                            self.stat_ranges['base'][stat]['max'] = stat_value
        # --- FIM DO CÁLCULO BASE ---

        # --- NOVO CÁLCULO DE ESCALA DINÂMICA PARA STATS FINAIS ---
        self.stat_ranges['final'] = {}
        PERFECT_LEVEL = 125
        PERFECT_IV = 31
        PERFECT_EVS = 4500 # Limite de EVs para o nível 125
        stats_to_calculate_final = ["hp", "attack", "defense", "special-attack", "special-defense", "speed", "energy", "hp_reg", "en_reg"]

        for stat in stats_to_calculate_final:
            self.stat_ranges['final'][stat] = {'max': 0}

        for poke_data in self.pokemon_data.values():
            if base_stats := poke_data.get("base_stats"):
                for stat in stats_to_calculate_final:
                    if stat_value := base_stats.get(stat):
                        # Calcula o stat final para um Pokémon "perfeito" com nature neutra
                        perfect_stat = self._calculate_final_stat(stat, stat_value, PERFECT_LEVEL, PERFECT_IV, PERFECT_EVS, "Hardy")
                        # Guarda o maior valor encontrado até agora
                        if perfect_stat > self.stat_ranges['final'][stat]['max']:
                            self.stat_ranges['final'][stat]['max'] = perfect_stat
        # --- FIM DO CÁLCULO FINAL ---

        self.pokedex_order = {name: i for i, name in enumerate(self.pokemon_data.keys())}

        # --- LÓGICA DE EVOLUÇÃO REVERSA ---
        self.reverse_evolutions = {}
        for pre_evo, post_evo in EVOLUTIONS.items():
            if isinstance(post_evo, list):
                for evo in post_evo:
                    self.reverse_evolutions[evo] = pre_evo
            else:
                self.reverse_evolutions[post_evo] = pre_evo
        # --- FIM DA LÓGICA ---

        # --- NOVO: Pré-cálculo dos Hotspots de EV ---
        self._calculate_ev_hotspots()
        # --- FIM DA LÓGICA ---

        self.setup_ui()

        self.setup_ui()
        self.connect_signals()
        self.load_settings_and_apply_theme()
        self.collection_tab.load_collection()

        # --- VERIFICA ATUALIZAÇÕES NA INICIALIZAÇÃO ---
        self.check_for_updates()

    def _calculate_ev_hotspots(self):
        """Pré-calcula os melhores locais de treino de EV para cada stat (V4)."""
        self.ev_hotspots_ranking = {}
        
        # As 9 chaves de stat que o seu novo JSON usa
        stats_to_rank = ['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed', 'energy', 'hp_reg', 'en_reg']

        for stat_key in stats_to_rank:
            hotspots_for_stat = []
            
            for poke_name, ev_info in self.ev_data.items():
                # Verifica se este Pokémon dá EV para o stat que estamos procurando
                ev_value = ev_info.get(stat_key, 0)
                if ev_value <= 0:
                    continue # Próximo Pokémon
                    
                # Se ele dá o EV, vamos encontrar seus mapas/taxas
                if spawn_list := self.spawn_rates.get(poke_name):
                    map_probabilities = {}
                    for spawn_data in spawn_list:
                        rate = spawn_data.get("rate", 0)
                        map_name = spawn_data.get("map")
                        # Filtra bosses e spawns com taxa 0
                        if rate > 0 and "Boss Rank" not in spawn_data.get("condition", ""):
                            probability = 1 / rate
                            map_probabilities[map_name] = map_probabilities.get(map_name, 0) + probability
                    
                    # Agora, calcula o "score" para cada mapa
                    for map_name, total_prob in map_probabilities.items():
                        # Score = (Valor do EV) x (Chance de achar ele nesse mapa)
                        score = ev_value * total_prob
                        hotspots_for_stat.append({
                            'pokemon': poke_name,
                            'map': map_name,
                            'score': score,
                            # Pega a string completa (ex: +1 Atk, +1 Energy)
                            'ev_yield_str': self._get_ev_yield_string(poke_name), 
                            'rate': 1 / total_prob if total_prob > 0 else float('inf')
                        })

            # Ordena os hotspots para este stat (ex: 'attack')
            sorted_hotspots = sorted(hotspots_for_stat, key=lambda x: x['score'], reverse=True)
            self.ev_hotspots_ranking[stat_key] = sorted_hotspots[:10]
        

    def check_for_updates(self):
            """Verifica se há uma nova versão do app no GitHub."""
            try:
                url = f"https://raw.githubusercontent.com/{self.github_repo}/main/version.json"
                response = requests.get(url, timeout=5) # Timeout de 5s para não travar
                response.raise_for_status()
                
                latest_info = response.json()
                latest_version = latest_info["latest_version"]

                # Compara as versões
                if latest_version > self.__version__:
                    should_update = QMessageBox.question(
                        self,
                        self.get_string("update.title"), # "Atualização Disponível!"
                        self.get_string("update.message").format(
                            latest=latest_version,
                            current=self.__version__
                        ) # "Uma nova versão (X) está disponível. Deseja atualizar?"
                    )

                    if should_update == QMessageBox.StandardButton.Yes:
                        download_url = latest_info["download_url"]
                        webbrowser.open(download_url) # Abre o link de download no navegador
                        self.close() # Fecha o app para o usuário poder instalar o novo
            except Exception as e:
                print(f"AVISO: Não foi possível verificar atualizações: {e}")

    # --- INÍCIO DOS NOVOS MÉTODOS DE LÓGICA ---

    def _load_app_data_from_remote(self, filename):
        """Tenta carregar um JSON da internet, com fallback para o arquivo local."""
        try:
            # Tenta baixar a versão mais recente do GitHub
            url = f"https://raw.githubusercontent.com/{self.github_repo}/main/{filename}"
            response = requests.get(url, timeout=3)
            response.raise_for_status()
            print(f"Sucesso: '{filename}' carregado da internet.")
            return response.json()
        except Exception as e:
            # Se falhar (sem internet, etc.), carrega o arquivo local
            print(f"AVISO: Falha ao carregar '{filename}' da internet ({e}). Usando versão local.")
            return load_json(filename) # Reutiliza sua função original para carregar localmente

    def get_pokedex_list(self):
        """ Retorna a lista de Pokémon na ordem da Pokédex. """
        return list(self.pokedex_order.keys())

    def _calculate_rankings(self):
        """ 
        Pré-calcula todos os rankings para a seção 'Tópicos' da Pokédex,
        usando a lógica de consolidação por mapa.
        """
        self.rankings = {}
        
        # Rankings de Stats (sem alteração)
        for stat in ["hp", "attack", "defense", "special-attack", "special-defense", "speed"]:
            try:
                top_pokemon = max(self.pokemon_data.items(), key=lambda item: item[1].get("base_stats", {}).get(stat, 0))
                self.rankings[f'stat_{stat}'] = (top_pokemon[0], top_pokemon[1]["base_stats"][stat])
            except (ValueError, KeyError):
                self.rankings[f'stat_{stat}'] = ('N/A', 0)

        # Ranking de Quests (sem alteração)
        all_quests = []
        for p_name, quests in self.quests_data.items():
            for quest in quests:
                all_quests.append({**quest, 'pokemon': p_name})
        
        if all_quests:
            max_money = max((q.get('money', 0) for q in all_quests), default=1) or 1
            max_xp = max((q.get('trainer_xp', 0) for q in all_quests), default=1) or 1
            self.rankings['quest_money'] = max(all_quests, key=lambda q: q.get('money', 0))
            self.rankings['quest_xp'] = max(all_quests, key=lambda q: q.get('trainer_xp', 0))
            self.rankings['quest_combo'] = max(all_quests, key=lambda q: (q.get('money', 0) / max_money) + (q.get('trainer_xp', 0) / max_xp))

        # Ranking de Candy Mais Caro (sem alteração)
        if self.loots_data:
             try:
                self.rankings['candy_price'] = max(self.loots_data.items(), key=lambda item: item[1].get('price', 0))
             except (ValueError, KeyError):
                self.rankings['candy_price'] = ('N/A', {'price': 0})
        
        # --- INÍCIO DA LÓGICA FINAL E CORRETA PARA COMUM E RARO ---
        pokemon_global_probability = {}
        
        for poke_name, spawn_list in self.spawn_rates.items():
            if not spawn_list or any("Anywhere" in spawn.get("condition", "") for spawn in spawn_list):
                continue

            # Etapa 1: Consolidar probabilidades por mapa
            map_probabilities = {}
            for spawn in spawn_list:
                condition = spawn.get("condition", "")
                if "Boss Rank" in condition or "Always Shiny" in condition:
                    continue
                
                rate = spawn.get("rate", 0)
                if rate > 0:
                    map_name = spawn['map']
                    probability = 1 / rate
                    map_probabilities[map_name] = map_probabilities.get(map_name, 0) + probability

            # Etapa 2: Calcular a probabilidade "global" somando as dos mapas
            if not map_probabilities:
                continue

            total_probability = sum(map_probabilities.values())
            
            if total_probability > 0:
                pokemon_global_probability[poke_name] = {
                    'prob': total_probability,
                    'maps': len(map_probabilities)
                }
                
        if pokemon_global_probability:
            # Etapa 3: Comparar as probabilidades globais
            # Mais Comum: Aquele com a maior probabilidade total
            most_common_name = max(pokemon_global_probability, key=lambda p: pokemon_global_probability[p]['prob'])
            common_data = pokemon_global_probability[most_common_name]
            # Convertendo de volta para o formato 1/X para exibição
            effective_rate_common = 1 / common_data['prob'] if common_data['prob'] > 0 else float('inf')
            self.rankings['most_common'] = (most_common_name, {'maps': common_data['maps'], 'rate': effective_rate_common})

            # Mais Raro: Aquele com a menor probabilidade total (maior que zero)
            most_rare_name = min(pokemon_global_probability, key=lambda p: pokemon_global_probability[p]['prob'])
            rare_data = pokemon_global_probability[most_rare_name]
            effective_rate_rare = 1 / rare_data['prob'] if rare_data['prob'] > 0 else float('inf')
            self.rankings['most_rare'] = (most_rare_name, {'maps': rare_data['maps'], 'rate': effective_rate_rare})

        # Adiciona Mew como um caso especial de raridade, pois ele é filtrado
        if 'Mew' in self.spawn_rates:
             self.rankings['most_rare'] = ('Mew', {'maps': 19, 'rate': 1000000.0})
        # --- FIM DA LÓGICA CORRIGIDA ---

    def run_comparison(self, pokemon_list):
        """ 
        Executa a lógica de comparação, agora com enumeração para identificar Pokémon iguais.
        """
        if not pokemon_list: return None
        
        final_form_species = self.get_true_final_form(pokemon_list[0]['species'])
        final_form_base_stats = self.pokemon_data[final_form_species]['base_stats']
        
        projections = []
        
        for i, p_user in enumerate(pokemon_list, 1):
            base_name = p_user.get('nickname') or p_user['species']
            display_name = f"{base_name} #{i}" if len(pokemon_list) > 1 else base_name
            
            final_stats = {}
            for stat in final_form_base_stats.keys():
                base_val = final_form_base_stats.get(stat, 0)
                final_stats[stat] = self._calculate_final_stat(
                    stat, base_val, 125, p_user['ivs'].get(stat,0), p_user['evs'].get(stat,0), p_user['nature']
                )

            tank_score = (final_stats.get('hp', 0) 
                          + final_stats.get('defense', 0) * 1.5 
                          + final_stats.get('special-defense', 0) * 1.5 
                          + final_stats.get('hp_reg', 0) * 1000)
                          
            attacker_score = (final_stats.get('attack', 0) * 1.5
                              + final_stats.get('special-attack', 0) * 1.5
                              + final_stats.get('energy', 0)
                              + final_stats.get('en_reg', 0) * 100)

            average_score = sum(final_stats.values())
            
            projections.append({
                'name': display_name,
                'tank_score': round(tank_score),
                'attacker_score': round(attacker_score),
                'average_score': round(average_score)
            })
        
        # CORREÇÃO: A estrutura de dados retornada foi ajustada para ser consistente e evitar o crash.
        best_tank_proj = max(projections, key=lambda p: p['tank_score'])
        best_attacker_proj = max(projections, key=lambda p: p['attacker_score'])
        best_average_proj = max(projections, key=lambda p: p['average_score'])
        
        results_list = [
            (self.get_string("comparison.archetype_tank"), {'name': best_tank_proj['name'], 'score': best_tank_proj['tank_score']}),
            (self.get_string("comparison.archetype_attacker"), {'name': best_attacker_proj['name'], 'score': best_attacker_proj['attacker_score']}),
            (self.get_string("comparison.archetype_average"), {'name': best_average_proj['name'], 'score': best_average_proj['average_score']})
        ]
        
        return results_list

    def get_true_final_form(self, pokemon_name):
        """ Navega para frente na linha evolutiva até encontrar a forma final. """
        evolution = EVOLUTIONS.get(pokemon_name)
        if not evolution:
            return pokemon_name
        
        # Se for multi-evo, consideramos a primeira como "padrão" para stats base
        if isinstance(evolution, list):
            evolution = evolution[0]
            
        return self.get_true_final_form(evolution)

    def get_string(self, key, default=""):
        lang = self.config.get('language', 'pt-br')
        lang_dict = self.translations.get(lang, self.translations.get('en-us', {}))
        
        keys = key.split('.')
        value = lang_dict
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            value_fallback = self.translations.get('en-us', {})
            try:
                for k in keys:
                    value_fallback = value_fallback[k]
                return value_fallback
            except (KeyError, TypeError):
                return default if default else key
            
    def get_sorted_pokemon_list(self):
        """
        A FONTE DA VERDADE. Retorna a lista de todos os nomes de Pokémon,
        respeitando a configuração de ordenação do usuário.
        """
        sort_mode = self.config.get("sort_order", "Ordem Alfabética")
        pokemon_names = list(self.pokedex_order.keys())

        if sort_mode == "Ordem da Pokédex":
            # A lista já está na ordem da Pokédex pelo pokemon_data.json
            return pokemon_names
        else: # Ordem Alfabética como padrão
            return sorted(pokemon_names)
        
    def update_all_pokemon_lists(self):
        """
        Avisa todas as abas relevantes para recarregarem suas listas de Pokémon
        com a nova ordenação.
        """
        # Atualiza as listas de seleção de Pokémon (ComboBoxes)
        self.collection_tab.update_pokemon_list()
        self.stats_calculator_tab.update_pokemon_list()
        self.ev_training_tab.update_pokemon_list()
        self.shiny_hunt_tab.update_pokemon_list()

        # Reordena as listas que exibem a coleção do usuário
        self.collection_tab.reload_and_sort_collection()
        self.team_analyzer_tab.update_collection()
        self.battle_planner_tab.update_collection()

    def _get_type_matchups(self, pokemon_name=None, p_types=None):
        if not p_types:
            if not pokemon_name:
                return {} # Retorna dicionário vazio se não tiver dados
            pokemon_info = self.pokemon_data.get(pokemon_name)
            if not pokemon_info:
                return {}
            p_types = list(filter(None, [pokemon_info.get("type1"), pokemon_info.get("type2")]))

        if not p_types:
            return {}

        # Vantagens (Ataque)
        advantages = set()
        for p_type in p_types:
            for opponent_type, multiplier in self.type_chart.get(p_type, {}).items():
                if multiplier > 1:
                    advantages.add(self.get_string(f"types.{opponent_type}", opponent_type))

        # --- NOVA LÓGICA DE DEFESA ---
        weaknesses = {} # Multiplicador > 1
        resistances = {} # 0 < Multiplicador < 1
        immunities = [] # Multiplicador == 0
        
        for attacking_type in self.type_chart.keys():
            multiplier = 1.0
            for p_type in p_types:
                multiplier *= self.type_chart[attacking_type].get(p_type, 1.0)
            
            type_name = self.get_string(f"types.{attacking_type}", attacking_type)
            if multiplier > 1:
                weaknesses[type_name] = multiplier
            elif 0 < multiplier < 1:
                resistances[type_name] = multiplier
            elif multiplier == 0:
                immunities.append(type_name)
        
        # Ordena os dicionários pelo valor do multiplicador (pior fraqueza/melhor resistência primeiro)
        sorted_weak = sorted(weaknesses.items(), key=lambda item: item[1], reverse=True)
        sorted_resist = sorted(resistances.items(), key=lambda item: item[1])

        return {
            "advantages": sorted(list(advantages)) or ["Nenhuma"],
            "weaknesses": [f"{name} (x{mult})" for name, mult in sorted_weak] or ["Nenhuma"],
            "resistances": [f"{name} (x{mult})" for name, mult in sorted_resist] or ["Nenhuma"],
            "immunities": sorted(immunities) or ["Nenhuma"]
        }


    def _calculate_final_stat(self, stat_name, base, level, iv, ev, nature):
        """
        Calcula os stats finais usando a LÓGICA DE SIMULAÇÃO DE LEVEL UP do Pokemon MMO 3D.
        Esta é a versão definitiva, que implementa os "Perfis de Crescimento" (com e sem nerf,
        rítmicos e lineares) descobertos e validados por Vega.
        """
        nature_mod = 1.0
        if nature_info := NATURES.get(nature):
            if nature_info.get('increase') == stat_name: nature_mod = 1.1
            elif nature_info.get('decrease') == stat_name: nature_mod = 0.9

        if stat_name == 'energy':
            base_energy_calc = (base * 2) + 50
            return math.floor(base_energy_calc + iv + (ev / 10))

        elif stat_name == 'hp':
            # --- PARTE 1: NÍVEIS ALTOS (>= 50) - FÓRMULA CORRIGIDA ---
            if level >= 50:
                base_calc = ((30 * base + 1500) * (level / 100.0)) + 75
                # CORREÇÃO: O bônus real começa a partir do IV 2.
                iv_calc = (iv - 1) * (0.15 * level) if iv > 0 else 0
                # CORREÇÃO: A fórmula de EV é mais simples.
                ev_calc = ev * (0.015 * level)
                return math.floor(base_calc + iv_calc + ev_calc)
            
            # --- PARTE 2: NÍVEIS BAIXOS (< 50) - SIMULAÇÃO COM REGRA UNIVERSAL ---
            else:
                current_hp = 0
                if base >= 250: current_hp = 165
                elif base >= 115: current_hp = 135
                elif base >= 100: current_hp = 120
                elif base >= 50: current_hp = 105
                else: current_hp = 90
                
                if level > 1:
                    profile = "DEFAULT"
                    if base < 50: profile = "BEGINNER_NERFED"
                    elif base == 60: profile = "RHYTHMIC_5"
                    elif base == 80: profile = "RHYTHMIC_COMPLEX"
                    elif base == 115: profile = "RHYTHMIC_3"
                    elif base == 160: profile = "RHYTHMIC_5_HEAVY"
                    elif base in [50, 250]: profile = "LINEAR"
                    
                    for i in range(2, level + 1):
                        growth_packet = 30 
                        if profile == "LINEAR":
                            if base == 50: growth_packet = 30
                            if base == 250: growth_packet = 90
                        elif profile == "RHYTHMIC_5":
                            growth_packet = 30
                            if i % 5 == 0: growth_packet = 45
                        elif profile == "RHYTHMIC_3":
                            cycle = (i - 2) % 3
                            growth_packet = 60 if cycle >= 2 else 45
                        elif profile == "RHYTHMIC_5_HEAVY":
                            growth_packet = 60
                            if i % 5 == 0: growth_packet = 75
                        elif profile == "RHYTHMIC_COMPLEX":
                            cycle = (i-2) % 4
                            growth_packet = 30 if cycle == 1 else 45
                        else: # DEFAULT e BEGINNER_NERFED
                            growth_packet = 45 if base >= 80 else 30
                        
                        # NOVO: REGRA UNIVERSAL DE NERF
                        if i in [11, 21, 31, 41]:
                            growth_packet -= 15

                        # Anomalias
                        if base == 35 and i == 4: growth_packet = 15 

                        current_hp += growth_packet

                iv_multiplier = 0
                if 1 <= level <= 3: iv_multiplier = 0.5
                elif 4 <= level <= 6: iv_multiplier = 1.0
                elif 7 <= level <= 10: iv_multiplier = 1.5
                elif 11 <= level <= 49: iv_multiplier = 2.0
                iv_calc = iv * iv_multiplier
                
                ev_calc = 0
                if level == 7 or (11 <= level <= 49):
                    ev_calc = ev * 0.5

                return math.floor(current_hp + iv_calc + ev_calc)

        elif stat_name in ['attack', 'defense', 'special-attack', 'special-defense', 'speed']:
            val = ((((2 * base) + iv + (ev / 10)) * level) / 100) + 5
            return math.floor(val * nature_mod)
            
        elif stat_name == 'hp_reg':
            ev_gain = (ev / 20) * 0.001
            return round((base / 100) + (iv / 1000) + ev_gain, 4)

        elif stat_name == 'en_reg':
            ev_gain = (ev / 20) * 0.001
            return round((base / 10) + (iv / 100) + ev_gain, 4)
            
        return base
    
    def _get_ev_yield_string(self, pokemon_name):
        """
        Lê o novo ev_data (V4) e retorna uma string formatada.
        """
        ev_data = self.ev_data.get(pokemon_name)
        if not ev_data:
            return self.get_string("globals.not_available", "N/A")

        # Mapeia as chaves internas para as chaves traduzidas da UI
        stat_label_map = {
            "hp": self.get_string('stats.hp'),
            "attack": self.get_string('stats.attack'),
            "defense": self.get_string('stats.defense'),
            "special-attack": self.get_string('stats.special-attack'),
            "special-defense": self.get_string('stats.special-defense'),
            "speed": self.get_string('stats.speed'),
            "energy": "EN", # O seu exemplo usa "EN", vamos manter
            "hp_reg": "HP Reg",
            "en_reg": "EN Reg"
        }
        
        parts = []
        for stat_key, value in ev_data.items():
            if value > 0:
                # Usa o mapa para obter o nome traduzido/curto
                stat_name = stat_label_map.get(stat_key, stat_key)
                parts.append(f"+{value} {stat_name}")
                
        if not parts:
            return self.get_string("globals.none", "Nenhum")
            
        return ", ".join(parts)

    def setup_ui(self, retranslating=False):
        if not retranslating:
            self.setWindowTitle(self.get_string("app_title") + " V2.0.1" + " by Vega")
            self.setGeometry(100, 100, 1200, 800)
            icon_path = resource_path('icon.ico')
            if os.path.exists(icon_path): self.setWindowIcon(QIcon(icon_path))
            self.tabs = QTabWidget()
            self.setCentralWidget(self.tabs)

        self.collection_tab = CollectionTab(self)
        self.stats_calculator_tab = StatsCalculatorTab(self)
        self.ev_training_tab = EVTrainingTab(self) 
        self.team_analyzer_tab = TeamAnalyzerTab(self)
        self.battle_planner_tab = BattlePlannerTab(self)
        self.pokedex_tab = PokedexTab(self)
        self.shiny_hunt_tab = ShinyHuntTab(self)
        self.settings_tab = SettingsTab(self)
        self.support_tab = SupportTab(self)

        pokebola_icon = get_icon_from_path(emojis.POKEBOLA)

        if pokebola_icon:
            self.tabs.addTab(self.collection_tab, pokebola_icon, self.get_string('tabs.collection'))
        else:
            self.tabs.addTab(self.collection_tab, self.get_string('tabs.collection'))
        self.tabs.addTab(self.stats_calculator_tab, f"{emojis.CAMERA} {self.get_string('tabs.ocr')}")
        self.tabs.addTab(self.ev_training_tab, f"{emojis.MUKI} {self.get_string('tabs.ev_yield')}")
        self.tabs.addTab(self.team_analyzer_tab, f"{emojis.CERÉBRAL} {self.get_string('tabs.teams')}")
        self.tabs.addTab(self.battle_planner_tab, f"{emojis.ESPADA} {self.get_string('tabs.bosses')}")
        self.tabs.addTab(self.pokedex_tab, pokebola_icon, self.get_string('tabs.pokedex', 'Pokédex'))
        self.tabs.addTab(self.shiny_hunt_tab, f"{emojis.SHINY} {self.get_string('tabs.shiny_hunt')}")
        self.tabs.addTab(self.settings_tab, f"{emojis.CONFIG} {self.get_string('tabs.settings')}")
        self.tabs.addTab(self.support_tab, f"{emojis.APOIO} {self.get_string('tabs.support')}")

    def get_true_base_form(self, pokemon_name):
        """Navega para trás na linha evolutiva até encontrar a forma mais básica."""
        pre_evo = self.reverse_evolutions.get(pokemon_name)
        if not pre_evo:
            return pokemon_name # Já é a forma base
        # Continua procurando para trás até não achar mais pré-evoluções
        return self.get_true_base_form(pre_evo)

    def _find_base_spawn_info_recursive(self, pokemon_name):
        """Busca recursivamente o mapa, voltando na linha evolutiva."""
        spawn_info = self.spawn_rates.get(pokemon_name)
        if spawn_info:
            return pokemon_name, spawn_info
        pre_evo = self.reverse_evolutions.get(pokemon_name)
        if pre_evo:
            return self._find_base_spawn_info_recursive(pre_evo)
        return None, None


    def get_pokedex_data(self, pokemon_name):
        """O método central que monta o 'dossiê' completo para a Pokédex."""
        pokemon_info = self.pokemon_data.get(pokemon_name)
        if not pokemon_info: return None

        data = {
            "species": pokemon_name,
            "image_path": get_pokemon_image_path(pokemon_name),
            "type1": pokemon_info.get("type1"),
            "type2": pokemon_info.get("type2"),
            "base_stats": pokemon_info.get("base_stats", {}),
            "family": self.get_evolution_family(pokemon_name)
        }

        base_pokemon_map, spawn_info = self._find_base_spawn_info_recursive(pokemon_name)
        
        if spawn_info:
            if base_pokemon_map != pokemon_name:
                data["location_name"] = self.get_string("pokedex.location_base_form").format(base_pokemon_map=base_pokemon_map)
            else:
                # CORREÇÃO: Usa chave de tradução
                data["location_name"] = self.get_string("pokedex.location_of").format(pokemon_name=pokemon_name)
            
            locations = []
            added_maps = set()
            for loc in spawn_info:
                map_name = loc.get("map")
                if map_name and map_name not in added_maps:
                    map_path = get_map_image_path(map_name)
                    if map_path:
                        locations.append({"name": map_name, "path": map_path})
                        added_maps.add(map_name)
            data["locations"] = locations
        else:
            data["location_name"] = self.get_string("pokedex.special_acquisition")
            data["locations"] = []
        
        return data
    
    def show_pokedex_for(self, pokemon_name):
        """Ponto de entrada único para abrir a Pokédex de qualquer lugar do app."""
        pokedex_data = self.get_pokedex_data(pokemon_name)
        if pokedex_data:
            dialog = PokedexDialog(pokedex_data, self) # Passa 'self' como parent
            dialog.exec()
        else:
            QMessageBox.warning(self, "Erro", f"Não foi possível encontrar dados para {pokemon_name}.")

    def connect_signals(self):
        self.collection_tab.collection_updated.connect(self.team_analyzer_tab.update_collection)
        self.collection_tab.collection_updated.connect(self.battle_planner_tab.update_collection)
        self.collection_tab.collection_updated.connect(self.ev_training_tab.update_my_pokemon_list)
        if OCR_ENABLED:
            self.stats_calculator_tab.send_to_collection.connect(self.add_ocr_pokemon_and_notify)
        self.settings_tab.theme_changed.connect(self.apply_theme)
        self.settings_tab.language_changed.connect(self.retranslate_ui)
        self.settings_tab.sort_preference_changed.connect(self.update_all_pokemon_lists)

    def _build_family_recursive(self, current_pokemon, family_set):
        """
        Função recursiva que explora todos os 'galhos' da árvore de evolução.
        Usa um 'set' para evitar adicionar o mesmo Pokémon duas vezes.
        """
        family_set.add(current_pokemon)
        
        evolutions = EVOLUTIONS.get(current_pokemon)
        if not evolutions:
            return # Fim da linha para este galho

        # Se for uma lista (ex: Eevee), chama a recursão para cada evolução
        if isinstance(evolutions, list):
            for evo in evolutions:
                if evo not in family_set: # Evita entrar em loops infinitos
                    self._build_family_recursive(evo, family_set)
        # Se for uma evolução única
        elif evolutions not in family_set:
            self._build_family_recursive(evolutions, family_set)

    # Substitua a sua função get_evolution_family antiga por esta
    def get_evolution_family(self, pokemon_name):
        """
        Monta a lista COMPLETA da família evolutiva, lidando com múltiplas
        evoluções e ramificações.
        """
        # 1. Encontra a forma mais básica da família
        base_form = self.get_true_base_form(pokemon_name)
        
        # 2. Usa a função recursiva para construir a árvore de evolução
        family_set = set()
        self._build_family_recursive(base_form, family_set)
        
        # 3. Tenta ordenar de uma forma lógica (pela ordem da Pokédex)
        # Isso ajuda a manter a ordem (ex: Bulbasaur, Ivysaur, Venusaur)
        sorted_family = sorted(list(family_set), key=lambda p: self.pokedex_order.get(p, 9999))
        
        return sorted_family

    def retranslate_ui(self):
        self.config = load_json("config.json", {"theme": "dark", "language": "pt-br"}, is_user_data=True)
        self.translations = load_json("translations.json")

        self.setWindowTitle(self.get_string("app_title") + " V2.0.1" + " by Vega")

        # Recria as abas complexas para garantir a tradução
        # Salva a aba que estava ativa
        current_index = self.tabs.currentIndex()

        # Desconecta sinais para evitar problemas durante a recriação
        self.collection_tab.collection_updated.disconnect()

        # Remove e deleta as abas antigas
        for i in range(self.tabs.count() -1, -1, -1):
            self.tabs.removeTab(i)

        self.collection_tab.deleteLater()
        self.stats_calculator_tab.deleteLater()
        self.ev_training_tab.deleteLater()
        self.team_analyzer_tab.deleteLater()
        self.battle_planner_tab.deleteLater()
        self.shiny_hunt_tab.deleteLater()
        self.settings_tab.deleteLater()
        self.support_tab.deleteLater()

        # Recria e readiciona todas as abas com o novo idioma
        self.setup_ui(retranslating=True)
        self.connect_signals()

        # Restaura a aba que estava ativa
        self.tabs.setCurrentIndex(current_index)

        QMessageBox.information(self, self.get_string("settings.language_change_title"), self.get_string("settings.language_change_text_success"))

    def load_settings_and_apply_theme(self):
        theme_key = self.config.get("theme", "dark")
        self.settings_tab.set_current_settings(self.config)
        self.apply_theme(theme_key)

    def apply_theme(self, theme_key):
        if theme_key == "dark": self.set_dark_theme()
        elif theme_key == "light": self.set_light_theme()
        elif theme_key == "pokemon": self.set_pokemon_theme()

    def set_dark_theme(self):
        self.setStyleSheet("""QWidget { background-color: #2b2b2b; color: #f0f0f0; border: none; } QTabWidget::pane { border-top: 2px solid #3c3c3c; } QTabBar::tab { background: #2b2b2b; color: #f0f0f0; padding: 10px; border: 1px solid #2b2b2b; } QTabBar::tab:selected { background: #3c3c3c; border-bottom: 2px solid #0078d7; } QPushButton { background-color: #3c3c3c; border: 1px solid #555; padding: 5px; border-radius: 3px; } QPushButton:hover { background-color: #4a4a4a; } QPushButton:pressed { background-color: #222222; } QPushButton:checked { background-color: #0078d7; border: 1px solid #005a9e; } QComboBox, QSpinBox, QLineEdit, QTextEdit { background-color: #3c3c3c; border: 1px solid #555; padding: 4px; border-radius: 3px; } QTableWidget { gridline-color: #444; background-color: #3c3c3c; } QHeaderView::section { background-color: #4a4a4a; border: 1px solid #555; padding: 4px; } QLabel { background-color: transparent; }""")

    def set_light_theme(self):
        self.setStyleSheet("""QWidget { background-color: #f0f0f0; color: #000000; border: none; } QTabWidget::pane { border-top: 2px solid #e1e1e1; } QTabBar::tab { background: #f0f0f0; color: #000000; padding: 10px; border: 1px solid #f0f0f0; } QTabBar::tab:selected { background: #e1e1e1; border-bottom: 2px solid #0078d7; } QPushButton { background-color: #e1e1e1; border: 1px solid #c0c0c0; padding: 5px; border-radius: 3px; } QPushButton:hover { background-color: #d4d4d4; } QPushButton:pressed { background-color: #c0c0c0; } QPushButton:checked { background-color: #0078d7; border: 1px solid #005a9e; color: white; } QComboBox, QSpinBox, QLineEdit, QTextEdit { background-color: #ffffff; border: 1px solid #c0c0c0; padding: 4px; border-radius: 3px; } QTableWidget { gridline-color: #dcdcdc; background-color: #ffffff; } QHeaderView::section { background-color: #e1e1e1; border: 1px solid #c0c0c0; padding: 4px; } QLabel { background-color: transparent; }""")

    def set_pokemon_theme(self):
        self.setStyleSheet("""QWidget { background-color: #d4e4ff; color: #1e2a3a; border: none; } QTabWidget::pane { border-top: 2px solid #3b5ca8; } QTabBar::tab { background: #a9c5ff; color: #1e2a3a; padding: 10px; border: 1px solid #a9c5ff; font-weight: bold; } QTabBar::tab:selected { background: #d4e4ff; border-bottom: 2px solid #ffcb05; } QPushButton { background-color: #ee1515; color: #ffffff; border: 2px solid #a30f0f; padding: 5px; border-radius: 5px; font-weight: bold; } QPushButton:hover { background-color: #c81010; } QPushButton:pressed { background-color: #a30f0f; } QPushButton:checked { background-color: #ffcb05; border: 2px solid #c7a008; color: #1e2a3a; } QComboBox, QSpinBox, QLineEdit, QTextEdit { background-color: #ffffff; border: 2px solid #3b5ca8; padding: 4px; border-radius: 5px; } QTableWidget { gridline-color: #a9c5ff; background-color: #ffffff; } QHeaderView::section { background-color: #3b5ca8; color: #ffcb05; border: 1px solid #2a4480; padding: 4px; font-weight: bold; } QLabel { background-color: transparent; }""")

    def add_ocr_pokemon_and_notify(self, data):
        self.collection_tab.add_pokemon_directly(data)
        self.tabs.setCurrentWidget(self.collection_tab)

    def closeEvent(self, event):
        if OCR_ENABLED and hasattr(self, 'stats_calculator_tab') and self.stats_calculator_tab.hotkey_listener:
            self.stats_calculator_tab.stop_listener()
        
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())