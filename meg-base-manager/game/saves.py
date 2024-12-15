import os
import json
from typing import List
from pathlib import Path

class SaveManager:
    def __init__(self):
        self.saves_dir = Path("saves")
        self.saves_dir.mkdir(exist_ok=True)
        
    def get_saves(self) -> List[str]:
        """Returns list of save file names without extension"""
        return [f.stem for f in self.saves_dir.glob("*.json")]
        
    def save_exists(self, name: str) -> bool:
        return (self.saves_dir / f"{name}.json").exists()
        
    def delete_save(self, name: str) -> bool:
        try:
            (self.saves_dir / f"{name}.json").unlink()
            return True
        except FileNotFoundError:
            return False
