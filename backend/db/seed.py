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
    ("مختبرات روابط", "مدير منتج", "Product", "الرياض / عن بعد", "دوام كامل", "$4,000 - $5,900", "قيادة استراتيجية المنتج وتحسين تجربة الملفات المهنية ثنائية اللغة."),
    ("مجموعة نمو الشرق الأوسط", "أخصائي استقطاب مواهب", "HR", "دبي / هجين", "دوام كامل", "$3,300 - $4,900", "إدارة عمليات التوظيف وبناء قنوات مرشحين للأسواق العربية."),
    ("تقنيات الميناء الأزرق", "مهندس واجهات أمامية", "Technology", "عن بعد", "دوام كامل", "$4,800 - $6,900", "بناء واجهات ويب احترافية وسريعة باستخدام React وتجارب استخدام مصقولة."),
    ("سيدر للاستثمار", "قائد عمليات", "Operations", "الرياض", "دوام كامل", "$3,700 - $5,300", "تطوير سير العمل والتقارير التشغيلية ودعم توسع الفرق."),
    ("منصة شام الرقمية", "محلل بيانات", "Data", "دمشق / عن بعد", "دوام كامل", "$2,800 - $4,200", "تحليل بيانات المستخدمين وبناء لوحات قياس تساعد الإدارة على اتخاذ القرار."),
    ("أفق البرمجيات", "مهندس باكند", "Technology", "عمّان / هجين", "دوام كامل", "$4,200 - $6,500", "تطوير خدمات API آمنة وقابلة للتوسع باستخدام Python وقواعد بيانات PostgreSQL."),
    ("بيت التصميم العربي", "مصمم تجربة مستخدم", "Design", "بيروت / عن بعد", "دوام كامل", "$2,700 - $4,100", "تصميم واجهات عربية احترافية وتحسين رحلات المستخدم في منتجات رقمية."),
    ("نواة المنتج", "مالك منتج", "Product", "دبي", "دوام كامل", "$5,000 - $7,200", "إدارة خارطة الطريق وتحويل احتياجات العملاء إلى مزايا قابلة للتنفيذ."),
    ("جسر المبيعات", "مدير مبيعات إقليمي", "Sales", "الرياض / سفر جزئي", "دوام كامل", "$4,500 - $7,000", "بناء علاقات مع العملاء وقيادة نمو الإيرادات في أسواق الخليج."),
    ("صوت السوق", "أخصائي تسويق رقمي", "Marketing", "القاهرة / عن بعد", "دوام كامل", "$2,200 - $3,600", "إدارة الحملات الرقمية وتحسين المحتوى العربي لقنوات التواصل والإعلانات."),
    ("رعاية بلس", "منسق خدمات صحية", "Healthcare", "جدة", "دوام كامل", "$2,600 - $3,800", "تنسيق خدمات المرضى ومتابعة جودة العمليات اليومية في مركز طبي."),
    ("أكاديمية البيان", "مصمم مناهج تدريبية", "Education", "الدوحة / هجين", "دوام كامل", "$3,000 - $4,700", "تطوير مسارات تعليمية عربية للمهارات المهنية والتقنية."),
    ("مدار الهندسة", "مهندس مدني", "Engineering", "أبوظبي", "دوام كامل", "$4,000 - $6,200", "متابعة مواقع المشاريع وضمان الالتزام بالجودة والجداول الزمنية."),
    ("تمكين الموارد", "مدير موارد بشرية", "HR", "الرياض", "دوام كامل", "$4,200 - $6,100", "قيادة سياسات الموارد البشرية والتوظيف وتطوير الأداء."),
    ("ميزان المالية", "محاسب أول", "Finance", "الكويت", "دوام كامل", "$3,200 - $4,800", "إعداد التقارير المالية ومراجعة القيود والامتثال للإجراءات المحاسبية."),
    ("روافد التشغيل", "محلل عمليات", "Operations", "مسقط / هجين", "دوام كامل", "$2,900 - $4,300", "تحليل العمليات وتحسين الإنتاجية ومتابعة مؤشرات الأداء التشغيلية."),
    ("سحابة العرب", "مهندس سحابة", "Technology", "عن بعد", "دوام كامل", "$5,500 - $8,000", "إدارة بنى سحابية آمنة ومراقبة الأداء والتكاليف."),
    ("رؤية البيانات", "مهندس ذكاء أعمال", "Data", "دبي / هجين", "دوام كامل", "$4,700 - $6,800", "بناء نماذج وتقارير BI وربط مصادر البيانات بلوحات تنفيذية."),
    ("مبدعو الهوية", "مصمم جرافيك", "Design", "عمّان", "دوام كامل", "$2,000 - $3,200", "تصميم مواد بصرية وهوية رقمية لمنصات عربية احترافية."),
    ("بوابة العملاء", "مدير نجاح العملاء", "Sales", "الرياض / هجين", "دوام كامل", "$3,800 - $5,600", "متابعة حسابات العملاء وضمان تحقيق القيمة وزيادة الاحتفاظ."),
    ("نبض المحتوى", "كاتب محتوى عربي", "Marketing", "عن بعد", "دوام جزئي", "$1,200 - $2,200", "كتابة محتوى عربي واضح للمدونات والرسائل التسويقية وصفحات المنتج."),
    ("شفاء التقنية", "محلل نظم صحية", "Healthcare", "الدمام", "دوام كامل", "$3,600 - $5,200", "تحليل متطلبات الأنظمة الصحية وربط الفرق الطبية بالتقنية."),
    ("تعلم المستقبل", "مدرب مهارات تقنية", "Education", "الرياض / عن بعد", "دوام كامل", "$2,800 - $4,400", "تقديم ورش تدريبية في المهارات الرقمية وإعداد مواد تطبيقية."),
    ("مكتب المشاريع الهندسية", "مهندس ميكانيك", "Engineering", "حلب / هجين", "دوام كامل", "$3,500 - $5,000", "تصميم ومراجعة أنظمة ميكانيكية ودعم فرق التنفيذ في المشاريع."),
    ("تحليلات الشرق", "عالم بيانات", "Data", "الرياض / هجين", "دوام كامل", "$6,200 - $8,900", "تطوير نماذج تحليلية وتوقعية لدعم قرارات الأعمال."),
    ("حلول المؤسسات", "استشاري تحول رقمي", "Operations", "دبي", "دوام كامل", "$5,800 - $8,200", "قيادة مشاريع تحسين العمليات وربط الأنظمة بين الإدارات."),
    ("مختبر تجربة المستخدم", "باحث تجربة مستخدم", "Design", "عن بعد", "دوام كامل", "$3,100 - $4,900", "إجراء مقابلات واختبارات استخدام وتحويل النتائج إلى توصيات عملية."),
    ("بوابة المدفوعات", "محلل مخاطر مالية", "Finance", "المنامة", "دوام كامل", "$4,000 - $6,100", "تحليل المخاطر المالية ومراقبة مؤشرات الاحتيال والامتثال."),
    ("مركز العناية الذكية", "مشرف دعم عملاء", "Sales", "القاهرة", "دوام كامل", "$1,800 - $2,900", "إدارة فريق الدعم وتحسين زمن الاستجابة ورضا العملاء."),
    ("منارة التعليم", "مدير برنامج تدريبي", "Education", "جدة / هجين", "دوام كامل", "$4,300 - $6,300", "إدارة برامج تدريبية مهنية ومتابعة جودة المحتوى والمدربين."),
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
