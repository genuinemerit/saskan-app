# SQLite DB Status

Certainly! You can use the following Python code using the `sqlite3` library to check if a SQLite database file contains any tables:

```python
import sqlite3

def has_tables(database_path):
    try:
        # Connect to the SQLite database
        connection = sqlite3.connect(database_path)

        # Create a cursor to execute SQL queries
        cursor = connection.cursor()

        # Execute a query to get the list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

        # Fetch all tables
        tables = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Check if there are any tables
        return bool(tables)

    except sqlite3.Error as e:
        print(f"Error checking tables: {e}")
        return False

# Provide the path to your SQLite database file
database_path = 'SASKAN.db'

# Check if the database has tables
if has_tables(database_path):
    print(f"The database '{database_path}' contains tables.")
else:
    print(f"The database '{database_path}' does not contain any tables.")
```

This code defines a function `has_tables` that takes the path to the SQLite database file as a parameter and checks if there are any tables in the database. It does this by executing a query to retrieve the names of tables from the `sqlite_master` table, which stores metadata about the database schema. The function returns `True` if there are tables and `False` otherwise.

Make sure to replace `'SASKAN.db'` with the actual path to your SQLite database file. If there's anything else you need or if you have further questions, feel free to ask!
