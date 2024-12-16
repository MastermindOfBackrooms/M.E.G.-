import random
import json
from typing import List, Dict

class Mission:
    def __init__(self, id: str, title: str, description: str, duration: int,
                 rewards: Dict, valid_levels: str | List[str] | None = None,
                 level_requirements: Dict = None, difficulty_multiplier: Dict = None,
                 chain_mission: Dict = None, prerequisites: Dict = None):
        self.id = id
        self.title = title
        self.description = description
        self.duration = duration
        self.rewards = rewards
        self.valid_levels = valid_levels  # Ora può essere None per missioni senza livello
        self.level_requirements = level_requirements  # Opzionale
        self.difficulty_multiplier = difficulty_multiplier or {}
        self.chain_mission = chain_mission or {}
        self.prerequisites = prerequisites or {}
        self.days_left = duration
        self.completed = False
        self.assigned_agent = None
        self.selected_level = None
        
    def calculate_rewards(self, level_difficulty: int) -> Dict:
        """Calcola le ricompense basate sulla difficoltà del livello"""
        adjusted_rewards = {"resources": {}, "stats": {}}
        
        # Applica i moltiplicatori di difficoltà alle risorse
        if "resources" in self.rewards:
            for resource, amount in self.rewards["resources"].items():
                multiplier = self.difficulty_multiplier.get("resources", 1.0)
                adjusted_amount = int(amount * (1 + (level_difficulty - 1) * (multiplier - 1) / 4))
                adjusted_rewards["resources"][resource] = adjusted_amount
                
        # Applica i moltiplicatori alle statistiche
        if "stats" in self.rewards:
            for stat, amount in self.rewards["stats"].items():
                multiplier = self.difficulty_multiplier.get(stat, 1.0)
                adjusted_amount = int(amount * (1 + (level_difficulty - 1) * (multiplier - 1) / 4))
                adjusted_rewards["stats"][stat] = adjusted_amount
                
        # Aggiusta i punti intel
        if "intel_points" in self.rewards:
            multiplier = self.difficulty_multiplier.get("intel_points", 1.0)
            adjusted_rewards["intel_points"] = int(self.rewards["intel_points"] * 
                                              (1 + (level_difficulty - 1) * (multiplier - 1) / 4))
            
        return adjusted_rewards

class MissionManager:
    def __init__(self):
        self.missions = self.load_missions()
        self.active_missions = []
        self.daily_missions = []  # Lista delle missioni giornaliere disponibili
        self.generate_daily_missions()  # Genera le prime missioni giornaliere
        
    def generate_daily_missions(self, force=False):
        """Genera 8 nuove missioni giornaliere casuali, includendo missioni concatenate quando disponibili
        
        Args:
            force (bool): Se True, forza la rigenerazione anche se ci sono ancora missioni
        """
        # Rigenera solo se non ci sono missioni o se viene forzato
        if force or not self.daily_missions:
            # Filtra le missioni escludendo quelle attive o completate
            available_missions = [m for m in self.missions 
                                if m not in self.active_missions and 
                                not hasattr(m, 'completed_today')]
            
            # Cerca missioni concatenate attualmente disponibili
            chain_missions = [m for m in self.missions 
                            if hasattr(m, 'chain_mission') and m.chain_mission and 
                            m.id in [am.chain_mission.get('next_mission') for am in self.active_missions 
                                   if hasattr(am, 'chain_mission') and am.chain_mission]]
            
            # Rimuove le missioni concatenate non ancora sbloccate dalla pool disponibile
            available_missions = [m for m in available_missions 
                                if m not in chain_missions or 
                                any(am.chain_mission and am.chain_mission.get('next_mission') == m.id 
                                    for am in self.active_missions)]
            
            if available_missions:
                # Assicura che le missioni concatenate disponibili siano incluse
                selected_missions = []
                remaining_slots = 8
                
                # Aggiunge prima le missioni concatenate disponibili
                for chain_mission in chain_missions:
                    if chain_mission in available_missions and remaining_slots > 0:
                        selected_missions.append(chain_mission)
                        available_missions.remove(chain_mission)
                        remaining_slots -= 1
                
                # Riempie i restanti slot con missioni casuali
                if remaining_slots > 0 and available_missions:
                    random_missions = random.sample(available_missions, 
                                                 min(remaining_slots, len(available_missions)))
                    selected_missions.extend(random_missions)
                
                for mission in selected_missions:
                    mission.completed_today = False
                self.daily_missions = selected_missions
        
    def load_missions(self) -> List[Mission]:
        """Carica le missioni dal file JSON"""
        try:
            with open("data/missions.json", encoding='utf-8') as f:
                data = json.load(f)
                missions = []
                for mission_data in data["missions"]:
                    # Imposta valori predefiniti per campi opzionali
                    mission_data.setdefault("valid_levels", "all")
                    mission_data.setdefault("level_requirements", {"min_knowledge": 0, "max_difficulty": 5})
                    mission_data.setdefault("difficulty_multiplier", {})
                    missions.append(Mission(**mission_data))
                return missions
        except Exception as e:
            print(f"Errore nel caricamento delle missioni: {e}")
            return []
            
    def get_mission_by_number(self, number: int) -> Mission:
        """Ottieni una missione dal suo numero (1-based)"""
        if 1 <= number <= len(self.missions):
            return self.missions[number - 1]
        return None
        
    def select_valid_level(self, mission: Mission, game_state) -> str:
        """Seleziona un livello valido per la missione se possibile"""
        # Se non ci sono requisiti di livello, restituisci None
        if not mission.valid_levels or mission.valid_levels == []:
            return None
            
        valid_levels = []
        all_levels = list(game_state.intel.levels_intel.keys())
        
        # Determina i livelli validi
        possible_levels = all_levels if mission.valid_levels == "all" else mission.valid_levels
        
        for level_id in possible_levels:
            level_info = game_state.intel.get_level_info(level_id)
            if not level_info:
                continue
                
            # Verifica requisiti del livello se presenti
            if mission.level_requirements:
                knowledge_level = game_state.intel.levels_intel[level_id].knowledge_level
                if knowledge_level < mission.level_requirements["min_knowledge"]:
                    continue
                    
                if "difficulty" in level_info:
                    if level_info["difficulty"] > mission.level_requirements["max_difficulty"]:
                        continue
                    
            valid_levels.append(level_id)
            
        # Se non ci sono livelli validi, la missione può procedere senza un livello specifico
        if not valid_levels:
            return None
            
        return random.choice(valid_levels)

    def check_prerequisites(self, mission: Mission, game_state) -> tuple[bool, str]:
        """Verifica se i prerequisiti della missione sono soddisfatti"""
        if not mission.prerequisites:
            return True, ""
            
        # Verifica missioni completate richieste
        if "completed_missions" in mission.prerequisites:
            for required_mission_id in mission.prerequisites["completed_missions"]:
                completed = any(m.id == required_mission_id and m.completed 
                              for m in self.missions)
                if not completed:
                    return False, f"Richiede il completamento della missione: {required_mission_id}"
        
        # Verifica prestigio minimo
        if "min_prestige" in mission.prerequisites:
            if game_state.stats.prestige < mission.prerequisites["min_prestige"]:
                return False, f"Richiede prestigio minimo: {mission.prerequisites['min_prestige']}"
                
        # Verifica intel totale minimo
        if "min_intel_total" in mission.prerequisites:
            total_intel = sum(level.intel_points for level in game_state.intel.levels_intel.values())
            if total_intel < mission.prerequisites["min_intel_total"]:
                return False, f"Richiede punti intel totali: {mission.prerequisites['min_intel_total']}"
                
        # Verifica corruzione minima se presente
        if "min_corruption" in mission.prerequisites:
            if not hasattr(game_state.stats, "corruption") or \
               game_state.stats.corruption < mission.prerequisites["min_corruption"]:
                return False, f"Richiede corruzione minima: {mission.prerequisites['min_corruption']}"
                
        # Verifica agenti persi se richiesto
        if "lost_agents" in mission.prerequisites:
            if not hasattr(game_state.stats, "lost_agents") or \
               game_state.stats.lost_agents < mission.prerequisites["lost_agents"]:
                return False, f"Richiede {mission.prerequisites['lost_agents']} agenti persi"
                
        return True, ""

    def start_mission(self, mission_number: int, agent_id: str, game_state) -> Dict:
        if not 1 <= mission_number <= len(self.daily_missions):
            return {"success": False, "message": "Numero missione non valido"}
            
        mission = self.daily_missions[mission_number - 1]
        
        # Verifica prerequisiti
        prerequisites_met, error_message = self.check_prerequisites(mission, game_state)
        if not prerequisites_met:
            return {"success": False, "message": f"Prerequisiti non soddisfatti: {error_message}"}
            
        # Rimuove la missione dalle missioni giornaliere
        if mission in self.daily_missions:
            self.daily_missions.remove(mission)
            # Rigenera le missioni solo se non ce ne sono più
            if not self.daily_missions:
                self.generate_daily_missions(force=True)
            
        # Verifica agente
        agent = game_state.personnel.get_agent(agent_id)
        if not agent or agent.status != "disponibile":
            return {"success": False, "message": "Agente non disponibile"}
            
        # Seleziona un livello valido se possibile
        selected_level = self.select_valid_level(mission, game_state)
        level_difficulty = 1
        
        # Se c'è un livello selezionato, ottieni le sue informazioni
        if selected_level:
            level_info = game_state.intel.get_level_info(selected_level)
            if level_info:
                level_difficulty = level_info.get("difficulty", 1)
                
        # Assegna agente alla missione
        game_state.personnel.assign_mission(agent_id, mission.title)
        
        # Calcola ricompense basate sulla difficoltà (se c'è un livello) o usa valori base
        mission.adjusted_rewards = mission.calculate_rewards(level_difficulty)
        
        mission.assigned_agent = agent_id
        mission.selected_level = selected_level
        self.active_missions.append(mission)
        
        # Prepara il messaggio di successo appropriato
        if selected_level and 'level_info' in locals():
            success_message = f"Missione avviata con {agent.name} nel {level_info['name']}"
            level_name = level_info['name']
        else:
            success_message = f"Missione avviata con {agent.name}"
            level_name = "nessun livello specifico"

        return {
            "success": True,
            "message": success_message,
            "level": level_name,
            "difficulty": level_difficulty
        }
        
    def calculate_death_probability(self, mission, agent, level_info):
        """Calcola la probabilità di morte dell'agente durante la missione"""
        # Aumentata la probabilità base per ogni livello di difficoltà
        base_probability = level_info.get("difficulty", 1) * 0.05  # 5% per livello di difficoltà
        
        # La durata della missione influisce maggiormente
        mission_modifier = mission.duration * 0.02  # 2% per giorno di missione
        
        # L'esperienza aiuta meno a ridurre il rischio
        experience_modifier = 0.05 - (agent.exp * 0.005)  # -0.5% per livello di esperienza
        
        # Aggiungi modificatore basato sul livello di conoscenza del livello
        intel_level = level_info.get("knowledge_level", 0)
        intel_modifier = 0.1 - (intel_level * 0.015)  # -1.5% per livello di intel
        
        final_probability = (base_probability + mission_modifier - experience_modifier + intel_modifier)
        
        # Aumentato il range di probabilità
        return max(0.05, min(0.75, final_probability))  # Limita tra 5% e 75%

    def check_chain_mission_requirements(self, mission: Mission, game_state) -> bool:
        """Verifica se i requisiti per sbloccare la prossima missione della catena sono soddisfatti"""
        if not mission.chain_mission:
            return False
            
        if "required_intel" in mission.chain_mission:
            # Verifica se il livello ha abbastanza punti intel
            if mission.selected_level:
                level_intel = game_state.intel.levels_intel.get(mission.selected_level)
                if level_intel and level_intel.intel_points >= mission.chain_mission["required_intel"]:
                    return True
        return False

    def unlock_next_chain_mission(self, mission: Mission):
        """Sblocca la prossima missione nella catena e fornisce feedback dettagliato"""
        if not mission.chain_mission or "next_mission" not in mission.chain_mission:
            return
            
        next_mission_id = mission.chain_mission["next_mission"]
        next_mission = next((m for m in self.missions if m.id == next_mission_id), None)
        
        if next_mission and next_mission not in self.daily_missions:
            self.daily_missions.append(next_mission)
            print(f"\n[bold green]Nuova missione sbloccata nella catena![/]")
            print(f"Titolo: {next_mission.title}")
            print(f"Descrizione: {next_mission.description}")
            if next_mission.prerequisites:
                print("\nPrerequisiti:")
                if "min_prestige" in next_mission.prerequisites:
                    print(f"- Prestigio minimo richiesto: {next_mission.prerequisites['min_prestige']}")
                if "min_intel_total" in next_mission.prerequisites:
                    print(f"- Punti intel totali richiesti: {next_mission.prerequisites['min_intel_total']}")
            print("\nQuesta missione è collegata alla catena di eventi in corso.")
            print("Completala per svelare ulteriori misteri delle Backrooms.")

    def update_missions(self, game_state):
        completed = []
        for mission in self.active_missions:
            mission.days_left -= 1
            
            # Controlla la possibilità di morte dell'agente ogni giorno
            if mission.assigned_agent:
                agent = game_state.personnel.get_agent(mission.assigned_agent)
                level_info = game_state.intel.get_level_info(mission.selected_level)
                
                if agent and level_info:
                    death_probability = self.calculate_death_probability(mission, agent, level_info)
                    if random.random() < death_probability:
                        # Effetti più severi per la morte di un agente
                        print(f"\n[ALERT] L'agente {agent.name} è morto durante la missione '{mission.title}'")
                        print(f"Causa: Incidente fatale nel {level_info['name']}")
                        
                        # Rimuovi l'agente
                        game_state.personnel.remove_agent(mission.assigned_agent)
                        
                        # Impatto grave sul morale
                        morale_loss = 30 + (agent.level * 5)  # Più l'agente era esperto, più grave è la perdita
                        game_state.stats.morale -= morale_loss
                        print(f"Il morale della base è crollato di {morale_loss} punti")
                        
                        # Perdita di prestigio
                        prestige_loss = 10 + (agent.level * 2)
                        game_state.stats.prestige -= prestige_loss
                        print(f"Il prestigio della base è diminuito di {prestige_loss} punti")
                        
                        # Perdita di risorse per le operazioni di recupero
                        recovery_resources = {
                            "almond_water": 5 + mission.duration,
                            "med_supplies": 3 + mission.duration,
                            "supplies": 5 + mission.duration
                        }
                        for resource, amount in recovery_resources.items():
                            game_state.resources.modify(resource, -amount)
                            print(f"Persi {amount} {resource} nelle operazioni di recupero")
                            
                        # La morte di un agente può destabilizzare il livello
                        if random.random() < 0.3:  # 30% di chance
                            intel_loss = random.randint(10, 25)
                            game_state.intel.levels_intel[mission.selected_level].intel_points -= intel_loss
                            print(f"La morte dell'agente ha destabilizzato il livello, persi {intel_loss} punti intel")
                        
                        mission.completed = True
                        completed.append(mission)
                        continue
            
            if mission.days_left <= 0:
                mission.completed = True
                completed.append(mission)
                
                # Assegna ricompense
                if hasattr(mission, 'adjusted_rewards'):
                    print(f"\nAssegnando ricompense per {mission.title}:")
                    
                    # Risorse
                    for resource, amount in mission.adjusted_rewards.get("resources", {}).items():
                        success = game_state.resources.modify(resource, amount)
                        print(f"- Risorsa {resource}: {amount} ({'successo' if success else 'fallito'})")
                    
                    # Statistiche
                    for stat, amount in mission.adjusted_rewards.get("stats", {}).items():
                        if hasattr(game_state.stats, stat):
                            current = getattr(game_state.stats, stat)
                            setattr(game_state.stats, stat, current + amount)
                            print(f"- Statistica {stat}: +{amount} (nuovo valore: {getattr(game_state.stats, stat)})")
                        else:
                            print(f"- Statistica {stat} non trovata")
                    
                    # Intel points per il livello specifico
                    if "intel_points" in mission.adjusted_rewards and mission.selected_level:
                        points = mission.adjusted_rewards["intel_points"]
                        game_state.intel.add_intel_points(
                            mission.selected_level,
                            points,
                            f"Missione: {mission.title}"
                        )
                        print(f"- Intel Points: +{points} per livello {mission.selected_level}")
                        
                        # Controlla se si può sbloccare la prossima missione della catena
                        if self.check_chain_mission_requirements(mission, game_state):
                            self.unlock_next_chain_mission(mission)
                
                # Libera l'agente se è sopravvissuto
                if mission.assigned_agent:
                    agent = game_state.personnel.get_agent(mission.assigned_agent)
                    if agent:
                        game_state.personnel.free_agent(mission.assigned_agent)
                        # Aumenta l'esperienza dell'agente
                        game_state.personnel.increase_agent_experience(mission.assigned_agent, 1)
                
                print("\nPremi INVIO per continuare...")
                input()
                print("\n")  # Aggiunge solo una riga vuota per separazione
                
        self.active_missions = [m for m in self.active_missions if not m.completed]
        return completed
        
    def to_dict(self) -> Dict:
        return {
            "active_missions": [
                {
                    "id": m.id,
                    "days_left": m.days_left,
                    "completed": m.completed,
                    "assigned_agent": m.assigned_agent,
                    "selected_level": m.selected_level
                } for m in self.active_missions
            ],
            "daily_missions": [m.id for m in self.daily_missions]
        }
        
    def from_dict(self, data: Dict):
        self.active_missions = []
        for mission_data in data["active_missions"]:
            mission = next((m for m in self.missions if m.id == mission_data["id"]), None)
            if mission:
                mission.days_left = mission_data["days_left"]
                mission.completed = mission_data["completed"]
                mission.assigned_agent = mission_data.get("assigned_agent")
                mission.selected_level = mission_data.get("selected_level")
                self.active_missions.append(mission)
        
        # Ripristina le missioni giornaliere
        self.daily_missions = []
        if "daily_missions" in data:
            for mission_id in data["daily_missions"]:
                mission = next((m for m in self.missions if m.id == mission_id), None)
                if mission:
                    self.daily_missions.append(mission)
        if not self.daily_missions:
            self.generate_daily_missions()
                
    def reset(self):
        self.active_missions = []
