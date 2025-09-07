# SQLite Empty or Null values

To select records from a SQLite database where the `delete_dt` column contains either an empty string `""` or a NULL value, you can use a `SELECT` statement with the `OR` operator in the `WHERE` clause.

Here’s how you can structure your SQL query:

```sql
SELECT *
FROM ACCT
WHERE delete_dt IS NULL OR delete_dt = '';
```

## Explanation

* **`SELECT *`**: This selects all columns from the records that meet the criteria.
* **`FROM ACCT`**: This specifies the table from which to retrieve the records.
* **`WHERE delete_dt IS NULL`**: This condition checks for rows where `delete_dt` is NULL.
* **`OR delete_dt = ''`**: This condition checks for rows where `delete_dt` is an empty string.

## Additional Notes

* This query will return all rows where `delete_dt` is either NULL or an empty string, effectively filtering out any rows with non-empty or non-null values in that column.
* Make sure to test the query in your SQLite environment to ensure it returns the expected results based on your data.
