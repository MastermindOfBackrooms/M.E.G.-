from dataclasses import dataclass
from typing import Dict, List
import random
import json

@dataclass
class Agent:
    id: str
    name: str
    role: str
    level: int = 1
    exp: int = 0
    morale: int = 70
    status: str = "disponibile"
    
    # Abilità base
    combat: int = 1      # Combattimento
    research: int = 1    # Ricerca
    survival: int = 1    # Sopravvivenza
    diplomacy: int = 1   # Diplomazia
    medical: int = 1     # Medicina
    
    def gain_exp(self, amount: int):
        self.exp += amount
        # Level up al raggiungimento di 100 exp
        while self.exp >= 100:
            self.level_up()
            self.exp -= 100
            
    def level_up(self):
        self.level += 1
        # Incrementa casualmente un'abilità
        abilities = ["combat", "research", "survival", "diplomacy", "medical"]
        chosen = random.choice(abilities)
        setattr(self, chosen, getattr(self, chosen) + 1)

class Personnel:
    def __init__(self):
        self.agents: List[Agent] = []
        self.max_agents = 10
        self.roles = self.load_roles()
        
    def load_roles(self) -> Dict:
        with open("data/roles.json") as f:
            data = json.load(f)
            return {role["id"]: role for role in data["roles"]}
        
    def hire_agent(self, name: str, role_id: str) -> bool:
        if len(self.agents) >= self.max_agents:
            return False
            
        if role_id not in self.roles:
            return False
            
        role_data = self.roles[role_id]
        base_stats = role_data["base_stats"]
        
        # Genera statistiche con base dal ruolo più variazione casuale
        agent = Agent(
            id=f"agent_{len(self.agents)+1}",
            name=name,
            role=role_data["name"],
            level=1,
            exp=0,
            morale=random.randint(60, 100),
            combat=base_stats["combat"] + random.randint(-1, 1),
            research=base_stats["research"] + random.randint(-1, 1),
            survival=base_stats["survival"] + random.randint(-1, 1),
            diplomacy=base_stats["diplomacy"] + random.randint(-1, 1),
            medical=base_stats["medical"] + random.randint(-1, 1)
        )
        self.agents.append(agent)
        return True
        
    def fire_agent(self, agent_id: str) -> bool:
        agent = self.get_agent(agent_id)
        if agent:
            self.agents.remove(agent)
            return True
        return False
        
    def get_agent(self, agent_id: str) -> Agent:
        return next((a for a in self.agents if a.id == agent_id), None)
        
    def assign_mission(self, agent_id: str, mission: str) -> bool:
        agent = self.get_agent(agent_id)
        if agent and agent.status == "disponibile":
            agent.status = mission
            return True
        return False
        
    def daily_update(self):
        for agent in self.agents:
            # Update morale
            if random.random() < 0.1:  # 10% chance
                change = random.randint(-5, 5)
                agent.morale = max(0, min(100, agent.morale + change))
                
            # Random skill improvement
            if random.random() < 0.05:  # 5% chance
                abilities = ["combat", "research", "survival", "diplomacy", "medical"]
                skill = random.choice(abilities)
                current_value = getattr(agent, skill)
                setattr(agent, skill, min(10, current_value + 1))
                
    def to_dict(self) -> Dict:
        return {
            "agents": [vars(agent) for agent in self.agents],
            "max_agents": self.max_agents
        }
        
    def from_dict(self, data: Dict):
        self.max_agents = data["max_agents"]
        self.agents = [Agent(**agent_data) for agent_data in data["agents"]]
        
    def reset(self):
        self.agents = []
        
        # Lista di 40 nomi inglesi per la generazione casuale
        nomi = [
            "Alex", "Blake", "Cameron", "Drew", "Ellis", "Francis", "Glen", "Harper",
            "Ian", "Jordan", "Kennedy", "Logan", "Morgan", "Noah", "Owen", "Parker",
            "Quinn", "Riley", "Sam", "Taylor", "Uri", "Val", "Winter", "Xavier",
            "Yuri", "Zion", "Ash", "Bailey", "Casey", "Dale", "Eden", "Finley",
            "Gray", "Hayden", "Indie", "Jamie", "Kai", "Lake", "Maven", "Noel"
        ]
        
        # Ruoli disponibili per il personale iniziale
        ruoli_disponibili = ["explorer", "researcher", "combat_specialist", "medic", 
                           "diplomat", "engineer", "survivalist", "psychologist", "scout"]
        
        # Mantieni traccia dei nomi usati e delle loro occorrenze
        nomi_usati = {}
        
        # Genera 5 agenti casuali con statistiche bilanciate
        for _ in range(5):
            nome_base = random.choice(nomi)
            
            # Gestisci i duplicati aggiungendo un numero
            if nome_base in nomi_usati:
                nomi_usati[nome_base] += 1
                nome_finale = f"{nome_base} {nomi_usati[nome_base]}"
            else:
                nomi_usati[nome_base] = 1
                nome_finale = nome_base
                
            ruolo = random.choice(ruoli_disponibili)
            self.hire_agent(nome_finale, ruolo)
