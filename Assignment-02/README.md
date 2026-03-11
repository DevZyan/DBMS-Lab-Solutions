````markdown
# Assignment 02 — SQL Schema Design and Query Practice

## Overview

This assignment focuses on practicing core **SQL operations** including schema creation, data manipulation, and query formulation.  
The database models a simple **student–course enrollment system** where students can register for courses and their enrollment details are stored relationally.

The assignment includes table creation, sample data insertion, and a collection of SQL queries demonstrating common database operations.

---

## Objectives

- Design relational database tables
- Define primary and foreign key relationships
- Modify table schemas using `ALTER TABLE`
- Insert, update, and delete records
- Retrieve and filter data using SQL queries
- Perform aggregation operations
- Use conditional logic and subqueries

---

## Database Schema

The database contains three tables.

### Students

Stores student information.

| Column | Type | Description |
|------|------|-------------|
| student_id | INTEGER | Primary key |
| full_name | VARCHAR | Student name |
| age | INTEGER | Student age |
| city | VARCHAR | City of residence |
| email | VARCHAR | Email address |

---

### Courses

Stores course-related information.

| Column | Type | Description |
|------|------|-------------|
| course_id | INTEGER | Primary key |
| course_name | VARCHAR | Name of the course |
| department | VARCHAR | Department offering the course |
| fees | INTEGER | Course fee |

---

### Enrollments

Represents course registrations of students.

| Column | Type | Description |
|------|------|-------------|
| enrollment_id | INTEGER | Primary key |
| student_id | INTEGER | References `Students.student_id` |
| course_id | INTEGER | References `Courses.course_id` |
| enroll_date | DATE | Enrollment date |

---

## Operations Performed

### Database and User Management

- Create and drop database users
- Create and drop databases
- Connect to a database using command-line tools

---

### Table Creation

Tables are created for:

- `Students`
- `Courses`
- `Enrollments`

---

### Table Modification

Schema changes are performed using `ALTER TABLE`.

Example:

```sql
ALTER TABLE Students
ADD COLUMN email VARCHAR(120);
````

---

### Data Manipulation

#### Insert

Sample records are inserted into the tables.

#### Update

```sql
UPDATE Students
SET email = 'amit.kumar@college.edu'
WHERE student_id = 1;
```

#### Delete

```sql
DELETE FROM Enrollments
WHERE enrollment_id = 1016;
```

---

## Query Practice

### Basic Retrieval

```sql
SELECT *
FROM Students
WHERE age > 20;
```

---

### Aggregation

```sql
SELECT MAX(fees), MIN(fees), AVG(fees)
FROM Courses;
```

---

### Filtering and Conditions

```sql
SELECT DISTINCT department
FROM Courses;
```

---

### Ordering Results

```sql
SELECT *
FROM Courses
ORDER BY fees DESC;
```

---

## Repository Structure

```
Assignment-02
│
├── schema.sql
├── data.sql
├── queries.sql
└── README.md
```

---

## Concepts Demonstrated

* Relational database schema design
* SQL Data Definition Language (DDL)
* SQL Data Manipulation Language (DML)
* Data querying and filtering
* Aggregation functions
* Subqueries and conditional logic

---

## Learning Outcome

This assignment provides practical experience in designing relational schemas, managing data, and writing SQL queries to retrieve and analyze information from structured databases.

```
```
:
