import random
import json
from typing import List, Dict

class Mission:
    def __init__(self, id: str, title: str, description: str, duration: int,
                 rewards: Dict, valid_levels: str | List[str] = "all",
                 level_requirements: Dict = None, difficulty_multiplier: Dict = None,
                 chain_mission: Dict = None, prerequisites: Dict = None):
        self.id = id
        self.title = title
        self.description = description
        self.duration = duration
        self.rewards = rewards
        self.valid_levels = valid_levels
        self.level_requirements = level_requirements or {"min_knowledge": 0, "max_difficulty": 5}
        self.difficulty_multiplier = difficulty_multiplier or {}
        self.chain_mission = chain_mission or {}
        self.prerequisites = prerequisites or {}
        self.days_left = duration
        self.completed = False
        self.assigned_agent = None
        self.selected_level = None
        
    def calculate_rewards(self, level_difficulty: int) -> Dict:
        """Calcola le ricompense basate sulla difficoltà del livello"""
        adjusted_rewards = {"resources": {}, "stats": {}}
        
        # Applica i moltiplicatori di difficoltà alle risorse
        if "resources" in self.rewards:
            for resource, amount in self.rewards["resources"].items():
                multiplier = self.difficulty_multiplier.get("resources", 1.0)
                adjusted_amount = int(amount * (1 + (level_difficulty - 1) * (multiplier - 1) / 4))
                adjusted_rewards["resources"][resource] = adjusted_amount
                
        # Applica i moltiplicatori alle statistiche
        if "stats" in self.rewards:
            for stat, amount in self.rewards["stats"].items():
                multiplier = self.difficulty_multiplier.get(stat, 1.0)
                adjusted_amount = int(amount * (1 + (level_difficulty - 1) * (multiplier - 1) / 4))
                adjusted_rewards["stats"][stat] = adjusted_amount
                
        # Aggiusta i punti intel
        if "intel_points" in self.rewards:
            multiplier = self.difficulty_multiplier.get("intel_points", 1.0)
            adjusted_rewards["intel_points"] = int(self.rewards["intel_points"] * 
                                              (1 + (level_difficulty - 1) * (multiplier - 1) / 4))
            
        return adjusted_rewards

class MissionManager:
    def __init__(self):
        self.missions = self.load_missions()
        self.active_missions = []
        
    def load_missions(self) -> List[Mission]:
        """Carica le missioni dal file JSON"""
        try:
            with open("data/missions.json", encoding='utf-8') as f:
                data = json.load(f)
                missions = []
                for mission_data in data["missions"]:
                    # Imposta valori predefiniti per campi opzionali
                    mission_data.setdefault("valid_levels", "all")
                    mission_data.setdefault("level_requirements", {"min_knowledge": 0, "max_difficulty": 5})
                    mission_data.setdefault("difficulty_multiplier", {})
                    missions.append(Mission(**mission_data))
                return missions
        except Exception as e:
            print(f"Errore nel caricamento delle missioni: {e}")
            return []
            
    def get_mission_by_number(self, number: int) -> Mission:
        """Ottieni una missione dal suo numero (1-based)"""
        if 1 <= number <= len(self.missions):
            return self.missions[number - 1]
        return None
        
    def select_valid_level(self, mission: Mission, game_state) -> str:
        """Seleziona un livello valido per la missione"""
        valid_levels = []
        all_levels = list(game_state.intel.levels_intel.keys())
        
        # Determina i livelli validi
        possible_levels = all_levels if mission.valid_levels == "all" else mission.valid_levels
        
        for level_id in possible_levels:
            level_info = game_state.intel.get_level_info(level_id)
            if not level_info:
                continue
                
            # Verifica requisiti del livello
            knowledge_level = game_state.intel.levels_intel[level_id].knowledge_level
            if knowledge_level < mission.level_requirements["min_knowledge"]:
                continue
                
            if "difficulty" in level_info:
                if level_info["difficulty"] > mission.level_requirements["max_difficulty"]:
                    continue
                    
            valid_levels.append(level_id)
            
        if not valid_levels:
            return None
            
        return random.choice(valid_levels)

    def start_mission(self, mission_number: int, agent_id: str, game_state) -> Dict:
        mission = self.get_mission_by_number(mission_number)
        if not mission:
            return {"success": False, "message": "Missione non valida"}
            
        # Verifica agente
        agent = game_state.personnel.get_agent(agent_id)
        if not agent or agent.status != "disponibile":
            return {"success": False, "message": "Agente non disponibile"}
            
        # Seleziona un livello valido
        selected_level = self.select_valid_level(mission, game_state)
        if not selected_level:
            return {"success": False, "message": "Nessun livello disponibile per questa missione"}
            
        # Ottieni informazioni sul livello
        level_info = game_state.intel.get_level_info(selected_level)
        level_difficulty = level_info.get("difficulty", 1)
            
        # Assegna agente alla missione
        game_state.personnel.assign_mission(agent_id, mission.title)
        
        # Calcola ricompense basate sulla difficoltà
        mission.adjusted_rewards = mission.calculate_rewards(level_difficulty)
        
        mission.assigned_agent = agent_id
        mission.selected_level = selected_level
        self.active_missions.append(mission)
        
        return {
            "success": True,
            "message": f"Missione avviata con {agent.name} nel {level_info['name']}",
            "level": level_info['name'],
            "difficulty": level_difficulty
        }
        
    def calculate_death_probability(self, mission, agent, level_info):
        """Calcola la probabilità di morte dell'agente durante la missione"""
        base_probability = level_info.get("difficulty", 1) * 0.02  # 2% per livello di difficoltà
        mission_modifier = mission.duration * 0.01  # 1% per giorno di missione
        experience_modifier = 0.1 - (agent.exp * 0.01)  # -1% per livello di esperienza
        
        final_probability = base_probability + mission_modifier - experience_modifier
        return max(0.01, min(0.5, final_probability))  # Limita tra 1% e 50%

    def update_missions(self, game_state):
        completed = []
        for mission in self.active_missions:
            mission.days_left -= 1
            
            # Controlla la possibilità di morte dell'agente ogni giorno
            if mission.assigned_agent:
                agent = game_state.personnel.get_agent(mission.assigned_agent)
                level_info = game_state.intel.get_level_info(mission.selected_level)
                
                if agent and level_info:
                    death_probability = self.calculate_death_probability(mission, agent, level_info)
                    if random.random() < death_probability:
                        print(f"\n[ALERT] L'agente {agent.name} è morto durante la missione '{mission.title}'")
                        print(f"Causa: Incidente fatale nel {level_info['name']}")
                        game_state.personnel.remove_agent(mission.assigned_agent)
                        game_state.stats.morale -= 20
                        mission.completed = True
                        completed.append(mission)
                        continue
            
            if mission.days_left <= 0:
                mission.completed = True
                completed.append(mission)
                
                # Assegna ricompense
                if hasattr(mission, 'adjusted_rewards'):
                    print(f"\nAssegnando ricompense per {mission.title}:")
                    
                    # Risorse
                    for resource, amount in mission.adjusted_rewards.get("resources", {}).items():
                        success = game_state.resources.modify(resource, amount)
                        print(f"- Risorsa {resource}: {amount} ({'successo' if success else 'fallito'})")
                    
                    # Statistiche
                    for stat, amount in mission.adjusted_rewards.get("stats", {}).items():
                        if hasattr(game_state.stats, stat):
                            current = getattr(game_state.stats, stat)
                            setattr(game_state.stats, stat, current + amount)
                            print(f"- Statistica {stat}: +{amount} (nuovo valore: {getattr(game_state.stats, stat)})")
                        else:
                            print(f"- Statistica {stat} non trovata")
                    
                    # Intel points per il livello specifico
                    if "intel_points" in mission.adjusted_rewards and mission.selected_level:
                        points = mission.adjusted_rewards["intel_points"]
                        game_state.intel.add_intel_points(
                            mission.selected_level,
                            points,
                            f"Missione: {mission.title}"
                        )
                        print(f"- Intel Points: +{points} per livello {mission.selected_level}")
                
                # Libera l'agente se è sopravvissuto
                if mission.assigned_agent:
                    agent = game_state.personnel.get_agent(mission.assigned_agent)
                    if agent:
                        game_state.personnel.free_agent(mission.assigned_agent)
                        # Aumenta l'esperienza dell'agente
                        game_state.personnel.increase_agent_experience(mission.assigned_agent, 1)
                
                print("\nPremi INVIO per continuare...")
                input()
                print("\n")  # Aggiunge solo una riga vuota per separazione
                
        self.active_missions = [m for m in self.active_missions if not m.completed]
        return completed
        
    def to_dict(self) -> Dict:
        return {
            "active_missions": [
                {
                    "id": m.id,
                    "days_left": m.days_left,
                    "completed": m.completed,
                    "assigned_agent": m.assigned_agent,
                    "selected_level": m.selected_level
                } for m in self.active_missions
            ]
        }
        
    def from_dict(self, data: Dict):
        self.active_missions = []
        for mission_data in data["active_missions"]:
            mission = next((m for m in self.missions if m.id == mission_data["id"]), None)
            if mission:
                mission.days_left = mission_data["days_left"]
                mission.completed = mission_data["completed"]
                mission.assigned_agent = mission_data.get("assigned_agent")
                mission.selected_level = mission_data.get("selected_level")
                self.active_missions.append(mission)
                
    def reset(self):
        self.active_missions = []
