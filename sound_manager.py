import numpy as np
import wave
import os
import tempfile
import math
import struct

# --- FUNÇÃO AUXILIAR ---
def _clamp(value, min_val=-32768, max_val=32767):
    """Garante que o valor da amostra de áudio esteja dentro do limite de 16-bit."""
    return max(min_val, min(value, max_val))

# --- O Cérebro do Som: Constantes ---
SAMPLE_RATE = 44100  # Qualidade de CD
AMPLITUDE = 16383    # Volume máximo para áudio 16-bit (metade de 32767 para evitar clipping)
MAX_AMPLITUDE = 32767.0 
# CONTROLE DE VOLUME GLOBAL (0.0 = mudo, 0.5 = 50%, 1.0 = máximo)
# Para o som ficar mais baixo, diminua este número. Tente 0.25 ou 0.3.
MASTER_VOLUME = 0.4 

# --- FÁBRICA DE SONS ---
# Cada função aqui é uma "receita" para um som diferente.
# Sinta-se à vontade para copiar, colar e experimentar com os valores!

def _create_classic_gb_sound(duration_s=2.0):
    """
    Uma recriação mais fiel do som de evolução do Game Boy.
    Combina uma onda quadrada, uma subida de tom exponencial e um vibrato rápido.

    TUTORIAL PARA VOCÊ, VEGA:
    - pitch_rise_speed: Altere este valor. Números maiores (ex: 4.0) fazem o tom subir mais rápido no final.
    - vibrato_rate: Velocidade da "oscilação". 30 é rápido e intenso. Tente 15 para algo mais lento.
    - vibrato_depth: "Força" da oscilação. Aumente para deixar o som mais "caótico".
    """
    num_samples = int(SAMPLE_RATE * duration_s)
    t = np.linspace(0, duration_s, num_samples, endpoint=False)

    # 1. A subida de tom (Pitch)
    start_freq = 100.0  # Começa bem grave
    end_freq = 500.0  # Termina bem agudo
    pitch_rise_speed = 3.0 # Controla a curva (mais alto = mais rápido no final)

    progress = t / duration_s
    base_freq = start_freq + (end_freq - start_freq) * (progress ** pitch_rise_speed)

    # 2. A modulação (Vibrato/Wobble)
    vibrato_rate = 19.0  # Hz - a velocidade da oscilação
    vibrato_depth = 50.0 * (1 - progress) # A força da oscilação diminui com o tempo
    lfo_wave = vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t)

    # 3. Combina o tom principal com o vibrato
    instant_freq = base_freq + lfo_wave

    # Calcula a fase correta para a frequência variável e gera a onda
    phase = np.cumsum(2 * np.pi * instant_freq / SAMPLE_RATE)

    # 4. O Timbre (Onda Quadrada) - a essência do som de Game Boy
    # Usamos np.sign(np.sin(...)) para criar uma onda quadrada perfeita
    raw_wave = np.sign(np.sin(phase))

    return raw_wave

def _create_synth_sound(duration_s=2.2):
    num_samples = int(SAMPLE_RATE * duration_s)
    t = np.linspace(0, duration_s, num_samples, endpoint=False)
    
    # Duas frequências que "desafinam" ligeiramente para criar um efeito de 'chorus'
    freq1 = 280.0
    freq2 = 282.0
    
    wave1 = np.sin(2 * np.pi * freq1 * t)
    wave2 = np.sin(2 * np.pi * freq2 * t)
    
    # Misturamos as ondas
    raw_wave = 0.6 * wave1 + 0.4 * wave2
    return raw_wave

def _create_scifi_sound(duration_s=2.0):
    num_samples = int(SAMPLE_RATE * duration_s)
    t = np.linspace(0, duration_s, num_samples, endpoint=False)

    start_freq, end_freq = 400.0, 1200.0
    instant_freq = np.linspace(start_freq, end_freq, num_samples)
    
    # Adiciona um vibrato (outra onda senoidal modulando a frequência)
    vibrato_rate = 7.0
    vibrato_depth = 15.0
    vibrato_wave = vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t)
    
    final_freq = instant_freq + vibrato_wave
    
    # A integral da frequência para obter a fase correta
    phase = np.cumsum(final_freq / SAMPLE_RATE)
    raw_wave = np.sin(2 * np.pi * phase)
    return raw_wave

def _generate_experimental_sound(duration_s=2.5): # <-- AGORA ACEITA duration_s
    """
    UMA BASE PARA VOCÊ BRINCAR, VEGA! (Versão modernizada com NumPy)
    Copie esta função, renomeie (ex: _meu_som_incrivel) e altere os valores abaixo.
    Depois, adicione o nome no SOUND_CATALOG no final deste arquivo.
    """
    # --- PARÂMETROS PARA VOCÊ MUDAR ---
    # sample_rate = 44100  # Pega o SAMPLE_RATE global, não precisa definir aqui
    # duration_s = 2.5    # Agora vem como argumento da função
    # volume = 0.4        # O volume agora é controlado pelo MASTER_VOLUME global
    start_freq = 800.0      # Frequência inicial (tom). Mais alto = mais agudo.
    end_freq = 200.0        # Frequência final. Aqui, o som vai de agudo para grave.
    vibrato_rate = 20.0     # Velocidade da vibração. Tente 5, 10, 20. 0 para desligar.
    vibrato_depth = 10.0    # "Força" da vibração. Tente 5, 15, 30. 0 para desligar.
    envelope_power = 1.5    # Controla a curva do fade out. 1.0 = linear, >1.0 = mais rápido.
    # --- FIM DOS PARÂMETROS ---

    num_samples = int(SAMPLE_RATE * duration_s)
    t = np.linspace(0, duration_s, num_samples, endpoint=False)
    progress = t / duration_s
    
    # Frequência principal (desce de start para end)
    main_freq = start_freq - (start_freq - end_freq) * progress
    # Modulação de vibração
    vibrato = vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t)
    current_freq = main_freq + vibrato
    # Envelope de volume (fade out)
    envelope = (1.0 - progress) ** envelope_power

    # Gera a fase e a onda senoidal
    phase = np.cumsum(2 * np.pi * current_freq / SAMPLE_RATE)
    raw_wave = np.sin(phase) * envelope
    
    return raw_wave

# --- O Catálogo de Sons ---
SOUND_CATALOG = {
    "Clássico (Game Boy)": (_create_classic_gb_sound, 2.0),
    "Synth Suave": (_create_synth_sound, 2.2),
    "Poder Sci-Fi": (_create_scifi_sound, 2.0),
    "Som Experimental": (_generate_experimental_sound, 2.5) 
}

def get_available_sounds():
    """Retorna uma lista com os nomes de todos os sons disponíveis."""
    return list(SOUND_CATALOG.keys())

def get_sound_path(sound_name: str):
    """
    Gera o som de evolução escolhido, aplica um envelope para evitar cliques,
    e o salva em um arquivo WAV temporário.
    """
    sound_function, duration_s = SOUND_CATALOG.get(sound_name, SOUND_CATALOG["Clássico (Game Boy)"])

    raw_wave = sound_function(duration_s)
    
    # --- O ANTÍDOTO PARA O "ESTALO" ---
    num_samples = len(raw_wave)
    fade_len = int(SAMPLE_RATE * 0.05) # 50ms de fade
    
    if fade_len * 2 > num_samples:
        fade_len = num_samples // 4
        
    fade_in = np.linspace(0.0, 1.0, fade_len)
    fade_out = np.linspace(1.0, 0.0, fade_len)
    
    # Aplica o envelope
    raw_wave[:fade_len] *= fade_in
    raw_wave[-fade_len:] *= fade_out
    
    # Normaliza a onda para o volume máximo e converte para 16-bit
    scaled_wave = np.int16((raw_wave / np.max(np.abs(raw_wave))) * MAX_AMPLITUDE * MASTER_VOLUME)
    
    try:
        fd, temp_path = tempfile.mkstemp(suffix='.wav')
        os.close(fd)
        with wave.open(temp_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(scaled_wave.tobytes())
        return temp_path
    except Exception as e:
        print(f"ERRO ao gerar arquivo de som temporário: {e}")
        return None