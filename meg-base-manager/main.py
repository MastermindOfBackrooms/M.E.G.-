from rich.console import Console
from game.base import GameState
from game.ui import UI

def main():
    console = Console()
    game = GameState()
    ui = UI(console, game)
    
    ui.show_welcome()
    
    while True:
        ui.show_main_menu()
        choice = ui.get_input()
        
        if choice == "1":
            ui.start_new_game()
        elif choice == "2":
            ui.load_game()
        elif choice == "3":
            ui.show_help()
        elif choice == "4":
            if ui.confirm_exit():
                break
        else:
            ui.show_error("Scelta non valida")

if __name__ == "__main__":
    main()
