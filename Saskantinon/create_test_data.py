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

    # The list of values is incorrect.
    # Several are missing.
    DB.execute_insert("INSERT_GALACTIC_CLUSTER", (
        "Perseus_Cluster",  # external_univ_nm_pk
        "Our_Universe",  # univ_nm_fk
        1.5e16,  # mass_kg
        0.2e16,  # dark_energy_kg
        0.5e16,  # dark_matter_kg
        0.8e16,  # baryonic_matter_kg
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
        10.0,  # timing_pulsar_pulse_per_ms
        12.0,  # timing_pulsar_loc_gly_x
        22.0,  # timing_pulsar_loc_gly_y
        32.0,  # timing_pulsar_loc_gly_z
    ))

    DB.execute_insert("INSERT_GALACTIC_CLUSTER", (
        "Virgo_Cluster",  # external_univ_nm_pk
        "Our_Universe",  # univ_nm_fk
        2.0e16,  # mass_kg
        0.3e16,  # dark_energy_kg
        0.6e16,  # dark_matter_kg
        1.0e16,  # baryonic_matter_kg
        -5.0,  # center_from_univ_center_gly_x
        25.0,  # center_from_univ_center_gly_y
        -15.0,  # center_from_univ_center_gly_z
        -10.0,  # boundary_gly_origin_x
        20.0,  # boundary_gly_origin_y
        -20.0,  # boundary_gly_origin_z
        30.0,  # boundary_gly_width_x
        25.0,  # boundary_gly_height_y
        35.0,  # boundary_gly_depth_z
        "spherical",  # cluster_shape
        1.0,  # shape_pc_x
        1.0,  # shape_pc_y
        1.0,  # shape_pc_z
        30.0,  # shape_axes_a
        25.0,  # shape_axes_b
        35.0,  # shape_axes_c
        0.0,  # shape_rot_pitch
        0.0,  # shape_rot_yaw
        0.0,  # shape_rot_roll
        18750.0,  # volume_pc3
        15.0,  # timing_pulsar_pulse_per_ms
        -3.0,  # timing_pulsar_loc_gly_x
        23.0,  # timing_pulsar_loc_gly_y
        -13.0,  # timing_pulsar_loc_gly_z
    ))

    DB.execute_insert("INSERT_GALACTIC_CLUSTER", (
        "Coma_Cluster",  # external_univ_nm_pk
        "Our_Universe",  # univ_nm_fk
        1.2e16,  # mass_kg
        0.1e16,  # dark_energy_kg
        0.4e16,  # dark_matter_kg
        0.7e16,  # baryonic_matter_kg
        -15.0,  # center_from_univ_center_gly_x
        -5.0,  # center_from_univ_center_gly_y
        10.0,  # center_from_univ_center_gly_z
        -20.0,  # boundary_gly_origin_x
        0.0,  # boundary_gly_origin_y
        5.0,  # boundary_gly_origin_z
        25.0,  # boundary_gly_width_x
        20.0,  # boundary_gly_height_y
        15.0,  # boundary_gly_depth_z
        "ellipsoid",  # cluster_shape
        1.0,  # shape_pc_x
        1.0,  # shape_pc_y
        1.0,  # shape_pc_z
        25.0,  # shape_axes_a
        20.0,  # shape_axes_b
        15.0,  # shape_axes_c
        0.0,  # shape_rot_pitch
        0.0,  # shape_rot_yaw
        0.0,  # shape_rot_roll
        7500.0,  # volume_pc3
        8.0,  # timing_pulsar_pulse_per_ms
        -13.0,  # timing_pulsar_loc_gly_x
        -3.0,  # timing_pulsar_loc_gly_y
        13.0,  # timing_pulsar_loc_gly_z
    ))

    DB.execute_insert("INSERT_GALACTIC_CLUSTER", (
        "Fornax_Cluster",  # external_univ_nm_pk
        "Our_Universe",  # univ_nm_fk
        2.5e16,  # mass_kg
        0.4e16,  # dark_energy_kg
        0.7e16,  # dark_matter_kg
        1.1e16,  # baryonic_matter_kg
        20.0,  # center_from_univ_center_gly_x
        15.0,  # center_from_univ_center_gly_y
        -25.0,  # center_from_univ_center_gly_z
        15.0,  # boundary_gly_origin_x
        10.0,  # boundary_gly_origin_y
        -30.0,  # boundary_gly_origin_z
        35.0,  # boundary_gly_width_x
        30.0,  # boundary_gly_height_y
        25.0,  # boundary_gly_depth_z
        "spherical",  # cluster_shape
        1.0,  # shape_pc_x
        1.0,  # shape_pc_y
        1.0,  # shape_pc_z
        35.0,  # shape_axes_a
        30.0,  # shape_axes_b
        25.0,  # shape_axes_c
        0.0,  # shape_rot_pitch
        0.0,  # shape_rot_yaw
        0.0,  # shape_rot_roll
        26250.0,  # volume_pc3
        20.0,  # timing_pulsar_pulse_per_ms
        22.0,  # timing_pulsar_loc_gly_x
        17.0,  # timing_pulsar_loc_gly_y
        -27.0,  # timing_pulsar_loc_gly_z
    ))

    DB.execute_insert("INSERT_GALACTIC_CLUSTER", (
        "Hydra_Cluster",  # external_univ_nm_pk
        "Our_Universe",  # univ_nm_fk
        0.8e16,  # mass_kg
        0.05e16,  # dark_energy_kg
        0.2e16,  # dark_matter_kg
        0.3e16,  # baryonic_matter_kg
        0.0,  # center_from_univ_center_gly_x
        -20.0,  # center_from_univ_center_gly_y
        0.0,  # center_from_univ_center_gly_z
        -5.0,  # boundary_gly_origin_x
        -25.0,  # boundary_gly_origin_y
        -5.0,  # boundary_gly_origin_z
        15.0,  # boundary_gly_width_x
        10.0,  # boundary_gly_height_y
        15.0,  # boundary_gly_depth_z
        "ellipsoid",  # cluster_shape
        1.0,  # shape_pc_x
        1.0,  # shape_pc_y
        1.0,  # shape_pc_z
        15.0,  # shape_axes_a
        10.0,  # shape_axes_b
        15.0,  # shape_axes_c
        0.0,  # shape_rot_pitch
        0.0,  # shape_rot_yaw
        0.0,  # shape_rot_roll
        2250.0,  # volume_pc3
        5.0,  # timing_pulsar_pulse_per_ms
        2.0,  # timing_pulsar_loc_gly_x
        -23.0,  # timing_pulsar_loc_gly_y
        2.0,  # timing_pulsar_loc_gly_z
    ))

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
