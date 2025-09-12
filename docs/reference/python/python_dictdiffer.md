# Diffs between Dicts

To find the differences between two dictionaries in Python, you can use the `dictdiffer` module, which is available in the `difflib` standard library. The `dictdiffer` module provides a flexible way to compare dictionaries and find the added, removed, and modified items. Here's an example:

```python
from dictdiffer import diff, patch, swap, revert

# Example dictionaries
dict1 = {'a': 1, 'b': 2, 'c': 3}
dict2 = {'a': 1, 'b': 3, 'd': 4}

# Find the differences
differences = list(diff(dict1, dict2))

# Print the differences
for diff_type, key, values in differences:
    print(f"{diff_type}: {key} - {values}")

# Example of applying the differences to create a new dictionary
new_dict = patch(differences, dict1)
print("New Dictionary:", new_dict)
```

This example uses the `dictdiffer` module to find the differences between `dict1` and `dict2`. The `diff` function returns a generator of differences, and each difference is a tuple indicating the type of difference (added, removed, or modified), the key, and the values.

If you don't have the `dictdiffer` module installed, you can install it using:

```bash
pip install dictdiffer
```

This method provides a fine-grained comparison, but if you're looking for a simpler approach and don't need the detailed differences, you can use the set operations. Here's an example:

```python
# Example dictionaries
dict1 = {'a': 1, 'b': 2, 'c': 3}
dict2 = {'a': 1, 'b': 3, 'd': 4}

# Find added, removed, and modified keys
added_keys = set(dict2.keys()) - set(dict1.keys())
removed_keys = set(dict1.keys()) - set(dict2.keys())
modified_keys = set(key for key in dict1.keys() & dict2.keys() if dict1[key] != dict2[key])

print("Added keys:", added_keys)
print("Removed keys:", removed_keys)
print("Modified keys:", modified_keys)
```

This second approach provides a more high-level view of the differences and might be sufficient for simpler use cases.
