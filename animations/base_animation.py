import os
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import pyqtSignal, QUrl, QTimer

import sound_manager

try:
    from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
    SOUND_ENABLED = True
except ImportError:
    print("AVISO: Módulo QtMultimedia não encontrado. O som da evolução será desativado.")
    QMediaPlayer, QAudioOutput = None, None
    SOUND_ENABLED = False

class BaseEvolutionAnimation(QWidget):
    animationFinished = pyqtSignal()

    def __init__(self, pre_evo_pixmap: QPixmap, post_evo_pixmap: QPixmap, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.pre_evo_pixmap = pre_evo_pixmap
        self.post_evo_pixmap = post_evo_pixmap
        
        self.player = None
        self.audio_output = None
        self.sound_file_path = None
        self._setup_sound()

    def _setup_sound(self):
        if not SOUND_ENABLED:
            return
            
        # Pega a escolha do usuário do arquivo de config
        sound_name = self.parent_widget.config.get("evolution_sound", "Arpejo Chiptune")
        
        self.sound_file_path = sound_manager.get_sound_path(sound_name)
        if self.sound_file_path:
            self.player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.player.setAudioOutput(self.audio_output)
            self.player.setSource(QUrl.fromLocalFile(self.sound_file_path))
            self.audio_output.setVolume(0.5)

    def start_animation(self):
        if self.player and self.sound_file_path:
            self.player.play()
        self.show()

    def _finalize(self):
        """
        Método final chamado por todas as animações filhas.
        Emite o sinal e agenda a limpeza para logo depois.
        """
        self.animationFinished.emit()
        # Usamos um QTimer para garantir que o evento de fechar
        # aconteça depois que a pilha de eventos atual for processada.
        QTimer.singleShot(0, self.close)

    def closeEvent(self, event):
        """
        Garante que o player libere o arquivo ANTES de tentarmos deletá-lo.
        """
        if self.player:
            self.player.stop()
            self.player.setSource(QUrl()) # <-- Ponto chave: desassocia o arquivo do player
        
        try:
            if self.sound_file_path and os.path.exists(self.sound_file_path):
                os.remove(self.sound_file_path)
                # print(f"DEBUG: Arquivo de som {self.sound_file_path} deletado.")
        except Exception as e:
            print(f"AVISO: Não foi possível deletar o arquivo de som temporário: {e}")
        super().closeEvent(event)

