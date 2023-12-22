CREATE TABLE IF NOT EXISTS star_systems (
    star_system_name TEXT PRIMARY KEY,
    galaxy_name_fk TEXT NOT NULL,
	star_system_object BLOB NOT NULL,
	FOREIGN KEY (galaxy_name_fk) REFERENCES galaxies(galaxy_name) ON DELETE CASCADE
);
