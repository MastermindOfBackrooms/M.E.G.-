from typing import Dict, List
import random

class Ending:
    def __init__(self, id: str, title: str, description: str, conditions: Dict):
        self.id = id
        self.title = title
        self.description = description
        self.conditions = conditions
        self.triggered = False

class EndingManager:
    def __init__(self):
        self.endings = {
            # Finale Classico - Sopravvivenza e prosperità
            "survival": Ending(
                "survival",
                "Guardiani delle Backrooms",
                "La tua base è diventata un faro di speranza nelle Backrooms. " \
                "Hai creato un avamposto sicuro e prospero, dimostrando che la " \
                "sopravvivenza è possibile anche nei luoghi più ostili.",
                {
                    "days_survived": 50,      # Sopravvivere 50 giorni
                    "prestige": 75,           # Alto prestigio
                    "morale": 70,             # Buon morale generale
                    "active_agents": 5        # Mantenere un team completo
                }
            ),
            # Finale Cattivo - Collasso della base
            "collapse": Ending(
                "collapse",
                "L'Oscurità Prevale",
                "Le Backrooms hanno vinto. La tua base è caduta nell'oscurità, " \
                "i sopravvissuti sono dispersi e le entità ora vagano liberamente " \
                "tra i corridoi abbandonati.",
                {
                    "morale": 20,             # Morale bassissimo
                    "resources_critical": True, # Risorse quasi esaurite
                    "active_agents": 2,        # Quasi tutti gli agenti persi
                    "prestige": 10            # Prestigio ai minimi
                }
            ),
            # Finale Nascosto - Scoperta di una verità nascosta
            "truth": Ending(
                "truth",
                "Al di là del Velo",
                "Attraverso meticolose ricerche e sacrifici, hai scoperto la " \
                "vera natura delle Backrooms. Ma questa conoscenza ha un prezzo...",
                {
                    "intel_points": 500,       # Accumulare molti punti intel
                    "discovered_secrets": 3,    # Scoprire segreti cruciali
                    "classified_documents": 2,  # Ottenere documenti classificati
                    "research_complete": True   # Completare ricerche speciali
                }
            ),
            # Finale Orrendo - Corruzione totale
            "horror": Ending(
                "horror",
                "L'Abisso Guarda Dentro",
                "La base esiste ancora, ma qualcosa è cambiato. Gli agenti " \
                "sorridono troppo, le pareti sussurrano, e tu... tu non sei " \
                "più sicuro di essere te stesso.",
                {
                    "corruption_level": 75,     # Alto livello di corruzione
                    "entity_encounters": 30,    # Molti incontri con entità
                    "failed_missions": 8,       # Serie di missioni fallite
                    "lost_agents": 3,          # Perdita di agenti significativa
                    "dark_events": 5           # Eventi oscuri accumulati
                }
            ),
            # Finale Criptico - Trascendenza
            "ascension": Ending(
                "ascension",
                "§¶∆∩♠☺",
                "...e così, quando l'ultimo livello si piegò su se stesso, " \
                "capisti che le Backrooms non erano mai state reali. O forse, " \
                "lo erano troppo.",
                {
                    "reality_fragments": 50,    # Raccogliere frammenti di realtà
                    "temporal_anomalies": 3,    # Sperimentare anomalie temporali
                    "visited_omega": True,      # Visitare il livello Omega
                    "transcendence_events": 2,  # Eventi di trascendenza
                    "dream_resonance": 100      # Risonanza onirica al massimo
                }
            )
        }
    
    def check_endings(self, game_state) -> Dict:
        """Verifica se sono state raggiunte le condizioni per un finale"""
        for ending_id, ending in self.endings.items():
            if not ending.triggered and self._check_conditions(ending, game_state):
                ending.triggered = True
                return {
                    "triggered": True,
                    "ending": ending
                }
        return {"triggered": False}
    
    def _check_conditions(self, ending: Ending, game_state) -> bool:
        """Verifica le condizioni specifiche per ogni finale"""
        try:
            # Condizioni per il finale classico
            if ending.id == "survival":
                return (game_state.stats.days_survived >= ending.conditions["days_survived"] and
                        game_state.stats.prestige >= ending.conditions["prestige"] and
                        game_state.stats.morale >= ending.conditions["morale"] and
                        len([a for a in game_state.personnel.agents if a.status != "morto"]) >= ending.conditions["active_agents"])
            
            # Condizioni per il finale del collasso
            elif ending.id == "collapse":
                critical_resources = all(amount <= 10 for amount in game_state.resources.resources.values())
                return (game_state.stats.morale <= ending.conditions["morale"] and
                        critical_resources and
                        len([a for a in game_state.personnel.agents if a.status != "morto"]) <= ending.conditions["active_agents"])
            
            # Condizioni per il finale della verità
            elif ending.id == "truth":
                return (game_state.intel.total_points >= ending.conditions["intel_points"] and
                        len(game_state.intel.discovered_secrets) >= ending.conditions["discovered_secrets"] and
                        game_state.intel.classified_documents >= ending.conditions["classified_documents"])
            
            # Condizioni per il finale dell'orrore
            elif ending.id == "horror":
                return (game_state.stats.corruption_level >= ending.conditions["corruption_level"] and
                        game_state.stats.entity_encounters >= ending.conditions["entity_encounters"] and
                        game_state.missions.failed_missions >= ending.conditions["failed_missions"] and
                        game_state.personnel.lost_agents >= ending.conditions["lost_agents"])
            
            # Condizioni per il finale criptico
            elif ending.id == "ascension":
                return (game_state.resources.get("reality_fragments", 0) >= ending.conditions["reality_fragments"] and
                        game_state.stats.temporal_anomalies >= ending.conditions["temporal_anomalies"] and
                        game_state.intel.visited_omega and
                        game_state.events.transcendence_count >= ending.conditions["transcendence_events"])
            
            return False
        except Exception as e:
            print(f"[red]Errore nel controllo delle condizioni per il finale {ending.id}: {e}[/]")
            return False
