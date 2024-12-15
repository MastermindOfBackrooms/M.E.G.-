from typing import Dict

class Resources:
    def __init__(self):
        self.resources = {
            "almond_water": 100,  # Acqua di mandorle
            "food": 100,         # Cibo
            "medical": 50,       # Forniture mediche
            "fuel": 75,          # Carburante
            "supplies": 50       # Rifornimenti generici
        }
        self.consumption_rates = {
            "almond_water": 2,
            "food": 3,
            "medical": 1,
            "fuel": 2,
            "supplies": 1
        }
        
    def get(self, resource: str) -> int:
        return self.resources.get(resource, 0)
        
    def modify(self, resource: str, amount: int) -> bool:
        if resource not in self.resources:
            return False
            
        new_value = self.resources[resource] + amount
        if new_value < 0:
            return False
            
        self.resources[resource] = new_value
        return True
        
    def daily_update(self):
        """Applica il consumo giornaliero delle risorse"""
        for resource, rate in self.consumption_rates.items():
            self.modify(resource, -rate)
            
    def to_dict(self) -> Dict:
        return {
            "resources": self.resources.copy(),
            "consumption_rates": self.consumption_rates.copy()
        }
        
    def from_dict(self, data: Dict):
        self.resources = data["resources"]
        self.consumption_rates = data["consumption_rates"]
        
    def reset(self):
        self.__init__()
