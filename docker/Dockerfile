# docker/Dockerfile
FROM apache/airflow:2.7.1

USER root
RUN apt-get update && apt-get install -y git

USER airflow

# Installation des librairies 
RUN pip install --no-cache-dir \
    pandas \
    numpy \
    scikit-learn \
    psycopg2-binary \
    pymongo \
    sqlalchemy \
    joblib