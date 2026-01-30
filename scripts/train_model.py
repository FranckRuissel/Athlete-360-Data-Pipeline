import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
import os

DB_HOST = os.getenv("DB_HOST", "localhost")
PG_URI = f"postgresql://user:password@{DB_HOST}:5432/athlete_db"

if os.path.exists("/opt/airflow/models"):
    MODEL_DIR = "/opt/airflow/models"
else:
    MODEL_DIR = "models"

os.makedirs(MODEL_DIR, exist_ok=True)

print(f"Répertoire de sauvegarde du modèle : {MODEL_DIR}")
print(f"Connexion Base de Données : {DB_HOST}")


def get_training_data():
    print(" Chargement des données depuis PostgreSQL...")
    try:
        engine = create_engine(PG_URI)
        
        query = """
        SELECT 
            g.date,
            g.player_id,
            g.total_distance_m,
            g.hsr_distance_m, -- High Speed Running
            g.max_speed_kmh,
            m.age,
            m.weight_kg,
            m.injury_history_index,
            m.last_vma_test
        FROM gps_metrics g
        JOIN medical_info m ON g.player_id = m.player_id
        """
        df = pd.read_sql(query, engine)
        print(f"Données chargées : {len(df)} entraînement.")
        return df
    except Exception as e:
        print(f"Erreur connexion SQL : {e}")
        raise e

def create_realistic_target(df):
    """
    Simule un risque basé sur le ratio de charge (ACWR) et l'historique.
    Approche probabiliste pour éviter que tout le monde soit 'Apte'.
    """
    # Simulation ACWR 
    df['acwr_simulated'] = df['total_distance_m'] / 7500  # 7500m est la moyenne supposée
    
    # Base risk : 5% de chance de pépin physique quoi qu'il arrive
    risk_prob = 0.05 
    
    # Facteur 1 : Surcharge (ACWR > 1.3) -> +30% de risque
    risk_prob += np.where(df['acwr_simulated'] > 1.3, 0.30, 0.0)
    
    # Facteur 2 : Haute Intensité (Sprints > 800m) -> +20%
    risk_prob += np.where(df['hsr_distance_m'] > 800, 0.20, 0.0)
    
    # Facteur 3 : Profil Fragile -> +15%
    risk_prob += np.where(df['injury_history_index'] > 2, 0.15, 0.0)
    
    # Facteur 4 : Âge -> +10% si > 30 ans
    risk_prob += np.where(df['age'] > 30, 0.10, 0.0)

    
    risk_prob = np.clip(risk_prob, 0, 0.95)
    
    # Tirage aléatoire Loi Binomiale   
    df['is_risk'] = np.random.binomial(1, risk_prob)
    
    # Stats pour vérifier dans les logs Airflow
    print(f" Stats ACWR moyen : {df['acwr_simulated'].mean():.2f}")
    print(f" Taux de blessure généré : {df['is_risk'].mean():.1%} (Cible : 10-20%)")
    
    return df

def train_model():
    # 1. Récupération
    df = get_training_data()
    
    if df is None or df.empty:
        print(" Aucune donnée pour l'entraînement. Vérifie l'ingestion.")
        return

    # 2. Création de la Target réaliste
    df = create_realistic_target(df)
    
    # 3. Préparation Features / Target
    features = [
        'total_distance_m', 'hsr_distance_m', 'max_speed_kmh', 
        'age', 'weight_kg', 'injury_history_index', 'last_vma_test'
    ]
    X = df[features]
    y = df['is_risk']
    
    # 4. Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 5. Entraînement
    print(" Entraînement du Random Forest...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    # 6. Évaluation
    y_pred = clf.predict(X_test)
    print("\n RÉSULTATS DU MODÈLE :")
    print(f"Accuracy : {accuracy_score(y_test, y_pred):.2f}")
    print("-" * 30)
    
    # 7. Explicabilité (Feature Importance)
    print(" IMPORTANCE DES VARIABLES :")
    importances = pd.DataFrame({
        'feature': features,
        'importance': clf.feature_importances_
    }).sort_values('importance', ascending=False)
    print(importances)
    
    # 8. Sauvegarde
    model_path = f"{MODEL_DIR}/injury_risk_model.pkl"
    joblib.dump(clf, model_path)
    print(f"\n Modèle sauvegardé sous : {model_path}")

if __name__ == "__main__":
    train_model()