# 🏃 Athlete 360 Data Pipeline

![Python](https://img.shields.io/badge/Python-3.9-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-orange)
![Airflow](https://img.shields.io/badge/Apache%20Airflow-ETL-red)
![FastAPI](https://img.shields.io/badge/FastAPI-Serving-green)

> **Le Défi :** Traiter des logs GPS hétérogènes pour alimenter un modèle de Machine Learning strict (XGBoost).

## 🏗️ Architecture & Choix Techniques

Ce projet met en œuvre une architecture basée sur la **séparation des responsabilités**, alliant la souplesse d'un Data Lake à la rigueur d'un Data Warehouse.

### 1️⃣ Ingestion (Raw Layer) - MongoDB
* **Pourquoi ?** Utilisation du NoSQL pour sa flexibilité (Schema-on-Read).
* **Avantage :** Permet d'ingérer les flux JSON bruts et changeants des capteurs sans casser le pipeline en cas d'évolution du schéma de données.

### 2️⃣ Serving (Gold Layer) - PostgreSQL
* **Pourquoi ?** Stockage relationnel structuré après nettoyage.
* **Avantage :** Indispensable pour garantir le **typage fort** nécessaire au modèle XGBoost et aux agrégations performantes du Dashboard.

## 🛠️ La Stack Technique

Le projet est entièrement conteneurisé et orchestré :

* **Docker & Docker Compose :** Pour l'isolation et le déploiement de l'infrastructure.
* **Apache Airflow :** Pour l'orchestration des pipelines ETL (Nettoyage, Transformation, Chargement).
* **FastAPI :** Pour exposer les prédictions du modèle et les données via une API REST performante.
* **Streamlit :** Pour la visualisation des métriques athlètes (Dashboard interactif).

## 🚀 Démo

*(Insérer ici un GIF animé de ton interface Streamlit ou un lien YouTube vers ta vidéo)*

## 📦 Installation & Démarrage

Cloner le projet :
```bash
git clone [https://github.com/FranckRuissel/athlete-360-pipeline.git](https://github.com/FranckRuissel/Athlete-360-Data-Pipeline.git)
cd athlete-360-pipeline


demo: https://www.linkedin.com/posts/franck-mboutou_dataengineering-architecture-nosql-activity-7415037466539302912-r3az?utm_source=share&utm_medium=member_desktop&rcm=ACoAAFTKCT4BT-dMNhFRbCvYMEtcGMWPaZd6nG0
