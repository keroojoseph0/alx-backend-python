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


# 🧪 Task 2: Mock HTTP Calls

## 🎯 Objective
Write unit tests for the `utils.get_json` function **without making real HTTP requests**.  
You’ll use **mocking** to simulate the behavior of the `requests.get` method.

---

## 🧩 Understanding the Function
The `get_json(url)` function likely looks like this:
```python
import requests

def get_json(url):
    response = requests.get(url)
    return response.json()


# 🧪 Task 3: Test Memoization

## 🎯 Objective
Test the `utils.memoize` decorator to ensure that a decorated method caches its result, so repeated calls do not recompute the value.

---

## 🧩 Understanding Memoization
Memoization caches the result of a method/property.  
Example:

```python
class TestClass:
    @memoize
    def a_property(self):
        return self.a_method()

