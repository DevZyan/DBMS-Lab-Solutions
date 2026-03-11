-- =========================
-- DBMS Lab Assignment 2
-- Schema Definition
-- =========================

-- Students Table
CREATE TABLE Students (
    student_id INTEGER PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    age INTEGER,
    city VARCHAR(50),
    email VARCHAR(100)
);

-- Courses Table
CREATE TABLE Courses (
    course_id INTEGER PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    department VARCHAR(10),
    fees INTEGER
);

-- Enrollments Table
CREATE TABLE Enrollments (
    enrollment_id INTEGER PRIMARY KEY,
    student_id INTEGER,
    course_id INTEGER,
    enroll_date DATE,

    FOREIGN KEY (student_id) REFERENCES Students(student_id),
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);
