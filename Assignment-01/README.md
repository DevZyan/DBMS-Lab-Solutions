# Assignment 01 — B-Tree Index for CSV Table

## Overview

This assignment implements a **B-Tree index** to support efficient lookup of records stored in a CSV-based relational table.

The program reads a CSV file, constructs a **B-Tree with maximum branching factor 4** on the **primary key column**, and retrieves records quickly when queried with a key value.

Instead of scanning the entire file linearly, the program stores **byte offsets of records** inside the B-Tree. When a key is searched, the offset is retrieved from the index and the corresponding record is fetched directly from the file.

---

## Program Usage

Run the program from the command line:

```
python btree_index.py <csv_file> <primary_key_value>
```

Example:

```
python btree_index.py students.csv 101
```

Example Output:

```
id,name,age,department
101,John,21,Computer Science
```

---

## How the Program Works

1. The CSV file is scanned once to build the index.
2. For every record:

   * The **primary key** (first column) is extracted.
   * The **byte position of the record in the file** is stored.
3. The key and file offset are inserted into a **B-Tree index**.
4. When a search query is issued:

   * The B-Tree is traversed to locate the key.
   * The stored offset is used to directly read the record from the file.

This avoids scanning the entire dataset and simulates how indexing works in database systems.

---

## Index Persistence

The B-Tree index is stored on disk using two files:

```
<csv_file>.btree_index.meta
<csv_file>.btree_index.nodes
```

* `.meta` stores metadata such as the root node and next node ID
* `.nodes` stores serialized B-Tree nodes

This allows the index to be reused without rebuilding it every time.

---

## Repository Structure

```
Assignment-01
│
├── btree_index.py   # B-Tree implementation and search program
├── sample.csv             # Example dataset
└── README.md
```

---

## Concepts Demonstrated

* B-Tree data structure
* Database indexing concepts
* File-based storage and byte offsets
* Efficient record retrieval from disk
* Command-line program design

---

## Learning Outcome

This assignment demonstrates how **database indexing structures such as B-Trees** enable efficient record retrieval, reducing search complexity from **O(n)** for a sequential scan to approximately **O(log n)** using indexed lookup.

