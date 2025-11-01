# 0. Getting Started with Python Generators

## Objective
Create a **Python generator** that streams rows from a **MySQL** database one by one.

---

## Description
This project demonstrates how to use Python generators to efficiently handle large datasets stored in a MySQL database.  
Instead of loading all records into memory, the generator fetches each row lazily (one at a time), improving performance and memory usage.

The script **`seed.py`** performs the following tasks:
1. Connects to the MySQL server.
2. Creates the database `ALX_prodev` if it does not exist.
3. Creates the `user_data` table if it does not exist.
4. Populates the table with data from `user_data.csv`.
5. Provides a generator function to stream data row by row.

---

## Database Schema

**Database Name:** `ALX_prodev`

**Table:** `user_data`

