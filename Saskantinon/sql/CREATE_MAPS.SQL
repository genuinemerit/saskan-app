CREATE TABLE IF NOT EXISTS maps (
    /* A map is always a rectangle.
       It will be overlaid with more detailed information
       relating to things like:
         - geography (mountains, hills, rivers, lakes, seas, oceans, etc.)
         - political boundaries (countries, provinces, states, counties, etc.)
         - roads, paths, trails, etc.
         - cities, towns, villages, etc.
         - other points of interest (ruins, temples, etc.)
         - natural resources (mines, quarries, etc.)
         - demographics (population density, etc.)
    */
    map_name TEXT PRIMARY KEY,
    demographic_ty TEXT NOT NULL,
	contained_by_fk TEXT NOT NULL,
    N_S_km NUMERIC NOT NULL,
    E_W_km NUMERIC NOT NULL,
    /*
    latitudes and longitudes are in decimal degrees.
    Lat north is positive, lat south is negative.
    Lon east (between universal meridien and international date line) is positive, lon west is negative.
    */
    N_dg_latd NUMERIC NOT NULL,
    S_dg_latd NUMERIC NOT NULL,
    E_dg_lond NUMERIC NOT NULL,
    W_dg_lond NUMERIC NOT NULL,
    map_object BLOB NOT NULL,
	FOREIGN KEY (contained_by_fk) REFERENCES maps(map_name) ON DELETE CASCADE
);
/*
map_object structure:
{"other_names": 
    {<lang_FK>: "value", ...},
 "contains": 
    {<map_FK>: "value", ...},
 "borders": 
    {<map_FK>: "value", ...}
}
*/