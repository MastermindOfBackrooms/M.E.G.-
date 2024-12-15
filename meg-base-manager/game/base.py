from dataclasses import dataclass
from typing import Dict, List
import json
import random
from .resources import Resources
from .personnel import Personnel
from .events import EventManager
from .missions import MissionManager
from .defense import DefenseSystem
from .intel import IntelSystem
from .diplomacy import DiplomaticSystem

@dataclass
class GameStats:
    day: int = 1
    prestige: int = 50
    morale: int = 70

class GameState:
    def __init__(self):
        self.stats = GameStats()
        self.resources = Resources()
        self.personnel = Personnel()
        self.events = EventManager()
        self.missions = MissionManager()
        self.defense = DefenseSystem()
        self.intel = IntelSystem()
        self.diplomacy = DiplomaticSystem()
        
    def new_game(self):
        self.stats = GameStats()
        self.resources.reset()
        self.personnel.reset()
        self.events.reset()
        self.missions.reset()
        self.diplomacy.reset()
    
    def advance_day(self):
        self.stats.day += 1
        self.resources.daily_update()
        self.personnel.daily_update()
        self.events.check_events(self)
        self.missions.update_missions(self)
        self.defense.daily_update(self)
        self.diplomacy.daily_update()
        
    def save_game(self, filename: str):
        save_data = {
            "stats": self.stats.__dict__,
            "resources": self.resources.to_dict(),
            "personnel": self.personnel.to_dict(),
            "missions": self.missions.to_dict(),
            "intel": self.intel.to_dict()
        }
        with open(f"saves/{filename}.json", "w") as f:
            json.dump(save_data, f)
            
    def load_game(self, filename: str):
        try:
            with open(f"saves/{filename}.json", "r") as f:
                data = json.load(f)
                self.stats = GameStats(**data["stats"])
                self.resources.from_dict(data["resources"])
                self.personnel.from_dict(data["personnel"])
                self.missions.from_dict(data["missions"])
            self.intel.from_dict(data["intel"])
        except FileNotFoundError:
            raise ValueError("Salvataggio non trovato")
