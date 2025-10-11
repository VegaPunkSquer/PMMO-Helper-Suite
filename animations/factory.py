from .classic_flash import ClassicFlashAnimation
from .crossfade import CrossfadeAnimation
from .slide_and_fade import SlideFadeAnimation # <-- Importa a nova animação

# O nosso catálogo de animações disponíveis
# É AQUI que a gente registra uma nova animação para ela aparecer nas Configurações
ANIMATION_CATALOG = {
    "Flash Clássico": ClassicFlashAnimation,
    "Crossfade Suave": CrossfadeAnimation,
    "Slide and Fade": SlideFadeAnimation # <-- Adiciona a nova opção
}

def get_animation_class(animation_name: str):
    """
    Retorna a classe de animação correspondente ao nome.
    Se o nome não for encontrado, retorna a animação padrão (ClassicFlash).
    """
    return ANIMATION_CATALOG.get(animation_name, ClassicFlashAnimation)

def get_available_animations():
    """Retorna uma lista com os nomes de todas as animações disponíveis."""
    return list(ANIMATION_CATALOG.keys())