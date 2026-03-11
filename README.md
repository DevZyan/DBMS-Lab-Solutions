# DBMS-Lab-Solutions

![Python](https://img.shields.io/badge/language-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-316192?style=flat-square&logo=postgresql&logoColor=white)
![Course](https://img.shields.io/badge/course-DBMS%20Lab-orange?style=flat-square)
![Status](https://img.shields.io/badge/Status-OnGoing-yellow?style=flat-square)

**Course:** Database Management Systems Lab  
**Institution:** IIT Kharagpur  
**Semester:** Spring 2026  

---

## Repository Overview

This repository contains complete solutions for the Database Management Systems Lab course. Each assignment demonstrates proficiency in database design, SQL query optimization, algorithm implementation, and memory-efficient data processing.

---

## Assignments

| # | Assignment | Focus Area | Key Deliverables | Tech Stack |
|---|------------|-----------|-----------------|------------|
| 1 | B-Tree Index on CSV | Index structures | B-Tree (order 4) implementation, disk-based search | Python |
| 2 | PostgreSQL RDBMS | Schema design | Table creation, ALTER statements, 12+ practice queries | PostgreSQL |
| 3 | Learning Management System | Relational modeling | 5 normalized tables, referential integrity, 7 analytical queries | PostgreSQL |
| MidSem | COMPANY Database | Advanced SQL | Full schema with constraints, views, complex joins and subqueries | PostgreSQL |
| 4 | Join Algorithms | Algorithm design | Sort-based and Hash-based natural join implementations | Python, pandas |
| 5 | Memory-Aware Hash Join | External memory algorithms | Grace Hash Join with p% RAM budget, skew handling, parallelism | Python, multiprocessing |

---

## Repository Structure

```text
DBMS-Lab-Solutions/
│
├── README.md                           # This documentation
│
├── Assignment-01/                      # B-Tree Index Implementation
│   ├── README.md
│   ├── btree_index.py
│   └── sample.csv
│
├── Assignment-02/                      # PostgreSQL Practice Queries
│   ├── README.md
│   ├── schema.sql
│   ├── data.sql
│   └── queries.sql
│
├── Assignment-03/                      # Learning Management System
│   ├── README.md
│   ├── schema.sql
│   ├── data.sql
│   └── queries.sql
│
├── Midsem-Solution/                    # COMPANY Database
│   ├── README.md
│   ├── schema.sql
│   ├── data.sql
│   └── queries.sql
│
├── Assignment-04/                      # Join Algorithms
│   ├── README.md
│   ├── sort_join.py
│   ├── hash_join.py
│   └── sample_data/
│       ├── P.csv
│       └── Q.csv
│
└── Assignment-05/                      # Memory-Aware Grace Hash Join
    ├── README.md
    ├── hash_join.py
    └── sample_data/
        ├── P.csv
        └── Q.csv
```

---

## Prerequisites

### For PostgreSQL Assignments (02, 03, MidSem)
- PostgreSQL 12 or higher
- `psql` command-line tool or GUI client (pgAdmin, DBeaver)

### For Python Assignments (01, 04, 05)
- Python 3.8 or higher
- Required packages:
  ```bash
  pip install pandas psutil
  ```

---

## Quick Start

### Running a PostgreSQL Assignment

```bash
# Navigate to assignment folder
cd Assignment-03

# Create and setup database
createdb lms_database
psql -U your_username -d lms_database -f schema.sql
psql -U your_username -d lms_database -f data.sql

# Execute queries
psql -U your_username -d lms_database -f queries.sql
```

### Running a Python Assignment

```bash
# Assignment 4: Hash-based join
python Assignment-04/hash_join.py sample_data/P.csv sample_data/Q.csv

# Assignment 5: Memory-aware Grace Hash Join (uses 50% of free RAM)
python Assignment-05/hash_join.py sample_data/P.csv sample_data/Q.csv 50
```

---

## Technical Highlights

### Database Design
- Normalized schemas with proper primary/foreign key relationships
- CHECK constraints for data validation at the database level
- Referential integrity with ON DELETE CASCADE/SET NULL policies
- PostgreSQL-specific features: regex validation, composite keys, views

### Algorithm Implementation
- **B-Tree Index**: Disk-aware search with node splitting and rebalancing
- **Sort-Based Join**: Merge-join algorithm with two-pointer technique
- **Hash-Based Join**: Build-probe with adaptive hash table sizing
- **Grace Hash Join**: External memory algorithm with partitioning, skew detection, and parallel execution

### Performance Optimizations (Assignment 5)
- Memory budgeting based on available RAM percentage
- In-memory fast path for small datasets
- CRC32 deterministic hashing for consistent multiprocessing
- Adaptive Bloom filter to reduce unnecessary probes
- Batched I/O with 1MB buffers for reduced syscall overhead
- Skew key detection and dedicated overflow handling
