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
    ("مديرية التنمية الادارية - حمص", "كاتب شؤون إدارية", "Operations", "حمص", "دوام كامل", "$275 - $350", "استقبال المعاملات، تنظيم البريد الإداري، أرشفة الملفات، ومتابعة سجلات الدوام. المتطلبات: شهادة ثانوية عامة أو تجارية، إجادة استخدام الحاسوب، ودقة في التعامل مع الوثائق."),
    ("مديرية التنمية الادارية - حمص", "محلل تطوير إداري", "Operations", "حمص", "دوام كامل", "$700 - $1,200", "تحليل إجراءات العمل، إعداد نماذج تبسيط الإجراءات، ورفع تقارير تحسين الأداء الإداري. المتطلبات: بكالوريوس في الإدارة أو الاقتصاد أو نظم المعلومات وخبرة جيدة في Excel وإعداد التقارير."),
    ("مديرية التنمية الادارية - حمص", "مشرف برامج تبسيط الإجراءات", "Operations", "حمص", "دوام كامل", "$1,000 - $1,500", "الإشراف على فرق دراسة الإجراءات، متابعة خطط التحسين، وتنسيق الاجتماعات مع الجهات العامة. المتطلبات: بكالوريوس مناسب وخبرة إشرافية في التطوير الإداري أو الجودة."),
    ("مديرية التربية - حمص", "أمين سر مدرسة", "Education", "حمص", "دوام كامل", "$275 - $340", "تنظيم سجلات الطلاب، متابعة المراسلات المدرسية، وتجهيز الوثائق اليومية. المتطلبات: شهادة ثانوية، سرعة طباعة جيدة، وقدرة على التعامل مع أولياء الأمور والكوادر التعليمية."),
    ("مديرية التربية - حمص", "منسق بيانات تعليمية", "Education", "حمص", "دوام كامل", "$700 - $1,050", "إدخال وتدقيق بيانات المدارس والطلاب، إعداد كشوف إحصائية، ومتابعة تقارير الحضور والنتائج. المتطلبات: بكالوريوس تربية أو إحصاء أو معلوماتية مع إجادة برامج الجداول."),
    ("مديرية التربية - حمص", "مشرف شؤون امتحانات", "Education", "حمص", "دوام كامل", "$1,000 - $1,400", "تنسيق جداول الامتحانات، الإشراف على لجان المتابعة، وضمان سلامة السجلات والوثائق الامتحانية. المتطلبات: بكالوريوس وخبرة في العمل التعليمي أو الإداري."),
    ("مصفاة حمص", "عامل تشغيل مساعد", "Engineering", "حمص", "دوام كامل", "$300 - $350", "مساندة فرق التشغيل في قراءة المؤشرات، تفقد التجهيزات، وتوثيق الملاحظات ضمن تعليمات السلامة. المتطلبات: شهادة ثانوية صناعية أو مهنية، التزام كامل بإجراءات السلامة والعمل بنظام الورديات."),
    ("مصفاة حمص", "فني سلامة صناعية", "Engineering", "حمص", "دوام كامل", "$800 - $1,150", "متابعة معدات الوقاية، تنفيذ جولات السلامة، وتوثيق ملاحظات المخاطر في وحدات العمل. المتطلبات: بكالوريوس أو معهد تقني في السلامة أو الهندسة وخبرة في بيئات صناعية."),
    ("مصفاة حمص", "مشرف وردية إنتاج", "Engineering", "حمص", "دوام كامل", "$1,200 - $1,500", "إدارة فريق الوردية، متابعة مؤشرات الإنتاج، والتنسيق مع الصيانة والسلامة عند الطوارئ. المتطلبات: شهادة هندسية أو تقنية وخبرة إشرافية في منشآت صناعية."),
    ("محافظة حمص - حمص", "موظف نافذة خدمة مواطن", "Operations", "حمص", "دوام كامل", "$275 - $330", "استقبال طلبات المواطنين، تدقيق الأوراق الأولية، وتوجيه المراجعين للدوائر المختصة. المتطلبات: شهادة ثانوية، مهارات تواصل عالية، وقدرة على استخدام أنظمة إدخال البيانات."),
    ("محافظة حمص - حمص", "مخطط خدمات محلية", "Operations", "حمص", "دوام كامل", "$800 - $1,200", "تحليل احتياجات الأحياء، إعداد خطط متابعة الخدمات، وتنسيق التقارير مع الوحدات الإدارية. المتطلبات: بكالوريوس إدارة عامة أو هندسة مدنية أو تخطيط وخبرة في العمل البلدي."),
    ("محافظة حمص - حمص", "مشرف متابعة المشاريع الخدمية", "Operations", "حمص", "دوام كامل", "$1,100 - $1,500", "متابعة تنفيذ المشاريع الخدمية، توثيق نسب الإنجاز، ورفع تقارير للإدارة. المتطلبات: بكالوريوس مناسب وخبرة إشرافية في المشاريع أو الخدمات العامة."),
    ("الرقابة والتفتيش - حمص", "مساعد أرشفة وتوثيق رقابي", "Administration", "حمص", "دوام كامل", "$290 - $340", "ترتيب ملفات الشكاوى والتقارير، حفظ الوثائق، وتجهيز السجلات للفرق الرقابية. المتطلبات: شهادة ثانوية، أمانة عالية، ودقة في التعامل مع الوثائق السرية."),
    ("الرقابة والتفتيش - حمص", "مفتش مالي وإداري مساعد", "Finance", "حمص", "دوام كامل", "$900 - $1,200", "مراجعة المستندات المالية والإدارية، إعداد مذكرات أولية، ومساندة فرق التفتيش الميدانية. المتطلبات: بكالوريوس حقوق أو اقتصاد أو محاسبة ومعرفة بأساسيات الرقابة الإدارية."),
    ("الرقابة والتفتيش - حمص", "مشرف فرق تدقيق ميداني", "Finance", "حمص", "دوام كامل", "$1,100 - $1,500", "تنظيم مهام فرق التدقيق، مراجعة نتائج الجولات، وضمان توثيق المخالفات وفق الأصول. المتطلبات: بكالوريوس وخبرة رقابية أو مالية لا تقل عن ثلاث سنوات."),
    ("مديرية المالية - حمص", "كاتب جباية وتحصيل", "Finance", "حمص", "دوام كامل", "$275 - $350", "تسجيل المدفوعات، ترتيب إيصالات التحصيل، ومساعدة المراجعين في إجراءات الجباية. المتطلبات: شهادة ثانوية تجارية أو عامة، دقة حسابية، ومعرفة أولية بالحاسوب."),
    ("مديرية المالية - حمص", "محاسب موازنة", "Finance", "حمص", "دوام كامل", "$850 - $1,200", "إعداد قيود الموازنة، تدقيق المصروفات، ومطابقة السجلات المالية مع التعليمات النافذة. المتطلبات: بكالوريوس محاسبة أو اقتصاد وخبرة في التقارير المالية."),
    ("مديرية المالية - حمص", "مشرف تدقيق ضريبي", "Finance", "حمص", "دوام كامل", "$1,000 - $1,450", "الإشراف على ملفات التدقيق الضريبي، مراجعة نتائج التحصيل، وتوجيه فريق العمل في الحالات المعقدة. المتطلبات: بكالوريوس محاسبة أو اقتصاد وخبرة إشرافية في الضرائب أو التدقيق."),
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
