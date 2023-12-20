CREATE TABLE IF NOT EXISTS maps (
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
	FOREIGN KEY (contained_by_fk) REFERENCES maps(map_name)
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