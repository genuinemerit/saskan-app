CREATE TABLE IF NOT EXISTS canal_map_x (
    map_name_fk INTEGER,
    canal_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name),
    FOREIGN KEY (canal_name_fk) REFERENCES canal(canal_name),
    PRIMARY KEY (map_name_fk, canal_name_fk)
);

CREATE TABLE IF NOT EXISTS lake_map_x (
    map_name_fk INTEGER,
    lake_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name),
    FOREIGN KEY (lake_name_fk) REFERENCES lake(lake_name),
    PRIMARY KEY (map_name_fk, lake_name_fk)
);

CREATE TABLE IF NOT EXISTS river_map_x (
    map_name_fk INTEGER,
    river_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name),
    FOREIGN KEY (river_name_fk) REFERENCES river(river_name),
    PRIMARY KEY (map_name_fk, river_name_fk)
);

CREATE TABLE IF NOT EXISTS road_map_x (
    map_name_fk INTEGER,
    road_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name),
    FOREIGN KEY (road_name_fk) REFERENCES road(road_name),
    PRIMARY KEY (map_name_fk, road_name_fk)
);

CREATE TABLE IF NOT EXISTS forest_map_x (
    map_name_fk INTEGER,
    forest_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name),
    FOREIGN KEY (forest_name_fk) REFERENCES forest(forest_name),
    PRIMARY KEY (map_name_fk, forest_name_fk)
);

CREATE TABLE IF NOT EXISTS mountain_map_x (
    map_name_fk INTEGER,
    mountain_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name),
    FOREIGN KEY (mountain_name_fk) REFERENCES mountain(mountain_name),
    PRIMARY KEY (map_name_fk, mountain_name_fk)
);

CREATE TABLE IF NOT EXISTS island_map_x (
    map_name_fk INTEGER,
    island_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name),
    FOREIGN KEY (island_name_fk) REFERENCES island(island_name),
    PRIMARY KEY (map_name_fk, island_name_fk)
);

CREATE TABLE IF NOT EXISTS hills_map_x (
    map_name_fk INTEGER,
    hills_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name),
    FOREIGN KEY (hills_name_fk) REFERENCES hills(hills_name),
    PRIMARY KEY (map_name_fk, hills_name_fk)
);

CREATE TABLE IF NOT EXISTS sea_map_x (
    map_name_fk INTEGER,
    sea_name_fk INTEGER,
    FOREIGN KEY (map_name_fk) REFERENCES maps(map_name),
    FOREIGN KEY (sea_name_fk) REFERENCES sea(sea_name),
    PRIMARY KEY (map_name_fk, sea_name_fk)
);
