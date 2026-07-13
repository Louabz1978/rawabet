# Rawabet

Rawabet is a bilingual English/Arabic professional network inspired by LinkedIn. It includes member profiles, resumes, certificates, work history, jobs, messaging UI, and a professional admin dashboard for users, analytics, and reports.

## Tech Stack

- Frontend: React, Vite, CSS
- Backend: Python, FastAPI, Pydantic, SQLAlchemy Core
- Database: PostgreSQL
- Uploads: local backend storage

## Local Setup

1. Install dependencies:

```bash
npm run install:all
```

2. Configure the database URL in `backend/.env`:

```bash
DATABASE_URL=postgresql://rawabet_user:password@host:5432/postgres
```

The FastAPI backend creates/updates the runtime schema it needs on startup.

3. Start the full app:

```bash
npm run dev
```

Frontend: http://localhost:5173  
Backend: http://localhost:4000
API docs: http://localhost:4000/docs

## Notes

The backend reads `backend/.env`. Uploaded files are stored under `backend/uploads`.

## EC2/Nginx deployment

Deployment helpers are in `deploy/`.

After pulling on EC2, copy `deploy/nginx/rawabet.conf` to `/etc/nginx/conf.d/rawabet.conf`, rebuild the frontend, reload Nginx, and restart the backend. See `deploy/EC2_DEPLOY.md`.
# rawabet
