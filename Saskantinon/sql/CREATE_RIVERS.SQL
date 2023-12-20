CREATE TABLE IF NOT EXISTS rivers (
    river_name TEXT PRIMARY KEY,
    sea_mouth_name_fk TEXT,
    avg_width_m NUMERIC,
    avg_depth_m NUMERIC,
    total_length_m NUMERIC,
    /* Avg area of land where rainfall is collected and drained into the river on each bank. For game purposes, just select a number
    of meters. */
    drainage_basin_m NUMERIC,
    /* Meters per hour on average */
    avg_velocity_m_per_h NUMERIC,
    gradient_m_per_km NUMERIC,
    flora_and_fauna TEXT,
    water_quality TEXT,
    navigation_type TEXT CHECK(navigation_type IN ('small craft', 'large craft', 'none')),
    historical_events TEXT,
    current_conditions TEXT,
    river_object BLOB NOT NULL,
	FOREIGN KEY (sea_mouth_name_fk) REFERENCES seas(sea_name) ON DELETE CASCADE
);
/*
Association table: river_map_x
Object structure:
{"other_names":
    { <langs_fk>: "name"}, ...},
{"path":
    [{"name": <path_name>,
      "path_origin_latd_dg": <path_origin>,
      "path_origin_lond_dg": <path_dest>}, ...},
      "path_dest_latd_dg": <path_dest>}, ...},
      "path_dest_long_dg": <path_dest>}, ...}
     }, ...],
 "hazards": [{"name": <text>,
                "type": <text>,
                "location": (lat, long)}, ...],
 "crossings": [{"name": <text>,
                "type": <text>,
                "location": (lat, long)}, ...],
 "tributaries": [<river_name_fk> ...],
 "mountains_source": [<mountain_name_fk> ...],
 "hills_source": [<hills_name_fk> ...],
"rivers_drain_into": [<river_name_fk> ...],  
 "lakes_source": [<lake_name_fk>, ...],
"lakes_drain_into": [<lake_name_fk>, ...]}
*/
