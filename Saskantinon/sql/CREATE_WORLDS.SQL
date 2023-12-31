CREATE TABLE IF NOT EXISTS worlds (
    /*
    A world is always a sphere in game terms.
    But it will be mapped onto a rectangle, initially at least,
    for simulation purposes. It will be a simple mapping of latitude
    and longitude to x and y coordinates, with the x and y coordinates
    being in decimal degrees.

    - Moons and other satellites are defined in a SATELLITES table.
    - Suns and stars are defined in the STAR_SYSTEMS table.
    - Planets are defined here, in the WORLDS table.
    - Asteroids, comets, and other small bodies are defined in the   
        SMALL_BODIES table. There is not a direct relationship between
        these and the WORLDS table, but they are related to the same
        STAR_SYSTEMS table.
    - A world is always contained by one STAR_SYSTEM, a relationship 
        defined by a FK here in the WORLDS table.
    - A world may have an FK relationship to zero to many SATELLITES;
        a one-to-many relationship defined in the SATELLITES table.
    - A world is related to zero-to-many maps, a many-to-many relationship 
        defined in the MAPS_WORLDS_X table.
    - A world may have zero to many "zones", meaning a large geographical
        area such as hemisphere or quadrant. This is a one-to-many 
        relationship defined by an FK on the ZONES table.
    */
    world_name TEXT PRIMARY KEY,
    star_system_name_fk TEXT NOT NULL,
    world_type TEXT NOT NULL CHECK(world_type IN ('Earth-like', 'gas giant', 'rocky', 'desert', 'oceanic', 'ice planet', 'molten','other')),
    obliquity_dg NUMERIC NOT NULL,
    distance_from_star_au NUMERIC NOT NULL,
    distance_from_star_km NUMERIC NOT NULL,
    diameter_km NUMERIC NOT NULL,
    mass_kg NUMERIC NOT NULL,
    gravity_m_per_s_per_s NUMERIC NOT NULL,
    orbit_days NUMERIC NOT NULL,
    orbit__turns NUMERIC NOT NULL,
    rotation_days NUMERIC NOT NULL,
    world_desc TEXT,
    atmosphere TEXT,
    biosphere TEXT,
    sentients TEXT,
    climate TEXT,
    tech_level TEXT,
    terrain TEXT,
	world_object BLOB NOT NULL,
	FOREIGN KEY (star_system_name_fk) REFERENCES star_systems(star_system_name) ON DELETE CASCADE
);
/*
Attributes defined in the object blob are the following...
{
    "other_names": 
        {<lang_FK>: "value", ...},
}
*/
