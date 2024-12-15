from dataclasses import dataclass
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

class DiplomaticSystem:
    def __init__(self):
        self.organizations = {
            "partygoers": Organization(
                "partygoers",
                "Festaioli",
                "Un gruppo che organizza feste infinite nel Livello Fun. Pericolosi ma utili per il commercio di risorse rare.",
                trade_bonus=1.5
            ),
            "meg": Organization(
                "meg",
                "M.E.G. Centrale", 
                "Il quartier generale del Major Exploration Group. Fornisce supporto e risorse ai vari avamposti.",
                trade_bonus=1.2
            ),
            "bluestar": Organization(
                "bluestar",
                "Stella Blu",
                "Un'organizzazione scientifica che studia le anomalie delle Backrooms. Esperti in ricerca e tecnologia.",
                trade_bonus=1.3
            ),
            "crimson": Organization(
                "crimson",
                "Ordine Cremisi",
                "Un gruppo militarizzato che mantiene l'ordine in alcuni livelli. Forniscono protezione in cambio di risorse.",
                trade_bonus=1.4
            ),
            "library": Organization(
                "library",
                "Biblioteca delle Backrooms",
                "Custodi della conoscenza delle Backrooms. Scambiano informazioni preziose.",
                trade_bonus=1.3
            ),
            "wanderers": Organization(
                "wanderers",
                "Vagabondi delle Backrooms",
                "Un gruppo nomade che vaga tra i livelli, commerciando risorse e informazioni. Ottimi esploratori.",
                trade_bonus=1.2
            ),
            "eyes": Organization(
                "eyes",
                "Gli Occhi",
                "Un misterioso gruppo che osserva e raccoglie informazioni. Possiedono conoscenze uniche sui livelli.",
                trade_bonus=1.4
            ),
            "facelings": Organization(
                "facelings",
                "I Senza Volto",
                "Entità native delle Backrooms che talvolta commerciano con gli umani. Imprevedibili ma potenti alleati.",
                trade_bonus=1.6
            )
        }
        self.embassy_built = False
        self.active_treaties = []

    def has_embassy(self) -> bool:
        return self.embassy_built

    def build_embassy(self):
        self.embassy_built = True
        # Sblocca le interazioni diplomatiche iniziali
        for org in self.organizations.values():
            org.intel_sharing = False
            org.military_support = False
            org.trade_bonus = 1.0

    def can_interact(self, organization_id: str) -> bool:
        return self.embassy_built and organization_id in self.organizations

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
            self.modify_relation(organization_id, -10)  # Diminuisce maggiormente in caso di rifiuto
            return {
                "success": False,
                "message": f"{org.name} ha rifiutato la richiesta"
            }

    def daily_update(self):
        """Aggiorna le relazioni diplomatiche giornalmente"""
        for org in self.organizations.values():
            if random.random() < 0.1:  # 10% di chance di cambiamento giornaliero
                change = random.randint(-2, 2)
                self.modify_relation(org.id, change)

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

    def reset(self):
        self.__init__()
