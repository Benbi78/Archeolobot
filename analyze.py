import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import config
from database import DatabaseManager


def analyze_statistics():
    """Affiche des statistiques sur la base de données."""
    db = DatabaseManager()
    
    print("\n" + "="*60)
    print("STATISTIQUES ARCHEOLOBOT")
    print("="*60)
    
    # Récupère les données
    archaeologists = db.get_all_archaeologists()
    
    if not archaeologists:
        print("\nAucune donnée pour le moment.")
        print("="*60 + "\n")
        return
    
    # Statistiques globales
    print("\nSTATISTIQUES GLOBALES")
    print("-" * 60)
    print(f"Nombre d'archéologues: {len(archaeologists)}")
    
    total_excavations = sum(a.total_excavations for a in archaeologists)
    print(f"Fouilles totales: {total_excavations}")
    
    total_artifacts = sum(len(a.artifacts) for a in archaeologists)
    print(f"Artefacts découverts: {total_artifacts}")
    
    total_coins = sum(a.coins for a in archaeologists)
    print(f"Pièces totales en circulation: 💰 {total_coins:,}")
    
    avg_level = sum(a.level for a in archaeologists) / len(archaeologists)
    print(f"Niveau moyen: {avg_level:.1f}")
    
    # Top 5
    print("\nTOP 5 ARCHÉOLOGUES")
    print("-" * 60)
    sorted_arch = sorted(archaeologists, key=lambda a: (a.level, a.experience), reverse=True)
    for idx, arch in enumerate(sorted_arch[:5], 1):
        medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][idx-1]
        print(f"{medal} {arch.username:20} | Niv {arch.level:2} | {arch.experience:4} XP | {len(arch.artifacts)} artefacts")
    
    # Statistiques par rareté
    print("\nARTEFACTS PAR RARETÉ")
    print("-" * 60)
    rarity_count = defaultdict(int)
    for arch in archaeologists:
        for artifact_id in arch.artifacts:
            artifact = db.get_artifact(artifact_id)
            if artifact:
                rarity_count[artifact.rarity] += 1
    
    for rarity in config.RARITY_LEVELS:
        count = rarity_count[rarity]
        if count > 0:
            print(f"  {rarity.capitalize():12} {count:3} artefacts")
    
    # Archéologues par niveau
    print("\nDISTRIBUTION DES NIVEAUX")
    print("-" * 60)
    level_count = defaultdict(int)
    for arch in archaeologists:
        level_count[arch.level] += 1
    
    for level in sorted(level_count.keys()):
        count = level_count[level]
        bar = "█" * count
        print(f"  Niveau {level:2}: {bar} ({count})")
    
    # Activité
    print("\nACTIVITÉ RÉCENTE")
    print("-" * 60)
    recent = sorted(
        archaeologists,
        key=lambda a: a.joined_at,
        reverse=True
    )[:3]
    
    for arch in recent:
        join_date = datetime.fromisoformat(arch.joined_at)
        print(f"  • {arch.username:20} inscrit le {join_date.strftime('%Y-%m-%d')}")
    
    print("\n" + "="*60 + "\n")


def export_statistics(output_file: str = "statistics.json"):
    """Exporte les statistiques en JSON."""
    db = DatabaseManager()
    archaeologists = db.get_all_archaeologists()
    
    data = {
        "timestamp": datetime.now().isoformat(),
        "total_archaeologists": len(archaeologists),
        "total_excavations": sum(a.total_excavations for a in archaeologists),
        "total_artifacts": sum(len(a.artifacts) for a in archaeologists),
        "leaderboard": db.get_leaderboard(limit=50),
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Statistiques exportées dans {output_file}")


if __name__ == "__main__":
    analyze_statistics()
    # Décommenter pour exporter:
    # export_statistics()
