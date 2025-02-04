from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pandas as pd
import requests
import io
import datetime as dt
import re
from datetime import datetime

# Placeholder URLs
CSV_URL = "{{ var.value.PARIS_OPEN_DATA_URL }}"  # Set as an Airflow variable
POSTGRES_CONN_ID = "{{ var.value.POSTGRES_CONN_ID }}"  # Airflow Postgres connection

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 2, 1),
    "retries": 1,
}

dag = DAG(
    "etl_que_faire_a_paris",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
)

def extract_data():
    """Extracts data from the Paris Open Data API and loads it into a Pandas DataFrame."""
    response = requests.get(CSV_URL)
    response.raise_for_status()
    df = pd.read_csv(io.StringIO(response.text), sep=";")
    df.to_csv("/tmp/que_faire_a_paris_raw.csv", index=False)

def transform_data():
    """Loads the raw CSV, applies transformations, and saves the cleaned data."""
    df = pd.read_csv("/tmp/que_faire_a_paris_raw.csv", sep=";")
    
    columns_to_keep = [
        "ID", "URL", "Titre", "Chapeau", "Date de début", "Date de fin",
        "Mots clés", "Nom du lieu", "Adresse du lieu", "Code postal", "Ville",
        "Coordonnées géographiques", "Accès PMR", "Accès mal voyant", "Accès mal entendant",
        "Type de prix", "URL de réservation", "Date de mise à jour", "audience"
    ]
    df = df[columns_to_keep]
    df.drop_duplicates(inplace=True)
    
    # Handle missing values
    fillna_values = {
        "Titre": "N/A", "Chapeau": "N/A", "Mots clés": "N/A", "Nom du lieu": "N/A", 
        "Adresse du lieu": "N/A", "URL de réservation": "N/A", "Code postal": "75000", 
        "Ville": "Paris"
    }
    df.fillna(fillna_values, inplace=True)
    
    today = dt.datetime.today()
    last_day_of_year = dt.datetime(today.year, 12, 31)
    df["Date de début"].fillna(today, inplace=True)
    df["Date de fin"].fillna(last_day_of_year, inplace=True)
    df["Date de mise à jour"].fillna(df["Date de mise à jour"].max(), inplace=True)
    
    # Standardize accessibility information
    df['Accès PMR'] = df['Accès PMR'].apply(lambda x: 'Accès PMR' if x == 1 else "Pas d'accès PMR")
    df['Accès mal voyant'] = df['Accès mal voyant'].apply(lambda x: 'Accès mal voyant' if x == 1 else "Pas d'accès mal voyant")
    df['Accès mal entendant'] = df['Accès mal entendant'].apply(lambda x: 'Accès mal entendant' if x == 1 else "Pas d'accès mal entendant")
    df['Accessibilité'] = df['Accès PMR'] + ' – ' + df['Accès mal voyant'] + ' – ' + df['Accès mal entendant']
    
    # Clean postal codes
    def clean_code_postal(code):
        code = code.strip()
        code = re.sub(r'\s+', '', code)
        code = re.sub(r'\D+$', '', code)
        if len(code) == 4:
            code = "0" + code
        if not re.match(r'^\d{5}$', code):
            code = "75000"
        return code
    df["Code postal"] = df["Code postal"].apply(clean_code_postal)
    
    # Normalize city names
    def clean_ville(ville):
        ville = ville.strip()
        if ville.startswith("Paris"):
            ville = "Paris"
        return ville.title()
    df["Ville"] = df["Ville"].apply(clean_ville)
    
    # Convert pricing type to title case
    df["Type de prix"] = df["Type de prix"].str.title()
    
    df.to_csv("/tmp/que_faire_a_paris_transformed.csv", index=False)

def load_data():
    """Loads the transformed data into PostgreSQL."""
    pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    engine = pg_hook.get_sqlalchemy_engine()
    df = pd.read_csv("/tmp/que_faire_a_paris_transformed.csv")
    df.to_sql("que_faire_a_paris", engine, if_exists="replace", index=False)

extract_task = PythonOperator(
    task_id="extract_data",
    python_callable=extract_data,
    dag=dag,
)

transform_task = PythonOperator(
    task_id="transform_data",
    python_callable=transform_data,
    dag=dag,
)

load_task = PythonOperator(
    task_id="load_data",
    python_callable=load_data,
    dag=dag,
)

extract_task >> transform_task >> load_task