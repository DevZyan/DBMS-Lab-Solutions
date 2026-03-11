# Sort-Based and Hash-Based Join Algorithms

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Database](https://img.shields.io/badge/Database-Algorithms-000000?style=flat-square)
![Status](https://img.shields.io/badge/Status-Completed-success?style=flat-square)

## Overview

This project implements two fundamental database join algorithms from scratch: **Sort-Based Join** and **Hash-Based Join**. Both algorithms compute the natural join of two relations stored as CSV files without relying on external database engines.

## Problem Statement

Given two relations P and Q with n and m attributes respectively, where both relations share common attributes, implement:
1. Sort-based algorithm for computing natural join
2. Hash-based algorithm for computing natural join

Input files are provided in CSV format with the first line containing attribute names. The solution must handle arbitrary attributes and identify join keys automatically.

## Algorithms

### Sort-Based Join

**Approach:** Sort-Merge Join  
**Time Complexity:** O(N log N + M log M)  
**Space Complexity:** O(1) for external sort, O(N + M) for in-memory sort

**Implementation Steps:**
1. Identify common attributes between both relations
2. Sort both relations on the common join attributes
3. Use two-pointer technique to scan both sorted relations simultaneously
4. Output matching tuples when join attribute values are equal

### Hash-Based Join

**Approach:** Build-Probe Join  
**Time Complexity:** O(N + M) average case  
**Space Complexity:** O(min(N, M)) for hash table storage

**Implementation Steps:**
1. Identify common attributes between both relations
2. Build hash table on the smaller relation using join attributes as composite key
3. Probe the hash table with tuples from the larger relation
4. Output matching tuples when hash lookup succeeds

## Usage

### Prerequisites

- Python 3.8 or higher
- pandas library (`pip install pandas`)
- No external database required

### Running the Algorithms

```bash
# Sort-based join
python sort_join.py p.csv q.csv

# Hash-based join
python hash_join.py p.csv q.csv
```

### Input Format

Both input CSV files must have:
- First line as header with attribute names
- At least two common attributes for natural join
- Comma-separated values

**Example p.csv:**
```csv
id,name,dept_id,salary
1,Alice,D1,50000
2,Bob,D2,60000
```

**Example q.csv:**
```csv
dept_id,location,budget
D1,New York,100000
D2,Boston,150000
```

### Output

Results are printed to stdout in CSV format with all attributes from both relations. Common attributes appear only once in the output.

## File Structure

```text
Assignment-04/
├── README.md           # Documentation
├── sort_join.py        # Sort-based join implementation
├── hash_join.py        # Hash-based join implementation
└── sample_data/        # Test CSV files
    ├── p.csv
    └── q.csv
```

## Algorithm Comparison

| Aspect | Sort-Based | Hash-Based |
| :--- | :--- | :--- |
| Time Complexity | O(N log N + M log M) | O(N + M) average |
| Space Complexity | O(1) external / O(N+M) memory | O(min(N, M)) |
| Best For | Pre-sorted data, large datasets | Unsorted data, memory available |
| Output Order | Sorted on join attributes | Unordered |
| Equality Join | Yes | Yes |

## Technical Highlights

- Automatic detection of common join attributes from CSV headers
- Handles composite join keys (multiple common attributes)
- Memory-efficient hash table implementation using Python dictionaries
- Clean separation of concerns (IO, Logic, Output)
- Pure Python implementation with pandas for CSV handling

## Notes

- Both implementations assume input files are well-formed CSVs
- Join attributes are identified by matching column names exactly
- Duplicate tuples are preserved in the output (bag semantics)