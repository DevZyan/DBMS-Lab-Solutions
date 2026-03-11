-- ============================================================================
-- File: schema.sql
-- Description: DDL statements for Learning Management System Database
-- Database: PostgreSQL
-- ============================================================================

-- ----------------------------------------------------------------------------
-- TABLE CREATION
-- Create tables in order of dependency (Parents before Children).
-- ----------------------------------------------------------------------------

-- Table: Students
-- Stores student profile information.
CREATE TABLE Students (
    student_id BIGINT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    joining_date DATE NOT NULL,
    CONSTRAINT chk_students_id CHECK (student_id BETWEEN 1000000000 AND 9999999999)
);

-- Table: Instructors
-- Stores faculty details and research specialization.
CREATE TABLE Instructors (
    instructor_id BIGINT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    main_area_of_research VARCHAR(200),
    CONSTRAINT chk_instructors_id CHECK (instructor_id BETWEEN 1000000000 AND 9999999999)
);

-- Table: Courses
-- Stores course catalog, pricing, and instructor assignment.
CREATE TABLE Courses (
    course_id CHAR(6) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    instructor_id BIGINT NOT NULL,
    price DECIMAL(8,2) NOT NULL,
    CONSTRAINT chk_courses_price CHECK (price >= 0),
    CONSTRAINT chk_courses_id_format CHECK (course_id ~ '^[A-Z]{2}[0-9]{4}$'),
    CONSTRAINT fk_courses_instructor FOREIGN KEY (instructor_id)
        REFERENCES Instructors(instructor_id)
        ON DELETE CASCADE
);

-- Table: Enrollments
-- Tracks student registration and completion status.
-- completion_date is nullable to account for ongoing/incomplete courses.
CREATE TABLE Enrollments (
    enrollment_id BIGINT PRIMARY KEY,
    student_id BIGINT NOT NULL,
    course_id CHAR(6) NOT NULL,
    enroll_date DATE NOT NULL,
    completion_date DATE,
    CONSTRAINT chk_enrollments_id CHECK (enrollment_id BETWEEN 1000000000 AND 9999999999),
    CONSTRAINT fk_enrollments_student FOREIGN KEY (student_id)
        REFERENCES Students(student_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_enrollments_course FOREIGN KEY (course_id)
        REFERENCES Courses(course_id)
        ON DELETE CASCADE
);

-- Table: Reviews
-- Stores student feedback and rating system.
CREATE TABLE Reviews (
    review_id BIGINT PRIMARY KEY,
    course_id CHAR(6) NOT NULL,
    student_id BIGINT NOT NULL,
    rating INTEGER NOT NULL,
    review_date DATE,
    CONSTRAINT chk_reviews_id CHECK (review_id BETWEEN 1000000000 AND 9999999999),
    CONSTRAINT chk_reviews_rating CHECK (rating BETWEEN 1 AND 5),
    CONSTRAINT fk_reviews_student FOREIGN KEY (student_id)
        REFERENCES Students(student_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_reviews_course FOREIGN KEY (course_id)
        REFERENCES Courses(course_id)
        ON DELETE CASCADE
);

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
