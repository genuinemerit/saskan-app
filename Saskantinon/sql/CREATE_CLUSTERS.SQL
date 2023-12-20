/*
univs 1-->n clusters
clusters n<--1 univs
*/
CREATE TABLE IF NOT EXISTS clusters (
    cluster_name TEXT PRIMARY KEY,
    univ_name_fk TEXT NOT NULL,
	cluster_object BLOB NOT NULL,
	FOREIGN KEY (univ_name_fk) REFERENCES univs(univ_name) ON DELETE CASCADE
);
