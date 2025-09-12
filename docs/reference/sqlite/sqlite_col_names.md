# SQLITE column names

To display column names in an SQLite3 table using Python, you can fetch the column names from the table's metadata. You can use the `PRAGMA table_info` SQL command to obtain information about the table's columns, including their names. Here's a step-by-step guide:

1. Import the SQLite3 library:

```python
import sqlite3
```

1. Connect to your SQLite database:

```python
conn = sqlite3.connect('your_database.db')
```

Replace `'your_database.db'` with the path to your SQLite database file.

1. Create a cursor:

```python
cursor = conn.cursor()
```

1. Execute the `PRAGMA table_info` query to retrieve column information:

```python
table_name = 'your_table_name'  # Replace with the name of your table
cursor.execute(f"PRAGMA table_info({table_name})")
```

1. Fetch and display the column names:

```python
columns = cursor.fetchall()
column_names = [column[1] for column in columns]

print("Column Names:")
for name in column_names:
    print(name)
```

Replace `'your_table_name'` with the name of the table you want to retrieve column names for.

Here's the complete code:

```python
import sqlite3

conn = sqlite3.connect('your_database.db')
cursor = conn.cursor()

table_name = 'your_table_name'  # Replace with the name of your table
cursor.execute(f"PRAGMA table_info({table_name})")

columns = cursor.fetchall()
column_names = [column[1] for column in columns]

print("Column Names:")
for name in column_names:
    print(name)

conn.close()
```

This code will connect to your SQLite database, retrieve the column names for the specified table, and then display them.
