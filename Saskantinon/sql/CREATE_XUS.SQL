/*
univs 1---1 xu
*/
CREATE TABLE IF NOT EXISTS xus (
    xu_name TEXT PRIMARY KEY,
    univ_name_fk TEXT NOT NULL,
	xu_object BLOB NOT NULL,
	FOREIGN KEY (univ_name_fk) REFERENCES univs(univ_name) ON DELETE CASCADE
);
