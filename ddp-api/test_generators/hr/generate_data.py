import os
import random
from datetime import datetime, timedelta

import MySQLdb
from faker import Faker

# --- 설정 ---
fake = Faker()
conn = MySQLdb.connect(host="test-db", user="root", passwd="admin")
cursor = conn.cursor()

# --- DDL 로드 및 실행 ---
script_dir = os.path.dirname(os.path.abspath(__file__))
ddl_path = os.path.join(script_dir, "ddl.sql")
with open(ddl_path, "r", encoding="utf-8") as f:
    ddl_script = f.read()

for statement in ddl_script.strip().split(";"):
    if statement.strip():
        try:
            cursor.execute(statement + ";")
        except Exception as e:
            print(f"❌ SQL 오류: {e}\n → {statement}")

conn.commit()


def execute(sql, data=None):
    cursor.execute(sql, data)
    conn.commit()


# --- 1. 부서 생성 ---
departments = ["Engineering", "HR", "Sales", "Marketing", "Finance", "Product", "Support", "QA", "Operations", "Legal"]
department_ids = []
for name in departments:
    execute("INSERT INTO departments (name, location) VALUES (%s, %s)", (name, fake.city()))
    department_ids.append(cursor.lastrowid)

# --- 2. 직책 생성 ---
titles = [
    "Intern",
    "Junior Developer",
    "Senior Developer",
    "Team Lead",
    "Manager",
    "Director",
    "VP",
    "CTO",
    "CFO",
    "CEO",
]
position_ids = []
for level, title in enumerate(titles, start=1):
    execute("INSERT INTO positions (title, level) VALUES (%s, %s)", (title, level))
    position_ids.append(cursor.lastrowid)

# --- 3. 직원 생성 + 고용 이력 + 급여 이력 ---
employee_ids = []
for i in range(1000):
    employee_code = f"EMP{i+1000}"
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.unique.email()
    phone = fake.phone_number()
    birth_date = fake.date_of_birth(minimum_age=20, maximum_age=60)
    gender = random.choice(["M", "F", "Other"])
    hire_date = fake.date_between(start_date="-10y", end_date="-30d")
    dept_id = random.choice(department_ids)
    pos_id = random.choice(position_ids)

    # 직원
    execute(
        """
        INSERT INTO employees (
            employee_code, first_name, last_name, email, phone, birth_date, gender,
            hire_date, department_id, position_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """,
        (employee_code, first_name, last_name, email, phone, birth_date, gender, hire_date, dept_id, pos_id),
    )
    emp_id = cursor.lastrowid
    employee_ids.append(emp_id)

    # 고용 이력
    execute(
        """
        INSERT INTO employment_history (employee_id, department_id, position_id, start_date)
        VALUES (%s, %s, %s, %s)
    """,
        (emp_id, dept_id, pos_id, hire_date),
    )

    # 급여 이력
    salary = random.randint(40000, 160000)
    bonus = round(salary * random.uniform(0.05, 0.2), 2)
    execute(
        """
        INSERT INTO salaries (employee_id, base_salary, bonus, effective_from)
        VALUES (%s, %s, %s, %s)
    """,
        (emp_id, salary, bonus, hire_date),
    )

# --- 4. 교육 과정 생성 ---
training_ids = []
for _ in range(8):
    execute(
        """
        INSERT INTO trainings (title, description, category, duration_hours, required)
        VALUES (%s, %s, %s, %s, %s)
    """,
        (
            f"{fake.word().capitalize()} Training",
            fake.text(100),
            random.choice(["Tech", "Management", "Compliance", "Soft Skills", "Security"]),
            random.randint(2, 16),
            random.random() < 0.5,
        ),
    )
    training_ids.append(cursor.lastrowid)

# --- 5. 교육 이수 및 평가 ---
enrollment_ids = []
for emp_id in random.sample(employee_ids, 700):  # 70% 직원 교육 이수
    training_id = random.choice(training_ids)
    completed_at = fake.date_between(start_date="-2y", end_date="today")
    execute(
        """
        INSERT INTO training_enrollments (employee_id, training_id, completed_at)
        VALUES (%s, %s, %s)
    """,
        (emp_id, training_id, completed_at),
    )
    enroll_id = cursor.lastrowid
    enrollment_ids.append(enroll_id)

    # 교육 평가
    score = random.randint(50, 100)
    feedback = fake.sentence()
    execute(
        """
        INSERT INTO training_results (enrollment_id, score, feedback)
        VALUES (%s, %s, %s)
    """,
        (enroll_id, score, feedback),
    )

# --- 6. 성과 평가 ---
from collections import defaultdict

# 직원별 교육 점수 평균 미리 계산
training_score_map = defaultdict(list)
cursor.execute(
    """
    SELECT te.employee_id, tr.score
    FROM training_results tr
    JOIN training_enrollments te ON tr.enrollment_id = te.enrollment_id
    WHERE te.completed_at IS NOT NULL
"""
)
for emp_id, score in cursor.fetchall():
    training_score_map[emp_id].append(score)

for emp_id in employee_ids:
    if random.random() < 0.8:  # 80% 성과 평가
        review_date = fake.date_between(start_date="-1y", end_date="today")
        review_score = random.randint(50, 95)
        reviewer = fake.name()
        weight = random.choice([10, 15, 20, 25])
        feedback = fake.sentence()

        training_scores = training_score_map.get(emp_id, [])
        avg_training_score = sum(training_scores) / len(training_scores) if training_scores else 0

        total_score = round((review_score * (100 - weight) + avg_training_score * weight) / 100)

        execute(
            """
            INSERT INTO performance_reviews (
                employee_id, review_date, reviewer,
                review_score, training_score_weight, total_score, feedback
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
            (emp_id, review_date, reviewer, review_score, weight, total_score, feedback),
        )
# --- 7. 부서별 관리자 지정 ---

for dept_id in department_ids:
    # 해당 부서의 직원들 중에서 Manager 이상만 필터링
    cursor.execute(
        """
        SELECT employee_id FROM employees
        WHERE department_id = %s
        AND position_id IN (
            SELECT position_id FROM positions WHERE level >= 5
        )
        ORDER BY RAND()
        LIMIT 1
    """,
        (dept_id,),
    )
    result = cursor.fetchone()

    if result:
        manager_id = result[0]
        execute(
            """
            INSERT INTO managers (department_id, manager_id)
            VALUES (%s, %s)
        """,
            (dept_id, manager_id),
        )
    else:
        print(f"⚠️ 부서 {dept_id}에 매니저급 직원이 없어 관리자 지정 생략됨.")
# --- 마무리 ---
cursor.close()
conn.close()
print("✅ HR 시뮬레이션 데이터 1000명 생성 완료!")
