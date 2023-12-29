from pydantic import BaseModel, Field, TypeAlias
from typing import List

class Coord_xyz(BaseModel):
    x: float
    y: float
    z: float

class Coord_abc(BaseModel):
    a: float
    b: float
    c: float

class Direction_pitch_yaw_roll_angle(BaseModel):
    pitch: float
    yaw: float
    roll: float

class GameRect(BaseModel):
    x: float
    y: float
    width: float
    height: float

# Type alias example
CustomList = List[Coord_xyz]

class TotalUniv(BaseModel):
    total_univ_nm_pk: str = ''

class GalacticCluster(BaseModel):
    total_univ_nm_fk: str
    distance_from_univ_center_giga_ly: float
    volume_parsec3: float
    mass_kg: float
    dark_energy_kg: float
    dark_matter_kg: float
    baryonic_matter_kg: float
    timing_pulsar_type: str
    timing_pulsar_pulse_per_ms: float
    timing_pulsar_loc_giga_ly: Coord_xyz
    ellipsoid_shape_parsecs: Coord_xyz
    ellipsoid_shape_semi_axes_parsecs: Coord_abc
    ellilpsoid_shape_rotation: Direction_pitch_yaw_roll_angle
    ellipsoid_bounding_rect_giga_ly: GameRect

def generate_sql_create_table(class_: BaseModel) -> str:
    table_name = class_.__name__
    columns = []

    for field_name, field in class_.__annotations__.items():
        # Extract type and constraints
        field_type = field.__name__ if isinstance(field, TypeAlias) else field
        constraints = []

        if field_name.endswith("_pk"):
            constraints.append("PRIMARY KEY")

        if field_name.endswith("_fk"):
            referenced_table = field_type.replace("_fk", "")
            constraints.append(f"FOREIGN KEY ({field_name}) REFERENCES {referenced_table}({referenced_table}_pk)")

        if not field.default:
            constraints.append("NOT NULL")

        columns.append(f"{field_name} {field_type} {' '.join(constraints)}")

    return f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)});"

# Example usage
galactic_cluster_create_table_sql = generate_sql_create_table(GalacticCluster)
print(galactic_cluster_create_table_sql)
