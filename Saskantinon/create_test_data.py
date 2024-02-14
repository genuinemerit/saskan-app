from pprint import pprint as pp
from io_db import DataBase
DB = DataBase()


class CreateUniverses(object):
    # I think maybe my constraints are OK and
    # it is the test data that is problematic.
    # Break it down one by one.
    universe_1_values = ('Our Universe', 93.0, 4.1855e80,
                         4.0e80, 13.8, 70.0, 3.0e52, 0.7,
                         0.25, 0.05)
    DB.execute_insert('INSERT_UNIVERSE', universe_1_values)
    external_universe_1_values = ('External Universe 1',
                                  'Our Universe',
                                  3.0e52, 0.7, 0.25, 0.05)
    DB.execute_insert('INSERT_EXTERNAL_UNIVERSE', external_universe_1_values)

    # Example 2: Small universe with faster expansion
    universe_2_values = ('Tiny Universe', 10.0, 41855.0,
                         0.4, 5.0,
                         200.0, 1.0e48, 0.5, 0.4, 0.1)
    DB.execute_insert('INSERT_UNIVERSE', universe_2_values)
    external_universe_2_values = ('External Universe 2',
                                  'Tiny Universe',
                                  1.0e48, 0.5, 0.4, 0.1)
    DB.execute_insert('INSERT_EXTERNAL_UNIVERSE', external_universe_2_values)

    # Example 3: Large universe with slow expansion
    universe_3_values = ('Vast Universe', 150.0, 88200.0,
                         100.0, 20.0,
                         30.0, 5.0e53, 0.9, 0.05, 0.05)
    DB.execute_insert('INSERT_UNIVERSE', universe_3_values)
    external_universe_3_values = ('External Universe 3',
                                  'Vast Universe',
                                  5.0e53, 0.9, 0.05, 0.05)
    DB.execute_insert('INSERT_EXTERNAL_UNIVERSE', external_universe_3_values)

    # Example 4: Universe with significant dark matter
    universe_4_values = ('Dark Universe', 75.0, 17663.0,
                         20.0, 10.0,
                         100.0, 2.0e51, 0.0, 1.0, 0.0)
    DB.execute_insert('INSERT_UNIVERSE', universe_4_values)
    external_universe_4_values = ('External Universe 4',
                                  'Dark Universe',
                                  2.0e51, 0.0, 1.0, 0.0)
    DB.execute_insert('INSERT_EXTERNAL_UNIVERSE', external_universe_4_values)

    # Example 5: Universe with dominant dark energy
    universe_5_values = ('Energetic Universe', 120.0,
                         64286.0, 60.0,
                         15.0, 50.0, 4.0e52, 1.0, 0.0, 0.0)
    DB.execute_insert('INSERT_UNIVERSE', universe_5_values)
    external_universe_5_values = ('External Universe 5',
                                  'Energetic Universe',
                                  4.0e52, 1.0, 0.0, 0.0)
    DB.execute_insert('INSERT_EXTERNAL_UNIVERSE', external_universe_5_values)

    # Test: Delete Universe #5
    # When checking result, note that the delete should
    #  cascade to the associated EXTERNAL_UNIVERSE record
    DB.execute_delete('DELETE_UNIVERSE', ['Energetic Universe'])

    # Test: Update Universe #4 and External Universe #4
    # Keep in mind that the UPDATE SQL requires passing in values
    #  for the entire record in a tuple, minus the PK, which is
    #  THEN provided separately in a list.
    DB.execute_update('UPDATE_UNIVERSE',
                      [76.0, 17663.0, 20.0, 10.0,
                       100.0, 2.0e51, 0.1, 1.5, 5.5],
                      ['Dark Universe'])
    DB.execute_update('UPDATE_EXTERNAL_UNIVERSE',
                      ['Dark Universe', 2.0e51, 0.9, 8.4, 4.5],
                      ['External Universe 4'])

    # Test: Select Unviverse #3 by PK
    data = DB.execute_select_by_pk('SELECT_BY_PK_UNIVERSE',
                                   ['Vast Universe'])
    pp((data))
    # Test: Select All Unviverses
    data = DB.execute_select_all('SELECT_ALL_UNIVERSE')
    pp((data))

    # Attach a Galactic Cluster to Universe #1 "Our Universe"
    DB.execute_insert("INSERT_GALACTIC_CLUSTER", (
        "Perseus Cluster",  # external_univ_nm_pk
        "Our Universe",  # univ_nm_fk
        10.0,  # center_from_univ_center_gly_x
        20.0,  # center_from_univ_center_gly_y
        30.0,  # center_from_univ_center_gly_z
        5.0,  # boundary_gly_origin_x
        15.0,  # boundary_gly_origin_y
        25.0,  # boundary_gly_origin_z
        20.0,  # boundary_gly_width_x
        30.0,  # boundary_gly_height_y
        40.0,  # boundary_gly_depth_z
        "ellipsoid",  # cluster_shape
        1.0,  # shape_pc_x
        1.0,  # shape_pc_y
        1.0,  # shape_pc_z
        20.0,  # shape_axes_a
        30.0,  # shape_axes_b
        40.0,  # shape_axes_c
        0.0,  # shape_rot_pitch
        0.0,  # shape_rot_yaw
        0.0,  # shape_rot_roll
        8000.0,  # volume_pc3
        1.5e16,  # mass_kg
        0.2e16,  # dark_energy_kg
        0.5e16,  # dark_matter_kg
        0.8e16,  # baryonic_matter_kg
        10.0,  # timing_pulsar_pulse_per_ms
        12.0,  # timing_pulsar_loc_gly_x
        22.0,  # timing_pulsar_loc_gly_y
        32.0  # timing_pulsar_loc_gly_z
    ))

    # Test: Select Galactic Cluster by PK
    data = DB.execute_select_by_pk('SELECT_BY_PK_GALACTIC_CLUSTER',
                                   ['Perseus Cluster'])
    pp((data))

    # Attach a Galaxy to Galactic Cluster "Perseus Cluster"
    DB.execute_insert("INSERT_GALAXY", (
        "Blackbird Galaxy",  # galaxy_nm_pk,
        "Perseus Cluster",  # galactic_cluster_nm_fk,
        "medium",  # relative_size,
        100.0,  # center_from_univ_center_kpc_x,
        50.0,   # center_from_univ_center_kpc_y,
        10.0,   # center_from_univ_center_kpc_z,
        100.0,  # halo_radius_pc,
        95.0,   # boundary_pc_origin_x,
        45.0,   # boundary_pc_origin_y,
        8.0,    # boundary_pc_origin_z,
        20.0,   # boundary_pc_width_x,
        5.0,    # boundary_pc_height_y,
        6.0,    # Boundary_pc_depth_z,
        20.0 * 5.0 * 6.0,   # volume_gpc3,
        1.5e14,  # mass_kg,
        'ellipsoid',  # bulge_shape,
        4.0,   # bulge_center_from_center_ly_x,
        2.0,   # bulge_center_from_center_ly_y,
        2.0,   # bulge_center_from_center_ly_z,
        1.0,   # bulge_dim_axes_a,
        0.4,   # bulge_dim_axes_b,
        0.5,   # bulge_dim_axes_c,
        20.0,  # bulge_dim_rot_pitch,
        5.0,   # bulge_dim_rot_yaw,
        2.0,   # bulge_dim_rot_roll,
        1.5e12,  # bulge_black_hole_mass_kg,
        (4.0 * 2.0 * 2.0) / 1000,   # bulge_volume_gpc3,
        1.5e13,   # bulge_total_mass_kg,
        'ellipsoid',  # star_field_shape,
        40.0,    # star_field_dim_from_center_ly_x,
        10.0,    # star_field_dim_from_center_ly_y,
        10.0,    # star_field_dim_from_center_ly_z,
        1.0,     # star_field_dim_axes_a,
        1.0,     # star_field_dim_axes_b,
        1.0,     # star_field_dim_axes_c,
        0.0,     # star_field_dim_rot_pitch,
        4.0,     # star_field_dim_rot_yaw,
        1.0,     # star_field_dim_rot_roll,
        (40.0 * 10.0 * 10.0) / 1000,  # star_field_vol_gpc3,
        1.5e10,  # star_field_mass_kg,
        1.5e8,  # interstellar_mass_kg,
    ))

    # Test: Select Galaxy by PK
    data = DB.execute_select_by_pk('SELECT_BY_PK_GALAXY',
                                   ['Blackbird Galaxy'])
    pp((data))

    # Attach Star Systems to the Galaxy "Blackbird Galaxy"

    DB.execute_insert("insert_star_system.sql", (
        "SmallStarSystem1",
        "Blackbird Galaxy",
        None,  # Nearest pulsar
        None,  # Nearest black hole
        None,  # Binary star system
        0,     # is_black_hole
        0,     # is_pulsar
        0.0,   # boundary_pc_origin_x
        0.0,   # boundary_pc_origin_y
        0.0,   # boundary_pc_origin_z
        10.0,  # boundary_pc_width_x
        10.0,  # boundary_pc_height_y
        10.0,  # boundary_pc_depth_z
        1000.0,  # volume_pc3
        1000.0,  # mass_kg
        "ellipsoid",  # system_shape
        0.0,   # center_from_galaxy_center_pc_x
        0.0,   # center_from_galaxy_center_pc_y
        0.0,   # center_from_galaxy_center_pc_z
        5.0,   # system_dim_axes_a
        5.0,   # system_dim_axes_b
        5.0,   # system_dim_axes_c
        0.0,   # system_dim_rot_pitch
        0.0,   # system_dim_rot_yaw
        0.0,   # system_dim_rot_roll
        "small",  # relative_size
        "G",   # spectral_class
        5.0,   # aprox_age_gyr
        "V",   # luminosity_class
        "rare",  # frequency_of_flares
        "low",  # intensity_of_flares
        "rare",  # frequency_of_comets
        0,     # unbound_planets_cnt
        0,     # orbiting_planets_cnt
        0.0,   # inner_habitable_boundary_au
        0.0,   # outer_habitable_boundary_au
        "circular",  # planetary_orbits_shape
        "stable",    # orbital_stability
        "sparse",    # asteroid_belt_density
        "inner"      # asteroid_belt_loc
    ))

    DB.execute_insert("insert_star_system.sql", (
        "MediumStarSystem1",
        "Blackbird Galaxy",
        None,
        None,
        None,
        0,
        0,
        0.0,
        0.0,
        0.0,
        20.0,
        20.0,
        20.0,
        5000.0,
        5000.0,
        "ellipsoid",
        0.0,
        0.0,
        0.0,
        10.0,
        15.0,
        20.0,
        0.0,
        0.0,
        0.0,
        "medium",
        "G",
        10.0,
        "V",
        "rare",
        "low",
        "rare",
        0,
        0,
        0.0,
        0.0,
        "circular",
        "stable",
        "sparse",
        "inner"
    ))

    DB.execute_insert("insert_star_system.sql", (
        "LargeStarSystem1",
        "Blackbird Galaxy",
        None,
        None,
        None,
        0,
        0,
        0.0,
        0.0,
        0.0,
        30.0,
        30.0,
        30.0,
        10000.0,
        10000.0,
        "ellipsoid",
        0.0,
        0.0,
        0.0,
        20.0,
        25.0,
        30.0,
        0.0,
        0.0,
        0.0,
        "large",
        "G",
        15.0,
        "V",
        "rare",
        "low",
        "rare",
        0,
        0,
        0.0,
        0.0,
        "circular",
        "stable",
        "sparse",
        "inner"
    ))

    DB.execute_insert("insert_star_system.sql", (
        "PulsarSystem1",
        "Blackbird Galaxy",
        None,   # this has to be a valid FK or None
        None,
        None,
        0,
        1,   # is_pulsar
        0.0,
        0.0,
        0.0,
        15.0,
        15.0,
        15.0,
        3000.0,
        3000.0,
        "ellipsoid",
        0.0,
        0.0,
        0.0,
        12.0,
        12.0,
        12.0,
        0.0,
        0.0,
        0.0,
        "medium",
        "G",
        10.0,
        "V",
        "rare",
        "low",
        "rare",
        0,
        0,
        0.0,
        0.0,
        "circular",
        "stable",
        "sparse",
        "inner"
    ))

    DB.execute_insert("insert_star_system.sql", (
        "BinaryStarSystem1",
        "Blackbird Galaxy",
        "PulsarSystem1",    # nearest pulsar
        None,
        None,   # Later, update this to point to binary pair
        0,
        0,
        0.0,
        0.0,
        0.0,
        25.0,
        25.0,
        25.0,
        7000.0,
        7000.0,
        "ellipsoid",
        0.0,
        0.0,
        0.0,
        18.0,
        18.0,
        18.0,
        0.0,
        0.0,
        0.0,
        "medium",
        "G",
        12.0,
        "V",
        "rare",
        "low",
        "rare",
        0,
        0,
        0.0,
        0.0,
        "circular",
        "stable",
        "sparse",
        "inner"
    ))

    DB.execute_insert("insert_star_system.sql", (
        "BinaryStarSystem2",
        "Blackbird Galaxy",
        "PulsarSystem1",      # nearest pulsar
        None,
        "BinaryStarSystem1",  # binary star system pair
        0,
        0,
        0.0,
        0.0,
        0.0,
        25.0,
        25.0,
        25.0,
        7000.0,
        7000.0,
        "ellipsoid",
        0.0,
        0.0,
        0.0,
        18.0,
        18.0,
        18.0,
        0.0,
        0.0,
        0.0,
        "medium",
        "G",
        12.0,
        "V",
        "rare",
        "low",
        "rare",
        0,
        0,
        0.0,
        0.0,
        "circular",
        "stable",
        "sparse",
        "inner"
    ))

    DB.execute_update("update_star_system.sql", [
        "Blackbird Galaxy",
        "PulsarSystem1",
        None,
        "BinaryStarSystem2",   # Updating to point to binary pair
        0,
        0,
        0.0,
        0.0,
        0.0,
        25.0,
        25.0,
        25.0,
        7000.0,
        7000.0,
        "ellipsoid",
        0.0,
        0.0,
        0.0,
        18.0,
        18.0,
        18.0,
        0.0,
        0.0,
        0.0,
        "medium",
        "G",
        12.0,
        "V",
        "rare",
        "low",
        "rare",
        0,
        0,
        0.0,
        0.0,
        "circular",
        "stable",
        "sparse",
        "inner"],
        ["BinaryStarSystem1"],
    )

    data = DB.execute_select_all('SELECT_ALL_STAR_SYSTEM')
    pp((data))
