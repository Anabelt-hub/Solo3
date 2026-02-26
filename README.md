2. Render Web Service is connected to the GitHub repository.
3. Render configuration:
- Root Directory:
  ```
  Solo-2-back-main/collection_api
  ```
- Build Command:
  ```
  pip install -r requirements.txt
  ```
- Start Command:
  ```
  gunicorn app:app
  ```
4. Any push to the `main` branch automatically redeploys the backend.

---

## How configuration and secrets are managed (environment variables)

Sensitive information is NOT stored in the repository.

Secrets are configured in Render using environment variables:

- **DATABASE_URL**
- Stores the PostgreSQL connection string
- Provided by Render PostgreSQL service
- Used by the Flask backend to connect to the database

Render automatically injects environment variables securely at runtime.

No database credentials are committed to GitHub.

---

## Live URLs

- **Frontend:**  
https://collection-manager.netlify.app

- **Backend API:**  
https://solo3.onrender.com

---

## Verification

The application supports:

- Full CRUD operations using PostgreSQL  
- Paging with configurable page size  
- Page size stored and restored via cookies  
- Search and filtering  
- Sorting  
- Image display per record  
- Stats view using database queries  
- Public HTTPS access  
