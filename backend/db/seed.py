import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.auth import hash_password
from app.config import DATABASE_URL
import psycopg

USERS = [
    ("Lou Abouzaid", "lou@rawabet.app", "user123", "member", "premium", "verified", "Founder and product builder", "New York, United States"),
    ("Rawabet Admin", "admin@rawabet.app", "admin123", "admin", "founder", "verified", "Platform administrator", "New York, United States"),
    ("Sara Alami", "sara.alami@example.com", "user123", "member", "premium", "active", "UX Lead", "Riyadh, Saudi Arabia"),
    ("Omar Khaled", "omar.khaled@example.com", "user123", "recruiter", "business", "active", "Talent Acquisition Manager", "Dubai, UAE"),
    ("Maya Haddad", "maya.haddad@example.com", "user123", "company", "enterprise", "verified", "People Operations", "Doha, Qatar"),
    ("Lina Nader", "lina.nader@example.com", "user123", "member", "free", "review", "Data Analyst", "Amman, Jordan"),
]

JOBS = [
    ("مختبرات روابط", "مدير منتج", "Product", "الرياض / عن بعد", "دوام كامل", "15,000 - 22,000 ريال", "قيادة استراتيجية المنتج وتحسين تجربة الملفات المهنية ثنائية اللغة."),
    ("مجموعة نمو الشرق الأوسط", "أخصائي استقطاب مواهب", "HR", "دبي / هجين", "دوام كامل", "12,000 - 18,000 درهم", "إدارة عمليات التوظيف وبناء قنوات مرشحين للأسواق العربية."),
    ("تقنيات الميناء الأزرق", "مهندس واجهات أمامية", "Technology", "عن بعد", "دوام كامل", "18,000 - 26,000 ريال", "بناء واجهات ويب احترافية وسريعة باستخدام React وتجارب استخدام مصقولة."),
    ("سيدر للاستثمار", "قائد عمليات", "Operations", "الرياض", "دوام كامل", "14,000 - 20,000 ريال", "تطوير سير العمل والتقارير التشغيلية ودعم توسع الفرق."),
]


def seed():
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            for user in USERS:
                full_name, email, password, role, plan, status, headline, location = user
                cur.execute(
                    """
                    INSERT INTO users (full_name, email, password_hash, role, plan, status, headline, location)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (email) DO UPDATE SET full_name = EXCLUDED.full_name
                    RETURNING id
                    """,
                    (full_name, email, hash_password(password), role, plan, status, headline, location),
                )
                user_id = cur.fetchone()[0]
                cur.execute(
                    """
                    INSERT INTO profiles (user_id, about, skills, profile_strength)
                    VALUES (%s,%s,%s,%s)
                    ON CONFLICT (user_id) DO NOTHING
                    """,
                    (user_id, "Experienced professional using Rawabet to build a verified bilingual career profile.", ["Leadership", "Communication", "Arabic", "English", "Product"], 88 if status == "verified" else 64),
                )

            cur.execute("SELECT id FROM users WHERE email = 'lou@rawabet.app'")
            loui_id = cur.fetchone()[0]
            cur.execute(
                """
                INSERT INTO experiences (user_id, title, company, location, start_date, is_current, description)
                SELECT %s, 'Founder', 'Rawabet', 'New York', '2025-01-01', true, 'Building a bilingual professional network.'
                WHERE NOT EXISTS (SELECT 1 FROM experiences WHERE user_id = %s AND company = 'Rawabet')
                """,
                (loui_id, loui_id),
            )
            cur.execute(
                """
                INSERT INTO education (user_id, school, degree, field, start_year, end_year)
                SELECT %s, 'University Program', 'Business and Technology', 'Product', 2021, 2025
                WHERE NOT EXISTS (SELECT 1 FROM education WHERE user_id = %s AND school = 'University Program')
                """,
                (loui_id, loui_id),
            )

            for job in JOBS:
                cur.execute(
                    """
                    INSERT INTO jobs (company_name, title, category, location, type, salary_range, description)
                    SELECT %s,%s,%s,%s,%s,%s,%s
                    WHERE NOT EXISTS (SELECT 1 FROM jobs WHERE company_name = %s AND title = %s)
                    """,
                    (*job, job[0], job[1]),
                )
    print("Seeded database")


if __name__ == "__main__":
    seed()
