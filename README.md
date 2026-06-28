# Rawabet

Rawabet is a bilingual English/Arabic professional network inspired by LinkedIn. It includes member profiles, resumes, certificates, work history, jobs, messaging UI, and a professional admin dashboard for users, analytics, and reports.

## Tech Stack

- Frontend: React, Vite, CSS
- Backend: Python, FastAPI
- Database: PostgreSQL
- Uploads: local backend storage

## Local Setup

1. Install dependencies:

```bash
npm run install:all
```

2. Create and seed the PostgreSQL database:

```bash
npm run db:setup
```

3. Start the full app:

```bash
npm run dev
```

Frontend: http://localhost:5173  
Backend: http://localhost:4000
API docs: http://localhost:4000/docs

## Demo Accounts

- Admin: `admin@rawabet.app` / `admin123`
- User: `lou@rawabet.app` / `user123`

## Notes

The backend reads `backend/.env`. The local database connection is configured for PostgreSQL on this Mac. Uploaded files are stored under `backend/uploads`.
# rawabet
