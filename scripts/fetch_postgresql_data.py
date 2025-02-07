import os
import json
import psycopg2
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# Load environment variables
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_NAME = os.getenv("DATABASE_NAME")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")

# Google Sheets API setup
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def fetch_postgresql_data():
    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        host=DATABASE_HOST,
        database=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD
    )
    cursor = conn.cursor()

    # Query to fetch data
    query = "SELECT * FROM que_faire_a_paris"
    cursor.execute(query)
    rows = cursor.fetchall()

    # Close the connection
    cursor.close()
    conn.close()
    return rows

def update_google_sheet(data):
    # Authenticate Google Sheets API
    credentials_info = json.loads(GOOGLE_CREDENTIALS)
    credentials = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
    service = build("sheets", "v4", credentials=credentials)

# Clear existing sheet data
service.spreadsheets().values().clear(
    spreadsheetId=GOOGLE_SHEET_ID,
    range="Sheet1!A:AB",  # Covers 28 columns
).execute()

# Write new data
body = {"values": data}
service.spreadsheets().values().update(
    spreadsheetId=GOOGLE_SHEET_ID,
    range="Sheet1!A:AB",  # Covers 28 columns
    valueInputOption="RAW",
    body=body,
).execute()

if __name__ == "__main__":
    # Fetch data from PostgreSQL
    rows = fetch_postgresql_data()

    # Format data into lists
    formatted_data = [list(row) for row in rows]

    # Update Google Sheets
    update_google_sheet(formatted_data)
