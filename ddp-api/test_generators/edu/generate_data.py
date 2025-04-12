import os
import random
from datetime import datetime, timedelta

import MySQLdb
from faker import Faker

# --- DB 연결 설정 ---
conn = MySQLdb.connect(
    host="test-db",
    user="root",
    passwd="admin",
)

cursor = conn.cursor()
fake = Faker()
script_dir = os.path.dirname(os.path.abspath(__file__))
ddl_path = os.path.join(script_dir, "ddl.sql")
# 0. 테이블 초기화
with open(ddl_path, "r", encoding="utf-8") as f:
    sql_script = f.read()

for statement in sql_script.strip().split(";"):
    if statement.strip():  # 빈 줄 제거
        try:
            cursor.execute(statement + ";")  # 명령어 실행
        except Exception as e:
            print(f"❌ 오류 발생: {e}\n문장: {statement}")

conn.commit()


def execute(sql, data=None):
    cursor.execute(sql, data)
    conn.commit()


# ------------------------
# 1. 사용자 생성
# ------------------------
user_ids = []
instructor_ids = []

for _ in range(10):  # 강사
    name = fake.name()
    execute(
        """
        INSERT INTO members (full_name, email, role, country, birth_date, gender)
        VALUES (%s, %s, 'Instructor', %s, %s, %s)
    """,
        (
            name,
            fake.unique.email(),
            fake.country(),
            fake.date_of_birth(minimum_age=30, maximum_age=55),
            random.choice(["M", "F", "Other"]),
        ),
    )
    user_id = cursor.lastrowid
    user_ids.append(user_id)
    instructor_ids.append(user_id)

for _ in range(100):  # 학생
    name = fake.name()
    execute(
        """
        INSERT INTO members (full_name, email, role, country, birth_date, gender)
        VALUES (%s, %s, 'Student', %s, %s, %s)
    """,
        (
            name,
            fake.unique.email(),
            fake.country(),
            fake.date_of_birth(minimum_age=18, maximum_age=40),
            random.choice(["M", "F", "Other"]),
        ),
    )
    user_ids.append(cursor.lastrowid)

# ------------------------
# 2. 강좌 생성
# ------------------------
course_ids = []
categories = ["Programming", "Design", "Marketing", "Finance", "AI", "Productivity"]

for _ in range(15):
    title = f"{random.choice(['Intro to', 'Mastering', 'Advanced'])} {fake.word().capitalize()}"
    execute(
        """
        INSERT INTO courses (title, description, category, level, language)
        VALUES (%s, %s, %s, %s, %s)
    """,
        (
            title,
            fake.text(200),
            random.choice(categories),
            random.choice(["Beginner", "Intermediate", "Advanced"]),
            random.choice(["English", "Korean", "Spanish"]),
        ),
    )
    course_ids.append(cursor.lastrowid)

# ------------------------
# 3. 강사 배정
# ------------------------
for course_id in course_ids:
    instructor_id = random.choice(instructor_ids)
    execute(
        """
        INSERT INTO instructors (user_id, course_id)
        VALUES (%s, %s)
    """,
        (instructor_id, course_id),
    )

# ------------------------
# 4. 수강 등록
# ------------------------
enrollment_ids = []

for user_id in user_ids:
    if random.random() < 0.7:  # 70% 수강
        course_id = random.choice(course_ids)
        progress = random.randint(0, 100)
        completed = datetime.now() if progress == 100 else None

        execute(
            """
            INSERT INTO enrollments (user_id, course_id, progress_percentage, completed_at)
            VALUES (%s, %s, %s, %s)
        """,
            (user_id, course_id, progress, completed),
        )
        enrollment_ids.append(cursor.lastrowid)

# ------------------------
# 5. 강의 생성
# ------------------------
lesson_ids = []

for course_id in course_ids:
    for i in range(1, random.randint(3, 7)):
        execute(
            """
            INSERT INTO lessons (course_id, title, content_url, order_number, duration_minutes)
            VALUES (%s, %s, %s, %s, %s)
        """,
            (course_id, f"Lesson {i}", fake.url(), i, random.randint(5, 20)),
        )
        lesson_ids.append(cursor.lastrowid)

# ------------------------
# 6. 퀴즈 생성
# ------------------------
quiz_ids = []

for lesson_id in lesson_ids:
    if random.random() < 0.6:  # 60% 강의에 퀴즈 있음
        course_id = random.choice(course_ids)
        execute(
            """
            INSERT INTO quizzes (course_id, lesson_id, title)
            VALUES (%s, %s, %s)
        """,
            (course_id, lesson_id, "Quiz on " + fake.word().capitalize()),
        )
        quiz_ids.append(cursor.lastrowid)

# ------------------------
# 7. 퀴즈 응시 기록
# ------------------------
for quiz_id in quiz_ids:
    for _ in range(random.randint(5, 15)):
        user_id = random.choice(user_ids)
        score = random.randint(40, 100)
        execute(
            """
            INSERT INTO quiz_attempts (quiz_id, user_id, score_obtained, passed)
            VALUES (%s, %s, %s, %s)
        """,
            (quiz_id, user_id, score, score >= 60),
        )

# ------------------------
# 8. 성적 등록
# ------------------------
for enrollment_id in enrollment_ids:
    if random.random() < 0.6:
        score = round(random.uniform(60.0, 100.0), 2)
        grade_letter = random.choice(["A", "B", "C"])
        execute(
            """
            INSERT INTO grades (enrollment_id, final_score, grade_letter)
            VALUES (%s, %s, %s)
        """,
            (enrollment_id, score, grade_letter),
        )

# 완료
cursor.close()
conn.close()
print("✅ 교육 플랫폼 시뮬레이션 데이터 생성 완료!")
