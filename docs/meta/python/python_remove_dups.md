# Remove dups from a collection

The most efficient way to remove duplicates from a Python list while maintaining the order of elements is to use a combination of a loop and a set. Here’s how you can do it:

### Method 1: Using a Loop and a Set

This method keeps the order of the original list while removing duplicates.

```python
def remove_duplicates(input_list):
    seen = set()  # Create a set to track seen elements
    result = []   # Create a new list to hold unique elements
    
    for item in input_list:
        if item not in seen:  # Check if the item has not been seen before
            seen.add(item)     # Add it to the seen set
            result.append(item)  # Append it to the result list
            
    return result

# Example usage
my_list = [1, 2, 3, 2, 1, 4, 5]
unique_list = remove_duplicates(my_list)
print(unique_list)  # Output: [1, 2, 3, 4, 5]
```

### Method 2: Using `dict.fromkeys()`

In Python 3.7 and later, dictionaries maintain insertion order, so you can use this method to remove duplicates while preserving order.

```python
def remove_duplicates(input_list):
    return list(dict.fromkeys(input_list))

# Example usage
my_list = [1, 2, 3, 2, 1, 4, 5]
unique_list = remove_duplicates(my_list)
print(unique_list)  # Output: [1, 2, 3, 4, 5]
```

### Method 3: Using List Comprehension with a Set

This is a concise version of the loop and set method.

```python
def remove_duplicates(input_list):
    seen = set()
    return [x for x in input_list if not (x in seen or seen.add(x))]

# Example usage
my_list = [1, 2, 3, 2, 1, 4, 5]
unique_list = remove_duplicates(my_list)
print(unique_list)  # Output: [1, 2, 3, 4, 5]
```

### Summary

* **Using a loop and a set**: This is efficient in terms of time complexity, maintaining the order of the list.
* **Using `dict.fromkeys()`**: This is a clean and straightforward method.
* **Using list comprehension**: This provides a compact way to achieve the same result.

All of these methods are effective, but using a loop with a set is often the most commonly used approach for its clarity and efficiency. If you have further questions or need assistance with something else, feel free to ask!
