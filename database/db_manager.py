import json
import os
import uuid
from pathlib import Path
from typing import Optional, List

from .models import Archaeologist, Artifact
import config


class DatabaseManager:
    #Gère la persistance des données en JSON.
    
    def __init__(self, db_path: str = config.DATABASE_PATH):
        #Initialise le gestionnaire de base de données.
        self.db_path = db_path
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        #Crée la structure de la base de données si elle n'existe pas.
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        if not os.path.exists(self.db_path):
            initial_data = {
                "archaeologists": {},
                "artifacts": {}
            }
            self._save_data(initial_data)
    
    def _load_data(self) -> dict:
        #Charge les données du fichier JSON.
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            if config.DEBUG:
                print(f"Erreur lors du chargement: {e}")
            return {"archaeologists": {}, "artifacts": {}}
    
    def _save_data(self, data: dict):
        #Sauvegarde les données dans le fichier JSON.
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            if config.DEBUG:
                print(f"Erreur lors de la sauvegarde: {e}")
    
    # ===== Archéologues =====
    
    def get_archaeologist(self, user_id: str) -> Optional[Archaeologist]:
        #Récupère un archéologue par son ID utilisateur.#
        data = self._load_data()
        archaeologist_data = data["archaeologists"].get(str(user_id))
        
        if archaeologist_data:
            return Archaeologist.from_dict(archaeologist_data)
        return None
    
    def create_archaeologist(self, user_id: str, username: str) -> Archaeologist:
        #Crée un nouvel archéologue.
        archaeologist = Archaeologist(
            user_id=str(user_id),
            username=username
        )
        
        data = self._load_data()
        data["archaeologists"][str(user_id)] = archaeologist.to_dict()
        self._save_data(data)
        
        return archaeologist
    
    def save_archaeologist(self, archaeologist: Archaeologist):
        #Sauvegarde les données d'un archéologue.
        data = self._load_data()
        data["archaeologists"][archaeologist.user_id] = archaeologist.to_dict()
        self._save_data(data)
    
    def get_all_archaeologists(self) -> List[Archaeologist]:
        #Récupère tous les archéologues.
        data = self._load_data()
        return [
            Archaeologist.from_dict(a)
            for a in data["archaeologists"].values()
        ]
    
    # ===== Artefacts =====
    
    def create_artifact(
        self, 
        name: str, 
        rarity: str, 
        description: str, 
        value: int, 
        discovered_by: str
    ) -> Artifact:
        #Crée un nouvel artefact.
        artifact = Artifact(
            name=name,
            rarity=rarity,
            description=description,
            value=value,
            discovered_by=discovered_by,
            artifact_id=str(uuid.uuid4())
        )
        
        data = self._load_data()
        data["artifacts"][artifact.artifact_id] = artifact.to_dict()
        self._save_data(data)
        
        return artifact
    
    def get_artifact(self, artifact_id: str) -> Optional[Artifact]:
        #Récupère un artefact par son ID.
        data = self._load_data()
        artifact_data = data["artifacts"].get(artifact_id)
        
        if artifact_data:
            return Artifact.from_dict(artifact_data)
        return None
    
    def get_archaeologist_artifacts(self, user_id: str) -> List[Artifact]:
        #Récupère tous les artefacts d'un archéologue.
        archaeologist = self.get_archaeologist(str(user_id))
        if not archaeologist:
            return []
        
        data = self._load_data()
        artifacts = []
        for artifact_id in archaeologist.artifacts:
            artifact_data = data["artifacts"].get(artifact_id)
            if artifact_data:
                artifacts.append(Artifact.from_dict(artifact_data))
        
        return artifacts

    # ===== Ventes d'artefacts =====

    def sell_single_artifact(self, user_id: str, artifact_name: str) -> tuple[int, Optional[str]]:
        #Vend un artefact par son nom (insensible à la casse). Retourne (coins_gagnés, artifact_id).
        data = self._load_data()
        archaeologist = data["archaeologists"].get(str(user_id))
        if not archaeologist:
            return 0, None

        remaining_artifacts = []
        coins_gained = 0
        sold_id = None

        for artifact_id in archaeologist.get("artifacts", []):
            artifact_data = data["artifacts"].get(artifact_id)
            if artifact_data and artifact_data["name"].lower() == artifact_name.lower() and not sold_id:
                coins_gained += int(artifact_data.get("value", 0))
                sold_id = artifact_id
                # On retire l'artefact vendu de la base
                data["artifacts"].pop(artifact_id, None)
            else:
                remaining_artifacts.append(artifact_id)

        if coins_gained == 0:
            return 0, None

        archaeologist["artifacts"] = remaining_artifacts
        archaeologist["coins"] = archaeologist.get("coins", 0) + coins_gained
        data["archaeologists"][str(user_id)] = archaeologist
        self._save_data(data)

        return coins_gained, sold_id

    def sell_artifacts_by_rarity(self, user_id: str, max_rarity: str) -> tuple[int, int]:
        #Vend tous les artefacts d'une rareté <= max_rarity. Retourne (coins_gagnés, nb_vendus).
        data = self._load_data()
        archaeologist = data["archaeologists"].get(str(user_id))
        if not archaeologist:
            return 0, 0

        if max_rarity not in config.RARITY_LEVELS:
            return 0, 0

        max_index = config.RARITY_LEVELS.index(max_rarity)
        allowed = set(config.RARITY_LEVELS[: max_index + 1])

        remaining_artifacts = []
        coins_gained = 0
        sold_count = 0

        for artifact_id in archaeologist.get("artifacts", []):
            artifact_data = data["artifacts"].get(artifact_id)
            if artifact_data and artifact_data.get("rarity") in allowed:
                coins_gained += int(artifact_data.get("value", 0))
                sold_count += 1
                data["artifacts"].pop(artifact_id, None)
            else:
                remaining_artifacts.append(artifact_id)

        if sold_count == 0:
            return 0, 0

        archaeologist["artifacts"] = remaining_artifacts
        archaeologist["coins"] = archaeologist.get("coins", 0) + coins_gained
        data["archaeologists"][str(user_id)] = archaeologist
        self._save_data(data)

        return coins_gained, sold_count
    
    def get_leaderboard(self, limit: int = 10) -> List[tuple]:
        #Récupère le classement par niveau, expérience et pièces.
        archaeologists = self.get_all_archaeologists()
        sorted_archaeologists = sorted(
            archaeologists,
            key=lambda a: (a.level, a.experience, a.coins),
            reverse=True
        )
        return [
            (a.username, a.level, a.experience, a.coins, len(a.artifacts))
            for a in sorted_archaeologists[:limit]
        ]
