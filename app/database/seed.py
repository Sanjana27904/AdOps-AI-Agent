
import pandas as pd
from pathlib import Path

from app.database.db import get_connection

# Locate the CSV dataset
BASE_DIR = Path(__file__).resolve().parents[2]
CSV_PATH = BASE_DIR / "data" / "campaigns.csv"


def seed_database():
    # Read campaign data from CSV
    df = pd.read_csv(CSV_PATH)

    # Connect to SQLite
    connection = get_connection()

    try:
        # Insert records into the campaigns table
        df.to_sql(
            "campaigns",
            connection,
            if_exists="replace",
            index=False
        )

        print("Campaign data successfully inserted!")

        # Display number of records
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM campaigns")
        count = cursor.fetchone()[0]

        print(f"Total campaign records: {count}")

    finally:
        connection.close()


if __name__ == "__main__":
    seed_database()
