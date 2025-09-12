# sqlite foreign keys

In SQLite, you can designate a column as a foreign key by defining specific constraints using the `FOREIGN KEY` constraint. Here's how you can do it when creating a table:

```sql
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date DATE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
```

In the example above, we're creating a table called "orders" with a column named "customer\_id." The `FOREIGN KEY` constraint is used to specify that the "customer\_id" column references the "customer\_id" column in another table called "customers." This establishes a foreign key relationship between the "orders" table and the "customers" table.

The `FOREIGN KEY` constraint ensures referential integrity, meaning that the values in the "customer\_id" column of the "orders" table must match values in the "customer\_id" column of the "customers" table.

When you define a foreign key, you're telling SQLite to enforce data integrity rules, such as ensuring that you can't insert a value into the "customer\_id" column of the "orders" table unless it already exists in the "customer\_id" column of the "customers" table.

Note that SQLite supports foreign keys by default, but foreign key enforcement is turned off by default. To enable foreign key support, you need to execute the following command after connecting to the database:

```sql
PRAGMA foreign_keys = ON;
```

Enabling foreign key support allows SQLite to enforce referential integrity constraints defined in your tables.

---

To enable foreign key support in SQLite when connecting to a SQLite database via Python, you can use the following code:

```python
import sqlite3

# Connect to the SQLite database and enable foreign keys
conn = sqlite3.connect('your_database.db')
conn.execute("PRAGMA foreign_keys = ON;")

# Create a cursor
cursor = conn.cursor()

# Now, you can work with the database and use foreign keys

# Don't forget to commit changes and close the connection when done
conn.commit()
conn.close()
```

In this code:

1. We connect to the SQLite database using `sqlite3.connect`.
2. We execute the `PRAGMA foreign_keys = ON;` statement on the database connection to enable foreign key support. This statement sets the foreign key enforcement mode to "ON."
3. We create a cursor to perform database operations.
4. You can then perform operations involving foreign keys as needed.
5. Finally, remember to commit changes and close the database connection when you're done.

By executing the `PRAGMA foreign_keys = ON;` statement, you enable foreign key support for the current database connection, and it will enforce referential integrity constraints as you work with the database.

---
