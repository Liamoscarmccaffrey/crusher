import sqlite3

# Path to your database file
db_file = "ass.db"

# Connect to the database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Query to list all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Print the table names
print("Tables in the database:")
for table in tables:
    print(table[0])

conn.close()