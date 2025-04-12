DROP DATABASE IF EXISTS test_hr;
CREATE DATABASE IF NOT EXISTS test_hr DEFAULT CHARACTER SET utf8mb4;
USE test_hr;

-- 부서
CREATE TABLE departments (
  department_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '부서 ID',
  name VARCHAR(100) NOT NULL COMMENT '부서명',
  location VARCHAR(100) COMMENT '근무 위치'
) COMMENT='회사 내 부서 정보';

-- 직급
CREATE TABLE positions (
  position_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '직책 ID',
  title VARCHAR(100) NOT NULL COMMENT '직책 이름',
  level INT COMMENT '직책 레벨 (높을수록 상위)'
) COMMENT='직원의 직책 정보';

-- 직원
CREATE TABLE employees (
  employee_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '직원 ID',
  employee_code VARCHAR(20) UNIQUE NOT NULL COMMENT '사번',
  first_name VARCHAR(50) NOT NULL COMMENT '이름',
  last_name VARCHAR(50) NOT NULL COMMENT '성',
  email VARCHAR(100) UNIQUE NOT NULL COMMENT '이메일',
  phone VARCHAR(30) COMMENT '전화번호',
  birth_date DATE COMMENT '생년월일',
  gender ENUM('M', 'F', 'Other') COMMENT '성별',
  hire_date DATE NOT NULL COMMENT '입사일',
  department_id INT COMMENT '현재 소속 부서',
  position_id INT COMMENT '현재 직책',
  is_active BOOLEAN DEFAULT TRUE COMMENT '재직 여부',
  FOREIGN KEY (department_id) REFERENCES departments(department_id),
  FOREIGN KEY (position_id) REFERENCES positions(position_id)
) COMMENT='직원 기본 정보';

-- 고용 이력
CREATE TABLE employment_history (
  history_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '이력 ID',
  employee_id INT NOT NULL COMMENT '직원 ID',
  department_id INT NOT NULL COMMENT '부서 ID',
  position_id INT NOT NULL COMMENT '직책 ID',
  start_date DATE NOT NULL COMMENT '시작일',
  end_date DATE COMMENT '종료일',
  FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
  FOREIGN KEY (department_id) REFERENCES departments(department_id),
  FOREIGN KEY (position_id) REFERENCES positions(position_id)
) COMMENT='직원의 조직 및 직책 이동 이력';

-- 급여 이력
CREATE TABLE salaries (
  salary_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '급여 이력 ID',
  employee_id INT NOT NULL COMMENT '직원 ID',
  base_salary DECIMAL(10,2) COMMENT '기본 급여',
  bonus DECIMAL(10,2) DEFAULT 0.0 COMMENT '보너스',
  effective_from DATE NOT NULL COMMENT '시작일',
  effective_to DATE COMMENT '종료일',
  FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
) COMMENT='직원 급여 이력';

-- 교육 과정
CREATE TABLE trainings (
  training_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '교육 ID',
  title VARCHAR(150) NOT NULL COMMENT '교육명',
  description TEXT COMMENT '설명',
  category VARCHAR(100) COMMENT '분류',
  duration_hours INT COMMENT '교육 시간',
  required BOOLEAN DEFAULT FALSE COMMENT '필수 여부',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '등록일'
) COMMENT='사내 교육 과정 정보';

-- 교육 이수 내역
CREATE TABLE training_enrollments (
  enrollment_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '교육 수강 ID',
  employee_id INT NOT NULL COMMENT '직원 ID',
  training_id INT NOT NULL COMMENT '교육 ID',
  enrolled_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '등록일',
  completed_at DATETIME COMMENT '이수일',
  FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
  FOREIGN KEY (training_id) REFERENCES trainings(training_id)
) COMMENT='직원의 교육 수강 내역';

-- 교육 평가 결과
CREATE TABLE training_results (
  result_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '교육 평가 ID',
  enrollment_id INT NOT NULL COMMENT '교육 수강 ID',
  score INT COMMENT '평가 점수 (0~100)',
  feedback TEXT COMMENT '강사 피드백',
  FOREIGN KEY (enrollment_id) REFERENCES training_enrollments(enrollment_id)
) COMMENT='교육 과정의 평가 결과';

-- 성과 평가
CREATE TABLE performance_reviews (
  review_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '평가 ID',
  employee_id INT NOT NULL COMMENT '직원 ID',
  review_date DATE NOT NULL COMMENT '평가일',
  reviewer VARCHAR(100) COMMENT '평가자',
  review_score INT COMMENT '성과 평가 점수 (0~100)',
  training_score_weight INT DEFAULT 20 COMMENT '교육 평가 반영 비율 (%)',
  total_score INT COMMENT '최종 점수 (성과 평가 + 교육 반영)',
  feedback TEXT COMMENT '평가 의견',
  FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
) COMMENT='직원의 성과 평가 기록 (교육 반영 포함)';

-- 부서 관리자
CREATE TABLE managers (
  department_id INT PRIMARY KEY COMMENT '부서 ID',
  manager_id INT NOT NULL COMMENT '관리자 직원 ID',
  assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '배정일시',
  FOREIGN KEY (department_id) REFERENCES departments(department_id),
  FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
) COMMENT='부서별 관리자 지정';