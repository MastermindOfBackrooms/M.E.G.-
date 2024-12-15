from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
import random
from .base import GameState
from .saves import SaveManager

class UI:
    def __init__(self, console: Console, game: GameState):
        self.console = console
        self.game = game
        self.save_manager = SaveManager()
        
    def show_welcome(self):
        self.console.print(Panel(
            "[bold yellow]Benvenuto al simulatore di Base M.E.G.[/]\n\n"
            "Sei il nuovo direttore di una base del M.E.G. nelle Backrooms.\n"
            "Il tuo compito è gestire risorse, personale e missioni per sopravvivere.\n\n"
            "[dim]Creato da Jashin L.[/]",
            title="M.E.G. Base Manager",
            box=box.DOUBLE
        ))
        
    def show_main_menu(self):
        self.console.print("\n[bold cyan]Menu Principale[/]")
        self.console.print("1. Nuova Partita")
        self.console.print("2. Carica Partita")
        self.console.print("3. Aiuto")
        self.console.print("4. Esci")
        
    def show_game_menu(self):
        self.console.print("\n[bold cyan]Menu Gioco[/]")
        self.console.print("1. Gestione Risorse")
        self.console.print("2. Gestione Personale")
        self.console.print("3. Missioni")
        self.console.print("4. Strutture")
        self.console.print("5. Intelligence")
        self.console.print("6. Diplomazia")
        self.console.print("7. Avanza Giorno")
        self.console.print("8. Salva")
        self.console.print("9. Torna al Menu")
        
    def show_stats(self):
        table = Table(title=f"Giorno {self.game.stats.day}")
        table.add_column("Statistica", style="cyan")
        table.add_column("Valore", justify="right")
        
        table.add_row("Prestigio", str(self.game.stats.prestige))
        table.add_row("Morale", str(self.game.stats.morale))
        
        self.console.print(table)
        
    def show_resources(self):
        table = Table(title="Risorse")
        table.add_column("Risorsa", style="cyan")
        table.add_column("Quantità", justify="right")
        table.add_column("Consumo/giorno", justify="right", style="red")
        
        for resource, amount in self.game.resources.resources.items():
            consumption = self.game.resources.consumption_rates[resource]
            table.add_row(
                resource.replace("_", " ").title(),
                str(amount),
                str(consumption)
            )
            
        self.console.print(table)
        
    def show_personnel(self):
        table = Table(title="Personale")
        table.add_column("ID", style="dim")
        table.add_column("Nome")
        table.add_column("Ruolo", style="cyan")
        table.add_column("Livello", justify="right")
        table.add_column("Exp", justify="right")
        table.add_column("Morale", justify="right")
        table.add_column("Stato")
        table.add_column("Abilità", justify="right")
        
        for agent in self.game.personnel.agents:
            abilities = f"C:{agent.combat} R:{agent.research} S:{agent.survival} D:{agent.diplomacy} M:{agent.medical}"
            table.add_row(
                agent.id,
                agent.name,
                agent.role,
                str(agent.level),
                str(agent.exp),
                str(agent.morale),
                agent.status,
                abilities
            )
            
        self.console.print(table)

    def show_missions(self):
        """Mostra le missioni disponibili usando pannelli"""
        self.console.print("\n[bold green]═══ MISSIONI DISPONIBILI ═══[/]")
        
        # Seleziona casualmente 8 missioni
        available_missions = self.game.missions.missions
        displayed_missions = available_missions if len(available_missions) <= 8 else random.sample(available_missions, 8)
        
        for idx, mission in enumerate(displayed_missions, 1):
            # Formatta le ricompense
            rewards = []
            for category, items in mission.rewards.items():
                if isinstance(items, dict):
                    for item, amount in items.items():
                        rewards.append(f"[yellow]{item.replace('_', ' ').title()}: {amount}[/]")
                else:
                    rewards.append(f"[yellow]{category.replace('_', ' ').title()}: {items}[/]")
            
            # Crea un pannello per ogni missione
            mission_text = (
                f"[bold cyan]Missione #{idx}:[/] [bold white]{mission.title}[/]\n"
                f"[dim]STATUS:[/] [green]Disponibile[/]  [dim]DURATA:[/] [blue]{mission.duration}g[/]\n"
                f"\n[dim]DESCRIZIONE:[/]\n{mission.description}\n"
                f"\n[dim]RICOMPENSE:[/]\n" + "\n".join(rewards)
            )
            
            self.console.print(Panel(
                mission_text,
                border_style="blue",
                expand=False,
                padding=(1, 2)
            ))
            self.console.print("")  # Aggiunge spazio tra le missioni
        
        if self.game.missions.active_missions:
            active_table = Table(title="Missioni Attive")
            active_table.add_column("Titolo", style="cyan")
            active_table.add_column("Giorni Rimanenti", justify="right")
            
            for mission in self.game.missions.active_missions:
                active_table.add_row(
                    mission.title,
                    str(mission.days_left)
                )
            
            self.console.print("\n")
            self.console.print(active_table)
        
    def get_input(self, prompt: str = "> ") -> str:
        return self.console.input(prompt)
        
    def show_error(self, message: str):
        self.console.print(f"[bold red]Errore:[/] {message}")
        
    def confirm_exit(self) -> bool:
        response = self.get_input("Sei sicuro di voler uscire? (s/n) ")
        return response.lower() == "s"
        
    def start_new_game(self):
        self.game.new_game()
        self.run_game()
        
    def load_game(self):
        saves = self.save_manager.get_saves()
        if not saves:
            self.show_error("Nessun salvataggio trovato")
            return
            
        self.console.print("\nSalvataggi disponibili:")
        for save in saves:
            self.console.print(f"- {save}")
            
        save_name = self.get_input("\nNome del salvataggio da caricare: ")
        try:
            self.game.load_game(save_name)
            self.run_game()
        except ValueError as e:
            self.show_error(str(e))
            
    def run_game(self):
        while True:
            self.show_stats()
            self.show_game_menu()
            choice = self.get_input()
            
            if choice == "1":
                self.show_resources()
            elif choice == "2":
                self.show_personnel()
            elif choice == "3":
                self.show_missions()
                
                self.console.print("\n[bold cyan]Azioni Missioni[/]")
                self.console.print("1. Avvia Nuova Missione")
                self.console.print("2. Torna al Menu")
                
                mission_choice = self.get_input()
                
                if mission_choice == "1":
                    try:
                        mission_number = int(self.get_input("Inserisci il numero della missione: "))
                        
                        # Mostra agenti disponibili
                        self.console.print("\nAgenti Disponibili:")
                        available_agents = [agent for agent in self.game.personnel.agents if agent.status == "disponibile"]
                        for idx, agent in enumerate(available_agents, 1):
                            self.console.print(f"{idx}. {agent.name} ({agent.role})")
                            
                        if not available_agents:
                            self.show_error("Nessun agente disponibile per la missione.")
                            return
                            
                        agent_num = int(self.get_input("\nSeleziona il numero dell'agente: "))
                        if 1 <= agent_num <= len(available_agents):
                            agent_id = available_agents[agent_num - 1].id
                            result = self.game.missions.start_mission(mission_number, agent_id, self.game)
                            if result["success"]:
                                self.console.print(f"[green]{result['message']}[/]")
                            else:
                                self.show_error(result["message"])
                        else:
                            self.show_error("Numero agente non valido.")
                    except ValueError:
                        self.show_error("Inserisci un numero valido.")
                        
            elif choice == "4":
                self.show_defense()
                defense_choice = self.get_input()
                
                if defense_choice == "1":
                    try:
                        struct_num = int(self.get_input("Inserisci il numero della struttura da costruire: "))
                        if self.game.defense.build_structure(struct_num, self.game):
                            self.console.print("[green]Struttura costruita con successo![/]")
                        else:
                            self.show_error("Risorse insufficienti o struttura non valida")
                    except ValueError:
                        self.show_error("Inserisci un numero valido")
                elif defense_choice == "2":
                    self.console.print("\n1. Aumenta Livello Allerta")
                    self.console.print("2. Diminuisci Livello Allerta")
                    alert_choice = self.get_input()
                    effects = None
                    if alert_choice == "1":
                        effects = self.game.defense.increase_alert()
                    elif alert_choice == "2":
                        effects = self.game.defense.decrease_alert()
                        
                    if effects:
                        self.console.print(f"\n[bold yellow]Livello Allerta cambiato da {effects['old_level']} a {effects['new_level']}[/]")
                        self.console.print(f"Effetti:")
                        self.console.print(f"- Morale: {effects['morale_effect']:+}")
                        self.console.print(f"- Difesa: {effects['defense_bonus']:+}")
                        self.console.print(f"- Consumo Risorse: x{effects['resource_multiplier']:.1f}")
                    else:
                        self.console.print("[yellow]Livello di allerta non può essere modificato ulteriormente.[/]")
                        
            elif choice == "5":
                self.show_intel()
            elif choice == "6":
                self.show_diplomacy()
            elif choice == "7":
                self.game.advance_day()
                self.show_daily_report()
            elif choice == "8":
                save_name = self.get_input("Nome del salvataggio: ")
                self.game.save_game(save_name)
                self.console.print("[green]Gioco salvato![/]")
            elif choice == "9":
                if self.confirm_exit():
                    break
            else:
                self.show_error("Scelta non valida")
                
    def show_help(self):
        self.console.print(Panel(
            "[italic]Note trovate su un vecchio terminale delle Backrooms...[/]\n\n"
            "Se stai leggendo questo, sei il nuovo direttore. Ecco alcuni consigli:\n\n"
            "- Le mura non sono sempre quello che sembrano\n"
            "- Ascolta i tuoi agenti, specialmente quando parlano di luci strane\n"
            "- L'acqua di mandorla è vita, letteralmente\n"
            "- Non tutti i vagabondi sono ostili, alcuni potrebbero sorprenderti\n"
            "- Se senti una festa in lontananza, non seguirla\n"
            "- Il morale è importante quanto le risorse\n"
            "- [dim]L'ultima riga è stata cancellata...[/]",
            title="Guida Misteriosa",
            box=box.DOUBLE
        ))

    def show_intel(self):
        """Mostra le informazioni di intelligence sui livelli"""
        for level_id in self.game.intel.levels_intel:
            info = self.game.intel.get_level_info(level_id)
            if not info:
                continue
                
            table = Table(title=f"Intel: {info['name']}")
            table.add_column("Informazione", style="cyan")
            table.add_column("Dettaglio")
            
            table.add_row(
                "Livello Conoscenza",
                f"{info['knowledge_level']}/5"
            )
            
            table.add_row("Descrizione", info['description'])
            
            if "difficulty" in info:
                table.add_row("Difficoltà", str(info['difficulty']))
                table.add_row("Livello Pericolo", info['danger_level'])
                
            if "entities" in info:
                table.add_row("Entità", ", ".join(info['entities']))
                
            if "resources" in info:
                table.add_row("Risorse", ", ".join(info['resources']))
                
            if "special_items" in info:
                table.add_row("Oggetti Speciali", ", ".join(info['special_items']))
                
            if "discovered_secrets" in info:
                secrets = info['discovered_secrets']
                if secrets:
                    table.add_row("Segreti Scoperti", "\n".join(secrets))
                    
            self.console.print("\n")
            self.console.print(table)

    def show_diplomacy(self):
        """Mostra il sistema diplomatico e permette interazioni con altre organizzazioni"""
        if not self.game.diplomacy.has_embassy():
            self.console.print("[yellow]Costruisci un'Ambasciata per sbloccare le interazioni diplomatiche![/]")
            return

        table = Table(title="Relazioni Diplomatiche")
        table.add_column("Organizzazione", style="cyan")
        table.add_column("Attitudine", justify="right")
        table.add_column("Intel", justify="center")
        table.add_column("Militare", justify="center")
        table.add_column("Bonus Commercio", justify="right")

        for org_id, org in self.game.diplomacy.organizations.items():
            intel_status = "✓" if org.intel_sharing else "✗"
            military_status = "✓" if org.military_support else "✗"
            
            attitude_color = "red"
            if org.attitude >= 80:
                attitude_color = "green"
            elif org.attitude >= 50:
                attitude_color = "yellow"
                
            # Prepara bonus speciali
            special_bonuses = []
            if org.id == "partygoers":
                special_bonuses.append("Bonus: Eventi speciali")
            elif org.id == "meg":
                special_bonuses.append("Bonus: Rifornimenti extra")
            elif org.id == "bluestar":
                special_bonuses.append("Bonus: Tecnologie avanzate")
            elif org.id == "crimson":
                special_bonuses.append("Bonus: Supporto militare")
            elif org.id == "library":
                special_bonuses.append("Bonus: Conoscenza antica")
            elif org.id == "wanderers":
                special_bonuses.append("Bonus: Rotte commerciali")
            elif org.id == "eyes":
                special_bonuses.append("Bonus: Intel speciale")
            elif org.id == "facelings":
                special_bonuses.append("Bonus: Poteri sovrannaturali")
                
            table.add_row(
                f"{org.name}\n{org.description}\n[dim]{', '.join(special_bonuses)}[/]",
                f"[{attitude_color}]{org.attitude}[/]",
                intel_status,
                military_status,
                f"x{org.trade_bonus:.1f}"
            )

        self.console.print(table)

        self.console.print("\n[bold cyan]Azioni Diplomatiche[/]")
        self.console.print("1. Richiedi Supporto")
        self.console.print("2. Torna al Menu")

        choice = self.get_input()
        
        if choice == "1":
            self.console.print("\nScegli un'organizzazione:")
            for idx, (org_id, org) in enumerate(self.game.diplomacy.organizations.items(), 1):
                self.console.print(f"{idx}. {org.name}")
                
            try:
                org_choice = int(self.get_input("Numero organizzazione: "))
                if 1 <= org_choice <= len(self.game.diplomacy.organizations):
                    org_id = list(self.game.diplomacy.organizations.keys())[org_choice - 1]
                    
                    self.console.print("\nTipo di supporto:")
                    self.console.print("1. Militare")
                    self.console.print("2. Intelligence")
                    
                    help_choice = self.get_input()
                    help_type = "military" if help_choice == "1" else "intel"
                    
                    result = self.game.diplomacy.request_help(org_id, help_type, self.game)
                    if result["success"]:
                        self.console.print(f"[green]{result['message']}[/]")
                    else:
                        self.console.print(f"[red]{result['message']}[/]")
                else:
                    self.show_error("Numero organizzazione non valido")
            except ValueError:
                self.show_error("Inserisci un numero valido")
                
    def show_daily_report(self):
        """Mostra il resoconto della giornata"""
        self.console.print("\n[bold cyan]Resoconto Giornaliero[/]")
        
        # Produzione strutture
        production_table = Table(title="Produzione Strutture")
        production_table.add_column("Struttura")
        production_table.add_column("Risorsa")
        production_table.add_column("Quantità", justify="right")
        
        for structure in self.game.defense.structures:
            for resource, amount in structure.daily_production.items():
                production_table.add_row(
                    structure.name,
                    resource.replace("_", " ").title(),
                    str(amount)
                )
        
        self.console.print(production_table)
        
        # Missioni completate
        if self.game.missions.active_missions:
            mission_table = Table(title="Stato Missioni")
            mission_table.add_column("Missione")
            mission_table.add_column("Agente")
            mission_table.add_column("Giorni Rimasti")
            
            for mission in self.game.missions.active_missions:
                agent = self.game.personnel.get_agent(mission.assigned_agent)
                mission_table.add_row(
                    mission.title,
                    agent.name if agent else "N/A",
                    str(mission.days_left)
                )
            
            self.console.print("\n")
            self.console.print(mission_table)
        
        # Eventi del giorno
        if self.game.events.active_events:
            event_table = Table(title="Eventi del Giorno")
            event_table.add_column("Evento")
            event_table.add_column("Descrizione")
            
            for event in self.game.events.active_events:
                event_table.add_row(event.title, event.description)
            
            self.console.print("\n")
            self.console.print(event_table)

    def show_defense(self):
        """Mostra lo stato del sistema difensivo e le strutture disponibili"""
        # Mostra statistiche di difesa
        stats_table = Table(title="Statistiche Difensive")
        stats_table.add_column("Statistica", style="cyan")
        stats_table.add_column("Valore", justify="right")
        
        alert_effects = self.game.defense.get_alert_effects()
        stats_table.add_row("Livello Allerta", f"{self.game.defense.alert_level}/5")
        stats_table.add_row("Difesa Totale", str(self.game.defense.get_total_defense()))
        stats_table.add_row("Effetto Morale", f"{alert_effects['morale_effect']:+}")
        stats_table.add_row("Consumo Risorse", f"x{alert_effects['resource_multiplier']:.1f}")
        stats_table.add_row("Resistenza Infiltrazioni", f"{alert_effects['infiltration_resistance']}%")
        stats_table.add_row("Bonus Ricerca", str(self.game.defense.get_research_bonus(self.game.personnel)))
        stats_table.add_row("Bonus Medico", str(self.game.defense.get_medical_bonus(self.game.personnel)))
        stats_table.add_row("Bonus Diplomatico", str(self.game.defense.get_diplomatic_bonus(self.game.personnel)))
        stats_table.add_row("Bonus Sopravvivenza", str(self.game.defense.get_survival_bonus(self.game.personnel)))
        stats_table.add_row("Bonus Morale", str(self.game.defense.get_morale_bonus(self.game.personnel)))
        
        self.console.print(stats_table)
        
        # Mostra strutture disponibili
        available_table = Table(title="\nStrutture Disponibili")
        available_table.add_column("ID", style="dim")
        available_table.add_column("Nome", style="cyan")
        available_table.add_column("Bonus", justify="left")
        available_table.add_column("Costo", justify="right")
        available_table.add_column("Produzione", justify="right")
        
        for idx, (struct_id, struct) in enumerate(self.game.defense.available_structures.items(), 1):
            # Prepara lista bonus
            bonuses = []
            if struct.defense_bonus: bonuses.append(f"Difesa +{struct.defense_bonus}")
            if struct.research_bonus: bonuses.append(f"Ricerca +{struct.research_bonus}")
            if struct.medical_bonus: bonuses.append(f"Medico +{struct.medical_bonus}")
            if struct.diplomatic_bonus: bonuses.append(f"Diplomatico +{struct.diplomatic_bonus}")
            if struct.survival_bonus: bonuses.append(f"Sopravvivenza +{struct.survival_bonus}")
            if struct.morale_bonus: bonuses.append(f"Morale +{struct.morale_bonus}")
            
            # Prepara costi
            costs = [f"{amount} {resource}" for resource, amount in struct.resource_cost.items()]
            
            # Prepara produzione
            production = []
            for resource, amount in struct.daily_production.items():
                if amount > 0:
                    production.append(f"+{amount} {resource}")
                else:
                    production.append(f"{amount} {resource}")
            
            available_table.add_row(
                str(idx),
                struct.name,
                "\n".join(bonuses),
                "\n".join(costs),
                "\n".join(production) if production else "-"
            )
            
        self.console.print(available_table)
        
        # Menu azioni
        self.console.print("\n[bold cyan]Azioni Strutture[/]")
        self.console.print("1. Costruisci Struttura")
        self.console.print("2. Modifica Livello Allerta")
        self.console.print("3. Torna al Menu")
        
        if self.game.defense.structures:
            struct_table = Table(title="Strutture della Base")
            struct_table.add_column("Nome")
            struct_table.add_column("Livello", justify="right")
            struct_table.add_column("Bonus", justify="right")
            struct_table.add_column("Specialisti", justify="right")
            
            for struct in self.game.defense.structures:
                bonus_list = []
                if struct.defense_bonus: bonus_list.append(f"Difesa: +{struct.defense_bonus}")
                if struct.research_bonus: bonus_list.append(f"Ricerca: +{struct.research_bonus}")
                if struct.medical_bonus: bonus_list.append(f"Medico: +{struct.medical_bonus}")
                if struct.diplomatic_bonus: bonus_list.append(f"Diplomatico: +{struct.diplomatic_bonus}")
                if struct.survival_bonus: bonus_list.append(f"Sopravvivenza: +{struct.survival_bonus}")
                if struct.morale_bonus: bonus_list.append(f"Morale: +{struct.morale_bonus}")
                
                specialists = []
                if struct.specialist_bonus:
                    for role, bonus in struct.specialist_bonus.items():
                        specialists.append(f"{role}: x{bonus}")
                
                struct_table.add_row(
                    struct.name,
                    str(struct.level),
                    "\n".join(bonus_list),
                    "\n".join(specialists)
                )
            
            self.console.print("\n")
            self.console.print(struct_table)
