/*
_univ_id_fk points to one and only one entry on
the univs table. It contains the value univ._id

location is JSON that can be expanded into a python dict:
{x: real, y: real, z: real}. It is the distance in gigaparsecs
of the cluster's center from the universe's center (big bang origin).

shape is JSON in the form:
{x: real, y: real, z: real, a: real, b: real, c: real}
defineing an ellipsoid (need to identify units)

*/
CREATE TABLE IF NOT EXISTS galactic_clusters (
	_id TEXT PRIMARY KEY,
	_univ_id_fk TEXT,
    name TEXT NOT NULL,
	location TEXT NOT NULL,
	shape TEXT NOT NULL
)
