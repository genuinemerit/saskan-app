SELECT CONCAT('DROP TABLE IF EXISTS ', LOWER(table_name), ';')
FROM information_schema.tables
WHERE table_name LIKE '%_map_x';
