import random
import json
from typing import List, Dict

class Event:
    def __init__(self, id: str, title: str, description: str, effects: Dict,
                 level: str = "all", weight: float = 1.0, conditions: Dict = None):
        self.id = id
        self.title = title
        self.description = description
        self.effects = effects
        self.level = level    # Livello specifico o "all" per eventi generici
        self.weight = weight  # Probabilità relativa dell'evento
        self.conditions = conditions or {}  # Condizioni per il trigger dell'evento

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
            try:
                # Filtra eventi basati sulle condizioni e livello
                valid_events = []
                current_level = game_state.current_level
                
                # Log per debug
                print(f"\n[cyan]DEBUG: Checking events for level {current_level}[/]")
                
                for event in self.events:
                    # Verifica se l'evento è valido per il livello corrente o è un evento generico
                    is_valid_level = (
                        event.level == "all" or 
                        event.level == current_level or 
                        (isinstance(event.level, list) and current_level in event.level)
                    )
                    
                    if is_valid_level:
                        if self._check_conditions(event, game_state):
                            valid_events.append(event)
                            print(f"[cyan]DEBUG: Found valid event {event.id} for level {current_level}[/]")
                
                if valid_events:
                    # Selezione pesata degli eventi
                    weights = [e.weight for e in valid_events]
                    selected_event = random.choices(valid_events, weights=weights, k=1)[0]
                    
                    print(f"\n[green]EVENT: Triggering {selected_event.id} ({selected_event.title}) for level {current_level}[/]")
                    print(f"[blue]Description: {selected_event.description}[/]")
                    
                    self.trigger_event(selected_event, game_state)
                else:
                    print(f"[yellow]DEBUG: No valid events found for level {current_level}[/]")
            except Exception as e:
                print(f"[red]Errore durante il controllo degli eventi: {e}[/]")
                import traceback
                print(f"[red]{traceback.format_exc()}[/]")
                return
                
    def _check_conditions(self, event: Event, game_state) -> bool:
        """Verifica se le condizioni dell'evento sono soddisfatte"""
        if not event.conditions:
            return True
            
        for stat, condition in event.conditions.items():
            current_value = 0
            
            # Controllo statistiche
            if hasattr(game_state.stats, stat):
                current_value = getattr(game_state.stats, stat)
            # Controllo risorse
            elif stat in game_state.resources.resources:
                current_value = game_state.resources.get(stat)
                
            # Verifica condizione
            operator = condition.get("operator", ">=")
            value = condition.get("value", 0)
            
            if operator == ">=":
                if current_value < value:
                    return False
            elif operator == "<=":
                if current_value > value:
                    return False
            elif operator == "==":
                if current_value != value:
                    return False
                    
        return True
            
    def trigger_event(self, event: Event, game_state):
        try:
            self.active_events.append(event)
            # Gestione risorse
            for resource, amount in event.effects.get("resources", {}).items():
                try:
                    game_state.resources.modify(resource, amount)
                except Exception as e:
                    print(f"[red]Errore nella modifica della risorsa {resource}: {e}[/]")
                    continue
            
            # Gestione statistiche
            for stat, amount in event.effects.get("stats", {}).items():
                try:
                    current_value = getattr(game_state.stats, stat, 0)
                    new_value = current_value + amount
                    # Assicuriamoci che i valori rimangano in un range sensato
                    new_value = max(0, min(100, new_value))
                    setattr(game_state.stats, stat, new_value)
                except Exception as e:
                    print(f"[red]Errore nell'aggiornamento della statistica {stat}: {e}[/]")
                    continue
                    
            # Verifica condizioni per i finali dopo ogni evento significativo
            ending_result = game_state.endings.check_endings(game_state)
            if ending_result["triggered"]:
                ending = ending_result["ending"]
                print(f"\n[bold magenta]FINALE RAGGIUNTO: {ending.title}[/]")
                print(f"[magenta]{ending.description}[/]")
                return {"ending_triggered": True, "ending": ending}
                
        except Exception as e:
            print(f"[red]Errore generale nel trigger dell'evento: {e}[/]")
            
        return {"ending_triggered": False}
            
    def reset(self):
        self.active_events = []
