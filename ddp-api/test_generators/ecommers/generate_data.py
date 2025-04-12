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

# --- 0. 테이블 초기화 ---
with open(ddl_path, "r", encoding="utf-8") as f:
    sql_script = f.read()

for statement in sql_script.strip().split(";"):
    if statement.strip():
        try:
            cursor.execute(statement + ";")
        except Exception as e:
            print(f"❌ SQL 오류: {e}\n → {statement}")

conn.commit()


def execute(query, data=None):
    cursor.execute(query, data)
    conn.commit()


def recent_datetime():
    return fake.date_time_between(start_date="-1y", end_date="now")


# --- 1. 카테고리 & 상품 생성 ---
category_ids = []
for name in ["Electronics", "Fashion", "Books", "Home", "Beauty"]:
    execute("INSERT INTO categories (name, description) VALUES (%s, %s)", (name, f"{name} category"))
    category_ids.append(cursor.lastrowid)

product_ids = []
for _ in range(50):
    name = fake.word().capitalize() + " " + fake.word().capitalize()
    execute(
        """
        INSERT INTO products (name, description, sku, price, stock_quantity, category_id, brand)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """,
        (
            name,
            fake.text(50),
            fake.unique.bothify(text="???-#####"),
            round(random.uniform(10, 500), 2),
            random.randint(10, 100),
            random.choice(category_ids),
            fake.company(),
        ),
    )
    product_ids.append(cursor.lastrowid)

# --- 2. 유저 생성 ---
user_ids = []

genders = ["M", "F"]


def birth_date():
    return fake.date_between_dates(date_start=datetime(1970, 1, 1), date_end=datetime(2005, 1, 1))


for _ in range(500):
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.unique.email()
    password_hash = "hashed_pw"
    phone = fake.phone_number()
    gender = random.choice(genders)
    address_line1 = fake.street_address()
    address_line2 = fake.secondary_address() if random.random() < 0.3 else None
    city = fake.city()
    state = fake.state()
    country = fake.country()
    zip_code = fake.postcode()
    registered_at = recent_datetime()
    last_login_at = fake.date_time_between(start_date=registered_at, end_date="now") if random.random() < 0.9 else None

    execute(
        """
        INSERT INTO users (
            first_name, last_name, email, password_hash,
            phone, gender, birth_date,
            address_line1, address_line2, city, state, country, zip_code,
            is_active, registered_at, last_login_at
        )
        VALUES (%s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                TRUE, %s, %s)
        """,
        (
            first_name,
            last_name,
            email,
            password_hash,
            phone,
            gender,
            birth_date(),
            address_line1,
            address_line2,
            city,
            state,
            country,
            zip_code,
            registered_at,
            last_login_at,
        ),
    )

    user_ids.append(cursor.lastrowid)

# --- 3. 유저 활동 시뮬레이션 ---
for user_id in user_ids:
    # 3.1 주문 (60%)
    if random.random() < 0.6:
        order_date = recent_datetime()
        order_number = f"ORD{random.randint(100000, 999999)}"
        order_status = random.choice(["Processing", "Shipped", "Delivered"])
        shipping_fee = random.choice([0.0, 5.0, 7.5])
        selected_products = random.sample(product_ids, random.randint(1, 3))

        total = 0.0
        execute(
            """
            INSERT INTO orders (user_id, order_number, order_status, payment_status, shipping_fee, total_amount, shipping_address, order_date)
            VALUES (%s, %s, %s, 'Pending', %s, %s, %s, %s)
        """,
            (
                user_id,
                order_number,
                order_status,
                shipping_fee,
                0.0,
                fake.address(),
                order_date,
            ),
        )
        order_id = cursor.lastrowid

        total_amount = 0.0
        for product_id in selected_products:
            qty = random.randint(1, 3)
            price = round(random.uniform(20, 300), 2)
            total_amount += qty * price
            execute(
                """
                INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                VALUES (%s, %s, %s, %s)
            """,
                (order_id, product_id, qty, price),
            )

        total_amount += shipping_fee
        execute("UPDATE orders SET total_amount = %s WHERE order_id = %s", (total_amount, order_id))

        # 3.2 결제 (90%)
        if random.random() < 0.9:
            execute(
                """
                INSERT INTO payments (order_id, payment_method, payment_status, paid_amount, transaction_id, paid_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
                (
                    order_id,
                    random.choice(["Credit Card", "PayPal", "KakaoPay"]),
                    "Completed",
                    total_amount,
                    f"TXN{random.randint(1000000,9999999)}",
                    order_date + timedelta(hours=2),
                ),
            )
            execute("UPDATE orders SET payment_status = 'Paid' WHERE order_id = %s", (order_id,))

    # 3.3 장바구니 활동 (40%)
    if random.random() < 0.4:
        execute("INSERT INTO cart (user_id) VALUES (%s)", (user_id,))
        cart_id = cursor.lastrowid
        for _ in range(random.randint(1, 3)):
            execute(
                "INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (%s, %s, %s)",
                (cart_id, random.choice(product_ids), random.randint(1, 5)),
            )

    # 3.4 리뷰 남기기 (30%)
    if random.random() < 0.3:
        execute(
            """
            INSERT INTO reviews (product_id, user_id, rating, title, comment, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """,
            (
                random.choice(product_ids),
                user_id,
                random.randint(3, 5),
                fake.sentence(nb_words=3),
                fake.text(100),
                recent_datetime(),
            ),
        )

# --- 종료 ---
cursor.close()
conn.close()
print("✅ 500명의 사용자 + 1년간 이커머스 활동 시뮬레이션 완료!")
