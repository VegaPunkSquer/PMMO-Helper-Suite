from PyQt6.QtWidgets import QLabel, QGraphicsOpacityEffect
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QSequentialAnimationGroup
from .base_animation import BaseEvolutionAnimation

class CrossfadeAnimation(BaseEvolutionAnimation):
    """
    Animação de crossfade polida, com efeito de alternância entre as formas.
    """
    def __init__(self, pre_evo_pixmap: QPixmap, post_evo_pixmap: QPixmap, parent=None):
        super().__init__(pre_evo_pixmap, post_evo_pixmap, parent)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.85);")
        
        if parent:
            self.setGeometry(parent.rect())

        self.pre_evo_label = self._create_label(self.pre_evo_pixmap)
        self.post_evo_label = self._create_label(self.post_evo_pixmap)
        
        self.pre_evo_opacity = QGraphicsOpacityEffect(opacity=1.0)
        self.pre_evo_label.setGraphicsEffect(self.pre_evo_opacity)
        
        self.post_evo_opacity = QGraphicsOpacityEffect(opacity=0.0)
        self.post_evo_label.setGraphicsEffect(self.post_evo_opacity)

    def _create_label(self, pixmap):
        label = QLabel(self)
        label.setPixmap(pixmap)
        label.setScaledContents(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("background: transparent;")
        if self.parent_widget:
            parent_size = self.parent_widget.size()
            width = int(parent_size.width() / 3.5)
            x = (parent_size.width() - width) // 2
            y = (parent_size.height() - width) // 2
            label.setGeometry(x, y, width, width)
        return label

    def start_animation(self):
        # Chama o start_animation da classe base para tocar o som
        super().start_animation()
        
        # Sequência principal que vai rodar tudo
        main_sequence = QSequentialAnimationGroup(self)
        
        # --- LÓGICA DE ALTERNÂNCIA ---
        num_alternations = 5 # Total de "piscadas" entre as formas
        duration_per_fade = 250 # Duração de cada fade in/out

        for i in range(num_alternations):
            is_final_fade = (i == num_alternations - 1)
            
            fading_in_opacity = self.post_evo_opacity if i % 2 == 0 else self.pre_evo_opacity
            fading_out_opacity = self.pre_evo_opacity if i % 2 == 0 else self.post_evo_opacity
            
            current_duration = duration_per_fade * 3 if is_final_fade else duration_per_fade
            
            fade_group = QParallelAnimationGroup()

            anim_in = QPropertyAnimation(fading_in_opacity, b"opacity")
            anim_in.setDuration(current_duration)
            anim_in.setStartValue(0.0)
            anim_in.setEndValue(1.0)
            anim_in.setEasingCurve(QEasingCurve.Type.InOutSine)

            anim_out = QPropertyAnimation(fading_out_opacity, b"opacity")
            anim_out.setDuration(current_duration)
            anim_out.setStartValue(1.0)
            anim_out.setEndValue(0.0)
            anim_out.setEasingCurve(QEasingCurve.Type.InOutSine)

            fade_group.addAnimation(anim_in)
            fade_group.addAnimation(anim_out)
            
            main_sequence.addAnimation(fade_group)

        main_sequence.addPause(800) # Pausa final para ver o resultado
        main_sequence.finished.connect(self.on_animation_complete)
        main_sequence.start()

    def on_animation_complete(self):
        self.animationFinished.emit()
        self.close()

