CREATE TABLE IF NOT EXISTS canal_map_x (
    map_name_fk INTEGER,
    canal_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name) ON DELETE CASCADE,
    FOREIGN KEY (canal_name_fk) REFERENCES canal(canal_name) ON DELETE CASCADE,
    PRIMARY KEY (map_name_fk, canal_name_fk)
);

CREATE TABLE IF NOT EXISTS lake_map_x (
    map_name_fk INTEGER,
    lake_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name) ON DELETE CASCADE,
    FOREIGN KEY (lake_name_fk) REFERENCES lake(lake_name) ON DELETE CASCADE,
    PRIMARY KEY (map_name_fk, lake_name_fk)
);

CREATE TABLE IF NOT EXISTS river_map_x (
    map_name_fk INTEGER,
    river_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name) ON DELETE CASCADE,
    FOREIGN KEY (river_name_fk) REFERENCES river(river_name) ON DELETE CASCADE,
    PRIMARY KEY (map_name_fk, river_name_fk)
);

CREATE TABLE IF NOT EXISTS road_map_x (
    map_name_fk INTEGER,
    road_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name) ON DELETE CASCADE,
    FOREIGN KEY (road_name_fk) REFERENCES road(road_name) ON DELETE CASCADE,
    PRIMARY KEY (map_name_fk, road_name_fk)
);

CREATE TABLE IF NOT EXISTS forest_map_x (
    map_name_fk INTEGER,
    forest_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name) ON DELETE CASCADE,
    FOREIGN KEY (forest_name_fk) REFERENCES forest(forest_name) ON DELETE CASCADE,
    PRIMARY KEY (map_name_fk, forest_name_fk)
);

CREATE TABLE IF NOT EXISTS mountain_map_x (
    map_name_fk INTEGER,
    mountain_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name) ON DELETE CASCADE,
    FOREIGN KEY (mountain_name_fk) REFERENCES mountain(mountain_name) ON DELETE CASCADE,
    PRIMARY KEY (map_name_fk, mountain_name_fk)
);

CREATE TABLE IF NOT EXISTS island_map_x (
    map_name_fk INTEGER,
    island_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name) ON DELETE CASCADE,
    FOREIGN KEY (island_name_fk) REFERENCES island(island_name) ON DELETE CASCADE,
    PRIMARY KEY (map_name_fk, island_name_fk)
);

CREATE TABLE IF NOT EXISTS hills_map_x (
    map_name_fk INTEGER,
    hills_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name) ON DELETE CASCADE,
    FOREIGN KEY (hills_name_fk) REFERENCES hills(hills_name) ON DELETE CASCADE,
    PRIMARY KEY (map_name_fk, hills_name_fk)
);

CREATE TABLE IF NOT EXISTS sea_map_x (
    map_name_fk INTEGER,
    sea_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name) ON DELETE CASCADE,
    FOREIGN KEY (sea_name_fk) REFERENCES sea(sea_name) ON DELETE CASCADE,
    PRIMARY KEY (map_name_fk, sea_name_fk)
);

CREATE TABLE IF NOT EXISTS world_map_x (
    map_name_fk INTEGER,
    world_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name) ON DELETE CASCADE,
    FOREIGN KEY (world_name_fk) REFERENCES worlds(world_name) ON DELETE CASCADE,
    PRIMARY KEY (map_name_fk, world_name_fk)
);

CREATE TABLE IF NOT EXISTS continent_map_x (
    map_name_fk INTEGER,
    continent_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name) ON DELETE CASCADE,
    FOREIGN KEY (continent_name_fk) REFERENCES continents(continent_name) ON DELETE CASCADE,
    PRIMARY KEY (map_name_fk, continent_name_fk)
);

CREATE TABLE IF NOT EXISTS zone_map_x (
    map_name_fk INTEGER,
    zone_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name) ON DELETE CASCADE,
    FOREIGN KEY (zone_name_fk) REFERENCES zones(zone_name) ON DELETE CASCADE,
    PRIMARY KEY (map_name_fk, zone_name_fk)
);

CREATE TABLE IF NOT EXISTS region_map_x (
    map_name_fk INTEGER,
    region_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name) ON DELETE CASCADE,
    FOREIGN KEY (region_name_fk) REFERENCES regions(region_name) ON DELETE CASCADE,
    PRIMARY KEY (map_name_fk, region_name_fk)
);

CREATE TABLE IF NOT EXISTS federation_map_x (
    map_name_fk INTEGER,
    federation_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name) ON DELETE CASCADE,
    FOREIGN KEY (federation_name_fk) REFERENCES federations(federation_name) ON DELETE CASCADE,
    PRIMARY KEY (map_name_fk, federation_name_fk)
);

CREATE TABLE IF NOT EXISTS province_map_x (
    map_name_fk INTEGER,
    province_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name) ON DELETE CASCADE,
    FOREIGN KEY (province_name_fk) REFERENCES provinces(province_name) ON DELETE CASCADE,
    PRIMARY KEY (map_name_fk, province_name_fk)
);

CREATE TABLE IF NOT EXISTS canton_map_x (
    map_name_fk INTEGER,
    canton_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name) ON DELETE CASCADE,
    FOREIGN KEY (canton_name_fk) REFERENCES cantons(canton_name) ON DELETE CASCADE,
    PRIMARY KEY (map_name_fk, canton_name_fk)
);

CREATE TABLE IF NOT EXISTS town_map_x (
    map_name_fk INTEGER,
    town_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name) ON DELETE CASCADE,
    FOREIGN KEY (town_name_fk) REFERENCES towns(town_name) ON DELETE CASCADE,
    PRIMARY KEY (map_name_fk, town_name_fk)
);

CREATE TABLE IF NOT EXISTS village_map_x (
    map_name_fk INTEGER,
    village_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name) ON DELETE CASCADE,
    FOREIGN KEY (village_name_fk) REFERENCES villages(village_name) ON DELETE CASCADE,
    PRIMARY KEY (map_name_fk, village_name_fk)
);

CREATE TABLE IF NOT EXISTS precinct_map_x (
    map_name_fk INTEGER,
    precinct_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name) ON DELETE CASCADE,
    FOREIGN KEY (precinct_name_fk) REFERENCES precincts(precinct_name) ON DELETE CASCADE,
    PRIMARY KEY (map_name_fk, precinct_name_fk)
);

CREATE TABLE IF NOT EXISTS scene_map_x (
    map_name_fk INTEGER,
    scene_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name) ON DELETE CASCADE,
    FOREIGN KEY (scene_name_fk) REFERENCES scenes(scene_name) ON DELETE CASCADE,
    PRIMARY KEY (map_name_fk, scene_name_fk)
);
