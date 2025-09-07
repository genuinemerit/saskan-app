# sqllite booleans

SQLite does not have a dedicated Boolean data type. However, it uses a dynamic type system, and Boolean values are typically represented using integer values. Specifically, SQLite uses the integer values 0 and 1 to represent false and true, respectively.

When you create a table in SQLite and define a column as BOOLEAN, INTEGER, or some other numeric type, you can use it to store Boolean values. Here's an example:

```sql
CREATE TABLE example_table (
    id INTEGER PRIMARY KEY,
    is_active BOOLEAN,  -- or INTEGER
    name TEXT
);

-- Inserting data
INSERT INTO example_table (is_active, name) VALUES (1, 'John Doe');
```

In this example, `is_active` is a column that can store Boolean values. You can use 0 for false and 1 for true. SQLite will treat these values as Booleans when querying or updating the data.

When you query data from the table, you can use conditions like:

```sql
-- Selecting active users
SELECT * FROM example_table WHERE is_active = 1;
```

SQLite doesn't enforce strict typing for columns, so you can also insert values like 0 and 1 directly into the `is_active` column without issues.
