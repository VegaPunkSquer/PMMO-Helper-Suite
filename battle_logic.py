import json
import os
import math

# Dicionário de modificadores de Natureza
NATURES = {
    # +Attack
    'Lonely': {'increase': 'attack', 'decrease': 'defense'},
    'Adamant': {'increase': 'attack', 'decrease': 'special-attack'},
    'Naughty': {'increase': 'attack', 'decrease': 'special-defense'},
    'Brave': {'increase': 'attack', 'decrease': 'speed'},
    # +Defense
    'Bold': {'increase': 'defense', 'decrease': 'attack'},
    'Impish': {'increase': 'defense', 'decrease': 'special-attack'},
    'Lax': {'increase': 'defense', 'decrease': 'special-defense'},
    'Relaxed': {'increase': 'defense', 'decrease': 'speed'},
    # +Special Attack
    'Modest': {'increase': 'special-attack', 'decrease': 'attack'},
    'Mild': {'increase': 'special-attack', 'decrease': 'defense'},
    'Rash': {'increase': 'special-attack', 'decrease': 'special-defense'},
    'Quiet': {'increase': 'special-attack', 'decrease': 'speed'},
    # +Special Defense
    'Calm': {'increase': 'special-defense', 'decrease': 'attack'},
    'Gentle': {'increase': 'special-defense', 'decrease': 'defense'},
    'Careful': {'increase': 'special-defense', 'decrease': 'special-attack'},
    'Sassy': {'increase': 'special-defense', 'decrease': 'speed'},
    # +Speed
    'Timid': {'increase': 'speed', 'decrease': 'attack'},
    'Hasty': {'increase': 'speed', 'decrease': 'defense'},
    'Jolly': {'increase': 'speed', 'decrease': 'special-attack'},
    'Naive': {'increase': 'speed', 'decrease': 'special-defense'},
    # Neutras
    'Hardy': {}, 'Docile': {}, 'Bashful': {}, 'Quirky': {}, 'Serious': {}
}

class BattleLogic:
    """
    Encapsula toda a lógica de cálculo de stats e simulação de batalhas.
    Recebe os dados necessários em seu construtor, tornando-a independente do sistema de arquivos.
    """
    def __init__(self, pokemon_data, boss_data, type_chart, moves_data):
        # Recebe os dados em vez de carregá-los
        self.pokemon_data = pokemon_data
        self.boss_data = boss_data
        self.type_chart = type_chart
        self.moves_data = moves_data
        
        # Constantes de Simulação
        self.BASE_BOSS_DAMAGE_MULTIPLIER = 1.6
        self.BASE_PLAYER_DAMAGE_CALIBRATION = 0.225
        self.AVERAGE_MOVE_POWER = 85
        self.ATTACK_INTERVAL = 2.0
        
        self.BOSS_SPECIFIC_MODIFIERS = {
            "Entei":    {"boss": 1.65, "player": 0.65},
            "Ho-Oh":    {"boss": 1.65, "player": 0.65},
            "Articuno": {"boss": 0.85, "player": 0.95},
        }

    def calculate_stats(self, level, base_stats, ivs, evs, nature, rank=None):
        """Calcula os stats de um Pokémon com base em seus atributos."""
        calculated_stats = {}
        nature_mods = NATURES.get(nature, {})

        for stat_name in ["attack", "defense", "special-attack", "special-defense", "speed", "energy", "hp_reg", "en_reg"]:
            base = base_stats.get(stat_name, 0)
            iv = ivs.get(stat_name, 0)
            ev = evs.get(stat_name, 0)
            stat_val = math.floor(((((2 * base) + iv + (ev / 10)) * level) / 100) + 5)
            
            nature_mod = 1.0
            for mod_stat, value in nature_mods.items():
                if mod_stat == stat_name:
                    nature_mod = value
            
            calculated_stats[stat_name] = math.floor(stat_val * nature_mod)

        base_hp = base_stats.get('hp', 0)
        iv_hp = ivs.get('hp', 0)
        ev_hp = evs.get('hp', 0)
        hp_from_stats = math.floor(((((2 * base_hp + iv_hp) * level) / 100) + level + 10))
        hp_from_evs = math.floor((ev_hp / 10) * 15)
        calculated_stats['hp'] = hp_from_stats + hp_from_evs
        
        if rank is not None and rank > 0:
            boss_buff = rank * 100
            calculated_stats['defense'] += boss_buff
            calculated_stats['special-defense'] += boss_buff
            
        return calculated_stats

    def _calculate_damage_per_hit(self, attacker_stats, defender_stats, attacker_level, defender_level, attacker_types, defender_types, attacker_moveset=None):
        """Calcula o dano médio de um único golpe."""
        attack_stat = max(attacker_stats.get('attack', 0), attacker_stats.get('special-attack', 0))
        defense_stat = defender_stats.get('defense', 1) if attack_stat == attacker_stats.get('attack', 0) else defender_stats.get('special-defense', 1)
        
        # --- SEU CÓDIGO ORIGINAL PARA CALCULAR O MULTIPLICADOR (ESTÁ PERFEITO) ---
        type_multiplier = 1.0
        if attacker_types:
            best_mult = 0
            for att_type in attacker_types:
                current_mult = 1.0
                for def_type in defender_types:
                    current_mult *= self.type_chart.get(att_type, {}).get(def_type, 1.0)
                best_mult = max(best_mult, current_mult)
            type_multiplier = best_mult if best_mult > 0 else 1.0
        
        # --- NOSSA NOVA REGRA ESPECIAL VAI AQUI, DEPOIS DO CÁLCULO NORMAL ---
        # Verificamos se o atacante TEM o golpe Freeze-Dry e se o defensor é do tipo Água
        if attacker_moveset and "Freeze-Dry" in attacker_moveset and "Water" in defender_types:
            # Se a condição for verdadeira, a gente ignora o multiplicador calculado antes
            # e CRAVA o valor em 2.0, porque essa é a regra especial do golpe.
            type_multiplier = 4.0
        # --- FIM DA REGRA ESPECIAL ---
        
        # --- CÁLCULO FINAL DO DANO (COMO ANTES) ---
        damage = (((((2 * attacker_level / 5) + 2) * self.AVERAGE_MOVE_POWER * (attack_stat / (defense_stat or 1))) / 50) + 2) * type_multiplier
        return damage

    def simulate_battle(self, p_user, boss_name, p_level=None, p_ivs=None, p_evs=None, p_nature=None):
        """Simula uma batalha 1v1 entre um Pokémon do usuário e um Boss."""
        p_data = self.pokemon_data.get(p_user["species"])
        boss_info = self.boss_data.get(boss_name)
        boss_data = self.pokemon_data.get(boss_name)
        if not all([p_data, boss_info, boss_data]): return None

        level = p_level if p_level is not None else p_user["level"]
        ivs = p_ivs if p_ivs is not None else p_user["ivs"]
        evs = p_evs if p_evs is not None else p_user["evs"]
        nature = p_nature if p_nature is not None else p_user["nature"]
        user_stats = self.calculate_stats(level, p_data["base_stats"], ivs, evs, nature)
        
        boss_level = boss_info.get("level", 100)
        max_ev = 2000 + (max(0, boss_level - 100) * 100)
        boss_ivs = {stat: 31 for stat in boss_data["base_stats"].keys()}
        boss_evs = {stat: max_ev for stat in boss_data["base_stats"].keys()}
        boss_rank = boss_info.get("rank")
        boss_stats = self.calculate_stats(boss_level, boss_data["base_stats"], boss_ivs, boss_evs, "Hardy", rank=boss_rank)

        if user_stats['hp'] <= 0: return None

        p_types = list(filter(None, [p_data.get("type1"), p_data.get("type2")]))
        boss_types = list(filter(None, [boss_data.get("type1"), boss_data.get("type2")]))
        
        boss_mods = self.BOSS_SPECIFIC_MODIFIERS.get(boss_name, {"boss": 1.0, "player": 1.0})
        final_boss_dmg_multiplier = self.BASE_BOSS_DAMAGE_MULTIPLIER * boss_mods["boss"]
        final_player_dmg_calibration = self.BASE_PLAYER_DAMAGE_CALIBRATION * boss_mods["player"]

        p_moves = [] 
        user_damage_per_hit = self._calculate_damage_per_hit(user_stats, boss_stats, level, boss_level, p_types, boss_types, p_moves)
        user_dps = (user_damage_per_hit * final_player_dmg_calibration) / self.ATTACK_INTERVAL

        boss_moveset = boss_info.get("moveset", [])
        boss_damage_per_hit = self._calculate_damage_per_hit(boss_stats, user_stats, boss_level, level, boss_types, p_types, boss_moveset)
        boss_dps = (boss_damage_per_hit * final_boss_dmg_multiplier) / self.ATTACK_INTERVAL
        
        user_dps += 1e-9
        boss_dps += 1e-9

        time_to_win = boss_stats['hp'] / user_dps
        time_to_faint = user_stats['hp'] / boss_dps
        
        battle_index = time_to_faint / time_to_win

        return {
            "pokemon": p_user, 
            "battle_index": battle_index,
            "ttf": time_to_faint,
        }

    def calculate_team_win_probability(self, battle_indices):
        """Calcula a probabilidade de vitória de um TIME com base em uma LISTA de battle_index."""
        if not battle_indices:
            return 0.0

        valid_indices = [idx for idx in battle_indices if idx > 0]
        if not valid_indices:
            return 0.0
        
        num_pokemon = len(valid_indices)
        team_geo_mean = math.prod(valid_indices) ** (1.0 / num_pokemon)

        team_win_prob = (team_geo_mean / (team_geo_mean + 1.5)) * 100

        return min(100.0, team_win_prob)
