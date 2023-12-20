SELECT map_name, demographic_ty, contained_by_fk, N_S_km, E_W_km, N_dg_latd, S_dg_latd, E_dg_lond, W_dg_lond, map_object FROM maps
ORDER BY contained_by_fk, map_name ASC;
