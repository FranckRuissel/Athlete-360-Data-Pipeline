from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import os

app = FastAPI(
    title="Athlete Insight API",
    description="API de prédiction de risque de blessure pour le staff médical.",
    version="1.0"
)

MODEL_PATH = "models/injury_risk_model.pkl"

if not os.path.exists(MODEL_PATH):
    raise Exception(f" Erreur : Le modèle n'est pas trouvé dans {MODEL_PATH}. Lance train_model.py d'abord !")

model = joblib.load(MODEL_PATH)
print("Modèle chargé avec succès.")

class PlayerMetrics(BaseModel):
    total_distance_m: float
    hsr_distance_m: float
    max_speed_kmh: float
    age: int
    weight_kg: float
    injury_history_index: int
    last_vma_test: float

# --- ENDPOINTS (Les routes de l'API) ---

@app.get("/")
def read_root():
    return {"status": "API en ligne", "service": "Athlete Risk Engine"}

@app.post("/predict")
def predict_risk(metrics: PlayerMetrics):
    """
    Reçoit les métriques d'un joueur et retourne son score de risque.
    """
    try:
        input_data = pd.DataFrame([metrics.dict()])
        
        #  Prédiction
        prediction = model.predict(input_data)[0] # 0 ou 1
        probability = model.predict_proba(input_data)[0][1] 
        
        #  Réponse JSON
        return {
            "risk_prediction": int(prediction),
            "risk_probability": round(float(probability), 2),
            "risk_level": "CRITIQUE" if probability > 0.7 else "MODÉRÉ" if probability > 0.3 else "FAIBLE",
            "message": "Attention, charge élevée détectée." if prediction == 1 else "Joueur apte."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)