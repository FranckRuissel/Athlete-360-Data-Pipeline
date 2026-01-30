import pandas as pd
import json
import os
from pymongo import MongoClient
from sqlalchemy import create_engine

DATA_DIR = "data"

# MongoDB
MONGO_URI = "mongodb://user:password@localhost:27017/"
MONGO_DB_NAME = "athlete_lake"

# PostgreSQL
PG_URI = "postgresql://user:password@localhost:5432/athlete_db"

def load_wellness_to_mongo():
    print("Chargement Wellness vers MongoDB...")
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB_NAME]
        collection = db["wellness_raw"]
        
        # Lecture du fichier
        with open(f"{DATA_DIR}/wellness_api_response.json", "r") as f:
            data = json.load(f)
        
        # vide la collection avant pour éviter les doublons 
        collection.delete_many({})
        collection.insert_many(data)
        
        print(f"Succès : {len(data)} documents Wellness insérés dans Mongo.")
    except Exception as e:
        print(f" Erreur Mongo : {e}")

def load_gps_to_mongo():
    print("Chargement GPS vers MongoDB...")
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB_NAME]
        collection = db["gps_raw"]
        
        df = pd.read_csv(f"{DATA_DIR}/gps_logs_raw.csv")
        records = df.to_dict("records")
        
        collection.delete_many({})
        collection.insert_many(records)
        print(f"Succès : {len(records)} logs GPS archivés dans Mongo.")
    except Exception as e:
        print(f" Erreur Mongo GPS : {e}")

def load_data_to_postgres():
    print(" Chargement Données -> PostgreSQL...")
    try:
        engine = create_engine(PG_URI)
        
        df_gps = pd.read_csv(f"{DATA_DIR}/gps_logs_raw.csv")
        
        initial_count = len(df_gps)
        df_gps = df_gps[df_gps['total_distance_m'] > 0]
        cleaned_count = len(df_gps)
        print(f"  Nettoyage GPS : {initial_count - cleaned_count} lignes aberrantes supprimées.")
        
        df_gps.to_sql('gps_metrics', engine, if_exists='replace', index=False)
        print("   -> Table 'gps_metrics' créée.")

        df_med = pd.read_csv(f"{DATA_DIR}/medical_tests.csv")
        df_med.to_sql('medical_info', engine, if_exists='replace', index=False)
        print("   -> Table 'medical_info' créée.")
        
        print(" Succès : Données relationnelles chargées dans Postgres.")
        
    except Exception as e:
        print(f" Erreur Postgres : {e}")

if __name__ == "__main__":
    print("--- DÉBUT DE L'INGESTION ---")
    load_wellness_to_mongo()
    load_gps_to_mongo()
    load_data_to_postgres()
    print("--- FIN ---")