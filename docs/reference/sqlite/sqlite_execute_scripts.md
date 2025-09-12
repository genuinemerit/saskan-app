# SQLite Execute Scripts

The `executescript()` method in the SQLite3 cursor allows you to execute multiple SQL statements in a single call. It is designed to handle cases where you have a script containing multiple SQL statements separated by semicolons (`;`).

Here's a brief explanation:

1. **Single Script String**: You pass a single string to `executescript()`. This string can contain one or more SQL statements separated by semicolons.

2. **Execution**: The method then executes each statement in the script sequentially.

3. **Transaction**: The entire script is executed as a single transaction. If an error occurs during the execution of any statement, the entire transaction is rolled back.

Here's a simple example:

```python
import sqlite3

# Connect to the SQLite database (replace 'example.db' with your database file)
connection = sqlite3.connect('example.db')

# Create a cursor
cursor = connection.cursor()

# SQL script with multiple statements
sql_script = """
    CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT);
    INSERT INTO users (name) VALUES ('John');
    INSERT INTO users (name) VALUES ('Alice');
    """

try:
    # Execute the script
    cursor.executescript(sql_script)

    # Commit the changes (since executescript starts a transaction)
    connection.commit()

except sqlite3.Error as e:
    # Handle any errors
    print(f"Error: {e}")
    # Rollback changes in case of an error
    connection.rollback()

finally:
    # Close the cursor and connection
    cursor.close()
    connection.close()
```

In this example, the `executescript()` method is used to create a table (`users`) and insert two rows into it. If any of the statements fails, the transaction will be rolled back.

It's worth noting that `executescript()` is useful for executing scripts, but for a single SQL statement, you might prefer to use `execute()` or `executemany()` methods.
