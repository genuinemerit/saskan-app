# Python list/dict extend vs. append vs. zip vs. update

The `.extend()` method in Python is used to **extend** a list by appending all the elements from another iterable (such as a list, tuple, string, etc.) to the end of the list. This method modifies the list in place (i.e., it does not return a new list).

## Syntax

```python
list1.extend(iterable)
```

* **`list1`**: The list you want to extend.
* **`iterable`**: The iterable whose elements will be added to `list1`. This can be a list, tuple, string, or any other iterable.

## Key Points

1. The `.extend()` method adds each individual item from the `iterable` to `list1`, **not the entire iterable**.
2. It modifies the original list (`list1`) and does not return a new list.
3. You can pass in any iterable (such as a list, tuple, or even a string), and the elements will be added individually to the list.

### Example 1: Using `.extend()` with a list

```python
# Initial list
list1 = [1, 2, 3]

# List to extend list1 with
list2 = [4, 5, 6]

# Use .extend() to add elements from list2 to list1
list1.extend(list2)

print(list1)
```

**Output**:

```python
[1, 2, 3, 4, 5, 6]
```

In this example, the elements from `list2` are added to the end of `list1`.

### Example 2: Using `.extend()` with a tuple

```python
# Initial list
list1 = [1, 2, 3]

# Tuple to extend list1 with
tuple1 = (4, 5, 6)

# Use .extend() to add elements from tuple1 to list1
list1.extend(tuple1)

print(list1)
```

**Output**:

```python
[1, 2, 3, 4, 5, 6]
```

In this example, a tuple is passed to the `.extend()` method, and its elements are added individually to `list1`.

### Example 3: Using `.extend()` with a string

```python
# Initial list
list1 = ['a', 'b', 'c']

# String to extend list1 with
string1 = "def"

# Use .extend() to add each character of the string to list1
list1.extend(string1)

print(list1)
```

**Output**:

```python
['a', 'b', 'c', 'd', 'e', 'f']
```

In this case, each character of the string `"def"` is added to the list individually.

## Comparison with `.append()`

* **`.append()`** adds **the entire object** as a single element to the list.
* **`.extend()`** adds **each individual element** from an iterable to the list.

```python
list1 = [1, 2]
list2 = [3, 4]

# Using append
list1.append(list2)  # Adds list2 as a single element
print(list1)  # Output: [1, 2, [3, 4]]

# Using extend
list1 = [1, 2]
list1.extend(list2)  # Adds elements of list2 individually
print(list1)  # Output: [1, 2, 3, 4]
```

## When to Use `.extend()`

* When you want to **combine multiple lists** or **add the contents of any iterable** to a list without nesting.
* If you are working with a sequence of elements (e.g., another list, tuple, or string) and you want to **unpack** them into your list.

In summary, `.extend()` is a method that allows you to efficiently add elements from one iterable to another list, making it more versatile than `.append()` when dealing with multiple elements.

---

## zip

The `zip()` function in Python is used to combine multiple iterables (like lists or tuples) element-wise into tuples. It "zips" the iterables together, so that the first elements of each iterable are paired together, then the second elements, and so on.

### Basic Syntax:

```python
zip(iterable1, iterable2, ...)
```

* **iterable1, iterable2, ...**: The iterables you want to zip together. They can be lists, tuples, or any iterable.

### Key Points:

* If the input iterables have different lengths, `zip()` stops at the shortest iterable and discards the remaining elements of the longer iterables.
* It returns an iterator, so you typically need to convert it to a list or another collection type to see the results.

### Example:

```python
list1 = [1, 2, 3]
list2 = ['a', 'b', 'c']

zipped = zip(list1, list2)
print(list(zipped))
```

**Output:**

```python
[(1, 'a'), (2, 'b'), (3, 'c')]
```

### Unzipping:

You can also "unzip" the result by using `zip(*zipped)`:

```python
zipped = [(1, 'a'), (2, 'b'), (3, 'c')]
unzipped = zip(*zipped)
print(list(unzipped))
```

**Output:**

```python
[(1, 2, 3), ('a', 'b', 'c')]
```

### Common Use Cases:

* Pairing related data (e.g., zipping names with ages).
* Iterating over multiple sequences simultaneously in loops.
* Transposing matrices (for example, switching rows and columns in 2D lists).

### Example with Different Lengths:

```python
list1 = [1, 2, 3]
list2 = ['a', 'b']

zipped = zip(list1, list2)
print(list(zipped))
```

**Output:**

```python
[(1, 'a'), (2, 'b')]
```

In this case, `zip()` stops at the end of the shorter list (`list2`).

---

## update (for dicts)

The `update()` method in Python is used to update a dictionary with elements from another dictionary or an iterable of key-value pairs. It modifies the dictionary in place and does not return a new dictionary.

### Syntax:

```python
dict.update(other_dict)
```

or

```python
dict.update(iterable_of_key_value_pairs)
```

* **`other_dict`**: A dictionary whose key-value pairs will be added to the original dictionary. If a key already exists in the dictionary, its value will be updated with the new value.
* **`iterable_of_key_value_pairs`**: An iterable (like a list of tuples) containing key-value pairs to update the dictionary.

### Key Points:

* If a key already exists in the dictionary, the value is updated.
* If the key doesn't exist, the key-value pair is added.
* The method operates **in-place**, modifying the dictionary directly.

### Example 1: Updating with another dictionary:

```python
my_dict = {'a': 1, 'b': 2}
other_dict = {'b': 3, 'c': 4}

my_dict.update(other_dict)
print(my_dict)
```

**Output:**

```python
{'a': 1, 'b': 3, 'c': 4}
```

Here, the value of `'b'` is updated, and the key `'c'` is added.

### Example 2: Updating with a list of key-value pairs:

```python
my_dict = {'a': 1, 'b': 2}
updates = [('b', 3), ('d', 4)]

my_dict.update(updates)
print(my_dict)
```

**Output:**

```python
{'a': 1, 'b': 3, 'd': 4}
```

Here, `'b'` is updated, and `'d'` is added.

### Example 3: Using keyword arguments:

```python
my_dict = {'a': 1, 'b': 2}
my_dict.update(c=3, d=4)
print(my_dict)
```

**Output:**

```python
{'a': 1, 'b': 2, 'c': 3, 'd': 4}
```

In this example, the update method uses keyword arguments to add new key-value pairs.

### Use Case

* Merging dictionaries.
* Updating specific keys with new values.
