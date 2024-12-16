from dataclasses import dataclass, field
from typing import Dict, List
import random
import json

@dataclass
class LevelIntel:
    level_id: str
    name: str = ""
    description: str = ""
    knowledge_level: int = 0  # Da 0 a 5
    intel_points: int = 0
    discovered_secrets: List[str] = field(default_factory=list)
    corruption_level: int = 0  # Livello di corruzione da 0 a 100
    suspicious_agents: List[str] = field(default_factory=list)  # Lista ID agenti sospetti
            
    def add_intel(self, points: int) -> bool:
        """Aggiunge punti intel e aumenta eventualmente il livello di conoscenza"""
        self.intel_points += points
        
        # Controlla se possiamo aumentare il livello di conoscenza
        if self.intel_points >= (self.knowledge_level + 1) * 100:
            if self.knowledge_level < 5:
                self.knowledge_level += 1
                return True
        return False

class IntelSystem:
    def __init__(self):
        self.levels_intel: Dict[str, LevelIntel] = {}
        self.load_levels()
        
    def get_level_info(self, level_id: str) -> Dict:
        """Ottiene informazioni sul livello in base al livello di conoscenza"""
        level = self.levels_intel.get(level_id)
        if not level:
            return None
            
        info = {
            "name": level.name,
            "description": level.description,
            "knowledge_level": level.knowledge_level
        }
        
        # Aggiunge informazioni in base al livello di conoscenza
        if level.knowledge_level >= 2:
            info["difficulty"] = "Alta"
            info["danger_level"] = "Elevato"
            
        if level.knowledge_level >= 3:
            info["entities"] = ["Entity 1", "Entity 2"]
            
        if level.knowledge_level >= 4:
            info["resources"] = ["Resource 1", "Resource 2"]
            info["special_items"] = ["Item 1", "Item 2"]
            
        if level.knowledge_level >= 5:
            info["discovered_secrets"] = level.discovered_secrets
            
        return info
        
    def add_intel_points(self, level_id: str, points: int) -> Dict:
        """Aggiunge punti intelligence per un livello"""
        if level_id not in self.levels_intel:
            return {
                "success": False,
                "message": "Livello non trovato"
            }
            
        level = self.levels_intel[level_id]
        if level.add_intel(points):
            return {
                "success": True,
                "message": f"Aumentato livello conoscenza a {level.knowledge_level}!"
            }
            
        return {
            "success": True,
            "message": f"Aggiunti {points} punti intel"
        }
        
    def discover_secret(self, level_id: str, secret: str) -> bool:
        """Aggiunge un segreto scoperto alla lista"""
        if level_id in self.levels_intel:
            level = self.levels_intel[level_id]
            if secret not in level.discovered_secrets:
                level.discovered_secrets.append(secret)
                return True
        return False
        
    def save_intel(self) -> Dict:
        """Salva lo stato dell'intelligence"""
        intel_data = {}
        for level_id, level in self.levels_intel.items():
            intel_data[level_id] = {
                "name": level.name,
                "description": level.description,
                "knowledge_level": level.knowledge_level,
                "intel_points": level.intel_points,
                "discovered_secrets": level.discovered_secrets,
                "corruption_level": level.corruption_level,
                "suspicious_agents": level.suspicious_agents
            }
        return intel_data
        
    def load_intel(self, intel_data: Dict):
        """Carica lo stato dell'intelligence"""
        self.levels_intel.clear()
        for level_id, data in intel_data.items():
            intel = LevelIntel(level_id=level_id)
            intel.name = data["name"]
            intel.description = data["description"]
            intel.knowledge_level = data["knowledge_level"]
            intel.intel_points = data["intel_points"]
            intel.discovered_secrets = data["discovered_secrets"]
            intel.corruption_level = data.get("corruption_level", 0)
            intel.suspicious_agents = data.get("suspicious_agents", [])
            self.levels_intel[level_id] = intel
            
    def load_levels(self):
        """Carica le informazioni base dei livelli"""
        try:
            with open("data/levels.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                for level in data["levels"]:
                    self.levels_intel[level["id"]] = LevelIntel(
                        level_id=level["id"],
                        name=level["name"],
                        description=level["description"]
                    )
        except FileNotFoundError:
            print("File levels.json non trovato")
        except json.JSONDecodeError:
            print("Errore nel parsing del file levels.json")
            
    def reset(self):
        """Resetta il sistema di intelligence"""
        self.load_levels()

    def investigate_agent(self, agent_id: str, game_state) -> Dict:
        """Investiga un agente sospetto usando punti intelligence"""
        intel_cost = 30  # Costo in punti intelligence
        current_level = game_state.current_level
        level_intel = self.levels_intel.get(current_level)
        
        if not level_intel or level_intel.intel_points < intel_cost:
            return {
                "success": False,
                "message": f"Punti intelligence insufficienti! Necessari: {intel_cost}"
            }
            
        # Riduce i punti intelligence
        level_intel.intel_points -= intel_cost
        
        # Controlla se l'agente è corrotto (30% di chance di scoprire se è corrotto)
        agent = game_state.personnel.get_agent(agent_id)
        if agent and agent.id in level_intel.suspicious_agents:
            if random.random() < 0.3:
                return {
                    "success": True,
                    "corrupted": True,
                    "message": f"[bold red]L'agente {agent.name} è corrotto![/]"
                }
            else:
                return {
                    "success": True,
                    "corrupted": False,
                    "message": f"Non sono state trovate prove concrete di corruzione per {agent.name}."
                }
        return {
            "success": True,
            "corrupted": False,
            "message": f"L'agente {agent.name if agent else 'sconosciuto'} sembra pulito."
        }
        
    def purify_agent(self, agent_id: str, game_state) -> Dict:
        """Purifica un agente usando acqua di mandorla"""
        almond_water_cost = 15
        if game_state.resources.get("almond_water") < almond_water_cost:
            return {
                "success": False,
                "message": f"Acqua di mandorla insufficiente! Necessaria: {almond_water_cost}"
            }
            
        # Consuma l'acqua di mandorla
        game_state.resources.modify("almond_water", -almond_water_cost)
        
        # Rimuove l'agente dalla lista dei sospetti
        current_level = game_state.current_level
        if current_level in self.levels_intel:
            level_intel = self.levels_intel[current_level]
            if agent_id in level_intel.suspicious_agents:
                level_intel.suspicious_agents.remove(agent_id)
                level_intel.corruption_level = max(0, level_intel.corruption_level - 20)
                return {
                    "success": True,
                    "message": "Agente purificato con successo!"
                }
                
        return {
            "success": True,
            "message": "La purificazione non ha avuto effetti evidenti."
        }
        
    def get_corruption_info(self, level_id: str) -> Dict:
        """Ottiene informazioni sul livello di corruzione"""
        level_intel = self.levels_intel.get(level_id)
        if not level_intel:
            return {
                "corruption_level": 0,
                "suspicious_count": 0,
                "warning_level": "Sicuro"
            }
            
        warning = "Sicuro"
        if level_intel.corruption_level >= 75:
            warning = "CRITICO"
        elif level_intel.corruption_level >= 50:
            warning = "Alto"
        elif level_intel.corruption_level >= 25:
            warning = "Moderato"
            
        return {
            "corruption_level": level_intel.corruption_level,
            "suspicious_count": len(level_intel.suspicious_agents),
            "warning_level": warning
        }
