from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Arguments par défaut
default_args = {
    'owner': 'franck',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Définition du DAG
with DAG(
    'athlete_pipeline_v1',
    default_args=default_args,
    description='Pipeline complet : Ingestion -> Entrainement -> Model',
    schedule_interval='@daily', # Tous les jours
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:

    # Tâche 1 : Génération (Simulation)
    t1_generate = BashOperator(
        task_id='generate_data',
        bash_command='python /opt/airflow/scripts/generate_data.py'
    )

    # Tâche 2 : Ingestion (ETL)
    t2_ingest = BashOperator(
        task_id='ingest_data',
        bash_command='python /opt/airflow/scripts/ingest_data.py'
    )

    # Tâche 3 : Ré-entraînement du modèle
    t3_train = BashOperator(
        task_id='train_model',
        bash_command='python /opt/airflow/scripts/train_model.py'
    )

    # L'ordre d'exécution
    t1_generate >> t2_ingest >> t3_train