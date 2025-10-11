from PyQt6.QtWidgets import QLabel, QGraphicsOpacityEffect
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QPoint, QTimer
from .base_animation import BaseEvolutionAnimation

class SlideFadeAnimation(BaseEvolutionAnimation):
    """
    Uma animação moderna onde o Pokémon antigo desliza para fora
    enquanto a evolução desliza para dentro.
    """
    def __init__(self, pre_evo_pixmap: QPixmap, post_evo_pixmap: QPixmap, parent=None):
        super().__init__(pre_evo_pixmap, post_evo_pixmap, parent)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.8);")
        
        if parent:
            self.setGeometry(parent.rect())

        self.pre_evo_label = self._create_label(self.pre_evo_pixmap)
        self.post_evo_label = self._create_label(self.post_evo_pixmap)
        
        self.pre_evo_opacity = QGraphicsOpacityEffect(opacity=1.0)
        self.pre_evo_label.setGraphicsEffect(self.pre_evo_opacity)
        
        self.post_evo_opacity = QGraphicsOpacityEffect(opacity=0.0)
        self.post_evo_label.setGraphicsEffect(self.post_evo_opacity)

        geom = self.post_evo_label.geometry()
        geom.moveLeft(self.width())
        self.post_evo_label.setGeometry(geom)

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

        self.animation_group = QParallelAnimationGroup(self)
        
        center_x = self.pre_evo_label.x()
        
        slide_out = QPropertyAnimation(self.pre_evo_label, b"pos")
        slide_out.setDuration(1200)
        slide_out.setStartValue(self.pre_evo_label.pos())
        slide_out.setEndValue(self.pre_evo_label.pos() - QPoint(self.width() // 2, 0))
        slide_out.setEasingCurve(QEasingCurve.Type.InCubic)
        
        fade_out = QPropertyAnimation(self.pre_evo_opacity, b"opacity")
        fade_out.setDuration(1200)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)

        slide_in = QPropertyAnimation(self.post_evo_label, b"pos")
        slide_in.setDuration(1200)
        slide_in.setStartValue(self.post_evo_label.pos())
        slide_in.setEndValue(QPoint(center_x, self.post_evo_label.y()))
        slide_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        fade_in = QPropertyAnimation(self.post_evo_opacity, b"opacity")
        fade_in.setDuration(1200)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        
        self.animation_group.addAnimation(slide_out)
        self.animation_group.addAnimation(fade_out)
        self.animation_group.addAnimation(slide_in)
        self.animation_group.addAnimation(fade_in)
        
        self.animation_group.finished.connect(self.on_animation_complete)
        self.animation_group.start()
        
    def on_animation_complete(self):
        QTimer.singleShot(500, self._finalize)

    def _finalize(self):
        self.animationFinished.emit()
        self.close()

