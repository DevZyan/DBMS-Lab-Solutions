-- =========================
-- DBMS Lab Assignment 2
-- Data Insertion
-- =========================

-- Students (12 rows)
INSERT INTO Students (student_id, full_name, age, city, email) VALUES
(1,'Amit Kumar',21,'Delhi','amit.kumar@gmail.com'),
(2,'Sara Khan',19,'Mumbai','sara.khan@yahoo.com'),
(3,'Rohan Mehta',22,'Pune','rohan.mehta@gmail.com'),
(4,'Neha Sharma',20,'Bengaluru','neha.sharma@outlook.com'),
(5,'John Mathew',23,'Chennai','john.mathew@gmail.com'),
(6,'Priya Singh',18,'Delhi','priya.singh@yahoo.com'),
(7,'Arjun Patel',24,'Ahmedabad','arjun.patel@gmail.com'),
(8,'Meera Iyer',21,'Chennai','meera.iyer@outlook.com'),
(9,'Kabir Verma',20,'Kolkata','kabir.verma@gmail.com'),
(10,'Ananya Das',22,'Kolkata','ananya.das@yahoo.com'),
(11,'Vikram Rao',19,'Hyderabad','vikram.rao@gmail.com'),
(12,'Fatima Ali',25,'Mumbai','fatima.ali@outlook.com');

-- Courses (8 rows)
INSERT INTO Courses (course_id, course_name, department, fees) VALUES
(101,'Database Systems','CS',6000),
(102,'Data Structures','CS',5500),
(103,'Digital Electronics','EE',5200),
(104,'Signals and Systems','EE',4800),
(105,'Thermodynamics','ME',4500),
(106,'Anatomy Basics','BIO',7000),
(107,'Biostatistics','BIO',6500),
(108,'Intro to AI','CS',8000);

-- Enrollments (20 rows)
INSERT INTO Enrollments (enrollment_id, student_id, course_id, enroll_date) VALUES
(1001,1,101,'2025-01-10'),
(1002,1,102,'2025-02-15'),
(1003,2,101,'2025-01-12'),
(1004,2,104,'2025-03-05'),
(1005,3,103,'2025-01-20'),
(1006,3,108,'2025-04-01'),
(1007,4,101,'2025-02-01'),
(1008,4,105,'2025-02-18'),
(1009,5,106,'2025-01-25'),
(1010,5,107,'2025-03-15'),
(1011,6,102,'2025-01-14'),
(1012,6,105,'2025-02-20'),
(1013,7,108,'2025-01-30'),
(1014,7,101,'2025-03-10'),
(1015,8,107,'2025-02-12'),
(1016,8,104,'2025-04-15'),
(1017,9,103,'2025-02-05'),
(1018,10,108,'2025-03-22'),
(1019,11,105,'2025-01-18'),
(1020,12,106,'2025-02-25');
