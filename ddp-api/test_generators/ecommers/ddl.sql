DROP DATABASE IF EXISTS test_ecommerce;
CREATE DATABASE IF NOT EXISTS test_ecommerce DEFAULT CHARACTER SET = 'utf8mb4';

USE test_ecommerce;

CREATE TABLE users (
  user_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '고유 사용자 ID',
  first_name VARCHAR(50) NOT NULL COMMENT '사용자 이름',
  last_name VARCHAR(50) NOT NULL COMMENT '사용자 성',
  email VARCHAR(100) NOT NULL UNIQUE COMMENT '이메일 주소 (고유)',
  password_hash CHAR(60) NOT NULL COMMENT '암호화된 비밀번호 (bcrypt)',
  phone VARCHAR(30) COMMENT '전화번호',
  gender ENUM('M', 'F') DEFAULT NULL COMMENT '성별',
  birth_date DATE COMMENT '생년월일',
  address_line1 VARCHAR(255) COMMENT '주소 1',
  address_line2 VARCHAR(255) COMMENT '주소 2 (선택)',
  city VARCHAR(100) COMMENT '도시',
  state VARCHAR(100) COMMENT '주/도',
  country VARCHAR(100) COMMENT '국가',
  zip_code VARCHAR(20) COMMENT '우편번호',
  is_active BOOLEAN DEFAULT TRUE COMMENT '활성 사용자 여부',
  registered_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '가입일시',
  last_login_at DATETIME COMMENT '마지막 로그인 일시'
) COMMENT='사용자 정보를 저장하는 테이블';

CREATE TABLE categories (
  category_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '카테고리 ID',
  name VARCHAR(100) NOT NULL COMMENT '카테고리 이름',
  parent_category_id INT DEFAULT NULL COMMENT '부모 카테고리 ID (자식일 경우)',
  description TEXT COMMENT '카테고리 설명',
  FOREIGN KEY (parent_category_id) REFERENCES categories(category_id)
) COMMENT='상품의 분류 정보를 저장하는 테이블';

CREATE TABLE products (
  product_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '상품 ID',
  name VARCHAR(150) NOT NULL COMMENT '상품명',
  description TEXT COMMENT '상품 설명',
  sku VARCHAR(50) UNIQUE COMMENT 'SKU (재고관리용 고유코드)',
  price DECIMAL(10,2) NOT NULL COMMENT '정가',
  discount_price DECIMAL(10,2) COMMENT '할인 가격',
  currency CHAR(3) DEFAULT 'USD' COMMENT '통화 단위 (예: USD)',
  stock_quantity INT DEFAULT 0 COMMENT '재고 수량',
  is_active BOOLEAN DEFAULT TRUE COMMENT '판매 중 여부',
  category_id INT COMMENT '카테고리 ID',
  brand VARCHAR(100) COMMENT '브랜드',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '등록일',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일',
  FOREIGN KEY (category_id) REFERENCES categories(category_id)
) COMMENT='상품 정보를 저장하는 테이블';

CREATE TABLE orders (
  order_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '주문 ID',
  user_id INT NOT NULL COMMENT '주문자 ID',
  order_number VARCHAR(20) UNIQUE NOT NULL COMMENT '주문번호 (고유)',
  order_date DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '주문일시',
  order_status ENUM('Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled') DEFAULT 'Pending' COMMENT '주문 상태',
  payment_status ENUM('Pending', 'Paid', 'Failed', 'Refunded') DEFAULT 'Pending' COMMENT '결제 상태',
  shipping_fee DECIMAL(10,2) DEFAULT 0.00 COMMENT '배송비',
  total_amount DECIMAL(10,2) NOT NULL COMMENT '총 결제 금액',
  shipping_address TEXT COMMENT '배송지 정보',
  notes TEXT COMMENT '주문 메모',
  FOREIGN KEY (user_id) REFERENCES users(user_id)
) COMMENT='사용자의 주문 내역을 저장하는 테이블';

CREATE TABLE order_items (
  order_item_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '주문 상세 ID',
  order_id INT NOT NULL COMMENT '주문 ID',
  product_id INT NOT NULL COMMENT '상품 ID',
  quantity INT NOT NULL COMMENT '수량',
  unit_price DECIMAL(10,2) NOT NULL COMMENT '단가 (당시 가격)',
  discount_applied DECIMAL(10,2) DEFAULT 0.00 COMMENT '적용된 할인 금액',
  FOREIGN KEY (order_id) REFERENCES orders(order_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id)
) COMMENT='주문에 포함된 상품 상세 정보를 저장하는 테이블';

CREATE TABLE cart (
  cart_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '장바구니 ID',
  user_id INT NOT NULL COMMENT '사용자 ID',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '장바구니 생성일시',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일시',
  FOREIGN KEY (user_id) REFERENCES users(user_id)
) COMMENT='사용자의 장바구니 정보를 저장하는 테이블';

CREATE TABLE cart_items (
  cart_item_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '장바구니 항목 ID',
  cart_id INT NOT NULL COMMENT '장바구니 ID',
  product_id INT NOT NULL COMMENT '상품 ID',
  quantity INT DEFAULT 1 COMMENT '수량',
  FOREIGN KEY (cart_id) REFERENCES cart(cart_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id)
) COMMENT='장바구니에 담긴 상품 목록을 저장하는 테이블';

CREATE TABLE payments (
  payment_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '결제 ID',
  order_id INT NOT NULL COMMENT '연결된 주문 ID',
  payment_method ENUM('Credit Card', 'PayPal', 'Bank Transfer', 'Apple Pay', 'KakaoPay') NOT NULL COMMENT '결제 방식',
  payment_status ENUM('Pending', 'Completed', 'Failed', 'Refunded') DEFAULT 'Pending' COMMENT '결제 상태',
  paid_amount DECIMAL(10,2) NOT NULL COMMENT '결제 금액',
  transaction_id VARCHAR(100) COMMENT '거래 번호 (PG사)',
  paid_at DATETIME COMMENT '결제 완료 일시',
  FOREIGN KEY (order_id) REFERENCES orders(order_id)
) COMMENT='결제 내역을 저장하는 테이블';

CREATE TABLE reviews (
  review_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '리뷰 ID',
  product_id INT NOT NULL COMMENT '상품 ID',
  user_id INT NOT NULL COMMENT '리뷰 작성자 ID',
  rating INT CHECK (rating BETWEEN 1 AND 5) COMMENT '평점 (1~5)',
  title VARCHAR(255) COMMENT '리뷰 제목',
  comment TEXT COMMENT '리뷰 내용',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '작성일',
  FOREIGN KEY (product_id) REFERENCES products(product_id),
  FOREIGN KEY (user_id) REFERENCES users(user_id)
) COMMENT='상품에 대한 사용자 리뷰를 저장하는 테이블';