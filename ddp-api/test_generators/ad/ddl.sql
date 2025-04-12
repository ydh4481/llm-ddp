DROP DATABASE IF EXISTS test_ad;
CREATE DATABASE IF NOT EXISTS test_ad DEFAULT CHARACTER SET = 'utf8mb4';
USE test_ad;

-- 광고주
CREATE TABLE advertisers (
  advertiser_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '광고주 ID',
  name VARCHAR(100) NOT NULL COMMENT '광고주 이름',
  industry VARCHAR(100) COMMENT '업종/산업',
  contact_email VARCHAR(100) COMMENT '이메일',
  contact_name VARCHAR(100) COMMENT '담당자 이름',
  phone VARCHAR(30) COMMENT '전화번호',
  status ENUM('Active', 'Inactive', 'Suspended') DEFAULT 'Active' COMMENT '활성 상태',
  contract_start DATE COMMENT '계약 시작일',
  contract_end DATE COMMENT '계약 종료일',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '등록일'
) COMMENT='광고주 정보를 저장하는 테이블';

-- 광고 채널 (Facebook, Google 등)
CREATE TABLE channels (
  channel_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '채널 ID',
  name VARCHAR(50) NOT NULL COMMENT '채널명',
  type ENUM('Social', 'Search', 'Display', 'Video', 'Affiliate') COMMENT '채널 유형',
  supports_image BOOLEAN DEFAULT TRUE COMMENT '이미지 지원 여부',
  supports_video BOOLEAN DEFAULT TRUE COMMENT '비디오 지원 여부',
  active_regions TEXT COMMENT '지원 지역 (CSV)',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) COMMENT='광고 송출 채널 정보를 저장하는 테이블';

-- 캠페인
CREATE TABLE campaigns (
  campaign_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '캠페인 ID',
  advertiser_id INT NOT NULL COMMENT '광고주 ID',
  name VARCHAR(150) NOT NULL COMMENT '캠페인명',
  objective ENUM('Brand Awareness', 'Traffic', 'Conversion', 'Lead') COMMENT '광고 목표',
  status ENUM('Draft', 'Active', 'Paused', 'Completed') DEFAULT 'Draft' COMMENT '상태',
  start_date DATE,
  end_date DATE,
  budget_limit DECIMAL(12,2) COMMENT '예산 한도',
  daily_limit DECIMAL(12,2) COMMENT '일일 예산 한도',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (advertiser_id) REFERENCES advertisers(advertiser_id)
) COMMENT='광고 캠페인 정보를 저장하는 테이블';

-- 광고 소재
CREATE TABLE creatives (
  creative_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '소재 ID',
  type ENUM('Image', 'Video', 'Carousel', 'Text') NOT NULL COMMENT '소재 유형',
  file_url TEXT NOT NULL COMMENT '소재 URL',
  thumbnail_url TEXT COMMENT '미리보기 이미지',
  duration_sec INT COMMENT '영상 길이 (초)',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) COMMENT='광고에 사용되는 소재 파일 정보';

-- 광고
CREATE TABLE ads (
  ad_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '광고 ID',
  campaign_id INT NOT NULL COMMENT '캠페인 ID',
  channel_id INT NOT NULL COMMENT '채널 ID',
  creative_id INT COMMENT '소재 ID',
  name VARCHAR(150) NOT NULL COMMENT '광고 제목',
  headline VARCHAR(255) COMMENT '광고 문구',
  cta_text VARCHAR(50) COMMENT 'Call to Action 문구',
  destination_url TEXT COMMENT '랜딩 URL',
  status ENUM('Scheduled', 'Running', 'Stopped', 'Finished') DEFAULT 'Scheduled',
  is_active BOOLEAN DEFAULT TRUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),
  FOREIGN KEY (channel_id) REFERENCES channels(channel_id),
  FOREIGN KEY (creative_id) REFERENCES creatives(creative_id)
) COMMENT='캠페인 내 실제 송출되는 광고 단위';

-- 광고 성과
CREATE TABLE ad_performance (
  performance_id INT AUTO_INCREMENT PRIMARY KEY,
  ad_id INT NOT NULL,
  report_datetime DATETIME NOT NULL COMMENT '성과 집계 시간',
  impressions INT DEFAULT 0,
  clicks INT DEFAULT 0,
  conversions INT DEFAULT 0,
  cost DECIMAL(10,2) DEFAULT 0.0,
  ctr DECIMAL(5,4) GENERATED ALWAYS AS (IF(impressions > 0, clicks / impressions, 0)) STORED COMMENT '클릭률',
  FOREIGN KEY (ad_id) REFERENCES ads(ad_id)
) COMMENT='시간 단위 광고 성과 기록 (리포트용)';

-- 타겟 설정
CREATE TABLE campaign_targets (
  target_id INT AUTO_INCREMENT PRIMARY KEY,
  campaign_id INT NOT NULL,
  age_min INT,
  age_max INT,
  gender ENUM('M', 'F', 'All') DEFAULT 'All',
  locations TEXT COMMENT '지역 리스트 (CSV)',
  interests TEXT COMMENT '관심사 (CSV)',
  device_type ENUM('Mobile', 'Desktop', 'All') DEFAULT 'All',
  language VARCHAR(50),
  custom_segment TEXT COMMENT '사용자 정의 세그먼트',
  FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
) COMMENT='캠페인의 타겟팅 설정 정보';

-- 결제
CREATE TABLE payments (
  payment_id INT AUTO_INCREMENT PRIMARY KEY,
  advertiser_id INT NOT NULL,
  campaign_id INT,
  amount DECIMAL(12,2) NOT NULL,
  vat DECIMAL(12,2) DEFAULT 0.0,
  total_amount DECIMAL(12,2) GENERATED ALWAYS AS (amount + vat) STORED,
  payment_method ENUM('Credit Card', 'Wire Transfer', 'PayPal') NOT NULL,
  invoice_number VARCHAR(100),
  status ENUM('Pending', 'Paid', 'Failed', 'Refunded') DEFAULT 'Pending',
  paid_at DATETIME,
  FOREIGN KEY (advertiser_id) REFERENCES advertisers(advertiser_id),
  FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
) COMMENT='광고비 결제 및 정산 내역';

-- 예산 히스토리
CREATE TABLE budget_history (
  history_id INT AUTO_INCREMENT PRIMARY KEY,
  campaign_id INT NOT NULL,
  changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  daily_budget DECIMAL(12,2),
  total_budget DECIMAL(12,2),
  reason TEXT,
  FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
) COMMENT='캠페인의 예산 변경 이력 기록';