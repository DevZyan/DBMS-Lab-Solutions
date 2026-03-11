# Optimized Grace Hash Join Algorithm

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Database](https://img.shields.io/badge/Database-Algorithms-000000?style=flat-square)
![Status](https://img.shields.io/badge/Status-Completed-success?style=flat-square)

## Overview

This project implements an optimized **Grace Hash Join** algorithm for computing the natural join of two large relations that cannot fit entirely in memory. The solution dynamically manages memory usage, handles data skew, and employs multiple performance optimizations to efficiently process large-scale CSV datasets.

## Problem Statement

Given two relations P and Q with n and m attributes respectively, where the first two attributes are common between both relations, implement an efficient hash-join algorithm with the following constraints:

- Relations are stored as CSV files with header rows
- Tuples are of variable length
- Relations cannot fit entirely in memory
- Maximum memory usage is limited to p% of available free RAM (supplied via command line)
- Program must handle large-scale data efficiently

## Algorithm

### Grace Hash Join

**Approach:** Partition-Based Hash Join  
**Time Complexity:** O(N + M) average case  
**Space Complexity:** O(p% of free RAM)

**Implementation Phases:**

1. **Schema Analysis:** Auto-detect common attributes from CSV headers
2. **Memory Budgeting:** Calculate available memory based on p% of free RAM
3. **Partitioning:** Split both relations into buckets using deterministic hash function
4. **Build-Probe:** Build hash table on smaller bucket, probe with larger bucket
5. **Merge:** Combine results from all bucket pairs

### Key Optimizations

| Optimization | Purpose | Benefit |
| :--- | :--- | :--- |
| **In-Memory Fast Path** | Skip partitioning if data fits in RAM | ~5s savings on 12MB × 12MB |
| **Adaptive Bloom Filter** | Filter non-matching keys before hash lookup | Reduces unnecessary probes |
| **Skew Detection** | Identify and handle hot keys separately | Prevents memory blowup |
| **Sequential Partitioning** | CPU-bound partition without threading | Avoids GIL overhead |
| **Adaptive Parallelism** | Parallel join only for large buckets | Amortizes subprocess spawn cost |
| **Type Normalization** | Unified handling of int/float/string keys | Correct cross-type equality |
| **Batched I/O** | 1MB buffers + batched writerows | ~128× fewer syscalls |
| **Deterministic Hash** | CRC32 instead of Python hash() | Consistent across processes |

## Usage

### Prerequisites

- Python 3.8 or higher
- pandas library (`pip install pandas`)
- psutil library (`pip install psutil`) - optional, for accurate memory detection

### Running the Algorithm

```bash
python hash_join.py <relation1.csv> <relation2.csv> <p>
```

**Arguments:**
- `relation1.csv` - CSV file for relation P (first line = header)
- `relation2.csv` - CSV file for relation Q (first line = header)
- `p` - Percentage of free RAM to use (0 < p ≤ 100)

### Example

```bash
python hash_join.py data/P.csv data/Q.csv 50
```

This uses 50% of available free RAM for the hash join operation.

### Input Format

Both CSV files must have:
- First line as header with attribute names
- At least two common attributes (first two columns)
- Comma-separated values
- Variable-length tuples supported

**Example P.csv:**
```csv
id,name,dept_id,course_id,gpa
1000000001,Alice,D1,CS1001,3.8
1000000002,Bob,D2,CS1002,3.5
```

**Example Q.csv:**
```csv
dept_id,course_id,location,credits,budget
D1,CS1001,New York,3,100000
D2,CS1002,Boston,4,150000
```

### Output

Results are written to a CSV file named `<relation1>_JOIN_<relation2>.csv` with:
- Header row with all attributes (common attributes appear once)
- All matching tuple combinations from the natural join

## File Structure

```text
Assignment-05/
├── README.md           # Documentation
├── hash_join.py        # Optimized Grace Hash Join implementation
└── sample_data/        # Test CSV files
    ├── P.csv
    └── Q.csv
```

## Technical Highlights

- **Memory-Aware:** Dynamically calculates and respects memory budget
- **Scalable:** Handles datasets larger than available RAM
- **Robust:** Handles type variations (int, float, string) in join keys
- **Deterministic:** Uses CRC32 for consistent hashing across processes
- **Production-Ready:** Comprehensive error handling and logging

## Algorithm Comparison

| Aspect | Simple Hash Join | Grace Hash Join (This Implementation) |
| :--- | :--- | :--- |
| Memory Requirement | O(N + M) | O(p% of RAM) |
| Large Data Support | No | Yes |
| Partitioning | None | Multi-phase |
| Skew Handling | None | Dedicated skew bucket |
| Parallelism | None | Adaptive multiprocessing |
| I/O Efficiency | Standard | Buffered + batched |

## Notes

- Output file is created in the current working directory
- Temporary files are stored in system temp directory and cleaned up automatically
- Logging output shows memory budget, partition count, and execution time
- For small datasets, automatically uses in-memory fast path (no partitioning)