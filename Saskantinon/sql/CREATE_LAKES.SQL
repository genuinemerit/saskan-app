CREATE TABLE IF NOT EXISTS lakes (
    lake_name TEXT PRIMARY KEY,
    lake_size TEXT NOT NULL CHECK(lake_size IN ('small', 'medium', 'large')),
    water_type TEXT NOT NULL CHECK(water_type IN ('freshwater', 'saline', 'partially_salinated')),
    tidal_influence BOOLEAN NOT NULL,
    lake_size_m2 NUMERIC,
    max_depth_m NUMERIC,
    avg_depth_m NUMERIC,
    lake_origin TEXT,
    lake_altitude_m NUMERIC,
    /* The area of land where rainfall is collected and drained into the lake.
    This is not the same as the area of the lake itself. For game purposes,
    let's assume it is a circle with a radium as defined here:
     */
    catchment_area_radius_m NUMERIC,
    flora_and_fauna TEXT,
    water_color TEXT,
    /* How easy it is to reach the lake, whether there are roads, trails, or settlements nearby.
       This can likely be quantified in other ways, but keep this attribute to help design: */
    accessibility TEXT,
    /* Any unique or notable features, like islands, underwater caves, or geothermal activity:*/
    special_features TEXT,
    /*  fishing, recreation, transportation, as a water source for nearby settlements, etc: */
    lake_usage TEXT,
    legends_or_myths TEXT,
    lake_history TEXT,
    /*  Efforts to protect or preserve the lake: */
    conservation_status TEXT,
    /* water quality, temperature, frozen, etc. */
    current_conditions TEXT,
    lake_object BLOB NOT NULL
);
/*
Association table: lake_map_x
Object structure:
{"other_names":
    { <langs_fk>: "name"}, ...},
{"shoreline":
    [{"name": <shoreline_name>,
      "shoreline_origin_latd_dg": <shoreline_origin>,
      "shoreline_origin_lond_dg": <shoreline_dest>}, ...},
      "shoreline_dest_latd_dg": <shoreline_dest>}, ...},
      "shoreline_dest_long_dg": <shoreline_dest>}, ...}
     }, ...]
}
*/
