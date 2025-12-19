#Modèles de données pour les archéologues et les artefacts.

from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional


@dataclass
class Artifact:
    #Représente un artefact archéologique découvert.
    
    name: str
    rarity: str
    description: str
    value: int
    discovered_by: str
    discovered_at: str = field(default_factory=lambda: datetime.now().isoformat())
    artifact_id: str = ""
    
    def to_dict(self) -> dict:
        #Convertit l'artefact en dictionnaire.
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Artifact":
        #Crée un artefact à partir d'un dictionnaire.
        return cls(**data)


@dataclass
class Archaeologist:
    #Représente un archéologue (joueur).
    
    user_id: str
    username: str
    level: int = 1
    experience: int = 0
    coins: int = 0
    artifacts: list[str] = field(default_factory=list)
    total_excavations: int = 0
    pickaxe: str = "basic"
    joined_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        #Convertit l'archéologue en dictionnaire.
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Archaeologist":
        #Crée un archéologue à partir d'un dictionnaire.
        return cls(**data)
    
    def add_experience(self, amount: int) -> bool:
        #Ajoute de l'expérience et vérifie la montée de niveau.
        self.experience += amount
        experience_per_level = 100
        
        if self.experience >= self.level * experience_per_level:
            self.level += 1
            return True
        return False
    
    def add_coins(self, amount: int):
        #Ajoute des pièces.#
        self.coins += amount
    
    def add_artifact(self, artifact_id: str):
        #Ajoute un artefact à la collection.
        if artifact_id not in self.artifacts:
            self.artifacts.append(artifact_id)
