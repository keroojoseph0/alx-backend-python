# 🧪 Task 0: Parameterize a Unit Test

## 🎯 Objective
Write your **first unit test** for the `utils.access_nested_map` function using Python’s `unittest` module.  
The goal is to verify that this function correctly returns values from nested dictionaries (maps) given a path of keys.

---

## 🧩 Understanding the Function
The function `access_nested_map(nested_map, path)` retrieves a value from a nested dictionary by following a sequence of keys.

Example:
```python
from utils import access_nested_map

result = access_nested_map({"a": {"b": 2}}, ("a", "b"))
print(result)  # Output: 2
