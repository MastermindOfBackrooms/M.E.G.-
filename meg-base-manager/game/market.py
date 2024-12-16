from dataclasses import dataclass, field
from typing import Dict, List, Optional
import random

@dataclass
class TradeGood:
    name: str
    base_price: int
    rarity: int  # 1-5, influenza prezzo e disponibilità
    organization_bonus: Dict[str, float] = field(default_factory=dict)  # Bonus prezzo per org specifiche
    special_effects: Dict[str, int] = field(default_factory=dict)  # Effetti speciali (morale, difesa, etc)
    infiltration_risk: float = 0.05  # Rischio base di infiltrazione

class Market:
    def __init__(self):
        self.trade_goods = {
            # Risorse Base
            "supplies": TradeGood(
                "Rifornimenti Standard",
                20,
                1,
                {"meg": 0.8, "wanderers": 0.9},
                {"morale": 1},
                0.02
            ),
            "medical": TradeGood(
                "Forniture Mediche",
                30,
                2,
                {"bluestar": 0.8, "meg": 0.9},
                {"medical_bonus": 2},
                0.03
            ),
            "fuel": TradeGood(
                "Carburante",
                25,
                2,
                {"crimson": 0.8, "wanderers": 0.9},
                {"defense_bonus": 1},
                0.03
            ),
            
            # Risorse Rare
            "almond_water": TradeGood(
                "Acqua di Mandorle",
                40,
                3,
                {"library": 0.7, "meg": 0.8},
                {"sanity": 5},
                0.04
            ),
            "reality_stabilizer": TradeGood(
                "Stabilizzatore di Realtà",
                100,
                5,
                {"bluestar": 0.6, "eyes": 0.7},
                {"defense_bonus": 5, "intel_bonus": 3},
                0.08
            ),
            
            # Risorse Organizzazione-Specifiche
            "partygoers_cake": TradeGood(
                "Torta dei Festaioli",
                60,
                4,
                {"partygoers": 0.5},
                {"morale": 10, "corruption": 2},
                0.10
            ),
            "faceling_mask": TradeGood(
                "Maschera dei Senza Volto",
                80,
                4,
                {"facelings": 0.6},
                {"stealth": 5, "corruption": 1},
                0.07
            ),
            "crimson_weapon": TradeGood(
                "Arma dell'Ordine Cremisi",
                70,
                4,
                {"crimson": 0.7},
                {"defense_bonus": 8},
                0.06
            ),
            "ancient_text": TradeGood(
                "Testo Antico",
                90,
                5,
                {"library": 0.6, "eyes": 0.7},
                {"intel_bonus": 10},
                0.08
            ),
        }
        
        self.daily_trades = 0  # Reset giornaliero
        self.infiltration_multiplier = 1.0  # Aumenta con più scambi
        
    def get_price_details(self, good_id: str, organization_id: str, quantity: int = 1, is_buying: bool = True) -> Dict:
        """Calcola e restituisce i dettagli del prezzo di un bene"""
        if good_id not in self.trade_goods:
            return {"success": False, "message": "Bene non disponibile"}
            
        good = self.trade_goods[good_id]
        base_price = good.base_price
        
        # Calcola i vari modificatori
        rarity_multiplier = 1 + (good.rarity - 1) * 0.2
        org_multiplier = (good.organization_bonus.get(organization_id, 1.0) if is_buying 
                         else good.organization_bonus.get(organization_id, 1.0) * 0.8)
        
        # Calcola il prezzo finale
        final_price = int(base_price * rarity_multiplier * org_multiplier * quantity)
        
        return {
            "success": True,
            "details": {
                "base_price": base_price,
                "rarity_multiplier": rarity_multiplier,
                "org_multiplier": org_multiplier,
                "quantity": quantity,
                "final_price": final_price,
                "currency": "supplies",  # Specifica la valuta usata
                "payment_resource": "supplies"  # Risorsa usata per il pagamento
            }
        }
        
    def get_price(self, good_id: str, organization_id: str, is_buying: bool = True) -> int:
        """Versione semplificata che restituisce solo il prezzo finale"""
        price_details = self.get_price_details(good_id, organization_id, 1, is_buying)
        return price_details["details"]["final_price"] if price_details["success"] else 0
        
    def calculate_infiltration_risk(self, good: TradeGood, organization_id: str, game_state) -> float:
        """Calcola il rischio di infiltrazione per uno scambio considerando vari fattori"""
        base_risk = good.infiltration_risk
        
        # Aumenta con il numero di scambi giornalieri
        risk = base_risk * self.infiltration_multiplier
        
        # Aumenta con la rarità del bene
        risk *= (1 + (good.rarity - 1) * 0.1)
        
        # Riduce il rischio in base all'attitudine dell'organizzazione
        org_attitude = game_state.diplomacy.organizations[organization_id].attitude
        attitude_modifier = max(0.5, 1 - (org_attitude / 200))  # Max 50% riduzione
        risk *= attitude_modifier
        
        # Aumenta il rischio se gli scambi sono troppo frequenti
        frequency_penalty = 1 + (self.daily_trades * 0.15)  # +15% per ogni scambio
        risk *= frequency_penalty
        
        # Il sistema di difesa della base riduce il rischio
        defense_bonus = game_state.defense.get_total_defense()
        defense_modifier = max(0.3, 1 - (defense_bonus / 150))  # Max 70% riduzione
        risk *= defense_modifier
        
        return min(risk, 0.75)  # Max 75% di rischio
        
    def trade(self, good_id: str, organization_id: str, quantity: int, 
             is_buying: bool, game_state) -> Dict:
        """Esegue uno scambio commerciale"""
        if good_id not in self.trade_goods:
            return {
                "success": False,
                "message": "Bene non disponibile per il commercio"
            }
            
        good = self.trade_goods[good_id]
        price = self.get_price(good_id, organization_id, is_buying) * quantity
        
        # Verifica risorse sufficienti
        if is_buying:
            if game_state.resources.get("supplies") < price:
                return {
                    "success": False,
                    "message": "Rifornimenti insufficienti per l'acquisto"
                }
        else:
            if game_state.resources.get(good_id) < quantity:
                return {
                    "success": False,
                    "message": f"{good.name} insufficiente per la vendita"
                }
                
        # Esegui lo scambio
        if is_buying:
            game_state.resources.modify("supplies", -price)
            game_state.resources.modify(good_id, quantity)
        else:
            game_state.resources.modify(good_id, -quantity)
            game_state.resources.modify("supplies", int(price * 0.8))  # 20% di perdita nella vendita
            
        # Applica effetti speciali
        if good.special_effects:
            for effect, value in good.special_effects.items():
                if effect == "morale":
                    game_state.stats.morale = min(100, 
                        game_state.stats.morale + value)
                elif effect == "defense_bonus":
                    game_state.defense.defense_rating += value
                elif effect == "intel_bonus":
                    game_state.intel.add_intel_points("level_0", value, 
                        f"Bonus commercio {good.name}")
                elif effect == "medical_bonus":
                    # Implementa bonus medico
                    pass
                elif effect == "corruption":
                    game_state.stats.corruption_level += value
                elif effect == "sanity":
                    # Implementa effetti sanità mentale
                    pass
                    
        # Aumenta attitudine dell'organizzazione
        attitude_gain = good.rarity * (2 if is_buying else 1)
        game_state.diplomacy.modify_relation(organization_id, attitude_gain)
        
        # Gestione scambi e relazioni
        self.daily_trades += 1
        trade_multiplier = 1 + (self.daily_trades * 0.1)
        
        # Calcola bonus relazione basato sulla rarità e quantità
        relation_bonus = good.rarity * quantity * 0.5
        if not is_buying:
            relation_bonus *= 1.2  # Bonus extra quando vendi
            
        # Applica modificatori organizzazione
        if good.organization_bonus and organization_id in good.organization_bonus:
            relation_bonus *= 1.5  # Bonus extra per beni preferiti
            
        # Modifica le relazioni
        game_state.diplomacy.modify_relation(organization_id, relation_bonus)
        
        # Gestione infiltrazione con nuovo sistema
        infiltration_risk = self.calculate_infiltration_risk(good, organization_id, game_state)
        if random.random() < infiltration_risk:
            # Calcola la severità dell'infiltrazione
            severity = random.randint(1, 3)  # 1: Minore, 2: Moderata, 3: Grave
            damage_multiplier = severity * good.rarity
            
            # Seleziona target basato sulla severità
            if severity == 1:
                targets = ["resources"]
            elif severity == 2:
                targets = ["resources", "morale"]
            else:
                targets = ["resources", "morale", "intel"]
                
            infiltration_message = f"Infiltrazione di livello {severity} rilevata!\n"
            
            for target in targets:
                if target == "resources":
                    resources = list(game_state.resources.resources.keys())
                    resource = random.choice(resources)
                    amount = random.randint(5, 10) * damage_multiplier
                    game_state.resources.modify(resource, -amount)
                    infiltration_message += f"- Persi {amount} {resource}\n"
                elif target == "morale":
                    penalty = 5 * damage_multiplier
                    game_state.stats.morale = max(0, game_state.stats.morale - penalty)
                    infiltration_message += f"- Morale diminuito di {penalty}\n"
                else:
                    penalty = 3 * damage_multiplier
                    game_state.intel.add_intel_points("level_0", -penalty, "Infiltrazione")
                    infiltration_message += f"- Persi {penalty} punti intel\n"
                    
            # Peggiora le relazioni in caso di infiltrazione grave
            if severity == 3:
                penalty = relation_bonus * 2
                game_state.diplomacy.modify_relation(organization_id, -penalty)
                infiltration_message += f"- Relazioni peggiorate di {int(penalty)} punti\n"
                
            return {
                "success": True,
                "message": f"Scambio completato con {game_state.diplomacy.organizations[organization_id].name}\n" \
                          f"{'Acquistati' if is_buying else 'Venduti'} {quantity} {good.name}\n" \
                          f"Costo: {price} rifornimenti\n" \
                          f"⚠️ {infiltration_message}"
            }
            
        return {
            "success": True,
            "message": f"Scambio completato con {game_state.diplomacy.organizations[organization_id].name}\n" \
                      f"{'Acquistati' if is_buying else 'Venduti'} {quantity} {good.name}\n" \
                      f"Costo: {price} rifornimenti"
        }
        
    def daily_update(self):
        """Reset giornaliero del sistema di mercato"""
        self.daily_trades = 0
        self.infiltration_multiplier = 1.0
        
    def to_dict(self) -> Dict:
        return {
            "daily_trades": self.daily_trades,
            "infiltration_multiplier": self.infiltration_multiplier
        }
        
    def from_dict(self, data: Dict):
        self.daily_trades = data["daily_trades"]
        self.infiltration_multiplier = data["infiltration_multiplier"]
        
    def reset(self):
        self.__init__()
