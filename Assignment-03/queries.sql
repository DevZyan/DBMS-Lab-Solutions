-- Courses with an average rating higher than the overall average
SELECT 
    course_id,
    AVG(rating) AS average_rating
FROM Reviews
GROUP BY course_id
HAVING AVG(rating) > (
    SELECT AVG(rating)
    FROM Reviews
);

-- Students who spent more than the average student
SELECT 
    student_id,
    total_spent
FROM (
    SELECT 
        e.student_id,
        SUM(c.price) AS total_spent
    FROM Enrollments e
    JOIN Courses c ON e.course_id = c.course_id
    GROUP BY e.student_id
) AS student_spending
WHERE total_spent > (
    SELECT AVG(total_spent)
    FROM (
        SELECT 
            SUM(c.price) AS total_spent
        FROM Enrollments e
        JOIN Courses c ON e.course_id = c.course_id
        GROUP BY e.student_id
    ) AS avg_calc
);

-- Instructors whose every course has at least one review
SELECT 
    i.instructor_id,
    i.name
FROM Instructors i
JOIN Courses c ON i.instructor_id = c.instructor_id
LEFT JOIN Reviews r ON c.course_id = r.course_id
GROUP BY i.instructor_id, i.name
HAVING COUNT(c.course_id) = COUNT(r.course_id)
   AND COUNT(c.course_id) > 0;

-- Students who reviewed a course they did not complete
SELECT DISTINCT 
    s.student_id,
    s.name,
    r.course_id
FROM Students s
JOIN Reviews r ON s.student_id = r.student_id
JOIN Enrollments e ON s.student_id = e.student_id 
    AND r.course_id = e.course_id
WHERE e.completion_date IS NULL 
   OR e.completion_date > r.review_date;

-- Students who completed all courses by a given instructor
SELECT 
    s.student_id,
    s.name,
    c.instructor_id
FROM Students s
JOIN Enrollments e ON s.student_id = e.student_id
JOIN Courses c ON e.course_id = c.course_id
WHERE e.completion_date IS NOT NULL
GROUP BY s.student_id, s.name, c.instructor_id
HAVING COUNT(DISTINCT c.course_id) = (
    SELECT COUNT(*)
    FROM Courses
    WHERE instructor_id = c.instructor_id
);

-- Students enrolled in at least 2 courses by the same instructor
SELECT 
    e.student_id,
    s.name,
    c.instructor_id,
    i.name AS instructor_name,
    COUNT(DISTINCT e.course_id) AS course_count
FROM Enrollments e
JOIN Students s ON e.student_id = s.student_id
JOIN Courses c ON e.course_id = c.course_id
JOIN Instructors i ON c.instructor_id = i.instructor_id
GROUP BY e.student_id, s.name, c.instructor_id, i.name
HAVING COUNT(DISTINCT e.course_id) >= 2;

-- Students who have reviewed every course they enrolled in
SELECT 
    e.student_id,
    s.name,
    COUNT(DISTINCT e.course_id) AS enrolled_courses,
    COUNT(DISTINCT r.course_id) AS reviewed_courses
FROM Enrollments e
JOIN Students s ON e.student_id = s.student_id
LEFT JOIN Reviews r ON e.student_id = r.student_id 
    AND e.course_id = r.course_id
GROUP BY e.student_id, s.name
HAVING COUNT(DISTINCT e.course_id) = COUNT(DISTINCT r.course_id);
