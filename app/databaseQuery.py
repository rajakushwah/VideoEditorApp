import sqlite3

def clear_database(db_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get the list of all tables except sqlite_sequence
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';")
    tables = cursor.fetchall()

    # Drop each user-defined table
    for table in tables:
        table_name = table[0]
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        print(f"Dropped table: {table_name}")

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print("All user-defined tables have been dropped successfully.")

# Usage
clear_database('/VideoEditorApp/app/videos.db')
