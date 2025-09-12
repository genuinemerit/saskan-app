# Sqlite Commits

In SQLite with Python, the `commit()` method is not called directly on the connection object; instead, it is called on the cursor object. The general workflow is as follows:

1. **Create Connection**: Open a connection to the SQLite database using the `connect` method. This connection object is used to establish a connection to the database.

2. **Create Cursor**: Create a cursor object using the `cursor()` method on the connection. The cursor is used to execute SQL queries.

3. **Execute SQL Statements**: Use the cursor to execute SQL statements, such as creating tables, inserting data, updating records, etc.

4. **Commit Changes**: If you have made changes to the database (e.g., inserts, updates, deletes), you need to call the `commit()` method on the connection object. This commits the changes to the database.

Here's a simple example:

```python
import sqlite3

# 1. Create Connection
conn = sqlite3.connect('example.db')

# 2. Create Cursor
cursor = conn.cursor()

# 3. Execute SQL Statements
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)')

# Insert data
cursor.execute('INSERT INTO users (name) VALUES (?)', ('John Doe',))

# 4. Commit Changes
conn.commit()

# Close Connection (optional)
conn.close()
```

In this example, `commit()` is called on the connection (`conn`) after making changes with the cursor. Always ensure that you commit changes after making modifications to the database.

Pylance might be warning you because it expects to see `commit()` on a cursor object, but in the context of SQLite in Python, it is indeed called on the connection.
