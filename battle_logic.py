import json
import os
import math
import re  # <-- NOVO: O Intérprete
import random # <-- NOVO: Para "chance to..."

# Dicionário de modificadores de Natureza (Mantido)
NATURES = {
    # ... (Natures permanecem iguais) ...
    'Lonely': {'increase': 'attack', 'decrease': 'defense'},
    'Adamant': {'increase': 'attack', 'decrease': 'special-attack'},
    'Naughty': {'increase': 'attack', 'decrease': 'special-defense'},
    'Brave': {'increase': 'attack', 'decrease': 'speed'},
    'Bold': {'increase': 'defense', 'decrease': 'attack'},
    'Impish': {'increase': 'defense', 'decrease': 'special-attack'},
    'Lax': {'increase': 'defense', 'decrease': 'special-defense'},
    'Relaxed': {'increase': 'defense', 'decrease': 'speed'},
    'Modest': {'increase': 'special-attack', 'decrease': 'attack'},
    'Mild': {'increase': 'special-attack', 'decrease': 'defense'},
    'Rash': {'increase': 'special-attack', 'decrease': 'special-defense'},
    'Quiet': {'increase': 'special-attack', 'decrease': 'speed'},
    'Calm': {'increase': 'special-defense', 'decrease': 'attack'},
    'Gentle': {'increase': 'special-defense', 'decrease': 'defense'},
    'Careful': {'increase': 'special-defense', 'decrease': 'special-attack'},
    'Sassy': {'increase': 'special-defense', 'decrease': 'speed'},
    'Timid': {'increase': 'speed', 'decrease': 'attack'},
    'Hasty': {'increase': 'speed', 'decrease': 'defense'},
    'Jolly': {'increase': 'speed', 'decrease': 'special-attack'},
    'Naive': {'increase': 'speed', 'decrease': 'special-defense'},
    'Hardy': {}, 'Docile': {}, 'Bashful': {}, 'Quirky': {}, 'Serious': {}
}

class BattleLogic:
    """
    VERSÃO 4.0 - O "Intérprete"
    Lê os dados raspados (moves_data_final e pokemon_learnsets_final)
    e usa RegEx para aplicar os efeitos reais dos golpes.
    """
    def __init__(self, pokemon_data, boss_data, type_chart, moves_data, learnsets_data):
        self.pokemon_data = pokemon_data
        self.boss_data = boss_data
        self.type_chart = type_chart
        self.moves_data = moves_data
        self.learnsets_data = learnsets_data # O "Grimório" (pokemon_learnsets.json)

        # --- Constantes da Simulação ---
        self.TICK_RATE = 0.1
        self.SIMULATION_TIMEOUT = 300.0
        self.POTION_COOLDOWN = 30.0
        self.POTION_HEAL_AMOUNT = 1500

        # --- ADICIONE ESTAS DUAS LINHAS DE VOLTA ---
        self.DEFAULT_ATTACK_COOLDOWN = 2.0 
        self.STATUS_MOVE_COOLDOWN = 10.0 # (A V3 usava isso, vamos manter por segurança)

        # --- NOVO (V4): O Motor RegEx de Efeitos ---
        self.STAT_MAP = {
            'att': 'attack', 'atk': 'attack', 'attack': 'attack',
            'def': 'defense', 'defense': 'defense',
            'sp. atk': 'special-attack', 'sp.att': 'special-attack',
            'sp. def': 'special-defense', 'sp.def': 'special-defense',
            'speed': 'speed'
        }
        
        # Mapeia os status do jogo para nossos debuffs internos
        self.STATUS_MAP = {
            'burn': 'burn', 'freeze': 'freeze', 'paralyze': 'paralysis',
            'poison': 'poison', 'sleep': 'sleep', 'flinch': 'flinch',
            'stun': 'flinch' # Stun e Flinch são funcionalmente idênticos
        }

    def calculate_stats(self, level, base_stats, ivs, evs, nature, rank=None):
        """
        Calcula os stats iniciais. (Mantida 100% igual à V3)
        """
        calculated_stats = {}
        nature_mods = NATURES.get(nature, {})
        for stat_name in ["attack", "defense", "special-attack", "special-defense", "speed"]:
            base = base_stats.get(stat_name, 0)
            iv = ivs.get(stat_name, 0)
            ev = evs.get(stat_name, 0)
            stat_val = math.floor(((((2 * base) + iv + (ev / 10)) * level) / 100) + 5)
            nature_mod = 1.0
            if nature_mods.get('increase') == stat_name: nature_mod = 1.1
            elif nature_mods.get('decrease') == stat_name: nature_mod = 0.9
            calculated_stats[stat_name] = math.floor(stat_val * nature_mod)
        
        base_hp = base_stats.get('hp', 0)
        iv_hp = ivs.get('hp', 0)
        ev_hp = evs.get('hp', 0)
        if level >= 50:
            base_calc = ((30 * base_hp + 1500) * (level / 100.0)) + 75
            iv_calc = (iv_hp - 1) * (0.15 * level) if iv_hp > 0 else 0
            ev_calc = ev_hp * (0.015 * level)
            calculated_stats['hp'] = math.floor(base_calc + iv_calc + ev_calc)
        else:
            current_hp = 0
            if base_hp >= 250: current_hp = 165
            elif base_hp >= 115: current_hp = 135
            elif base_hp >= 100: current_hp = 120
            elif base_hp >= 50: current_hp = 105
            else: current_hp = 90
            if level > 1:
                profile = "DEFAULT"
                if base_hp < 50: profile = "BEGINNER_NERFED"
                elif base_hp == 60: profile = "RHYTHMIC_5"
                elif base_hp == 80: profile = "RHYTHMIC_COMPLEX"
                elif base_hp == 115: profile = "RHYTHMIC_3"
                elif base_hp == 160: profile = "RHYTHMIC_5_HEAVY"
                elif base_hp in [50, 250]: profile = "LINEAR"
                for i in range(2, level + 1):
                    growth_packet = 30 
                    if profile == "LINEAR":
                        if base_hp == 50: growth_packet = 30
                        if base_hp == 250: growth_packet = 90
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
                    else: 
                        growth_packet = 45 if base_hp >= 80 else 30
                    if i in [11, 21, 31, 41]: growth_packet -= 15
                    if base_hp == 35 and i == 4: growth_packet = 15 
                    current_hp += growth_packet
            iv_multiplier = 0
            if 1 <= level <= 3: iv_multiplier = 0.5
            elif 4 <= level <= 6: iv_multiplier = 1.0
            elif 7 <= level <= 10: iv_multiplier = 1.5
            elif 11 <= level <= 49: iv_multiplier = 2.0
            iv_calc = iv_hp * iv_multiplier
            ev_calc = 0
            if level == 7 or (11 <= level <= 49):
                ev_calc = ev_hp * 0.5
            calculated_stats['hp'] = math.floor(current_hp + iv_calc + ev_calc)
        
        base_en = base_stats.get('energy', 0)
        iv_en = ivs.get('energy', 0)
        ev_en = evs.get('energy', 0)
        calculated_stats['energy'] = math.floor((base_en * 2) + 50 + iv_en + (ev_en / 10))
        base_hp_reg = base_stats.get('hp_reg', 0)
        iv_hp_reg = ivs.get('hp_reg', 0)
        ev_hp_reg = evs.get('hp_reg', 0)
        calculated_stats['hp_reg'] = round((base_hp_reg / 100) + (iv_hp_reg / 1000) + ((ev_hp_reg / 20) * 0.001), 4)
        base_en_reg = base_stats.get('en_reg', 0)
        iv_en_reg = ivs.get('en_reg', 0)
        ev_en_reg = evs.get('en_reg', 0)
        calculated_stats['en_reg'] = round((base_en_reg / 10) + (iv_en_reg / 100) + ((ev_en_reg / 20) * 0.001), 4)

        if rank is not None and rank > 0:
            boss_buff = rank * 100
            calculated_stats['defense'] += boss_buff
            calculated_stats['special-defense'] += boss_buff
            
        return calculated_stats

    # --- FUNÇÃO ATUALIZADA (V4) ---
    def _select_optimal_moveset(self, pokemon_species, pokemon_level, opponent_types):
        """
        O "ESTRATEGISTA" (V4).
        Lê o 'pokemon_learnsets.json' e filtra os golpes que o Pokémon
        realmente pode ter naquele nível.
        """
        # 1. Pega o "Grimório" do Pokémon
        move_list_data = self.learnsets_data.get(pokemon_species, [])
        if not move_list_data:
            return [] 

        # 2. Filtra pelo Nível
        # Pega todos os golpes que o Pokémon aprende ATÉ o seu nível atual
        available_moves = []

        for move_dict in move_list_data: 
            # Tenta pegar "level" (minúsculo) ou "Level" (maiúsculo)
            move_level = move_dict.get("level", move_dict.get("Level"))

            # Se encontrou um dos dois E o nível é válido
            if move_level is not None and move_level <= pokemon_level:
                available_moves.append(move_dict["move"])
        
        # 3. Remove duplicatas (ex: Growl Lvl 0 e Lvl 1)
        movepool = list(set(available_moves))

        # 4. A lógica de "scoring" (a mesma da V3, mas agora no movepool correto)
        scored_moves = []
        for move_name in movepool:
            move_info = self.moves_data.get(move_name)
            if not move_info:
                continue

            score = 0
            category = move_info.get("category")
            
            if category in ["Physical", "Special"]:
                score = 10
                move_type = move_info.get("type")
                type_multiplier = 1.0
                for def_type in opponent_types:
                    type_multiplier *= self.type_chart.get(move_type, {}).get(def_type, 1.0)
                
                if type_multiplier > 1: score = 50
                elif type_multiplier < 1 and type_multiplier > 0: score = 5
                elif type_multiplier == 0: score = 0
            
            elif category == "Status":
                # IA Burra: Por enquanto, só prioriza golpes de Status
                score = 40 
            
            if move_info.get("power", 0) > 0:
                score += (move_info.get("power", 0) / 10)

            scored_moves.append((score, move_name))

        scored_moves.sort(key=lambda x: x[0], reverse=True)
        optimal_moveset = [move_name for score, move_name in scored_moves[:6]]
        
        return optimal_moveset

    def _get_initial_state(self, entity_data, level, ivs, evs, nature, rank=None, moveset=[], potion_quantity=0):
        """(V4) Cria o objeto de estado 'vivo'."""
        
        species = entity_data["species"]
        base_stats = self.pokemon_data.get(species, {}).get("base_stats", {})
        initial_stats = self.calculate_stats(level, base_stats, ivs, evs, nature, rank)
        
        state = {
            'name': entity_data.get('nickname') or species,
            'species': species,
            'initial_stats': initial_stats,
            'current_hp': initial_stats['hp'],
            'current_energy': initial_stats['energy'],
            'types': list(filter(None, [
                self.pokemon_data.get(species, {}).get("type1"),
                self.pokemon_data.get(species, {}).get("type2")
            ])),
            'moveset': moveset, 
            'level': level,
            'potion_count': potion_quantity,
            # --- ATUALIZADO (V4) ---
            # Os buffs agora são valores, não "estágios"
            'buffs': { 
                'attack': {'value': 0, 'duration': 0.0},
                'defense': {'value': 0, 'duration': 0.0},
                'special-attack': {'value': 0, 'duration': 0.0},
                'special-defense': {'value': 0, 'duration': 0.0},
                'speed': {'value': 0, 'duration': 0.0},
            },
            'debuffs': {
                # 'poison': {'damage': 50, 'duration': 10.0}
            },
            'cooldowns': { 
                # O cooldown agora é lido do moves_data.json
                # 'Tackle': 4.0 
            }
        }
        return state

    def _update_timers(self, state):
        """(V4) Reduz todos os timers."""
        
        # Cooldowns de Golpes
        for move_name in list(state['cooldowns'].keys()):
            if state['cooldowns'][move_name] > 0:
                state['cooldowns'][move_name] -= self.TICK_RATE
            if state['cooldowns'][move_name] <= 0:
                del state['cooldowns'][move_name] # Remove do dict quando o CD acabar

        # Cooldown da Poção
        if 'potion' in state['cooldowns']:
             if state['cooldowns']['potion'] > 0:
                state['cooldowns']['potion'] -= self.TICK_RATE
             if state['cooldowns']['potion'] <= 0:
                del state['cooldowns']['potion']

        # Buffs
        for stat_name in state['buffs']:
            if state['buffs'][stat_name]['duration'] > 0:
                state['buffs'][stat_name]['duration'] -= self.TICK_RATE
                if state['buffs'][stat_name]['duration'] <= 0:
                    state['buffs'][stat_name]['value'] = 0 # Buff expirou
        
        # Debuffs (ex: DoT)
        for debuff_name in list(state['debuffs'].keys()):
            if state['debuffs'][debuff_name]['duration'] > 0:
                state['debuffs'][debuff_name]['duration'] -= self.TICK_RATE
                if state['debuffs'][debuff_name]['duration'] <= 0:
                    del state['debuffs'][debuff_name] # Debuff expirou

    def _apply_regen_and_debuffs(self, state, tick_counter):
        """(V4) Aplica regeneração e dano de debuff (ex: a cada 1 segundo)."""
        if tick_counter % 10 != 0: # Roda 1x por segundo (10 ticks de 0.1s)
            return

        # 1. Regeneração
        hp_gain = state['initial_stats']['hp_reg']
        en_gain = state['initial_stats']['en_reg']
        state['current_hp'] = min(state['initial_stats']['hp'], state['current_hp'] + hp_gain)
        state['current_energy'] = min(state['initial_stats']['energy'], state['current_energy'] + en_gain)

        # 2. Debuffs (ex: Poison)
        if 'poison' in state['debuffs']:
            damage = state['debuffs']['poison']['damage']
            state['current_hp'] -= damage
        if 'leech_seed' in state['debuffs']:
            damage = state['debuffs']['leech_seed']['damage']
            state['current_hp'] -= damage
            # (Aqui poderíamos adicionar a cura ao oponente, se quiséssemos)

    def _get_smarter_ai_action(self, attacker, defender, use_potions_logic):
        """
        (V4) IA atualizada para simplesmente priorizar "Status" > "Dano".
        """
        
        # 1. PRIORIDADE MÁXIMA: CURA
        if use_potions_logic and attacker['potion_count'] > 0 and 'potion' not in attacker['cooldowns']:
            hp_percent = (attacker['current_hp'] / attacker['initial_stats']['hp']) * 100
            if hp_percent < 30.0:
                return 'use_potion', None

        # 2. PRIORIDADE: BUFFS (Se CD pronto)
        for move_name in attacker['moveset']:
            move_info = self.moves_data.get(move_name, {})
            if (move_info.get("category") == "Status" and 
                move_name not in attacker['cooldowns'] and
                attacker['current_energy'] >= move_info.get("cost", 0)):
                
                # IA "Burra" V4: assume que qualquer buff vale a pena se não estiver ativo
                # (Precisamos de uma IA V5 para ler a descrição e ser mais inteligente)
                is_buffed = any(b['duration'] > 0 for b in attacker['buffs'].values())
                if not is_buffed:
                    return 'use_move', move_name 

        # 3. PRIORIDADE: ATAQUE (Se CD pronto)
        best_damage_move = None
        best_damage = -1

        for move_name in attacker['moveset']:
            move_info = self.moves_data.get(move_name, {})
            if (move_info.get("category") in ["Physical", "Special"] and
                move_name not in attacker['cooldowns'] and
                attacker['current_energy'] >= move_info.get("cost", 0)):
                
                # Lógica de "scoring" (a mesma da V3)
                damage = move_info.get("power", 0)
                move_type = move_info.get("type")
                type_multiplier = 1.0
                for def_type in defender['types']:
                    type_multiplier *= self.type_chart.get(move_type, {}).get(def_type, 1.0)
                
                final_potential_damage = damage * type_multiplier

                if final_potential_damage > best_damage:
                    best_damage = final_potential_damage
                    best_damage_move = move_name

        if best_damage_move:
            return 'use_move', best_damage_move

        return 'wait', None

    # --- FUNÇÃO ATUALIZADA (V4) ---
    def _apply_action(self, attacker_state, defender_state, action_type, move_name, log_callback):
        """
        O "INTÉRPRETE" (V4).
        Aplica o resultado de uma ação lendo os dados do moves_data.json.
        """
        
        if action_type == 'wait':
            return

        if action_type == 'use_potion':
            attacker_state['current_hp'] = min(
                attacker_state['initial_stats']['hp'],
                attacker_state['current_hp'] + self.POTION_HEAL_AMOUNT
            )
            attacker_state['cooldowns']['potion'] = self.POTION_COOLDOWN
            attacker_state['potion_count'] -= 1 # <-- ADICIONE ESTA LINHA
            log_callback(f"{attacker_state['name']} usou Potion. Restam {attacker_state['potion_count']}.") # <-- LINHA ATUALIZADA
            return

        if action_type == 'use_move':
            move_info = self.moves_data.get(move_name)
            if not move_info:
                return

            # Deduz o custo de energia
            attacker_state['current_energy'] -= move_info.get("cost", 0)
            
            # Coloca o golpe em Cooldown
            attacker_state['cooldowns'][move_name] = move_info.get("cooldown", self.DEFAULT_ATTACK_COOLDOWN)

            # --- AÇÃO: MOVIMENTO DE DANO (PHYSICAL/SPECIAL) ---
            if move_info.get("category") in ["Physical", "Special"]:
                
                # 1. Pega os Stats (com buffs)
                if move_info["category"] == "Physical":
                    attack_stat_name = 'attack'; defense_stat_name = 'defense'
                else: 
                    attack_stat_name = 'special-attack'; defense_stat_name = 'special-defense'

                attack_stat = attacker_state['initial_stats'][attack_stat_name] + attacker_state['buffs'][attack_stat_name]['value']
                defense_stat = defender_state['initial_stats'][defense_stat_name] + defender_state['buffs'][defense_stat_name]['value']
                
                # 2. Multiplicador de Tipo
                type_multiplier = 1.0
                move_type = move_info.get("type")
                for def_type in defender_state['types']:
                    type_multiplier *= self.type_chart.get(move_type, {}).get(def_type, 1.0)
                
                if move_name == "Freeze-Dry" and "Water" in defender_state['types']:
                    type_multiplier = 2.0
                
                # 3. Fórmula de Dano (Usa o Power real do JSON)
                level = attacker_state['level']
                move_power = move_info.get("power", 50)
                
                # Fórmula de dano padrão (simplificada)
                damage = (((((2 * level / 5) + 2) * move_power * (attack_stat / (defense_stat or 1))) / 50) + 2) * type_multiplier
                
                # 4. Aplica o dano
                defender_state['current_hp'] -= damage
                log_callback(f"{attacker_state['name']} usou {move_name} e causou {int(damage)} de dano!")
                
                # 5. Aplica Efeitos Secundários (ex: Absorb)
                self._parse_and_apply_effect(move_name, move_info.get("description", ""), attacker_state, defender_state, log_callback, damage_dealt=damage)
                return

            # --- AÇÃO: MOVIMENTO DE STATUS (BUFF/DEBUFF) ---
            elif move_info.get("category") == "Status":
                log_callback(f"{attacker_state['name']} usou {move_name}!")
                self._parse_and_apply_effect(move_name, move_info.get("description", ""), attacker_state, defender_state, log_callback)
                return

    # --- NOVA FUNÇÃO (V4) ---
    def _parse_and_apply_effect(self, move_name, description, attacker, defender, log_callback, damage_dealt=0):
        """
        O Motor RegEx. Lê a descrição do golpe e aplica o efeito.
        Esta função é o coração da V4 e é onde adicionaremos mais lógicas.
        """
        
        # --- Lógica 1: Buffs/Debuffs baseados em Nível (ex: Swords Dance, Growl) ---
        # "Increase your attack by (0.75 * level) for 15s."
        # "Reduces the enemy's Atk and Sp. Atk by (0.5 x level) while inside."
        
        # Padrão RegEx para: "Increase/Reduces" + "your/enemy's" + "Stats" + "by (VALOR * level)" + "for DURAÇÃOs"
        pattern = re.compile(
            r"(Increase[s]?|Reduces) (your|the enemy's) ([\w\s.]+) by \(([\d\.]+) \× level\) ... ([\d\.]+)s", 
            re.IGNORECASE
        )
        match = pattern.search(description)
        
        if match:
            action = match.group(1).lower()
            target_str = match.group(2).lower()
            stats_str = match.group(3).lower()
            multiplier = float(match.group(4))
            duration = float(match.group(5))
            
            # Define o alvo (self ou oponente)
            target_state = attacker if target_str == 'your' else defender
            
            # Calcula o valor do buff/debuff
            value = int(multiplier * attacker['level'])
            if action == 'reduces':
                value = -value # É um debuff
            
            # Encontra todos os stats mencionados (ex: "Atk and Sp. Atk")
            for stat_key, internal_name in self.STAT_MAP.items():
                if stat_key in stats_str:
                    target_state['buffs'][internal_name]['value'] = value
                    target_state['buffs'][internal_name]['duration'] = duration
                    log_callback(f"  -> {move_name} aplicou um buff/debuff de {value} em {internal_name} por {duration}s!")
            return

        # --- Lógica 2: Buff/Debuff com % de chance (ex: Acid) ---
        # "25% chance to lower target's special defense by (25 + (0.25 x level)) for 10 seconds."
        pattern_chance = re.compile(
            r"(\d+)% chance to (lower|raise) target's ([\w\s.]+) by \(([\d\.]+) \+ \(([\d\.]+) x level\)\) for (\d+) seconds",
            re.IGNORECASE
        )
        match_chance = pattern_chance.search(description)
        
        if match_chance:
            chance = int(match_chance.group(1))
            
            # Rola o dado
            if random.randint(1, 100) <= chance:
                action = match_chance.group(2).lower()
                stats_str = match_chance.group(3).lower()
                base_val = float(match_chance.group(4))
                multiplier = float(match_chance.group(5))
                duration = float(match_chance.group(6))
                
                value = int(base_val + (multiplier * attacker['level']))
                if action == 'lower':
                    value = -value
                
                for stat_key, internal_name in self.STAT_MAP.items():
                    if stat_key in stats_str:
                        defender['buffs'][internal_name]['value'] = value
                        defender['buffs'][internal_name]['duration'] = duration
                        log_callback(f"  -> {move_name} ativou o efeito! Debuff de {value} em {internal_name} por {duration}s!")
                return

        # --- Lógica 3: Drenar Vida (ex: Absorb) ---
        # "Drains the target's life, healing 50% of the damage dealt."
        if 'healing 50% of the damage dealt' in description.lower():
            heal_amount = int(damage_dealt * 0.5)
            attacker['current_hp'] = min(attacker['initial_stats']['hp'], attacker['current_hp'] + heal_amount)
            log_callback(f"  -> {move_name} drenou {heal_amount} HP!")
            return

        # --- Lógica 4: Status (ex: Poison Sting, Ember) ---
        # "30% chance to poison."
        # "10% chance on hit to burn."
        pattern_status = re.compile(r"(\d+)% chance .* to (poison|burn|freeze|paralyze|sleep|flinch|stun)", re.IGNORECASE)
        match_status = pattern_status.search(description)
        
        if match_status:
            chance = int(match_status.group(1))
            status_name = match_status.group(2).lower()
            
            if random.randint(1, 100) <= chance:
                debuff_key = self.STATUS_MAP.get(status_name)
                if debuff_key:
                    # Lógica de DoT (Dano por Tempo)
                    if debuff_key == 'poison':
                        defender['debuffs']['poison'] = {'damage': 50, 'duration': 10.0} # Chute, precisamos da descrição do "Poison"
                        log_callback(f"  -> {move_name} ativou o efeito! {defender['name']} está envenenado!")
                    # (Adicionar lógica para paralysis, freeze, etc. aqui)
                return

    # --- FUNÇÃO ATUALIZADA (V4) ---
    def run_simulation(self, p_user_data, boss_name, use_potions, manual_moveset=None, potion_quantity=0):
        """
        Executa a simulação (V4).
        Se 'manual_moveset' for fornecido, usa ele.
        Senão, usa o "Estrategista" para escolher os golpes.
        """
        
        battle_log = []
        current_time = 0.0 # Define current_time no escopo mais alto
        
        def log_action(message):
            battle_log.append(f"[{int(current_time)}s] {message}")

        boss_info_json = self.boss_data.get(boss_name)
        boss_pokemon_data = self.pokemon_data.get(boss_name)
        if not boss_info_json or not boss_pokemon_data:
            return {'error': 'Boss data not found.', 'log': []}
        
        boss_types = list(filter(None, [boss_pokemon_data.get("type1"), boss_pokemon_data.get("type2")]))
        
        p_user_level = p_user_data['level']

        if manual_moveset:
            p_moves = manual_moveset
            log_action("Usando Moveset Manual.")
        else:
            # --- O ESTRATEGISTA ENTRA EM AÇÃO ---
            p_moves = self._select_optimal_moveset(p_user_data['species'], p_user_level, boss_types)
            if not p_moves:
                 return {'error': f"Nenhum golpe encontrado no 'learnsets.json' para {p_user_data['species']} no Nível {p_user_level}.", 'log': []}
            log_action(f"Moveset Otimizado do Player: {', '.join(p_moves)}")
        
        # Pega os golpes do boss direto do boss_data.json
        boss_moves_list = boss_info_json.get("moveset", [])
        # Filtra a lista para ter certeza que todos os golpes existem no nosso moves_data
        boss_moves = [move for move in boss_moves_list if move in self.moves_data]

        boss_level = boss_info_json.get("level", 100)
        max_ev = 2000 + (max(0, boss_level - 100) * 100)
        boss_ivs = {stat: 31 for stat in boss_pokemon_data.get("base_stats", {}).keys()}
        boss_evs = {stat: max_ev for stat in boss_pokemon_data.get("base_stats", {}).keys()}
        
        player_state = self._get_initial_state(
            entity_data=p_user_data,
            level=p_user_level,
            ivs=p_user_data['ivs'],
            evs=p_user_data['evs'],
            nature=p_user_data['nature'],
            moveset=p_moves,
            potion_quantity=potion_quantity
        )
        
        boss_state = self._get_initial_state(
            entity_data={'species': boss_name},
            level=boss_level,
            ivs=boss_ivs,
            evs=boss_evs,
            nature="Hardy",
            rank=boss_info_json.get("rank"),
            moveset=boss_moves
        )

        # --- O GAME LOOP (V4) ---
        tick_counter = 0
        
        while (player_state['current_hp'] > 0 and 
               boss_state['current_hp'] > 0 and
               current_time < self.SIMULATION_TIMEOUT):
            
            self._update_timers(player_state)
            self._update_timers(boss_state)
            
            self._apply_regen_and_debuffs(player_state, tick_counter)
            self._apply_regen_and_debuffs(boss_state, tick_counter)

            player_action_type, player_move = self._get_smarter_ai_action(player_state, boss_state, use_potions)
            boss_action_type, boss_move = self._get_smarter_ai_action(boss_state, player_state, False)

            self._apply_action(player_state, boss_state, player_action_type, player_move, log_action)
            if boss_state['current_hp'] <= 0:
                break
                
            self._apply_action(boss_state, player_state, boss_action_type, boss_move, log_action)
            if player_state['current_hp'] <= 0:
                break

            current_time += self.TICK_RATE
            tick_counter += 1

        # --- FIM DA SIMULAÇÃO ---
        if player_state['current_hp'] <= 0:
            winner = "boss"
            log_action(f"--- {player_state['name']} foi derrotado! ---")
        elif boss_state['current_hp'] <= 0:
            winner = "player"
            log_action(f"--- {boss_state['name']} foi derrotado! ---")
        else:
            winner = "timeout"
            log_action(f"--- A batalha atingiu o tempo limite! ---")
            
        return {
            'winner': winner,
            'time_elapsed': current_time,
            'player_final_hp_percent': (player_state['current_hp'] / player_state['initial_stats']['hp']) * 100,
            'boss_final_hp_percent': (boss_state['current_hp'] / boss_state['initial_stats']['hp']) * 100,
            'log': battle_log,
            'used_moveset': p_moves 
        }