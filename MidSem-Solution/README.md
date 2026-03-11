# COMPANY Database - Midsem Solution

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat-square&logo=postgresql&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-000000?style=flat-square&logo=postgresql&logoColor=white)
![Status](https://img.shields.io/badge/Status-Completed-success?style=flat-square)

## Overview

This project implements the COMPANY database schema with comprehensive integrity constraints and analytical queries. The solution covers table creation, foreign key relationships, data insertion, and complex SQL queries for employee, department, and project analysis.

## Database Schema

The COMPANY database consists of six relations modeling a typical organizational structure:

```mermaid
erDiagram
    Employee {
        varchar fname
        char minit
        varchar lname
        bigint ssn PK
        date bdate
        varchar address
        char sex
        integer salary
        bigint super_ssn FK
        integer dno FK
    }
    Department {
        varchar dname
        integer dnumber PK
        bigint mgr_ssn FK
        date mgr_start_date
    }
    Dept_Locations {
        integer dnumber PK,FK
        varchar dlocation PK
    }
    Works_On {
        bigint essn PK,FK
        integer pno PK,FK
        numeric hours
    }
    Project {
        varchar pname
        integer pnumber PK
        varchar plocation
        integer dnum FK
    }
    Dependent {
        bigint essn PK,FK
        varchar dependent_name PK
        char sex
        date bdate
        varchar relationship
    }

    Employee ||--o{ Dependent : "has"
    Employee ||--o{ Works_On : "works on"
    Employee }|--|| Employee : "supervises"
    Department ||--o{ Employee : "employs"
    Department ||--o{ Dept_Locations : "located at"
    Department ||--o{ Project : "controls"
    Project ||--o{ Works_On : "includes"
```

### Table Specifications

| Table | Primary Key | Foreign Keys | Description |
| :--- | :--- | :--- | :--- |
| **Employee** | `ssn` | `super_ssn`, `dno` | Employee personal and employment details |
| **Department** | `dnumber` | `mgr_ssn` | Department information and management |
| **Dept_Locations** | `dnumber`, `dlocation` | `dnumber` | Multiple locations per department |
| **Works_On** | `essn`, `pno` | `essn`, `pno` | Employee project assignments |
| **Project** | `pnumber` | `dnum` | Project details and controlling department |
| **Dependent** | `essn`, `dependent_name` | `essn` | Employee dependent information |

## Integrity Constraints

| Constraint Type | Field | Rule |
| :--- | :--- | :--- |
| **Primary Key** | All tables | Unique identification |
| **Foreign Key** | All relationships | Referential integrity with ON DELETE CASCADE/SET NULL |
| **Check** | `sex` | Values restricted to 'M', 'F', 'O' |
| **Check** | `salary` | Non-negative values |
| **Check** | `hours` | Between 0 and 100 |
| **Unique** | `email` | No duplicate employee emails |

## Queries Implemented

| # | Query | Technique |
| :--- | :--- | :--- |
| 1 | Create database with integrity constraints | DDL, CHECK, FOREIGN KEY |
| 2 | Departments with avg salary > 30000 | JOIN, GROUP BY, HAVING |
| 3 | Employees in dept with highest salary | Nested Subquery |
| 4 | Employees whose supervisor's supervisor = given SSN | Self JOIN (3 levels) |
| 5 | Employees making 10000+ more than minimum salary | Subquery, Arithmetic |
| 6 | View: Project statistics | CREATE VIEW, Aggregation |
| 7 | View: Department statistics | CREATE VIEW, Aggregation |

## Usage

### Prerequisites

- PostgreSQL 12 or higher
- `psql` command-line tool or GUI client (pgAdmin, DBeaver)

### Setup

```bash
# Create database
createdb company_db

# Run schema and data
psql -U your_username -d company_db -f schema.sql

# Run queries
psql -U your_username -d company_db -f queries.sql
```

### Verify Tables

```sql
\dt
```

### Sample Query

```sql
-- View project statistics
SELECT * FROM Project_Stats;
```

## File Structure

```text
Midsem-Solution/
├── README.md           # Documentation
├── schema.sql          # Table creation and constraints
├── data.sql            # Sample data insertion
└── queries.sql         # All 7 queries and views
```

## Technical Highlights

- Comprehensive foreign key relationships with cascading deletes
- Self-referential relationship for employee supervision hierarchy
- Composite primary keys for junction tables (Works_On, Dept_Locations, Dependent)
- View creation for reusable query logic
- Nested subqueries for complex analytical requirements
- Standard SQL JOIN syntax for clarity and maintainability

## Notes

- SSN values are 9-digit integers as per standard format
- Salary values are stored as integers (no decimal places)
- Hours worked on projects allow decimal values (NUMERIC type)
- NULL values permitted for supervisor SSN (top-level executives)