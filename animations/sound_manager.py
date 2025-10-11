import wave
import math
import struct
import tempfile
import os
import sys

# --- FUNÇÃO AUXILIAR ---
def _clamp(value, min_val=-32768, max_val=32767):
    """Garante que o valor da amostra de áudio esteja dentro do limite de 16-bit."""
    return max(min_val, min(value, max_val))

# --- GERADORES DE SOM INDIVIDUAIS ---

def _generate_chiptune_arpeggio():
    """O som original, estilo Game Boy. Funciona bem."""
    sample_rate = 22050
    duration_ms = 1800
    start_freq, end_freq = 220.0, 880.0
    steps, volume = 48, 0.25
    wav_data = bytearray()
    num_samples_per_step = int((duration_ms / steps) * (sample_rate / 1000))

    for i in range(steps):
        progress = i / (steps - 1)
        current_freq = start_freq * math.pow(end_freq / start_freq, progress)
        for j in range(num_samples_per_step):
            value = math.sin(2.0 * math.pi * current_freq * (float(j) / sample_rate))
            amplitude = 32767 * volume if value > 0 else -32768 * volume
            wav_data.extend(struct.pack('<h', int(amplitude)))
    return wav_data, sample_rate

def _generate_synth_swell():
    """Um som mais suave e moderno, agora corrigido."""
    sample_rate = 22050
    duration_s = 2.2
    start_freq, end_freq = 280.0, 560.0 # Um pouco mais grave
    volume = 0.5
    wav_data = bytearray()
    num_samples = int(duration_s * sample_rate)

    for i in range(num_samples):
        progress = i / num_samples
        envelope = math.sin(progress * math.pi) # Envelope de volume (fade in/out)
        current_freq = start_freq + (end_freq - start_freq) * (progress ** 2) # Acelera a subida
        
        value = math.sin(2.0 * math.pi * current_freq * (float(i) / sample_rate))
        amplitude = 32767 * volume * envelope
        wav_data.extend(struct.pack('<h', int(_clamp(amplitude)))) # <-- CORREÇÃO: Clamp
    return wav_data, sample_rate

def _generate_sci_fi_powerup():
    """Um som com vibrato, agora corrigido e mais audível."""
    sample_rate = 22050
    duration_s = 2.0
    base_freq = 400.0
    vibrato_depth, vibrato_rate = 15.0, 8.0
    volume = 0.4
    wav_data = bytearray()
    num_samples = int(duration_s * sample_rate)

    for i in range(num_samples):
        t = float(i) / sample_rate
        vibrato = vibrato_depth * math.sin(2.0 * math.pi * vibrato_rate * t)
        current_freq = base_freq + vibrato
        envelope = (1.0 - (i / num_samples)) ** 2 # Fade out mais suave
        
        value = math.sin(2.0 * math.pi * current_freq * t)
        amplitude = 32767 * volume * envelope
        wav_data.extend(struct.pack('<h', int(_clamp(amplitude)))) # <-- CORREÇÃO: Clamp
    return wav_data, sample_rate

def _generate_experimental_sound():
    """
    UMA BASE PARA VOCÊ BRINCAR, VEGA!
    Copie esta função, renomeie (ex: _meu_som_incrivel) e altere os valores abaixo.
    Depois, adicione o nome no SOUND_CATALOG no final deste arquivo.
    """
    # --- PARÂMETROS PARA VOCÊ MUDAR ---
    sample_rate = 22050     # Qualidade do som. 22050 é bom.
    duration_s = 2.5        # Duração em segundos.
    volume = 0.4            # Volume (de 0.0 a 1.0).
    start_freq = 800.0      # Frequência inicial (tom). Mais alto = mais agudo.
    end_freq = 200.0        # Frequência final. Aqui, o som vai de agudo para grave.
    vibrato_rate = 20.0     # Velocidade da vibração. Tente 5, 10, 20. 0 para desligar.
    vibrato_depth = 10.0    # "Força" da vibração. Tente 5, 15, 30. 0 para desligar.
    # --- FIM DOS PARÂMETROS ---

    wav_data = bytearray()
    num_samples = int(duration_s * sample_rate)
    for i in range(num_samples):
        t = float(i) / sample_rate
        progress = i / num_samples
        
        # Frequência principal (desce de start para end)
        main_freq = start_freq - (start_freq - end_freq) * progress
        # Modulação de vibração
        vibrato = vibrato_depth * math.sin(2.0 * math.pi * vibrato_rate * t)
        current_freq = main_freq + vibrato
        # Envelope de volume (fade out)
        envelope = (1.0 - progress) ** 1.5

        value = math.sin(2.0 * math.pi * current_freq * t)
        amplitude = 32767 * volume * envelope
        wav_data.extend(struct.pack('<h', int(_clamp(amplitude))))
    return wav_data, sample_rate


# --- FÁBRICA DE SONS ---
SOUND_CATALOG = {
    "Arpejo Chiptune": _generate_chiptune_arpeggio,
    "Synth Suave": _generate_synth_swell,
    "Poder Sci-Fi": _generate_sci_fi_powerup,
    "Som Experimental": _generate_experimental_sound # <-- SEU NOVO SOM!
}

def get_available_sounds():
    """Retorna uma lista com os nomes de todos os sons disponíveis."""
    return list(SOUND_CATALOG.keys())

def get_sound_path(sound_name: str):
    generator_func = SOUND_CATALOG.get(sound_name, _generate_chiptune_arpeggio)
    wav_data, sample_rate = generator_func()
    
    try:
        fd, temp_path = tempfile.mkstemp(suffix='.wav')
        os.close(fd)
        with wave.open(temp_path, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(wav_data)
        return temp_path
    except Exception as e:
        print(f"ERRO ao gerar arquivo de som temporário: {e}")
        return None