#!/usr/bin/env python3
"""
Hash-Based Natural Join Algorithm

Computes the natural join of two CSV relations by building a hash table
on one relation and probing with the other.

Time Complexity: O(N + M) average case
Space Complexity: O(min(N, M)) for hash table storage
"""

import pandas as pd
import sys
from typing import List, Dict, Tuple


def read_csv(filename: str) -> pd.DataFrame:
    """Read CSV file and return as DataFrame."""
    return pd.read_csv(filename)


def find_common_columns(df1: pd.DataFrame, df2: pd.DataFrame) -> List[str]:
    """Find common column names between two DataFrames."""
    return list(set(df1.columns) & set(df2.columns))


def build_hash_table(df: pd.DataFrame, common_cols: List[str]) -> Dict[Tuple, List[List]]:
    """
    Build hash table with common columns as composite key.
    
    Args:
        df: DataFrame to build hash table from
        common_cols: List of column names to use as hash key
    
    Returns:
        Dictionary mapping join keys to list of rows
    """
    hash_table = {}
    cols = list(df.columns)
    key_indices = [cols.index(col) for col in common_cols]
    
    for row in df.values.tolist():
        key = tuple(row[idx] for idx in key_indices)
        if key not in hash_table:
            hash_table[key] = []
        hash_table[key].append(row)
    
    return hash_table


def hash_based_join(df_p: pd.DataFrame, df_q: pd.DataFrame) -> pd.DataFrame:
    """
    Perform hash-based natural join on two DataFrames.
    
    Args:
        df_p: First relation (P)
        df_q: Second relation (Q)
    
    Returns:
        DataFrame containing the natural join result
    """
    # Identify common attributes for join
    common_cols = find_common_columns(df_p, df_q)
    
    if not common_cols:
        raise ValueError("No common attributes found for natural join")
    
    # Build hash table on smaller relation (optimization)
    if len(df_p) <= len(df_q):
        hash_table = build_hash_table(df_p, common_cols)
        probe_df = df_q
        build_cols = list(df_p.columns)
        probe_cols = list(df_q.columns)
    else:
        hash_table = build_hash_table(df_q, common_cols)
        probe_df = df_p
        build_cols = list(df_q.columns)
        probe_cols = list(df_p.columns)
    
    # Get column indices
    build_key_idx = [build_cols.index(col) for col in common_cols]
    probe_key_idx = [probe_cols.index(col) for col in common_cols]
    
    # Get indices of non-common columns in probe relation
    probe_uncommon_idx = [i for i, col in enumerate(probe_cols) if col not in common_cols]
    
    # Build output column names
    output_cols = build_cols + [probe_cols[i] for i in probe_uncommon_idx]
    
    # Probe hash table and build result
    result = []
    for probe_row in probe_df.values.tolist():
        key = tuple(probe_row[idx] for idx in probe_key_idx)
        if key in hash_table:
            for build_row in hash_table[key]:
                joined_row = build_row + [probe_row[idx] for idx in probe_uncommon_idx]
                result.append(joined_row)
    
    return pd.DataFrame(result, columns=output_cols)


def main():
    """Main entry point for hash-based join."""
    if len(sys.argv) != 3:
        print("Usage: python hash_join.py <file1.csv> <file2.csv>", file=sys.stderr)
        sys.exit(1)
    
    try:
        df_p = read_csv(sys.argv[1])
        df_q = read_csv(sys.argv[2])
        
        result = hash_based_join(df_p, df_q)
        print(result.to_csv(index=False))
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()