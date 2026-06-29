import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import psycopg

from app.config import DATABASE_URL
from seed import JOB_SCREENING_QUESTIONS


def update_job_screening_questions():
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            for title, questions in JOB_SCREENING_QUESTIONS.items():
                cur.execute(
                    """
                    UPDATE jobs
                    SET screening_questions = %s::jsonb
                    WHERE title = %s
                    """,
                    (json.dumps(questions, ensure_ascii=False), title),
                )
    print(f"Updated screening questions for {len(JOB_SCREENING_QUESTIONS)} jobs")


if __name__ == "__main__":
    update_job_screening_questions()
