# sqlite blobs (text, blob, pickles)

## Pickles

Here's a simple example in Python that demonstrates how to create a pickled object and insert it into an SQLite table as a BLOB (Binary Large Object) data type:

```python
import sqlite3
import pickle

# Connect to the SQLite database
conn = sqlite3.connect('my_database.db')
cursor = conn.cursor()

# Create a table to store pickled objects as BLOB
cursor.execute('''CREATE TABLE PickledObjects (
                  id INTEGER PRIMARY KEY,
                  pickled_data BLOB
                )''')

# Create a sample Python object (dictionary) to pickle
sample_data = {'name': 'John', 'age': 30, 'city': 'New York'}

# Serialize (pickle) the object
pickled_data = pickle.dumps(sample_data)

# Insert the pickled object into the table
cursor.execute("INSERT INTO PickledObjects (pickled_data) VALUES (?)", (pickled_data,))

# Commit the changes
conn.commit()

# Retrieve and deserialize the pickled object
cursor.execute("SELECT pickled_data FROM PickledObjects WHERE id = 1")
result = cursor.fetchone()
if result:
    stored_pickled_data = result[0]
    stored_data = pickle.loads(stored_pickled_data)
    print("Stored data:", stored_data)

# Close the connection
conn.close()
```

In this example:

1. We connect to an SQLite database and create a table named `PickledObjects` with an `id` (primary key) and a `pickled_data` column of type BLOB.

2. We create a sample Python object (a dictionary) called `sample_data`.

3. We use the `pickle.dumps()` function to serialize (pickle) the object into a binary format, which can be stored as a BLOB in the database.

4. We insert the pickled data into the table using a parameterized query.

5. We commit the changes to the database.

6. We retrieve and deserialize the pickled object using `pickle.loads()` when querying the data from the table.

This allows you to store pickled objects in an SQLite table rather than saving them as standalone files.

---

## TEXT

In SQLite, the maximum storage capacity for a `TEXT` data attribute is determined by the maximum database page size, which is 64 kilobytes (KB) by default. Each row in an SQLite table is stored as one or more pages, and the `TEXT` data, along with other column data, contributes to the row size.

While there isn't a strict limit on the size of a `TEXT` column itself, the effective limit depends on the overall row size and the available space within a database page. The actual storage size is influenced by factors such as the presence of other columns in the table, indexing, and any additional storage overhead.

If your text data is exceptionally large, and you need to store very long strings, you might consider using the `BLOB` data type instead. `BLOB` columns can store binary data, including large text content.

Always keep in mind that the practical limit for your use case may depend on factors such as the specific SQLite version, the platform, and the configuration settings used during SQLite compilation.

---

## BLOB (and JSON)

The `BLOB` (Binary Large Object) data type in SQLite can be used to store binary data, including plain text and JSON. When you store text or JSON in a `BLOB` column, SQLite treats it as binary data, allowing you to store arbitrary byte sequences.

Here's a simple example in Python using SQLite to demonstrate storing and retrieving text data in a `BLOB` column:

```python
import sqlite3

# Connect to SQLite database (creates a new one if not exists)
conn = sqlite3.connect('example.db')
cursor = conn.cursor()

# Create a table with a BLOB column
cursor.execute('''
    CREATE TABLE IF NOT EXISTS my_table (
        id INTEGER PRIMARY KEY,
        data BLOB
    )
''')

# Insert plain text data into the BLOB column
text_data = "This is some plain text."
cursor.execute('INSERT INTO my_table (data) VALUES (?)', (text_data,))

# Retrieve the data from the table
cursor.execute('SELECT * FROM my_table')
row = cursor.fetchone()

# Extract and print the text data from the BLOB column
retrieved_text_data = row[1].decode('utf-8')
print(retrieved_text_data)

# Commit the transaction and close the connection
conn.commit()
conn.close()
```

In this example, `data BLOB` is used to define a `BLOB` column, and the `INSERT` statement is used to insert the text data into that column. When retrieving the data, it's necessary to decode it from bytes to a text representation using an appropriate encoding (e.g., UTF-8).

The same approach can be used for storing and retrieving JSON data as well. Just serialize your JSON object to a string, encode it as bytes (if needed), and store it in the `BLOB` column.
