import sqlite3
import pandas as pd
import os

def export_db_to_csv(db_path, output_dir='exported_csvs'):
    """
    Exports all tables from a SQLite database to CSV files.

    Parameters:
    - db_path (str): Path to the SQLite .db file.
    - output_dir (str): Directory to save the CSV files. Defaults to 'exported_csvs'.
    """
    # Check if the database file exists
    if not os.path.exists(db_path):
        print(f"Database file '{db_path}' does not exist.")
        return

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Retrieve all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]

        if not table_names:
            print("No tables found in the database.")
            return

        print("Tables in the database:")
        for name in table_names:
            print(f"- {name}")

        # Create the output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"\nCreated directory '{output_dir}' for CSV exports.")
        else:
            print(f"\nUsing existing directory '{output_dir}' for CSV exports.")

        # Export each table to a CSV file
        for table_name in table_names:
            print(f"\nExporting '{table_name}' table to CSV...")
            
            # Load table data into DataFrame
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            
            # Define CSV file path
            csv_path = os.path.join(output_dir, f"{table_name}.csv")
            
            # Export to CSV
            df.to_csv(csv_path, index=False)
            
            print(f"'{table_name}' exported successfully to '{csv_path}'")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the database connection
        conn.close()
        print("\nDatabase connection closed.")

if __name__ == "__main__":
    # Replace with your actual .db file path
    db_path = 'kinaxis.db'
    
    # Optionally, specify a different output directory
    output_dir = 'exported_csvs'
    
    export_db_to_csv(db_path, output_dir)