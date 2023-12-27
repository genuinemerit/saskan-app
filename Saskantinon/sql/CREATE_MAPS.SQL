CREATE TABLE IF NOT EXISTS maps (
    /* A map is always a rectangle.
       This structure is for defining 'templates' of maps
         that lay over a grid. For example, there might be
         a map_name that is associated with provinces and
         a different one that is associated with regions.
         There could also be multiple variations of, say,
         county-level maps, depending on large or small, for
         example.
       It will be associated with table w/ more detailed info
       relating to things like:
         - geography (mountains, hills, rivers, lakes, seas, oceans, etc.)
         - political boundaries (countries, provinces, states, counties, etc.)
         - roads, paths, trails, waterways, bodies of water, etc.
         - cities, towns, villages, etc.
         - other points of interest (ruins, temples, etc.)
         - natural resources (mines, quarries, etc.)
         - demographics (population density, etc.)
    */
    map_name TEXT PRIMARY KEY,
    demographic_ty TEXT NOT NULL,
	contained_by_fk TEXT NOT NULL,
    /*
    latitudes and longitudes are in decimal degrees.
    Lat north is positive, lat south is negative.
    Lon east (between universal meridien and international date line) is positive, lon west is negative. The idea is to use
    degrees as the main specifier, and then compute km based on
    scaling to the grid. It may or may not make sense to store
    km on the database record.
    */
    N_dg_latd NUMERIC NOT NULL,
    S_dg_latd NUMERIC NOT NULL,
    E_dg_lond NUMERIC NOT NULL,
    W_dg_lond NUMERIC NOT NULL,
    N_S_km NUMERIC,
    E_W_km NUMERIC,
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