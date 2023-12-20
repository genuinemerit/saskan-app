/*
clusters 1-->n galaxies
*/
CREATE TABLE IF NOT EXISTS galaxies (
    galaxy_name TEXT PRIMARY KEY,
    cluster_name_fk TEXT NOT NULL,
	galaxy_object BLOB NOT NULL,
	FOREIGN KEY (cluster_name_fk) REFERENCES clusters(cluster_name) ON DELETE CASCADE
);
