import json
import sys

from jsonschema import Draft202012Validator

schema_path, data_path = sys.argv[1], sys.argv[2]
schema = json.load(open(schema_path))
data = json.load(open(data_path))
errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: e.path)
for e in errors:
    print(f"{list(e.path)}: {e.message}")
sys.exit(1 if errors else 0)
