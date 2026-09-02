# src/dota/api.py

import requests
import time
import json
from pathlib import Path
from typing import List, Optional, Dict, Tuple


def get_match(match_id: int) -> Optional[Dict]:
    """Получает данные о матче по его ID."""
    url = f"https://api.opendota.com/api/matches/{match_id}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Ошибка {response.status_code} для матча {match_id}")
            return None
    except Exception as e:
        print(f"Исключение: {e}")
        return None


def get_match_safe(match_id: int, retries: int = 3) -> Optional[Dict]:
    """Безопасное получение матча с повторными попытками."""
    for attempt in range(retries):
        match = get_match(match_id)
        if match:
            return match
        
        if attempt < retries - 1:
            time.sleep(2)
    
    return None


def parse_match(match: Dict) -> Dict:
    """Извлекает ключевую информацию из матча."""
    return {
        "match_id": match.get("match_id"),
        "radiant_win": match.get("radiant_win"),
        "duration_min": match.get("duration", 0) / 60,
        "game_mode": match.get("game_mode"),
        "radiant_team": [],
        "dire_team": [],
        "players": []
    }


def get_team_picks(match: Dict) -> Tuple[List[int], List[int]]:
    """Возвращает (radiant_picks, dire_picks)."""
    radiant = []
    dire = []
    
    players = match.get("players", [])
    for player in players:
        hero_id = player.get("hero_id")
        if hero_id is None:
            continue
        
        if player.get("player_slot", 0) < 5:
            radiant.append(hero_id)
        else:
            dire.append(hero_id)
    
    return radiant, dire


def collect_matches(start_id: int, count: int = 10, delay: float = 1.0) -> List[Dict]:
    """Собирает count матчей, начиная с start_id."""
    matches = []
    
    for i in range(count):
        match_id = start_id - i
        print(f"Сбор матча {match_id}...")
        
        if i > 0:
            time.sleep(delay)
        
        match = get_match_safe(match_id)
        if match:
            matches.append(match)
            print(f"  ✓ Загружен")
        else:
            print(f"  ✗ Не найден")
    
    return matches


def save_matches(matches: List[Dict], filepath: str = "data/raw/matches.json"):
    """Сохраняет матчи в JSON файл."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(matches, f, ensure_ascii=False, indent=2)
    
    print(f"Сохранено {len(matches)} матчей в {filepath}")


def load_matches(filepath: str = "data/raw/matches.json") -> List[Dict]:
    """Загружает матчи из JSON файла."""
    path = Path(filepath)
    
    if not path.exists():
        print(f"Файл {filepath} не найден")
        return []
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_heroes() -> List[Dict]:
    """Получает список всех героев."""
    url = "https://api.opendota.com/api/heroes"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return []


def get_hero_name(hero_id: int, heroes: List[Dict] = None) -> str:
    """Возвращает имя героя по его ID."""
    if heroes is None:
        heroes = get_heroes()
    
    for hero in heroes:
        if hero.get("id") == hero_id:
            return hero.get("localized_name", f"Hero {hero_id}")
    
    return f"Hero {hero_id}"


if __name__ == "__main__":
    # Самопроверка при прямом запуске
    print("Проверка модуля api...")
    
    # Проверяем подключение
    heroes = get_heroes()
    if heroes:
        print(f"✓ API доступен, загружено {len(heroes)} героев")
        print(f"  Первый герой: {heroes[0].get('localized_name')}")
    else:
        print("✗ API недоступен")
    
    # Проверяем функции
    match = get_match(7654321098)
    if match:
        print(f"✓ Матч 7654321098 загружен")
        radiant, dire = get_team_picks(match)
        print(f"  Radiant: {radiant}")
        print(f"  Dire: {dire}")
    
    print("Модуль api готов")