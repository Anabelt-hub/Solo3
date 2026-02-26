# DEPLOYMENT (Solo Project 3)

## Domain + Registrar
- Domain: YOURDOMAIN.com
- Registrar: (Namecheap / Google Domains / etc.)

## Hosting Provider
- Frontend: Netlify (static site)
- Backend: Render (Flask API)
- Database: Render PostgreSQL

## Tech Stack
- Frontend: HTML/CSS/JS (Netlify)
- Backend: Python Flask (Render)
- Database: PostgreSQL (Render)
- Images: image_url per record + placeholder fallback

## Environment Variables / Secrets
Configured in Render (NOT committed to Git):
- DATABASE_URL = (Render Postgres “Internal Database URL”)
- (optional) PORT set automatically by Render

## Seeding
- Backend seeds at least 30 records automatically if DB has fewer than 30.

## How to Deploy / Update

### Backend (Render)
1. Create a new Render Web Service connected to your GitHub repo.
2. Build command:
   - `pip install -r requirements.txt`
3. Start command:
   - `gunicorn app:app`
4. Add environment variable:
   - `DATABASE_URL` from your Render Postgres instance.
5. Deploy.

### Frontend (Netlify)
1. Deploy the `frontend/` folder on Netlify.
2. Set your custom domain in Netlify.
3. Ensure HTTPS is enabled (Netlify will handle certs).
4. Update `frontend/app.js`:
   - `API_BASE = "https://YOUR-RENDER-BACKEND.onrender.com"`

## Verification Checklist (Incognito)
- App loads on custom domain with HTTPS
- List view shows images (broken URL -> placeholder)
- Search/filter works
- Sorting works
- Paging works
- Page size persists after refresh (cookie)
- CRUD works and persists (SQL)
- Stats shows total records + current page size + domain stat
