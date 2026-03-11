-- ==========================================
-- DBMS Lab Assignment 2
-- Query Collection
-- ==========================================


-- ==========================================
-- 1. Table Modification
-- ==========================================

-- Q2.2 Modify the data type of the fees column
ALTER TABLE Courses
ALTER COLUMN fees TYPE INTEGER;



-- ==========================================
-- 2. Data Manipulation
-- ==========================================

-- Q4.2 Increase fees of CS department courses by 10x
UPDATE Courses
SET fees = fees * 10
WHERE department = 'CS';

-- Q4.3 Delete students younger than 18
DELETE FROM Students
WHERE age < 18;



-- ==========================================
-- 3. Basic Retrieval Queries
-- ==========================================

-- Q5.1 Retrieve all students
SELECT *
FROM Students;

-- Q5.2 Retrieve student names and emails
SELECT full_name, email
FROM Students;

-- Q5.3 Students older than 20
SELECT student_id, full_name, age, city
FROM Students
WHERE age > 20;

-- Q5.4 First 3 students ordered by ID
SELECT *
FROM Students
ORDER BY student_id
LIMIT 3;

-- Q5.5 Aggregate statistics on course fees
SELECT
    MAX(fees) AS max_fee,
    MIN(fees) AS min_fee,
    SUM(fees) AS total_fee,
    AVG(fees) AS avg_fee
FROM Courses;

-- Q5.6 Students aged 18, 20, or 22
SELECT *
FROM Students
WHERE age IN (18, 20, 22);

-- Q5.7 Distinct departments
SELECT DISTINCT department
FROM Courses;

-- Q5.8 Courses ordered by highest fees
SELECT course_id, course_name, department, fees
FROM Courses
ORDER BY fees DESC;

-- Q5.9 Students older than 20 from Delhi
SELECT *
FROM Students
WHERE age > 20
AND city = 'Delhi';



-- ==========================================
-- 4. Conditional Queries
-- ==========================================

-- H1 Students from Delhi or Mumbai aged 19–23
SELECT *
FROM Students
WHERE city IN ('Delhi', 'Mumbai')
AND age BETWEEN 19 AND 23
ORDER BY age DESC;

-- H2 Gmail or Outlook users not from Chennai
SELECT *
FROM Students
WHERE email LIKE '%gmail%'
   OR email LIKE '%outlook%'
AND city <> 'Chennai';

-- H3 Names starting with 'A' or ending with 'a' and age ≥ 20
SELECT *
FROM Students
WHERE (full_name LIKE 'A%' OR full_name LIKE '%a')
AND age >= 20;

-- H4 Students excluding age 22
SELECT *
FROM Students
WHERE age <> 22
ORDER BY age DESC
LIMIT 5;

-- H5 Distinct cities excluding Delhi
SELECT DISTINCT city
FROM Students
WHERE city <> 'Delhi';

-- H6 CS and EE courses with fees greater than 5000
SELECT *
FROM Courses
WHERE department IN ('CS', 'EE')
AND fees > 5000
ORDER BY fees DESC;

-- H7 Courses containing 'Data' or 'Intro' but not BIO
SELECT *
FROM Courses
WHERE (course_name LIKE '%Data%' OR course_name LIKE '%Intro%')
AND department <> 'BIO';

-- H8 Three lowest fee courses excluding fee = 4500
SELECT *
FROM Courses
WHERE fees <> 4500
ORDER BY fees ASC
LIMIT 3;



-- ==========================================
-- 5. Enrollment Queries
-- ==========================================

-- H9 Enrollments after Feb 1, 2025 for selected courses
SELECT *
FROM Enrollments
WHERE enroll_date > '2025-02-01'
AND course_id IN (101, 102, 108);

-- H10 January enrollments for students 1–6
SELECT *
FROM Enrollments
WHERE enroll_date BETWEEN '2025-01-01' AND '2025-01-31'
AND student_id BETWEEN 1 AND 6;



-- ==========================================
-- 6. Subqueries
-- ==========================================

-- H11 Students enrolled in at least one course
SELECT *
FROM Students
WHERE student_id IN (
    SELECT student_id
    FROM Enrollments
);

-- H12 Students not enrolled in any course
SELECT *
FROM Students
WHERE student_id NOT IN (
    SELECT student_id
    FROM Enrollments
);

-- H13 Courses with enrollments
SELECT *
FROM Courses
WHERE course_id IN (
    SELECT course_id
    FROM Enrollments
);

-- H14 Courses with no enrollments
SELECT *
FROM Courses
WHERE course_id NOT IN (
    SELECT course_id
    FROM Enrollments
);

-- H15 Students older than the average age
SELECT *
FROM Students
WHERE age > (
    SELECT AVG(age)
    FROM Students
);

-- H16 Courses with above-average fees excluding BIO
SELECT *
FROM Courses
WHERE fees > (
    SELECT AVG(fees)
    FROM Courses
)
AND department <> 'BIO';

-- H17 Enrollments for the cheapest course
SELECT *
FROM Enrollments
WHERE course_id = (
    SELECT course_id
    FROM Courses
    ORDER BY fees ASC
    LIMIT 1
);

-- H18 Students from Delhi or Mumbai not enrolled in course 101
SELECT *
FROM Students
WHERE city IN ('Delhi', 'Mumbai')
AND student_id NOT IN (
    SELECT student_id
    FROM Enrollments
    WHERE course_id = 101
);
