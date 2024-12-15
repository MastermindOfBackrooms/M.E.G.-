from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json

@dataclass
class LevelIntel:
    level_id: str
    knowledge_level: int = 0  # Da 0 a 5
    intel_points: int = 0
    discovered_secrets: List[str] = field(default_factory=list)
            
    def add_intel(self, points: int) -> bool:
        """Aggiunge punti intel e aumenta eventualmente il livello di conoscenza"""
        self.intel_points += points
        old_level = self.knowledge_level
        
        # Calcola il nuovo livello di conoscenza
        # Richiede più punti per ogni livello successivo
        threshold = [10, 25, 50, 100, 200]
        for level, required in enumerate(threshold, 1):
            if self.intel_points >= required:
                self.knowledge_level = level
                
        return self.knowledge_level > old_level

class IntelSystem:
    def __init__(self):
        self.levels_intel: Dict[str, LevelIntel] = {}
        self.load_levels()
        
    def load_levels(self):
        """Carica i livelli dal file di configurazione"""
        with open("data/levels.json") as f:
            data = json.load(f)
            for level in data["levels"]:
                self.levels_intel[level["id"]] = LevelIntel(level["id"])
                
    def get_level_info(self, level_id: str, include_secrets: bool = True) -> Dict:
        """Restituisce le informazioni disponibili per un livello"""
        with open("data/levels.json") as f:
            data = json.load(f)
            level_data = next((l for l in data["levels"] if l["id"] == level_id), None)
            if not level_data:
                return {}  # Ritorna un dizionario vuoto invece di None
                
            intel = self.levels_intel.get(level_id)
            if not intel:
                return {}  # Ritorna un dizionario vuoto invece di None
                
            # Info base sempre disponibili
            info = {
                "id": level_data["id"],
                "name": level_data["name"],
                "description": level_data["description"],
                "knowledge_level": intel.knowledge_level
            }
            
            # Informazioni aggiuntive in base al livello di conoscenza
            if intel.knowledge_level >= 1:
                info["difficulty"] = level_data["difficulty"]
                info["danger_level"] = level_data["danger_level"]
                
            if intel.knowledge_level >= 2:
                info["entities"] = level_data["entities"]
                
            if intel.knowledge_level >= 3:
                info["resources"] = level_data["resources"]
                
            if intel.knowledge_level >= 4:
                info["special_items"] = level_data["special_items"]
                
            if include_secrets and intel.knowledge_level >= 5:
                info["discovered_secrets"] = intel.discovered_secrets
                
            return info
            
    def add_intel_points(self, level_id: str, points: int, source: str) -> Dict:
        """Aggiunge punti intel a un livello e restituisce eventuali aggiornamenti"""
        if level_id not in self.levels_intel:
            return {}  # Ritorna un dizionario vuoto invece di None
            
        intel = self.levels_intel[level_id]
        leveled_up = intel.add_intel(points)
        
        return {
            "level_id": level_id,
            "points_gained": points,
            "new_total": intel.intel_points,
            "knowledge_level": intel.knowledge_level,
            "leveled_up": leveled_up,
            "source": source
        }
        
    def to_dict(self) -> Dict:
        return {
            level_id: {
                "knowledge_level": intel.knowledge_level,
                "intel_points": intel.intel_points,
                "discovered_secrets": intel.discovered_secrets
            }
            for level_id, intel in self.levels_intel.items()
        }
        
    def from_dict(self, data: Dict):
        for level_id, intel_data in data.items():
            if level_id in self.levels_intel:
                intel = self.levels_intel[level_id]
                intel.knowledge_level = intel_data["knowledge_level"]
                intel.intel_points = intel_data["intel_points"]
                intel.discovered_secrets = intel_data["discovered_secrets"]
                
    def reset(self):
        self.load_levels()
