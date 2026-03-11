-- ============================================================================
-- Departments with avg salary > 30000
-- ============================================================================

SELECT 
    d.dname,
    COUNT(e.ssn) AS employee_count
FROM Department d
JOIN Employee e ON d.dnumber = e.dno
GROUP BY d.dname
HAVING AVG(e.salary) > 30000;

-- ============================================================================
-- Employees in dept with highest salary employee
-- ============================================================================

SELECT 
    e.fname,
    e.lname
FROM Employee e
WHERE e.dno = (
    SELECT e2.dno
    FROM Employee e2
    WHERE e2.salary = (SELECT MAX(salary) FROM Employee)
);

-- ============================================================================
-- Employees whose supervisor's supervisor = given SSN
-- ============================================================================

SELECT 
    e.fname,
    e.lname
FROM Employee e
JOIN Employee supervisor ON e.super_ssn = supervisor.ssn
JOIN Employee supersuper ON supervisor.super_ssn = supersuper.ssn
WHERE supersuper.ssn = 123456789;

-- ============================================================================
-- Employees making 10000+ more than minimum salary
-- ============================================================================

SELECT 
    fname,
    lname,
    salary
FROM Employee
WHERE salary > (SELECT MIN(salary) FROM Employee) + 10000;

-- ============================================================================
-- View - Project Statistics
-- ============================================================================

CREATE VIEW Project_Stats AS
SELECT 
    p.pname AS project_name,
    d.dname AS department_name,
    COUNT(w.essn) AS employee_count,
    COALESCE(SUM(w.hours), 0) AS total_hours
FROM Project p
JOIN Department d ON p.dnum = d.dnumber
LEFT JOIN Works_On w ON p.pnumber = w.pno
GROUP BY p.pname, d.dname;

-- ============================================================================
-- View - Department Statistics (Alternative since Q7 = Q6)
-- ============================================================================

CREATE VIEW Department_Stats AS
SELECT 
    d.dname,
    COUNT(e.ssn) AS employee_count,
    AVG(e.salary) AS avg_salary,
    MAX(e.salary) AS max_salary,
    MIN(e.salary) AS min_salary
FROM Department d
LEFT JOIN Employee e ON d.dnumber = e.dno
GROUP BY d.dname;