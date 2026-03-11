# Learning Management System Database

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat-square&logo=postgresql&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-000000?style=flat-square&logo=postgresql&logoColor=white)
![Status](https://img.shields.io/badge/Status-Completed-success?style=flat-square)

## Overview

This project implements a Relational Database Management System (RDBMS) for a Learning Management System (LMS). The solution defines a normalized schema with strict integrity constraints and implements complex analytical queries to extract insights regarding student performance, instructor metrics, and course reviews.

## Problem Statement

The objective was to design a database capable of managing students, instructors, courses, enrollments, and reviews while enforcing specific data validity rules. The system must support analytical queries to identify trends such as high-spending students, course completion rates, and review consistency.

## Database Schema

The database consists of five relations with established referential integrity.

```mermaid
erDiagram
    Students {
        bigint student_id PK
        varchar name
        varchar email
        date joining_date
    }
    Instructors {
        bigint instructor_id PK
        varchar name
        varchar main_area_of_research
    }
    Courses {
        char course_id PK
        varchar name
        bigint instructor_id FK
        decimal price
    }
    Enrollments {
        bigint enrollment_id PK
        bigint student_id FK
        char course_id FK
        date enroll_date
        date completion_date
    }
    Reviews {
        bigint review_id PK
        char course_id FK
        bigint student_id FK
        numeric rating
        date review_date
    }

    Students ||--o{ Enrollments : "enrolls in"
    Students ||--o{ Reviews : "writes"``
    Instructors ||--o{ Courses : "teaches"
    Courses ||--o{ Enrollments : "contains"
    Courses ||--o{ Reviews : "receives"
```

### Table Specifications

| Table | Primary Key | Foreign Keys | Description |
| :--- | :--- | :--- | :--- |
| **Students** | `student_id` | None | Student profile and contact information |
| **Instructors** | `instructor_id` | None | Faculty details and research area |
| **Courses** | `course_id` | `instructor_id` | Course catalog and pricing |
| **Enrollments** | `enrollment_id` | `student_id`, `course_id` | Registration and completion tracking |
| **Reviews** | `review_id` | `student_id`, `course_id` | Course ratings and feedback |

## Integrity Constraints

The schema enforces data validity at the database level using PostgreSQL constraints:

| Constraint Type | Field | Rule |
| :--- | :--- | :--- |
| **Check** | `student_id`, `instructor_id`, `enrollment_id`, `review_id` | Must be 10-digit integers (1000000000 - 9999999999) |
| **Check** | `course_id` | Alphanumeric: 2 uppercase letters followed by 4 digits (Regex: `^[A-Z]{2}[0-9]{4}$`) |
| **Check** | `rating` | Integer value between 1 and 5 |
| **Check** | `price` | Non-negative decimal value |
| **Unique** | `email` | Ensures no duplicate student email addresses |
| **Referential** | All Foreign Keys | `ON DELETE CASCADE` enabled to maintain consistency |

## Queries Implemented

The solution includes seven analytical queries defined in `solution.sql`:

| # | Query Objective | SQL Techniques |
| :--- | :--- | :--- |
| 1 | Courses with average rating higher than overall average | Subquery, Aggregation (`AVG`) |
| 2 | Students who spent more than the average student | JOIN, Nested Subquery, `GROUP BY` |
| 3 | Instructors whose every course has at least one review | `LEFT JOIN`, `HAVING` clause |
| 4 | Students who reviewed a course they did not complete | Multi-table JOIN, Date comparison |
| 5 | Students who completed all courses by a given instructor | Relational Division, `COUNT` |
| 6 | Students enrolled in at least 2 courses by the same instructor | `GROUP BY`, `HAVING` |
| 7 | Students who have reviewed every course they enrolled in | `LEFT JOIN`, Universal Quantification |

## Usage

### Prerequisites

- PostgreSQL 12 or higher
- `psql` command-line tool

### Setup

1.  Create a new database:
    ```bash
    createdb lms_database
    ```

2.  Execute the schema and queries:
    ```bash
    psql -U your_username -d lms_database -f solution.sql
    ```

3.  Verify tables:
    ```sql
    \dt
    ```

## File Structure

```text
Assignment-03/
├── README.md           # Documentation
└── solution.sql        # DDL schema and DML queries
```

## Technical Highlights

- **PostgreSQL Specifics:** Utilizes regular expression operators (`~`) for strict `course_id` validation.
- **Data Integrity:** Comprehensive use of `CHECK` constraints to prevent invalid data entry.
- **Complex Logic:** Implements relational division patterns to handle "all/every" query requirements.
```

