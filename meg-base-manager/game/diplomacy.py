from dataclasses import dataclass, field
from typing import Dict, List
import random

@dataclass
class Organization:
    id: str
    name: str
    description: str
    attitude: int = 50  # da 0 (ostile) a 100 (alleato)
    trade_bonus: float = 1.0
    intel_sharing: bool = False
    military_support: bool = False
    special_event_chance: float = 0.1  # Probabilità di eventi speciali
    unique_ability: str = ""  # Abilità unica dell'organizzazione
    relationship_threshold: Dict[str, int] = field(default_factory=lambda: {
        "hostile": 20,      # Sotto 20: ostile
        "unfriendly": 35,   # 20-35: poco amichevole
        "neutral": 50,      # 35-50: neutrale
        "friendly": 75,     # 50-75: amichevole
        "allied": 90        # 75-90: alleato
        # Sopra 90: alleato fidato
    })

class DiplomaticSystem:
    def __init__(self):
        self.organizations = {
            "partygoers": Organization(
                "partygoers",
                "Festaioli",
                "Un gruppo che organizza feste infinite nel Livello Fun. Pericolosi ma utili per il commercio di risorse rare.",
                trade_bonus=1.5,
                special_event_chance=0.15,
                unique_ability="Festa Eterna: Può aumentare drasticamente il morale della base, ma con rischi di corruzione"
            ),
            "meg": Organization(
                "meg",
                "M.E.G. Centrale", 
                "Il quartier generale del Major Exploration Group. Fornisce supporto e risorse ai vari avamposti.",
                trade_bonus=1.2,
                special_event_chance=0.08,
                unique_ability="Supporto Centrale: Accesso a rifornimenti d'emergenza e supporto logistico avanzato"
            ),
            "bluestar": Organization(
                "bluestar",
                "Stella Blu",
                "Un'organizzazione scientifica che studia le anomalie delle Backrooms. Esperti in ricerca e tecnologia.",
                trade_bonus=1.3,
                special_event_chance=0.12,
                unique_ability="Ricerca Avanzata: Può sbloccare tecnologie uniche e potenziamenti per la base"
            ),
            "crimson": Organization(
                "crimson",
                "Ordine Cremisi",
                "Un gruppo militarizzato che mantiene l'ordine in alcuni livelli. Forniscono protezione in cambio di risorse.",
                trade_bonus=1.4,
                special_event_chance=0.1,
                unique_ability="Supporto Tattico: Fornisce addestramento militare avanzato e supporto in combattimento"
            ),
            "library": Organization(
                "library",
                "Biblioteca delle Backrooms",
                "Custodi della conoscenza delle Backrooms. Scambiano informazioni preziose.",
                trade_bonus=1.3,
                special_event_chance=0.1,
                unique_ability="Sapienza Antica: Accesso a conoscenze rare e segreti dimenticati delle Backrooms"
            ),
            "wanderers": Organization(
                "wanderers",
                "Vagabondi delle Backrooms",
                "Un gruppo nomade che vaga tra i livelli, commerciando risorse e informazioni. Ottimi esploratori.",
                trade_bonus=1.2,
                special_event_chance=0.13,
                unique_ability="Rete di Contatti: Può scoprire nuove rotte commerciali e opportunità di scambio"
            ),
            "eyes": Organization(
                "eyes",
                "Gli Occhi",
                "Un misterioso gruppo che osserva e raccoglie informazioni. Possiedono conoscenze uniche sui livelli.",
                trade_bonus=1.4,
                special_event_chance=0.11,
                unique_ability="Visione Oscura: Può prevedere e prevenire eventi pericolosi"
            ),
            "facelings": Organization(
                "facelings",
                "I Senza Volto",
                "Entità native delle Backrooms che talvolta commerciano con gli umani. Imprevedibili ma potenti alleati.",
                trade_bonus=1.6,
                special_event_chance=0.2,
                unique_ability="Poteri Anomali: Può fornire protezione sovrannaturale e abilità uniche"
            )
        }
        self.embassy_built = False
        self.active_treaties = []

    def has_embassy(self) -> bool:
        return self.embassy_built

    def build_embassy(self):
        """Costruisce l'ambasciata e inizializza le relazioni diplomatiche"""
        self.embassy_built = True
        self.initialize_organizations()
        print("\n[bold green]Ambasciata costruita con successo![/]")
        print("Ora puoi interagire con le seguenti organizzazioni:")
        for org in self.organizations.values():
            print(f"- {org.name}: {org.description}")
        print("\nOgni organizzazione ha un'attitudine iniziale verso la tua base.")
        print("Migliora le relazioni attraverso missioni diplomatiche e scambi.")

    def can_interact(self, organization_id: str) -> bool:
        """Verifica se è possibile interagire con un'organizzazione"""
        if not self.embassy_built:
            return False
        if organization_id not in self.organizations:
            return False
        return True

    def modify_relation(self, organization_id: str, amount: int) -> bool:
        if not self.can_interact(organization_id):
            return False

        org = self.organizations[organization_id]
        old_attitude = org.attitude
        org.attitude = max(0, min(100, org.attitude + amount))

        # Aggiorna bonus in base all'attitudine
        if org.attitude >= 80 and not org.intel_sharing:
            org.intel_sharing = True
        elif org.attitude < 80 and org.intel_sharing:
            org.intel_sharing = False

        if org.attitude >= 90 and not org.military_support:
            org.military_support = True
        elif org.attitude < 90 and org.military_support:
            org.military_support = False

        org.trade_bonus = 1.0 + (org.attitude / 100)
        return org.attitude != old_attitude

    def request_help(self, organization_id: str, help_type: str, game_state) -> Dict:
        if not self.can_interact(organization_id):
            return {"success": False, "message": "Interazione non disponibile"}

        org = self.organizations[organization_id]
        chance = org.attitude / 100
        success = random.random() < chance

        if help_type == "military" and not org.military_support:
            return {"success": False, "message": "Supporto militare non disponibile"}

        if help_type == "intel" and not org.intel_sharing:
            return {"success": False, "message": "Condivisione intel non disponibile"}

        if success:
            self.modify_relation(organization_id, -5)  # Diminuisce leggermente il rapporto per ogni richiesta
            
            # Effetti speciali in base all'organizzazione
            special_effects = ""
            if org.id == "partygoers":
                if help_type == "military":
                    game_state.defense.defense_rating += 5
                    special_effects = "Bonus difesa temporaneo ottenuto"
                else:
                    game_state.intel.add_intel_points("level_0", 15, "Festaioli")
                    special_effects = "Informazioni sul Livello Fun ottenute"
                    
            elif org.id == "meg":
                if help_type == "military":
                    game_state.resources.modify("supplies", 20)
                    special_effects = "Rifornimenti extra ricevuti"
                else:
                    game_state.intel.add_intel_points("level_0", 10, "M.E.G. Centrale")
                    special_effects = "Database M.E.G. consultato"
                    
            elif org.id == "bluestar":
                if help_type == "military":
                    game_state.resources.modify("medical", 15)
                    special_effects = "Tecnologie mediche avanzate ricevute"
                else:
                    game_state.intel.add_intel_points("level_0", 20, "Stella Blu")
                    special_effects = "Analisi anomalie effettuata"
                    
            elif org.id == "crimson":
                if help_type == "military":
                    game_state.defense.defense_rating += 10
                    special_effects = "Squadra d'assalto inviata"
                else:
                    game_state.intel.add_intel_points("level_0", 5, "Ordine Cremisi")
                    special_effects = "Rapporto situazionale ricevuto"
                    
            elif org.id == "library":
                if help_type == "military":
                    game_state.resources.modify("almond_water", 10)
                    special_effects = "Scorte di emergenza condivise"
                else:
                    game_state.intel.add_intel_points("level_0", 25, "Biblioteca")
                    special_effects = "Archivi consultati"
                    
            elif org.id == "wanderers":
                if help_type == "military":
                    game_state.resources.modify("fuel", 15)
                    special_effects = "Carburante extra ricevuto"
                else:
                    game_state.intel.add_intel_points("level_0", 15, "Vagabondi")
                    special_effects = "Nuove rotte commerciali scoperte"
                    
            elif org.id == "eyes":
                if help_type == "military":
                    game_state.stats.prestige += 5
                    special_effects = "Prestigio aumentato"
                else:
                    game_state.intel.add_intel_points("level_0", 30, "Gli Occhi")
                    special_effects = "Informazioni segrete ottenute"
                    
            elif org.id == "facelings":
                if help_type == "military":
                    game_state.defense.defense_rating += 15
                    special_effects = "Protezione sovrannaturale ottenuta"
                else:
                    game_state.intel.add_intel_points("level_0", 35, "Senza Volto")
                    special_effects = "Conoscenza antica rivelata"

            return {
                "success": True,
                "message": f"Aiuto ricevuto da {org.name}. {special_effects}",
                "help_type": help_type
            }
        else:
            # Penalità più severe per infiltrazioni fallite
            self.modify_relation(organization_id, -15)  # Diminuisce maggiormente le relazioni
            game_state.stats.morale -= 5  # Impatta il morale della base
            game_state.stats.prestige -= 3  # Danneggia il prestigio
            if random.random() < 0.2:  # 20% di chance di perdere risorse
                game_state.resources.modify("supplies", -10)
                game_state.resources.modify("medical", -5)
            return {
                "success": False,
                "message": f"{org.name} ha scoperto il tentativo di infiltrazione! Relazioni danneggiate e risorse perse."
            }
            return {
                "success": False,
                "message": f"{org.name} ha rifiutato la richiesta"
            }

    def get_relationship_status(self, organization_id: str) -> str:
        """Determina lo status della relazione con un'organizzazione"""
        if not self.can_interact(organization_id):
            return "non disponibile"
            
        org = self.organizations[organization_id]
        attitude = org.attitude
        
        if attitude >= org.relationship_threshold["allied"]:
            return "alleato fidato"
        elif attitude >= org.relationship_threshold["friendly"]:
            return "alleato"
        elif attitude >= org.relationship_threshold["neutral"]:
            return "amichevole"
        elif attitude >= org.relationship_threshold["unfriendly"]:
            return "neutrale"
        elif attitude >= org.relationship_threshold["hostile"]:
            return "poco amichevole"
        else:
            return "ostile"
            
    def trigger_special_event(self, organization_id: str, game_state) -> Dict:
        """Attiva un evento speciale basato sull'organizzazione"""
        if not self.can_interact(organization_id):
            return {"success": False, "message": "Organizzazione non disponibile"}
            
        org = self.organizations[organization_id]
        status = self.get_relationship_status(organization_id)
        
        # Solo organizzazioni amichevoli o meglio possono triggerare eventi positivi
        if status in ["ostile", "poco amichevole", "neutrale"]:
            return {"success": False, "message": "Relazioni insufficienti per eventi speciali"}
            
        if random.random() > org.special_event_chance:
            return {"success": False, "message": "Nessun evento speciale attivato"}
            
        # Eventi specifici per organizzazione
        special_events = {
            "partygoers": {
                "title": "Festa Interdimensionale",
                "effects": {
                    "morale": 20,
                    "corruption": 5,
                    "resources": {"almond_water": 10, "food": 15}
                }
            },
            "meg": {
                "title": "Supporto Centrale M.E.G.",
                "effects": {
                    "defense": 10,
                    "resources": {"supplies": 30, "medical": 15}
                }
            },
            "bluestar": {
                "title": "Breakthrough Tecnologico",
                "effects": {
                    "research": 15,
                    "defense": 5,
                    "resources": {"reality_stabilizer": 1}
                }
            },
            "crimson": {
                "title": "Operazione Congiunta",
                "effects": {
                    "defense": 20,
                    "morale": 10,
                    "resources": {"fuel": 20}
                }
            },
            "library": {
                "title": "Rivelazione Antica",
                "effects": {
                    "intel": 25,
                    "research": 10,
                    "resources": {"ancient_text": 1}
                }
            },
            "wanderers": {
                "title": "Rotta Commerciale Segreta",
                "effects": {
                    "trade_bonus": 0.2,
                    "resources": {"supplies": 25, "fuel": 15}
                }
            },
            "eyes": {
                "title": "Visione del Futuro",
                "effects": {
                    "intel": 30,
                    "defense": 15,
                    "corruption": -5
                }
            },
            "facelings": {
                "title": "Benedizione dei Senza Volto",
                "effects": {
                    "defense": 25,
                    "corruption": 10,
                    "resources": {"faceling_mask": 1}
                }
            }
        }
        
        event = special_events[organization_id]
        effects = event["effects"]
        
        # Applica gli effetti
        message = f"[bold]{event['title']}[/]\n"
        for effect, value in effects.items():
            if effect == "morale":
                game_state.stats.morale = min(100, game_state.stats.morale + value)
                message += f"Morale {value:+}\n"
            elif effect == "corruption":
                game_state.stats.corruption_level = max(0, min(100, 
                    game_state.stats.corruption_level + value))
                message += f"Corruzione {value:+}\n"
            elif effect == "defense":
                game_state.defense.defense_rating += value
                message += f"Difesa {value:+}\n"
            elif effect == "research":
                # Implementa bonus ricerca
                message += f"Ricerca {value:+}\n"
            elif effect == "intel":
                game_state.intel.add_intel_points("level_0", value, event["title"])
                message += f"Intel {value:+}\n"
            elif effect == "trade_bonus":
                org.trade_bonus += value
                message += f"Bonus Commercio {value:+.1f}\n"
            elif effect == "resources":
                for resource, amount in value.items():
                    game_state.resources.modify(resource, amount)
                    message += f"{resource.replace('_', ' ').title()} {amount:+}\n"
                    
        return {
            "success": True,
            "message": message
        }

    def daily_update(self, game_state):
        """Aggiorna le relazioni diplomatiche giornalmente"""
        for org in self.organizations.values():
            # Base chance di cambiamento giornaliero
            if random.random() < 0.1:
                # Più probabile migliorare relazioni se amichevole, peggiorarle se ostile
                status = self.get_relationship_status(org.id)
                if status in ["alleato fidato", "alleato", "amichevole"]:
                    change = random.randint(-1, 3)  # Più probabile migliorare
                elif status in ["ostile", "poco amichevole"]:
                    change = random.randint(-3, 1)  # Più probabile peggiorare
                else:
                    change = random.randint(-2, 2)  # Neutrale
                    
                self.modify_relation(org.id, change)
                
            # Chance di evento speciale
            if random.random() < org.special_event_chance:
                self.trigger_special_event(org.id, game_state)

    def to_dict(self) -> Dict:
        return {
            "embassy_built": self.embassy_built,
            "organizations": {
                org_id: {
                    "attitude": org.attitude,
                    "intel_sharing": org.intel_sharing,
                    "military_support": org.military_support,
                    "trade_bonus": org.trade_bonus
                }
                for org_id, org in self.organizations.items()
            }
        }

    def from_dict(self, data: Dict):
        self.embassy_built = data["embassy_built"]
        for org_id, org_data in data["organizations"].items():
            if org_id in self.organizations:
                org = self.organizations[org_id]
                org.attitude = org_data["attitude"]
                org.intel_sharing = org_data["intel_sharing"]
                org.military_support = org_data["military_support"]
                org.trade_bonus = org_data["trade_bonus"]

    def debug_status(self) -> Dict:
        """Restituisce lo stato corrente del sistema diplomatico per debug"""
        return {
            "embassy_status": self.embassy_built,
            "organizations_status": {
                org_id: {
                    "name": org.name,
                    "attitude": org.attitude,
                    "can_interact": self.can_interact(org_id)
                }
                for org_id, org in self.organizations.items()
            }
        }

    def reset(self):
        self.__init__()

    def initialize_organizations(self):
        """Inizializza le relazioni con le varie organizzazioni"""
        for org in self.organizations.values():
            # Reset degli stati
            org.intel_sharing = False
            org.military_support = False
            
            # Imposta attitudine iniziale in base all'organizzazione
            if org.id == "meg":
                org.attitude = 65  # La M.E.G. Centrale è naturalmente più amichevole
                org.trade_bonus = 1.2
            elif org.id == "library":
                org.attitude = 60  # La Biblioteca è relativamente aperta alla cooperazione
                org.trade_bonus = 1.3
            elif org.id == "wanderers":
                org.attitude = 55  # I Vagabondi sono neutrali ma aperti
                org.trade_bonus = 1.2
            elif org.id == "bluestar":
                org.attitude = 50  # La Stella Blu è neutrale
                org.trade_bonus = 1.3
            elif org.id == "crimson":
                org.attitude = 45  # L'Ordine Cremisi è cauto
                org.trade_bonus = 1.4
            elif org.id == "eyes":
                org.attitude = 40  # Gli Occhi sono sospettosi
                org.trade_bonus = 1.4
            elif org.id == "partygoers":
                org.attitude = 35  # I Festaioli sono imprevedibili
                org.trade_bonus = 1.5
            elif org.id == "facelings":
                org.attitude = 30  # I Senza Volto sono i più diffidenti
                org.trade_bonus = 1.6
                
            # Sblocca condivisione intel per organizzazioni più amichevoli
            if org.attitude >= 60:
                org.intel_sharing = True