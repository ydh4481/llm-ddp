import os
import random
from datetime import datetime, timedelta

import MySQLdb
from faker import Faker

# 연결 정보
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


def execute(query, data=None):
    cursor.execute(query, data)
    conn.commit()


# --------------------------
# 1. 광고 채널 등록
# --------------------------
channels = ["Facebook", "Google", "Instagram", "YouTube", "LinkedIn"]
channel_ids = []

for ch in channels:
    execute(
        """
        INSERT INTO channels (name, type, supports_image, supports_video, active_regions)
        VALUES (%s, %s, %s, %s, %s)
    """,
        (ch, random.choice(["Social", "Search", "Display"]), True, True, "US,KR,JP"),
    )
    channel_ids.append(cursor.lastrowid)

# --------------------------
# 2. 광고주 생성
# --------------------------
advertiser_ids = []

for _ in range(10):
    execute(
        """
        INSERT INTO advertisers (name, industry, contact_email, contact_name, phone, contract_start, contract_end)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """,
        (
            fake.company(),
            fake.job(),
            fake.unique.email(),
            fake.name(),
            fake.phone_number(),
            fake.date_between(start_date="-3y", end_date="-1y"),
            fake.date_between(start_date="today", end_date="+1y"),
        ),
    )
    advertiser_ids.append(cursor.lastrowid)

# --------------------------
# 3. 캠페인 생성
# --------------------------
campaign_ids = []

for advertiser_id in advertiser_ids:
    for _ in range(random.randint(2, 4)):
        start_date = fake.date_between(start_date="-1y", end_date="today")
        end_date = start_date + timedelta(days=random.randint(30, 90))

        execute(
            """
            INSERT INTO campaigns (advertiser_id, name, objective, status, start_date, end_date, budget_limit, daily_limit)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (
                advertiser_id,
                "Campaign " + fake.word().capitalize(),
                random.choice(["Brand Awareness", "Traffic", "Conversion"]),
                random.choice(["Active", "Paused", "Completed"]),
                start_date,
                end_date,
                round(random.uniform(1000, 10000), 2),
                round(random.uniform(50, 300), 2),
            ),
        )
        campaign_ids.append(cursor.lastrowid)

# --------------------------
# 4. 소재 등록
# --------------------------
creative_ids = []

for _ in range(50):
    execute(
        """
        INSERT INTO creatives (type, file_url, thumbnail_url, duration_sec)
        VALUES (%s, %s, %s, %s)
    """,
        (random.choice(["Image", "Video"]), fake.image_url(), fake.image_url(), random.randint(15, 60)),
    )
    creative_ids.append(cursor.lastrowid)

# --------------------------
# 5. 광고 등록
# --------------------------
ad_ids = []

for campaign_id in campaign_ids:
    for _ in range(random.randint(2, 5)):
        execute(
            """
            INSERT INTO ads (campaign_id, channel_id, creative_id, name, headline, cta_text, destination_url, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (
                campaign_id,
                random.choice(channel_ids),
                random.choice(creative_ids),
                "Ad " + fake.word().capitalize(),
                fake.sentence(nb_words=6),
                random.choice(["Shop Now", "Learn More", "Sign Up"]),
                fake.url(),
                random.choice(["Running", "Stopped", "Finished"]),
            ),
        )
        ad_ids.append(cursor.lastrowid)

# --------------------------
# 6. 광고 성과 데이터 생성
# --------------------------
for ad_id in ad_ids:
    start = datetime.now() - timedelta(days=10)
    for i in range(24 * 7):  # 7일간 시간 단위 성과
        dt = start + timedelta(hours=i)
        impressions = random.randint(100, 5000)
        clicks = random.randint(0, impressions // 10)
        conversions = random.randint(0, clicks)
        cost = round(random.uniform(0.01, 0.2) * impressions, 2)

        execute(
            """
            INSERT INTO ad_performance (ad_id, report_datetime, impressions, clicks, conversions, cost)
            VALUES (%s, %s, %s, %s, %s, %s)
        """,
            (ad_id, dt, impressions, clicks, conversions, cost),
        )

# --------------------------
# 7. 결제 데이터
# --------------------------
for advertiser_id in advertiser_ids:
    if random.random() < 0.8:
        campaign_id = random.choice(campaign_ids)
        amount = round(random.uniform(1000, 5000), 2)
        vat = round(amount * 0.1, 2)

        execute(
            """
            INSERT INTO payments (advertiser_id, campaign_id, amount, vat, payment_method, invoice_number, status, paid_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (
                advertiser_id,
                campaign_id,
                amount,
                vat,
                random.choice(["Credit Card", "Wire Transfer"]),
                fake.uuid4(),
                "Paid",
                fake.date_time_between(start_date="-1y", end_date="now"),
            ),
        )

# --------------------------
# 8. 예산 변경 이력
# --------------------------
for campaign_id in campaign_ids:
    for _ in range(random.randint(1, 3)):
        execute(
            """
            INSERT INTO budget_history (campaign_id, daily_budget, total_budget, reason)
            VALUES (%s, %s, %s, %s)
        """,
            (campaign_id, round(random.uniform(50, 300), 2), round(random.uniform(1000, 10000), 2), fake.sentence()),
        )

# 마무리
cursor.close()
conn.close()
print("✅ 광고사 시뮬레이션 데이터가 성공적으로 생성되었습니다.")
