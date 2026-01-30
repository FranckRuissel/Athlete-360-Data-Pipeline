import streamlit as st
import requests
import pandas as pd
import json

st.set_page_config(page_title="Athlete 360", layout="wide")

st.title("Athlete 360 - Monitoring & Prédiction")
st.markdown("---")

st.sidebar.header("Saisie Données du Jour")

def user_input_features():
    age = st.sidebar.slider("Âge", 18, 40, 24)
    weight = st.sidebar.slider("Poids (kg)", 60, 100, 75)
    injury_hist = st.sidebar.slider("Historique Blessures (Index)", 0, 5, 1)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Séance du jour")
    dist = st.sidebar.number_input("Distance Totale (m)", 0, 15000, 8500)
    hsr = st.sidebar.number_input("Distance Haute Vitesse (m)", 0, 2000, 400)
    speed = st.sidebar.number_input("Vitesse Max (km/h)", 0.0, 36.0, 28.5)
    vma = st.sidebar.number_input("Dernière VMA", 10.0, 25.0, 18.0)
    
    data = {
        "total_distance_m": dist,
        "hsr_distance_m": hsr,
        "max_speed_kmh": speed,
        "age": age,
        "weight_kg": weight,
        "injury_history_index": injury_hist,
        "last_vma_test": vma
    }
    return data

# Récupération des données saisies
input_data = user_input_features()

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Profil Athlète")
    st.write(f"**Âge:** {input_data['age']} ans")
    st.write(f"**Poids:** {input_data['weight_kg']} kg")
    st.info(f"Charge du jour : {input_data['total_distance_m']} mètres")

# Appel à l'API
if st.button(" Analyser le Risque"):
    try:
        api_url = "http://127.0.0.1:8000/predict"
        response = requests.post(api_url, json=input_data)
        
        if response.status_code == 200:
            result = response.json()
            
            with col2:
                st.subheader("Résultat de l'IA")
                
                risk_level = result['risk_level']
                prob = result['risk_probability'] * 100
                
                if risk_level == "CRITIQUE":
                    st.error(f" RISQUE CRITIQUE ({prob:.1f}%)")
                    st.warning(result['message'])
                elif risk_level == "MODÉRÉ":
                    st.warning(f"🔸 RISQUE MODÉRÉ ({prob:.1f}%)")
                else:
                    st.success(f" JOUEUR APTE ({prob:.1f}%)")
                    
                st.progress(result['risk_probability'])
                
                with st.expander("Voir la réponse API "):
                    st.json(result)
        else:
            st.error("Erreur lors de l'appel API")
            
    except requests.exceptions.ConnectionError:
        st.error(" L'API ne répond pas. Vérifie que tu as lancé 'uvicorn' dans un autre terminal !")