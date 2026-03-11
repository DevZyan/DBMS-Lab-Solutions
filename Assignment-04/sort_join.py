#!/usr/bin/env python3
"""
Sort-Based Natural Join Algorithm

Computes the natural join of two CSV relations by sorting on common attributes
and using a merge-join technique.

Time Complexity: O(N log N + M log M)
Space Complexity: O(N + M) for in-memory storage
"""

import pandas as pd
import sys
from typing import List, Tuple


def read_csv(filename: str) -> pd.DataFrame:
    """Read CSV file and return as DataFrame."""
    return pd.read_csv(filename)


def find_common_columns(df1: pd.DataFrame, df2: pd.DataFrame) -> List[str]:
    """Find common column names between two DataFrames."""
    return list(set(df1.columns) & set(df2.columns))


def sort_based_join(df_p: pd.DataFrame, df_q: pd.DataFrame) -> pd.DataFrame:
    """
    Perform sort-based natural join on two DataFrames.
    
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
    
    # Sort both DataFrames on common columns
    df_p_sorted = df_p.sort_values(by=common_cols).reset_index(drop=True)
    df_q_sorted = df_q.sort_values(by=common_cols).reset_index(drop=True)
    
    # Convert to list for efficient iteration
    p_rows = df_p_sorted.values.tolist()
    q_rows = df_q_sorted.values.tolist()
    
    # Get column indices for common attributes
    p_cols = list(df_p.columns)
    q_cols = list(df_q.columns)
    
    p_common_idx = [p_cols.index(col) for col in common_cols]
    q_common_idx = [q_cols.index(col) for col in common_cols]
    
    # Get indices of non-common columns in Q
    q_uncommon_idx = [i for i, col in enumerate(q_cols) if col not in common_cols]
    
    # Build output column names (common columns appear once)
    output_cols = p_cols + [q_cols[i] for i in q_uncommon_idx]
    
    # Perform merge join using two-pointer technique
    result = []
    i, j = 0, 0
    
    while i < len(p_rows) and j < len(q_rows):
        # Extract join key values
        key_p = [p_rows[i][idx] for idx in p_common_idx]
        key_q = [q_rows[j][idx] for idx in q_common_idx]
        
        if key_p == key_q:
            # Find all matching rows in Q with same key
            temp_j = j
            while temp_j < len(q_rows):
                next_key = [q_rows[temp_j][idx] for idx in q_common_idx]
                if next_key == key_p:
                    # Create joined tuple
                    joined_row = p_rows[i] + [q_rows[temp_j][idx] for idx in q_uncommon_idx]
                    result.append(joined_row)
                    temp_j += 1
                else:
                    break
            
            i += 1
            j = temp_j
        elif key_p < key_q:
            i += 1
        else:
            j += 1
    
    return pd.DataFrame(result, columns=output_cols)


def main():
    """Main entry point for sort-based join."""
    if len(sys.argv) != 3:
        print("Usage: python sort_join.py <file1.csv> <file2.csv>", file=sys.stderr)
        sys.exit(1)
    
    try:
        df_p = read_csv(sys.argv[1])
        df_q = read_csv(sys.argv[2])
        
        result = sort_based_join(df_p, df_q)
        print(result.to_csv(index=False))
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()