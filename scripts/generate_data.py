import pandas as pd
import numpy as np
import json
import random
from datetime import datetime, timedelta
import os

# Si le dossier Docker existe, on l'utilise. Sinon, on utilise le dossier local "data"
if os.path.exists("/opt/airflow/data"):
    DATA_DIR = "/opt/airflow/data"
else:
    DATA_DIR = "data"

print(f" Répertoire de génération des données : {DATA_DIR}")

# Assurer que le dossier data existe
os.makedirs(DATA_DIR, exist_ok=True)

# Configuration de la simulation
NUM_PLAYERS = 100000
NUM_DAYS = 30
START_DATE = datetime(2026, 1, 1)

# Liste de joueurs fictifs
PLAYERS = [f"Player_{i}" for i in range(1, NUM_PLAYERS + 1)]

def generate_gps_data():
    """Simule des données GPS brutes (CSV) exportées par des gilets type Catapult/StatsSports"""
    print(" Génération des données GPS...")
    gps_records = []
    
    for day in range(NUM_DAYS):
        current_date = START_DATE + timedelta(days=day)
        is_match_day = (day % 7 == 6) # Match tous les dimanches
        
        for player_id in PLAYERS:
            # Simulation réaliste : Un match est plus intense qu'un entraînement
            if is_match_day:
                duration = random.randint(90, 100) # Minutes
                distance = random.normalvariate(10500, 1000) # Moyenne 10.5km
                high_speed_running = random.normalvariate(800, 200) # Mètres > 20km/h
                max_speed = random.normalvariate(31.5, 2.0) # km/h
            else:
                duration = random.randint(60, 90)
                distance = random.normalvariate(6000, 1500)
                high_speed_running = random.normalvariate(300, 100)
                max_speed = random.normalvariate(28.0, 3.0)
            
            # Introduction de quelques données manquantes/aberrantes (pour le nettoyage plus tard)
            if random.random() < 0.05: 
                distance = -100 # Erreur capteur
            
            gps_records.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "player_id": player_id,
                "session_type": "Match" if is_match_day else "Training",
                "duration_min": int(duration),
                "total_distance_m": round(distance, 2),
                "hsr_distance_m": round(high_speed_running, 2),
                "max_speed_kmh": round(max_speed, 2)
            })
            
    df_gps = pd.DataFrame(gps_records)
    # Utilisation du chemin dynamique
    df_gps.to_csv(f"{DATA_DIR}/gps_logs_raw.csv", index=False)
    print(f"GPS sauvegardé : {len(df_gps)} lignes.")

def generate_wellness_data():
    """Simule des réponses quotidiennes aux questionnaires (Format JSON type API)"""
    print("🧘 Génération des données Wellness (JSON)...")
    wellness_records = []
    
    for day in range(NUM_DAYS):
        current_date = START_DATE + timedelta(days=day)
        
        for player_id in PLAYERS:
            # Logique : Après un match (Lundi), la fatigue est élevée
            is_post_match = (day % 7 == 0) 
            
            fatigue = random.randint(6, 9) if is_post_match else random.randint(1, 4)
            sleep_quality = random.randint(1, 10)
            soreness = random.randint(5, 9) if is_post_match else random.randint(1, 3)
            
            record = {
                "timestamp": current_date.strftime("%Y-%m-%dT08:00:00Z"),
                "user": {
                    "id": player_id,
                    "name": f"Name_{player_id}"
                },
                "metrics": {
                    "fatigue": fatigue, # 1 (Frais) - 10 (Épuisé)
                    "sleep_quality": sleep_quality, # 1 (Mauvais) - 10 (Excellent)
                    "soreness": soreness, # Douleurs musculaires
                    "mood": random.randint(1, 10)
                },
                "comments": "Leg pain" if soreness > 8 else None
            }
            wellness_records.append(record)
            
    # Sauvegarde en JSON
    with open(f"{DATA_DIR}/wellness_api_response.json", "w") as f:
        json.dump(wellness_records, f, indent=4)
    print(f" Wellness sauvegardé : {len(wellness_records)} entrées JSON.")

def generate_medical_data():
    """Simule un fichier Excel/CSV de suivi médical et tests physiques"""
    print(" Génération des données Médicales & Tests...")
    medical_records = []
    
    for player_id in PLAYERS:
        # Données statiques
        age = random.randint(18, 34)
        weight = random.randint(65, 95)
        
        # Historique blessures (0 = jamais, 1 = fragile)
        injury_history_score = random.randint(0, 5)
        
        # Test physique (VMA - Vitesse Max Aérobie)
        vma_score = random.normalvariate(18, 1.5)
        
        medical_records.append({
            "player_id": player_id,
            "age": age,
            "weight_kg": weight,
            "injury_history_index": injury_history_score,
            "last_vma_test": round(vma_score, 1),
            "medical_clearance": "Yes" if injury_history_score < 4 else "Monitor"
        })
        
    df_med = pd.DataFrame(medical_records)
    df_med.to_csv(f"{DATA_DIR}/medical_tests.csv", index=False)
    print("Médical sauvegardé.")

if __name__ == "__main__":
    generate_gps_data()
    generate_wellness_data()
    generate_medical_data()
    print(f"\n Données générées avec succès dans {DATA_DIR} !")
