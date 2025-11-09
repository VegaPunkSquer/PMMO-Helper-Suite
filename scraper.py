import requests
import json
from bs4 import BeautifulSoup
import time
import re
import os

# Dependências
try:
    from selenium import webdriver
    # --- MUDANÇA V12: USANDO OS IMPORTS CORRETOS DO EDGE (SELENIUM 4) ---
    from selenium.webdriver.edge.service import Service as EdgeService
    from selenium.webdriver.edge.options import Options as EdgeOptions
    
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("ERRO: Bibliotecas do Selenium não encontradas.")
    print("Verifique se o 'selenium' (V4+) está instalado: pip install selenium")
    exit()


# --- DICIONÁRIOS DE MAPEAMENTO (DE-PARA) ---
# (Corretos)
ICON_TO_TYPE_MAP = {
    "6c061079a43344d5826f9a86794ad4a4": "Fairy",
    "2fb32479e62d4d0b8e85f4e918fd4891": "Poison",
    "ddae14342f19491ea0d509cd90f68935": "Bug",
    "d36e1e7c8d68411494802059862c6bd7": "Steel",
    "51c5eed7e07b475f89b0974ab0a8c2b0": "Dragon",
    "116edacb79c34169a0174e84e4d93b2c": "Normal",
    "871995d0ddb646279cc36ae78ab2604e": "Ice",
    "b3a4f3633f114e91bedbf909c014174b": "Rock",
    "afe73bdebbcc44e5b66959bf98b6391b": "Flying",
    "4c38c892b68641a1bc28e2b213efa33a": "Psychic",
    "5f6d44d95a434d4292e3195cd7766e70": "Electric",
    "9478c0184eab430497b3ad164008a0de": "Ghost",
    "ae373bccacda432785f0c43f98078994": "Dark",
    "21d4626586164e4b8d636b2c9c47a022": "Ground",
    "f40ccba1863b4cd2aab9f4b77643f7e8": "Water",
    "b483758e851b442585ed2d171b264e0b": "Fighting",
    "a8132a118ac448cfa7a856c76132ae07": "Fire",
    "e1d2c06b397e46be949f490557f0fa33": "Grass"
}
PHYSICAL_ICON_HASH = "e460ceefd9a949debd406848c5eb3034"
SPECIAL_ICON_HASH = "e9305b89d9664444b93cbff863a75953"

# --- FUNÇÕES DO SCRAPER (Sem mudanças na lógica de parse) ---

def get_move_list(driver, list_url):
    print(f"Buscando lista de golpes em {list_url}...")
    try:
        driver.get(list_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="wiki/attacks/"]'))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        move_links = {} 
        table_bodies = soup.find_all('tbody', class_='VUpDdz')
        if not table_bodies:
            print("ERRO: Nenhuma tabela de golpes encontrada na 'attacks-list'.")
            return None

        for table in table_bodies:
            links = table.select('a[data-testid="linkElement"][href*="wiki/attacks/"]')
            for link in links:
                name = link.text.strip()
                slug = link.get('href', '').split('/')[-1]
                if name and slug and not name.isdigit():
                    move_links[name] = slug
        
        if not move_links:
             print("ERRO: Tabelas encontradas, mas nenhum link de golpe válido.")
             return None

        print(f"Encontrados {len(move_links)} golpes. Iniciando raspagem individual...")
        return move_links
    except Exception as e:
        print(f"ERRO CRÍTICO: Falha ao buscar lista de golpes. {e}")
        return None

def parse_move_stats_table(table_body):
    try:
        cols = table_body.find('tr').find_all('td')
        
        category_icon_src = cols[1].find('img')['src'] if cols[1].find('img') else ''
        type_icon_src = cols[2].find('img')['src'] if cols[2].find('img') else ''
        
        move_type = "Unknown"
        for hash_key, type_name in ICON_TO_TYPE_MAP.items():
            if hash_key in type_icon_src:
                move_type = type_name
                break
        
        power_str = cols[3].text.strip()
        power = int(power_str) if power_str.isdigit() else 0
        
        cooldown_str = cols[4].text.strip()
        cooldown = float(cooldown_str) if cooldown_str else 0.0
        
        range_str = cols[5].text.strip()
        range_val = int(range_str) if range_str.isdigit() else 0
        
        energy_str = cols[6].text.strip()
        energy = int(energy_str) if energy_str.isdigit() else 0
        
        duration_str = cols[7].text.strip()
        duration = float(duration_str) if duration_str else 0.0
        
        multiplier_str = cols[8].text.strip()
        multiplier = float(multiplier_str) if multiplier_str else 0.0

        category = "Unknown"
        if power == 0:
            category = "Status"
        elif PHYSICAL_ICON_HASH in category_icon_src:
            category = "Physical"
        elif SPECIAL_ICON_HASH in category_icon_src:
            category = "Special"
        else:
            category = "Physical" 

        return {
            "type": move_type, "category": category, "power": power, "cost": energy,
            "cooldown": cooldown, "range": range_val, "duration": duration, "multiplier": multiplier
        }
    except Exception as e:
        print(f"    -> Aviso: Falha ao ler linha da tabela de stats. O JS pode não ter carregado. {e}")
        return None

def parse_pokemon_learn_table(table_body):
    pokemon_list = []
    try:
        rows = table_body.find_all('tr', class_='UhXTve')
        for row in rows:
            cols = row.find_all('td', class_='VG9vCO')
            
            level_str = cols[0].text.strip()
            level = int(level_str) if level_str.isdigit() else 0
            
            pokemon_name = cols[2].text.strip()
            in_game = cols[9].text.strip()

            if pokemon_name and in_game.lower() == 'yes':
                pokemon_list.append({ "pokemon": pokemon_name, "level": level })
        return pokemon_list
    except Exception as e:
        print(f"    -> Aviso: Falha ao ler linha da tabela 'Pokemon that can learn'. {e}")
        return []

def scrape_move_page(driver, move_name, slug):
    url = f"https://pmmo3d.wixsite.com/wiki/attacks/{slug}"
    
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//tbody/tr/td[10]"))
        )
        time.sleep(0.2) 

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        move_data = None
        learned_by = []
        desc_tag = soup.find('div', id='comp-m9t1bcdl')
        description = desc_tag.text.strip() if desc_tag else ""
        all_table_bodies = soup.find_all('tbody', class_='VUpDdz')
        
        if not all_table_bodies:
            print("    -> Aviso: Nenhuma tabela (tbody) encontrada na página.")
            return None, []

        for tbody in all_table_bodies:
            first_row = tbody.find('tr')
            if not first_row: continue
            
            columns = first_row.find_all('td')
            num_cols = len(columns)

            if num_cols == 9:
                move_data = parse_move_stats_table(tbody)
            elif num_cols == 10:
                learned_by = parse_pokemon_learn_table(tbody)
        
        if move_data:
            move_data['description'] = description
            
        return move_data, learned_by
    except Exception as e:
        print(f"  -> ERRO de Selenium/timeout para {move_name}: {e}. Pulando.")
        return None, []

def invert_learnsets(learnsets_by_move):
    print("\nInvertendo dados para criar 'pokemon_learnsets_final.json'...")
    pokemon_learnsets = {}
    
    for move_name, pokemon_list in learnsets_by_move.items():
        for item in pokemon_list:
            poke_name = item['pokemon']
            level = item['level']
            
            if poke_name not in pokemon_learnsets:
                pokemon_learnsets[poke_name] = []
                
            pokemon_learnsets[poke_name].append({
                "level": level,
                "move": move_name
            })
            
    for poke_name in pokemon_learnsets:
        pokemon_learnsets[poke_name].sort(key=lambda x: x['level'])
        
    return pokemon_learnsets

# --- FUNÇÃO PRINCIPAL (V12 - USANDO EDGE + SELENIUM 4) ---
def main():
    ATTACKS_LIST_URL = "https://pmmo3d.wixsite.com/wiki/attacks-list"
    OUTPUT_MOVES = "moves_data_final.json"
    OUTPUT_LEARNSETS = "pokemon_learnsets_final.json"
    
    print("Iniciando o driver do Selenium (Microsoft Edge - Manual V12)...")
    
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # --- MUDANÇA V12: Apontando para o msedgedriver.exe ---
        driver_path = os.path.join(script_dir, "msedgedriver.exe")

        if not os.path.exists(driver_path):
            print(f"ERRO CRÍTICO: 'msedgedriver.exe' não encontrado em {script_dir}")
            print("Verifique se você baixou o driver V142 do Edge e o colocou na mesma pasta do scraper.py.")
            return

        # --- MUDANÇA V12: Usando EdgeOptions ---
        options = EdgeOptions()
        options.add_argument("--headless")
        options.add_argument("--log-level=3")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # --- MUDANÇA V12: Usando EdgeService e webdriver.Edge ---
        service = EdgeService(executable_path=driver_path)
        driver = webdriver.Edge(service=service, options=options)
    
    except Exception as e:
        print(f"ERRO CRÍTICO: Falha ao iniciar o msedgedriver.exe local.")
        print(f"Erro: {e}")
        return
    
    print("Driver iniciado. Começando a raspagem.")
    
    move_list = get_move_list(driver, ATTACKS_LIST_URL)
    
    if not move_list:
        print("Não foi possível obter a lista de golpes. Abortando.")
        driver.quit()
        return

    final_moves_data = {}
    learnsets_by_move = {} 
    total = len(move_list)
    falhas = 0

    for i, (move_name, slug) in enumerate(move_list.items()):
        print(f"Processando ({i+1}/{total}): {move_name}...")
        
        move_data, learned_by = scrape_move_page(driver, move_name, slug)
        
        if move_data:
            final_moves_data[move_name] = move_data
        else:
            falhas += 1
            print(f"    -> Falha ao processar {move_name}.")
        
        if learned_by:
            learnsets_by_move[move_name] = learned_by
            
    driver.quit()
    print("Navegador fechado.")

    final_learnsets = invert_learnsets(learnsets_by_move)

    try:
        with open(OUTPUT_MOVES, 'w', encoding='utf-8') as f:
            json.dump(final_moves_data, f, indent=2, ensure_ascii=False)
        print(f"\n[SUCESSO] Arquivo '{OUTPUT_MOVES}' criado com os stats de {len(final_moves_data)} golpes.")
        
        with open(OUTPUT_LEARNSETS, 'w', encoding='utf-8') as f:
            json.dump(final_learnsets, f, indent=2, ensure_ascii=False)
        print(f"\n[SUCESSO] Arquivo '{OUTPUT_LEARNSETS}' criado com os golpes de {len(final_learnsets)} Pokémon.")
        
        if falhas > 0:
            print(f"\nAviso: {falhas} golpes falharam ao ser raspados (provavelmente páginas vazias ou com erro).")
        print("\n'Operação Inversão Total' (V12 Edge/Selenium4) concluída.")
        
    except IOError as e:
        print(f"\nERRO CRÍTICO: Falha ao salvar arquivos. {e}")

if __name__ == "__main__":
    main()