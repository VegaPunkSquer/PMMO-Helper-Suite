from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup, QRect
)
from .base_animation import BaseEvolutionAnimation

class ClassicFlashAnimation(BaseEvolutionAnimation):
    """
    Animação de 'pisca-pisca', agora 100% corrigida: sem fundo preto, com flash real
    e fechando corretamente no final.
    """
    def __init__(self, pre_evo_pixmap: QPixmap, post_evo_pixmap: QPixmap, parent=None):
        super().__init__(pre_evo_pixmap, post_evo_pixmap, parent)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.75);")
        
        if parent:
            self.setGeometry(parent.rect())

        self.container = QWidget(self)
        self.container.setStyleSheet("background: transparent;") # <-- Correção do fundo preto

        self.pokemon_label = QLabel(self.container)
        self.pokemon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pokemon_label.setScaledContents(True)
        self.pokemon_label.setStyleSheet("background: transparent;")

        self.flash_overlay = QWidget(self.container)
        self.flash_overlay.setStyleSheet("background-color: white;")
        self.flash_overlay.setFixedSize(0,0)

        self.resize_and_center_widgets()

    def start_animation(self):
        # Toca o som da classe base
        super().start_animation()
        
        self.pokemon_label.setPixmap(self.pre_evo_pixmap)
        
        self.main_sequence = QSequentialAnimationGroup(self)

        strobe_sequence = self._create_strobe_effect(4, 80)
        transform_sequence = self._create_transform_effect()

        self.main_sequence.addAnimation(strobe_sequence)
        self.main_sequence.addAnimation(transform_sequence)
        self.main_sequence.addPause(100)
        
        # O truque está aqui: agora tudo está numa única sequência
        # A troca de imagem acontece como um evento DENTRO da sequência
        self.main_sequence.addPause(10).finished.connect(self._swap_pixmap_and_flash)
        
        self.main_sequence.start()

    def _swap_pixmap_and_flash(self):
        self.pokemon_label.setPixmap(self.post_evo_pixmap)
        self.resize_and_center_widgets()
        
        climax_sequence = QSequentialAnimationGroup(self)
        
        flash_anim = QPropertyAnimation(self.flash_overlay, b"geometry")
        flash_anim.setDuration(150)
        flash_anim.setStartValue(QRect(0,0,0,0))
        flash_anim.setEndValue(self.pokemon_label.rect())
        flash_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        flash_hide = QPropertyAnimation(self.flash_overlay, b"geometry")
        flash_hide.setDuration(1)
        flash_hide.setStartValue(self.pokemon_label.rect())
        flash_hide.setEndValue(QRect(0,0,0,0))
        
        fade_out = QPropertyAnimation(self, b"windowOpacity")
        fade_out.setDuration(400)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)

        climax_sequence.addAnimation(flash_anim)
        climax_sequence.addPause(200)
        climax_sequence.addAnimation(flash_hide)
        climax_sequence.addPause(500)
        climax_sequence.addAnimation(fade_out) # Fade-out agora faz parte do final
        
        climax_sequence.finished.connect(self._finalize)
        climax_sequence.start()

    def _create_strobe_effect(self, flashes, duration):
        # ... (implementação completa aqui)
        group = QSequentialAnimationGroup(self)
        for _ in range(flashes):
            flash_on = QPropertyAnimation(self.flash_overlay, b"geometry")
            flash_on.setDuration(duration // 2)
            flash_on.setStartValue(QRect(0,0,0,0))
            flash_on.setEndValue(self.pokemon_label.rect())
            
            flash_off = QPropertyAnimation(self.flash_overlay, b"geometry")
            flash_off.setDuration(duration // 2)
            flash_off.setStartValue(self.pokemon_label.rect())
            flash_off.setEndValue(QRect(0,0,0,0))
            
            group.addAnimation(flash_on)
            group.addAnimation(flash_off)
        return group
        
    def _create_transform_effect(self):
        # ... (implementação completa aqui)
        group = QSequentialAnimationGroup(self)
        original_geom = self.pokemon_label.geometry()
        
        for _ in range(3):
            anim1 = QPropertyAnimation(self.pokemon_label, b"geometry")
            anim1.setDuration(75)
            anim1.setStartValue(original_geom)
            anim1.setEndValue(original_geom.adjusted(-10, -10, 10, 10))
            anim1.setEasingCurve(QEasingCurve.Type.InOutQuad)

            anim2 = QPropertyAnimation(self.pokemon_label, b"geometry")
            anim2.setDuration(75)
            anim2.setStartValue(original_geom.adjusted(-10, -10, 10, 10))
            anim2.setEndValue(original_geom)
            anim2.setEasingCurve(QEasingCurve.Type.InOutQuad)
            
            group.addAnimation(anim1)
            group.addAnimation(anim2)
        return group

    def _finalize(self):
        self.animationFinished.emit()
        self.close()

    def resize_and_center_widgets(self):
        if not self.parent(): return
        parent_size = self.parent().size()
        container_size = int(parent_size.width() / 3.5)
        
        x = (parent_size.width() - container_size) // 2
        y = (parent_size.height() - container_size) // 2
        
        self.container.setGeometry(x, y, container_size, container_size)
        self.pokemon_label.setGeometry(0, 0, container_size, container_size)
        self.flash_overlay.setGeometry(self.pokemon_label.rect())
        
    def resizeEvent(self, event):
        if self.parent_widget:
            self.setGeometry(self.parent_widget.rect())
            self.resize_and_center_widgets()
        super().resizeEvent(event)

