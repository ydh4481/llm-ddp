DROP DATABASE IF EXISTS test_edu;
CREATE DATABASE IF NOT EXISTS test_edu DEFAULT CHARACTER SET utf8mb4;
USE test_edu;

-- 사용자 (학생 & 강사)
CREATE TABLE members (
  user_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '사용자 고유 ID',
  full_name VARCHAR(100) NOT NULL COMMENT '사용자 이름',
  email VARCHAR(100) UNIQUE NOT NULL COMMENT '이메일 (고유)',
  role ENUM('Student', 'Instructor', 'Admin') DEFAULT 'Student' COMMENT '역할',
  registered_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '가입일',
  country VARCHAR(100) COMMENT '국가',
  birth_date DATE COMMENT '생년월일',
  gender ENUM('M', 'F', 'Other') COMMENT '성별',
  is_active BOOLEAN DEFAULT TRUE COMMENT '활성 여부'
) COMMENT='교육 플랫폼 사용자 (학생/강사)';

-- 강좌
CREATE TABLE courses (
  course_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '강좌 ID',
  title VARCHAR(150) NOT NULL COMMENT '강좌 제목',
  description TEXT COMMENT '강좌 설명',
  category VARCHAR(100) COMMENT '카테고리 (예: 프로그래밍, 디자인)',
  level ENUM('Beginner', 'Intermediate', 'Advanced') DEFAULT 'Beginner' COMMENT '난이도',
  language VARCHAR(30) DEFAULT 'English' COMMENT '사용 언어',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '강좌 생성일',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일',
  is_published BOOLEAN DEFAULT TRUE COMMENT '출시 여부'
) COMMENT='개별 교육 강좌 정보';

-- 수강 등록
CREATE TABLE enrollments (
  enrollment_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '수강 등록 ID',
  user_id INT NOT NULL COMMENT '수강자 ID',
  course_id INT NOT NULL COMMENT '강좌 ID',
  enrolled_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '등록 일시',
  progress_percentage INT DEFAULT 0 COMMENT '진도율 (%)',
  completed_at DATETIME COMMENT '완료일',
  FOREIGN KEY (user_id) REFERENCES members(user_id),
  FOREIGN KEY (course_id) REFERENCES courses(course_id)
) COMMENT='사용자의 강좌 수강 등록 내역';

-- 강사-강좌 연결
CREATE TABLE instructors (
  instructor_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '강사-강좌 연결 ID',
  user_id INT NOT NULL COMMENT '강사 ID',
  course_id INT NOT NULL COMMENT '강좌 ID',
  assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '배정일',
  FOREIGN KEY (user_id) REFERENCES members(user_id),
  FOREIGN KEY (course_id) REFERENCES courses(course_id)
) COMMENT='강좌를 맡고 있는 강사 정보';

-- 강의 콘텐츠
CREATE TABLE lessons (
  lesson_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '강의 ID',
  course_id INT NOT NULL COMMENT '강좌 ID',
  title VARCHAR(150) COMMENT '강의 제목',
  content_url TEXT COMMENT '영상 또는 자료 URL',
  order_number INT COMMENT '강의 순서',
  duration_minutes INT COMMENT '강의 시간 (분)',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '생성일',
  FOREIGN KEY (course_id) REFERENCES courses(course_id)
) COMMENT='강좌 내 개별 강의 콘텐츠';

-- 퀴즈
CREATE TABLE quizzes (
  quiz_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '퀴즈 ID',
  course_id INT NOT NULL COMMENT '강좌 ID',
  lesson_id INT COMMENT '강의 ID (옵션)',
  title VARCHAR(100) COMMENT '퀴즈 제목',
  total_score INT DEFAULT 100 COMMENT '퀴즈 총점',
  is_active BOOLEAN DEFAULT TRUE COMMENT '활성 여부',
  FOREIGN KEY (course_id) REFERENCES courses(course_id),
  FOREIGN KEY (lesson_id) REFERENCES lessons(lesson_id)
) COMMENT='강좌 또는 강의에 연결된 퀴즈';

-- 퀴즈 응시 기록
CREATE TABLE quiz_attempts (
  attempt_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '응시 ID',
  quiz_id INT NOT NULL COMMENT '퀴즈 ID',
  user_id INT NOT NULL COMMENT '응시자 ID',
  attempted_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '응시 시간',
  score_obtained INT COMMENT '획득 점수',
  passed BOOLEAN COMMENT '통과 여부',
  FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id),
  FOREIGN KEY (user_id) REFERENCES members(user_id)
) COMMENT='사용자의 퀴즈 응시 결과';

-- 성적
CREATE TABLE grades (
  grade_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '성적 ID',
  enrollment_id INT NOT NULL COMMENT '수강 등록 ID',
  final_score DECIMAL(5,2) COMMENT '최종 점수',
  grade_letter CHAR(2) COMMENT '성적 등급 (A/B/C)',
  graded_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '성적 입력일',
  FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id)
) COMMENT='수강자의 강좌 성적 정보';