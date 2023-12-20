CREATE TABLE IF NOT EXISTS canals (
    canal_name TEXT PRIMARY KEY,
    canal_desc TEXT NOT NULL,
    canal_type TEXT NOT NULL,
    origin_sea_name_fk TEXT,
    origin_lake_name_fk TEXT,
    origin_river_name_fk TEXT,
    dest_sea_name_fk TEXT,
    dest_lake_name_fk TEXT,
    dest_river_name_fk TEXT,
    has_locks BOOLEAN NOT NULL,
    has_wiers BOOLEAN NOT NULL,
    width_m NUMERIC NOT NULL,
    depth_m NUMERIC NOT NULL,
    length_km NUMERIC NOT NULL,
    origin_latd_dg: number,
    origin_longd_dg: number,
    dest_latd_dg: number,
    dest_longd_dg: number,
	canal_object BLOB NOT NULL,
	FOREIGN KEY (origin_sea_name_fk) REFERENCES seas(sea_name),
	FOREIGN KEY (origin_lake_name_fk) REFERENCES lakes(lake_name),
	FOREIGN KEY (origin_river_name_fk) REFERENCES rivers(river_name),
	FOREIGN KEY (dest_sea_name_fk) REFERENCES seas(sea_name),
	FOREIGN KEY (dest_lake_name_fk) REFERENCES lakes(lake_name),
	FOREIGN KEY (dest_river_name_fk) REFERENCES rivers(river_name)
);
/*
Association table: canal_map_x
Object structure:
{"other_names":
    { <langs_fk>: "name"}, ...},
{"paths":
    [{"name": <path_name>,
      "path_origin_latd_dg": <path_origin>,
      "path_origin_lond_dg": <path_dest>}, ...},
      "path_dest_latd_dg": <path_dest>}, ...},
      "path_dest_long_dg": <path_dest>}, ...},
      "is_navigable": <is_navigable>}, ...},
      "navigation_type": <navigation_type>}
     }, ...]
}
*/
