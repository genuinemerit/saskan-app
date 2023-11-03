/*
univs 1---1 xu
*/
DROP TABLE IF EXISTS xus;
CREATE TABLE IF NOT EXISTS xus (
    xu_name TEXT PRIMARY KEY,
    univ_name_fk TEXT NOT NULL,
	xu_object BLOB NOT NULL
)
