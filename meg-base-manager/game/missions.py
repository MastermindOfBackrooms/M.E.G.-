import random
import json
from typing import List, Dict

class Mission:
    def __init__(self, id: str, title: str, description: str, duration: int, 
                 requirements: Dict, rewards: Dict):
        self.id = id
        self.title = title
        self.description = description
        self.duration = duration
        self.requirements = requirements
        self.rewards = rewards
        self.days_left = duration
        self.completed = False

class MissionManager:
    def __init__(self):
        self.missions = self.load_missions()
        self.active_missions = []
        
    def load_missions(self) -> List[Mission]:
        with open("data/missions.json") as f:
            data = json.load(f)
            return [Mission(**mission) for mission in data["missions"]]
            
    def get_mission_by_number(self, number: int) -> Mission:
        """Ottieni una missione dal suo numero (1-based)"""
        if number < 1 or number > len(self.missions):
            return None
        return self.missions[number - 1]
        
    def start_mission(self, mission_number: int, agent_id: str, game_state) -> Dict:
        mission = self.get_mission_by_number(mission_number)
        if not mission:
            return {"success": False, "message": "Missione non valida"}
            
        # Verifica agente
        agent = game_state.personnel.get_agent(agent_id)
        if not agent or agent.status != "disponibile":
            return {"success": False, "message": "Agente non disponibile"}
            
        # Check requirements
        for resource, amount in mission.requirements.get("resources", {}).items():
            if game_state.resources.get(resource) < amount:
                return {"success": False, "message": f"Risorse insufficienti: {resource}"}
                
        # Deduct resources
        for resource, amount in mission.requirements.get("resources", {}).items():
            game_state.resources.modify(resource, -amount)
            
        # Assegna agente alla missione
        game_state.personnel.assign_mission(agent_id, mission.title)
        
        mission.assigned_agent = agent_id
        self.active_missions.append(mission)
        return {"success": True, "message": f"Missione avviata con {agent.name}"}
        
    def update_missions(self, game_state):
        completed = []
        for mission in self.active_missions:
            mission.days_left -= 1
            if mission.days_left <= 0:
                mission.completed = True
                completed.append(mission)
                
                # Generazione intel points in base al tipo di missione
                if "explore" in mission.id:
                    # Le missioni di esplorazione danno più intel points
                    game_state.intel.add_intel_points("level_0", 15, f"Missione: {mission.title}")
                elif "rescue" in mission.id:
                    # Le missioni di soccorso danno intel points medi
                    game_state.intel.add_intel_points("level_0", 10, f"Missione: {mission.title}")
                else:
                    # Altre missioni danno meno intel points
                    game_state.intel.add_intel_points("level_0", 5, f"Missione: {mission.title}")
                
        self.active_missions = [m for m in self.active_missions if not m.completed]
        return completed
        
    def to_dict(self) -> Dict:
        return {
            "active_missions": [
                {
                    "id": m.id,
                    "days_left": m.days_left,
                    "completed": m.completed
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
                self.active_missions.append(mission)
                
    def reset(self):
        self.active_missions = []
