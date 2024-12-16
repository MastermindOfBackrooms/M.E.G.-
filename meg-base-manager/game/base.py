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
from .market import Market

@dataclass
class GameStats:
    day: int = 1
    prestige: int = 50
    morale: int = 70
    defense_rating: int = 50  # Rating difensivo base
    rank: str = "Recluta"  # Rank iniziale
    
    def calculate_rank(self) -> str:
        if self.prestige >= 90:
            return "Comandante"
        elif self.prestige >= 70:
            return "Veterano"
        elif self.prestige >= 50:
            return "Esperto"
        elif self.prestige >= 30:
            return "Agente"
        else:
            return "Recluta"
            
    def update_rank(self) -> bool:
        """Aggiorna il rank e restituisce True se è stato raggiunto un nuovo rank"""
        new_rank = self.calculate_rank()
        if new_rank != self.rank:
            self.rank = new_rank
            # Aggiornamento bonus basati sul rank
            if self.rank == "Comandante":
                self.defense_rating += 20
            elif self.rank == "Veterano":
                self.defense_rating += 15
            elif self.rank == "Esperto":
                self.defense_rating += 10
            elif self.rank == "Agente":
                self.defense_rating += 5
            return True
        return False

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
        self.market = Market()
        
    def new_game(self):
        self.stats = GameStats()  # Inizializza con i valori predefiniti
        self.resources.reset()
        self.personnel.reset()
        self.events.reset()
        self.missions.reset()
        self.diplomacy.reset()
        self.defense.reset()
        
        # Aggiungi agenti iniziali
        self.personnel.hire_agent("Gray", "medic")
        self.personnel.hire_agent("Val", "combat_specialist")
        self.personnel.hire_agent("Taylor", "scout")
        self.personnel.hire_agent("Owen", "researcher")
        self.personnel.hire_agent("Noah", "survivalist")
    
    def advance_day(self):
        try:
            self.stats.day += 1
            
            # Aggiornamenti giornalieri
            try:
                self.resources.daily_update()
                self.personnel.daily_update()
                self.events.check_events(self)
                self.missions.update_missions(self)
                self.defense.daily_update(self)
                self.diplomacy.daily_update()
                
                # Controlla se è stato raggiunto un nuovo rank
                if self.stats.update_rank():
                    # Aggiungi un nuovo agente quando si raggiunge un nuovo rank
                    if self.personnel.add_random_agent():
                        print(f"\n[bold green]Congratulazioni! Hai raggiunto il rank {self.stats.rank}![/]")
                        print("[green]Un nuovo agente si è unito alla tua base![/]")
                        print(f"[blue]Bonus Difesa: +{20 if self.stats.rank == 'Comandante' else 15 if self.stats.rank == 'Veterano' else 10 if self.stats.rank == 'Esperto' else 5}[/]")
                    else:
                        print(f"\n[bold yellow]Hai raggiunto il rank {self.stats.rank}, ma la base è al massimo della capacità![/]")
            except Exception as e:
                print(f"Errore durante l'aggiornamento giornaliero: {e}")
                # Continuiamo comunque l'esecuzione per evitare blocchi totali
        except Exception as e:
            print(f"Errore critico nell'avanzamento del giorno: {e}")
            # Se c'è un errore critico, assicuriamoci almeno di incrementare il giorno
            if hasattr(self.stats, 'day'):
                self.stats.day += 1
        
    def save_game(self, filename: str):
        try:
            # Assicuriamoci che la cartella saves esista
            import os
            if not os.path.exists("saves"):
                os.makedirs("saves")
                
            save_data = {
                "stats": {
                    "day": self.stats.day,
                    "prestige": self.stats.prestige,
                    "morale": self.stats.morale,
                    "defense_rating": self.stats.defense_rating
                },
                "resources": self.resources.to_dict(),
                "personnel": self.personnel.to_dict(),
                "missions": self.missions.to_dict(),
                "intel": self.intel.to_dict()
            }
            
            save_path = f"saves/{filename}.json"
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=4)
            print(f"Partita salvata con successo in: {save_path}")
        except Exception as e:
            print(f"Errore durante il salvataggio: {e}")
            raise ValueError("Impossibile salvare la partita")
            
    def load_game(self, filename: str):
        try:
            save_path = f"saves/{filename}.json"
            if not os.path.exists(save_path):
                raise FileNotFoundError(f"File di salvataggio non trovato: {save_path}")
                
            with open(save_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Reset dello stato prima del caricamento
            self.events.reset()
            self.missions.reset()
            self.diplomacy.reset()
            
            # Caricamento dei dati
            self.stats = GameStats(
                day=data["stats"]["day"],
                prestige=data["stats"]["prestige"],
                morale=data["stats"]["morale"],
                defense_rating=data["stats"]["defense_rating"]
            )
            
            self.resources.from_dict(data["resources"])
            self.personnel.from_dict(data["personnel"])
            self.missions.from_dict(data["missions"])
            self.intel.from_dict(data["intel"])
            
            print(f"Partita caricata con successo da: {save_path}")
        except FileNotFoundError as e:
            print(f"Errore: {e}")
            raise ValueError("Salvataggio non trovato")
        except json.JSONDecodeError:
            print("Errore: Il file di salvataggio è corrotto")
            raise ValueError("File di salvataggio corrotto")
        except Exception as e:
            print(f"Errore durante il caricamento: {e}")
            raise ValueError("Impossibile caricare la partita")