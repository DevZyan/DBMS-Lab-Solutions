-- ============================================================================
-- File: schema.sql
-- Description: COMPANY Database Schema with Integrity Constraints
-- Database: PostgreSQL
-- ============================================================================

-- ----------------------------------------------------------------------------
-- TABLE: Employee
-- ----------------------------------------------------------------------------
CREATE TABLE Employee (
    fname VARCHAR(255) NOT NULL,
    minit CHAR(1),
    lname VARCHAR(255) NOT NULL,
    ssn BIGINT PRIMARY KEY,
    bdate DATE,
    address VARCHAR(255),
    sex CHAR(1),
    salary INTEGER,
    super_ssn BIGINT,
    dno INTEGER,
    CONSTRAINT chk_employee_ssn CHECK (ssn BETWEEN 100000000 AND 999999999),
    CONSTRAINT chk_employee_sex CHECK (sex IN ('M', 'F', 'O')),
    CONSTRAINT chk_employee_salary CHECK (salary >= 0)
);

-- ----------------------------------------------------------------------------
-- TABLE: Department
-- ----------------------------------------------------------------------------
CREATE TABLE Department (
    dname VARCHAR(255) NOT NULL,
    dnumber INTEGER PRIMARY KEY,
    mgr_ssn BIGINT,
    mgr_start_date DATE,
    CONSTRAINT chk_department_number CHECK (dnumber > 0)
);

-- ----------------------------------------------------------------------------
-- TABLE: Dept_Locations
-- ----------------------------------------------------------------------------
CREATE TABLE Dept_Locations (
    dnumber INTEGER,
    dlocation VARCHAR(255),
    PRIMARY KEY (dnumber, dlocation)
);

-- ----------------------------------------------------------------------------
-- TABLE: Works_On
-- ----------------------------------------------------------------------------
CREATE TABLE Works_On (
    essn BIGINT,
    pno INTEGER,
    hours NUMERIC(4,2),
    PRIMARY KEY (essn, pno),
    CONSTRAINT chk_works_on_hours CHECK (hours >= 0 AND hours <= 100)
);

-- ----------------------------------------------------------------------------
-- TABLE: Project
-- ----------------------------------------------------------------------------
CREATE TABLE Project (
    pname VARCHAR(255) NOT NULL,
    pnumber INTEGER PRIMARY KEY,
    plocation VARCHAR(255),
    dnum INTEGER,
    CONSTRAINT chk_project_number CHECK (pnumber > 0)
);

-- ----------------------------------------------------------------------------
-- TABLE: Dependent
-- ----------------------------------------------------------------------------
CREATE TABLE Dependent (
    essn BIGINT,
    dependent_name VARCHAR(255),
    sex CHAR(1),
    bdate DATE,
    relationship VARCHAR(255),
    PRIMARY KEY (essn, dependent_name),
    CONSTRAINT chk_dependent_sex CHECK (sex IN ('M', 'F', 'O'))
);

-- ----------------------------------------------------------------------------
-- FOREIGN KEY CONSTRAINTS
-- ----------------------------------------------------------------------------

ALTER TABLE Employee
    ADD CONSTRAINT fk_employee_super_ssn FOREIGN KEY (super_ssn)
        REFERENCES Employee(ssn) ON DELETE SET NULL,
    ADD CONSTRAINT fk_employee_dno FOREIGN KEY (dno)
        REFERENCES Department(dnumber) ON DELETE SET NULL;

ALTER TABLE Department
    ADD CONSTRAINT fk_department_mgr_ssn FOREIGN KEY (mgr_ssn)
        REFERENCES Employee(ssn) ON DELETE SET NULL;

ALTER TABLE Dept_Locations
    ADD CONSTRAINT fk_dept_locations_dnumber FOREIGN KEY (dnumber)
        REFERENCES Department(dnumber) ON DELETE CASCADE;

ALTER TABLE Works_On
    ADD CONSTRAINT fk_works_on_essn FOREIGN KEY (essn)
        REFERENCES Employee(ssn) ON DELETE CASCADE,
    ADD CONSTRAINT fk_works_on_pno FOREIGN KEY (pno)
        REFERENCES Project(pnumber) ON DELETE CASCADE;

ALTER TABLE Project
    ADD CONSTRAINT fk_project_dnum FOREIGN KEY (dnum)
        REFERENCES Department(dnumber) ON DELETE SET NULL;

ALTER TABLE Dependent
    ADD CONSTRAINT fk_dependent_essn FOREIGN KEY (essn)
        REFERENCES Employee(ssn) ON DELETE CASCADE;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================