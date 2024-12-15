import random
import json
from typing import List, Dict

class Event:
    def __init__(self, id: str, title: str, description: str, effects: Dict):
        self.id = id
        self.title = title
        self.description = description
        self.effects = effects

class EventManager:
    def __init__(self):
        self.events = self.load_events()
        self.active_events = []
        
    def load_events(self) -> List[Event]:
        with open("data/events.json") as f:
            data = json.load(f)
            return [Event(**event) for event in data["events"]]
            
    def check_events(self, game_state):
        if random.random() < 0.3:  # 30% chance per day
            event = random.choice(self.events)
            self.trigger_event(event, game_state)
            
    def trigger_event(self, event: Event, game_state):
        self.active_events.append(event)
        for resource, amount in event.effects.get("resources", {}).items():
            game_state.resources.modify(resource, amount)
        for stat, amount in event.effects.get("stats", {}).items():
            setattr(game_state.stats, stat, getattr(game_state.stats, stat) + amount)
            
    def reset(self):
        self.active_events = []
