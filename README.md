# Videoflix - Netflix-like Video Streaming Platform Backend

A Django REST Framework backend for a Netflix-like video streaming platform. Features include user authentication with email activation, JWT-based cookie authentication, HLS video streaming, background video processing, and automated thumbnail generation.

## 📑 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
  - [Prerequisites](#prerequisites)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Environment Configuration](#2-environment-configuration)
  - [3. Start with Docker](#3-start-with-docker)
  - [4. Add Videos](#4-add-videos)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [RQ Queue Configuration](#rq-queue-configuration)
  - [Email Configuration](#email-configuration)
- [API Endpoints](#api-endpoints)
  - [Authentication](#authentication)
  - [Video](#video)
- [API Usage Examples](#api-usage-examples)
  - [Registration](#registration)
  - [Account Activation](#account-activation)
  - [Login](#login)
  - [Logout](#logout)
  - [Password Reset](#password-reset)
  - [Video List](#video-list)
  - [HLS Playlist](#hls-playlist)
  - [HLS Segment](#hls-segment)
- [Video Upload & Processing](#video-upload--processing)
  - [Upload Flow](#upload-flow)
  - [HLS File Structure](#hls-file-structure)
- [Authentication Flow](#authentication-flow)
- [Admin Panel](#admin-panel)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)
- [License](#license)

---

## Features

- **Email-based Authentication**: Register and login with email instead of username
- **Account Activation**: Email verification with activation link
- **JWT Cookie Authentication**: Secure httpOnly cookies for access and refresh tokens
- **Token Blacklisting**: Invalidate refresh tokens on logout
- **Password Reset**: Email-based password reset flow
- **HLS Video Streaming**: Serve `.m3u8` playlists and `.ts` segments
- **Automatic Video Conversion**: Background ffmpeg conversion to 480p, 720p and 1080p
- **Thumbnail Generation**: Automatic thumbnail extraction via ffmpeg
- **HTML Email Templates**: Branded email templates with dark mode support

## Tech Stack

- **Django 6.0.3**
- **Django REST Framework 3.16.1**
- **djangorestframework-simplejwt** — JWT authentication
- **django-rq** — Background job queue
- **Redis** — Queue broker and cache
- **PostgreSQL** — Database
- **ffmpeg** — Video conversion and thumbnail generation
- **Whitenoise** — Static file serving
- **django-cors-headers** — CORS support
- **python-decouple** — Environment variable management
- **Docker & Docker Compose** — Containerization
- **Gunicorn** — WSGI server

## Project Structure

```
Videoflix/
├── core/                          # Main project settings
│   ├── settings.py
│   └── urls.py
├── auth_app/                      # Authentication
│   ├── api/
│   │   ├── permissions.py         # CookieJWTAuthentication
│   │   ├── serializers.py
│   │   ├── utils.py               # Email helpers, token helpers
│   │   ├── views.py
│   │   └── urls.py
│   └── admin.py
├── upload_app/                    # Video file upload
│   ├── api/
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── models.py                  # FileUpload model
│   ├── signals.py                 # Auto-create Video, trigger conversion
│   ├── tasks.py                   # HLS conversion & thumbnail RQ tasks
│   └── apps.py                    # Signal registration
├── content_app/                   # Video content delivery
│   ├── api/
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── models.py                  # Video model
│   └── admin.py
├── templates/
│   └── emails/
│       ├── activation_email.html
│       └── password_reset_email.html
├── media/                         # Uploaded files (local mount)
│   ├── uploads/                   # Raw uploaded videos
│   ├── videos/                    # HLS converted videos
│   │   └── <video_id>/
│   │       ├── 480p/
│   │       ├── 720p/
│   │       └── 1080p/
│   └── thumbnails/                # Generated thumbnails
├── static/                        # Collected static files
├── backend.Dockerfile
├── backend.entrypoint.sh
├── docker-compose.yml
├── manage.py
├── requirements.txt
└── .env
```

## Installation & Setup

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- [Git](https://git-scm.com/) installed

### 1. Clone the Repository

**Windows (PowerShell):**
```powershell
git clone https://github.com/hcplayer1988/Videoflix.git
cd Videoflix
```

**Linux / Mac:**
```bash
git clone https://github.com/hcplayer1988/Videoflix.git
cd Videoflix
```

### 2. Environment Configuration

Create your `.env` file from the template:

**Windows (PowerShell):**
```powershell
copy .env.template .env
```

**Linux / Mac:**
```bash
cp .env.template .env
```

Now open the `.env` file and fill in your values. Here is a complete example:

```env
# Superuser — created automatically on first start
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=adminpassword
DJANGO_SUPERUSER_EMAIL=admin@example.com

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
CORS_ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500

# URLs
FRONTEND_URL=http://127.0.0.1:5500
BACKEND_URL=http://127.0.0.1:8000

# Database
DB_NAME=videoflix_db
DB_USER=videoflix_user
DB_PASSWORD=your_database_password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_LOCATION=redis://redis:6379/1
REDIS_PORT=6379
REDIS_DB=0

# Email
EMAIL_HOST=your-smtp-host
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=your-email@domain.com
```

> ⚠️ **Important:** If your `SECRET_KEY` contains a `#` character, wrap the entire value in double quotes:
> ```env
> SECRET_KEY="your#secret#key"
> ```

> ⚠️ **Windows only:** The `.env` file must be **UTF-8 encoded**. If you edited it with Notepad, convert it with PowerShell to be safe:
> ```powershell
> Get-Content .env | Set-Content -Encoding UTF8 .env_temp
> Remove-Item .env
> Rename-Item .env_temp .env
> ```

### 3. Start with Docker

```bash
docker-compose up --build
```

The API will be available at: `http://127.0.0.1:8000/`

On first startup the container automatically:
1. Waits for PostgreSQL to be ready
2. Runs `collectstatic`
3. Runs `makemigrations` and `migrate`
4. Creates the superuser from the `.env` credentials
5. Starts the RQ worker for background jobs
6. Starts Gunicorn

> ℹ️ The first build takes a few minutes. On subsequent starts use `docker-compose up` without `--build`.

To stop the containers:
```bash
docker-compose down
```

### 4. Add Videos

The database is empty after a fresh setup — videos must be added manually via the Django Admin.

1. Open `http://127.0.0.1:8000/admin/` and log in with your superuser credentials
2. Go to **Upload App → File Uploads → Add File Upload**
3. Fill in the following fields:
   - **Title** — video title shown in the frontend
   - **Description** — short description
   - **Category** — genre (e.g. `Drama`, `Action`, `Comedy`)
   - **File** — select a `.mp4` video file from your computer
4. Click **Save**

After saving, the backend automatically:
- Creates a `Video` object in the database
- Starts HLS conversion to 480p, 720p and 1080p in the background
- Generates a thumbnail from the video

> ℹ️ **Note:** The browser may briefly show a 500 error after saving in the Admin Panel. This is normal — simply refresh the page. The video will appear correctly and the HLS conversion continues in the background.

> ℹ️ **Note:** The video will not be playable immediately. Wait for the HLS conversion to finish. Monitor progress with:
> ```powershell
> docker-compose logs web --tail=50
> ```
> Look for: `Successfully completed upload_app.tasks.convert_to_hls`

---

## Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DJANGO_SUPERUSER_USERNAME` | Admin username | `admin` |
| `DJANGO_SUPERUSER_PASSWORD` | Admin password | `adminpassword` |
| `DJANGO_SUPERUSER_EMAIL` | Admin email | `admin@example.com` |
| `SECRET_KEY` | Django secret key | `your-secret-key` |
| `DEBUG` | Debug mode | `True` / `False` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` |
| `FRONTEND_URL` | Frontend base URL for email links | `http://127.0.0.1:5500` |
| `BACKEND_URL` | Backend base URL | `http://127.0.0.1:8000` |
| `DB_NAME` | PostgreSQL database name | `videoflix_db` |
| `DB_USER` | PostgreSQL user | `videoflix_user` |
| `DB_PASSWORD` | PostgreSQL password | `your_password` |
| `DB_HOST` | PostgreSQL host (use `db` in Docker) | `db` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `REDIS_HOST` | Redis host (use `redis` in Docker) | `redis` |
| `REDIS_LOCATION` | Redis location for cache | `redis://redis:6379/1` |
| `REDIS_PORT` | Redis port | `6379` |
| `REDIS_DB` | Redis DB index | `0` |
| `EMAIL_HOST` | SMTP host | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP port | `587` |
| `EMAIL_HOST_USER` | SMTP username | `your@email.com` |
| `EMAIL_HOST_PASSWORD` | SMTP password | `your_password` |
| `EMAIL_USE_TLS` | Use TLS | `True` |
| `EMAIL_USE_SSL` | Use SSL | `False` |
| `DEFAULT_FROM_EMAIL` | Sender email address | `noreply@videoflix.com` |

### RQ Queue Configuration

The project uses a single `default` queue with a 3600s timeout to handle all background tasks including HLS video conversion:

| Queue | Use Case | Timeout |
|-------|----------|---------|
| `default` | HLS conversion, thumbnail generation | 3600s |

The RQ worker starts automatically in the Docker container and listens on the `default` queue.

### Email Configuration

The project uses HTML email templates with dark mode support. Emails are sent directly (not via queue) for reliability.

Tested SMTP providers: All-inkl, Gmail, Outlook, any standard SMTP server.

---

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/register/` | Register new user | No |
| GET | `/api/activate/<uidb64>/<token>/` | Activate account | No |
| POST | `/api/login/` | Login and set JWT cookies | No |
| POST | `/api/logout/` | Logout and invalidate tokens | Refresh-Token-Cookie |
| POST | `/api/password_reset/` | Send password reset email | No |
| POST | `/api/password_confirm/<uidb64>/<token>/` | Set new password | No |
| POST | `/api/token/refresh/` | Refresh access token | Refresh-Token-Cookie |

### Video

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/video/` | List all videos with metadata | JWT |
| GET | `/api/video/<id>/<resolution>/index.m3u8` | HLS master playlist | JWT |
| GET | `/api/video/<id>/<resolution>/<segment>/` | HLS video segment | JWT |

**Resolutions:** `480p`, `720p`, `1080p`

---

## API Usage Examples

### Registration

```bash
POST http://127.0.0.1:8000/api/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "confirmed_password": "securepassword"
}
```

**Response (201):**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com"
  },
  "token": "activation_token"
}
```

After registration an activation email is sent. The account remains inactive until the email link is clicked.

### Account Activation

```
GET http://127.0.0.1:8000/api/activate/<uidb64>/<token>/
```

**Response (200):**
```json
{
  "message": "Account successfully activated."
}
```

### Login

```bash
POST http://127.0.0.1:8000/api/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response (200):** Sets `access_token` (15 min) and `refresh_token` (7 days) as httpOnly cookies.
```json
{
  "detail": "Login successful",
  "user": {
    "id": 1,
    "username": "user@example.com"
  }
}
```

> ℹ️ If the account is not activated or the credentials are wrong, the response is always `"Wrong user or password!"` for security reasons.

### Logout

```bash
POST http://127.0.0.1:8000/api/logout/
```

**Response (200):**
```json
{
  "detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."
}
```

### Password Reset

```bash
POST http://127.0.0.1:8000/api/password_reset/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response (200):**
```json
{
  "detail": "An email has been sent to reset your password."
}
```

### Video List

```bash
GET http://127.0.0.1:8000/api/video/
```

**Response (200):** Videos sorted by creation date descending (newest first).
```json
[
  {
    "id": 1,
    "created_at": "2026-01-01T12:00:00Z",
    "title": "Movie Title",
    "description": "Movie Description",
    "thumbnail_url": "http://127.0.0.1:8000/media/thumbnails/1.jpg",
    "category": "Drama"
  }
]
```

### HLS Playlist

```bash
GET http://127.0.0.1:8000/api/video/1/720p/index.m3u8
```

Returns the HLS playlist file (`Content-Type: application/vnd.apple.mpegurl`).

### HLS Segment

```bash
GET http://127.0.0.1:8000/api/video/1/720p/000.ts/
```

Returns the binary TS segment (`Content-Type: video/MP2T`).

---

## Video Upload & Processing

### Upload Flow

1. Open the Django Admin at `http://127.0.0.1:8000/admin/`
2. Go to **Upload App → File Uploads → Add File Upload**
3. Fill in title, description, category and select a video file
4. Click **Save**
5. A `Video` object is automatically created
6. HLS conversion (480p, 720p, 1080p) runs in the background via RQ
7. Thumbnail is extracted and saved automatically

### HLS File Structure

After conversion, files are stored as:

```
media/
├── uploads/
│   └── original_video.mp4
├── videos/
│   └── 1/
│       ├── 480p/
│       │   ├── index.m3u8
│       │   ├── 000.ts
│       │   └── 001.ts
│       ├── 720p/
│       │   ├── index.m3u8
│       │   └── ...
│       └── 1080p/
│           ├── index.m3u8
│           └── ...
└── thumbnails/
    └── 1.jpg
```

---

## Authentication Flow

```
Register → Activation Email → Activate Account → Login
                                                    ↓
                                        access_token cookie (15 min)
                                        refresh_token cookie (7 days)
                                                    ↓
                                        API requests use access_token cookie
                                                    ↓
                                        POST /api/token/refresh/ → new access_token
                                                    ↓
                                        POST /api/logout/ → blacklist refresh_token, delete cookies
```

---

## Admin Panel

Access the Django admin at: `http://127.0.0.1:8000/admin/`

Login with the superuser credentials from your `.env`:
- **Username:** value of `DJANGO_SUPERUSER_USERNAME`
- **Password:** value of `DJANGO_SUPERUSER_PASSWORD`

**Features:**
- User management (activate/deactivate accounts)
- Video management (add, edit, delete)
- File upload management
- RQ job monitoring at `/django-rq/`

---

## Troubleshooting

### Issue: `exec ./backend.entrypoint.sh: no such file or directory`

**Cause:** The `backend.entrypoint.sh` file has Windows line endings (CRLF) instead of Unix line endings (LF). This happens when the file is edited or cloned on Windows.

**Solution:**
1. Open `backend.entrypoint.sh` in VS Code
2. Click on `CRLF` in the bottom right status bar
3. Select `LF`
4. Save the file
5. Restart Docker:
```powershell
docker-compose down
docker-compose up --build
```

### Issue: `password authentication failed for user "..."`

**Cause:** Docker still has an old PostgreSQL volume from a previous setup with different credentials. The database was already initialized with different values and ignores the new `.env`.

**Solution:** Delete all volumes and restart:
```powershell
docker-compose down -v
docker-compose up --build
```

> ⚠️ This deletes all data in the database. You will need to add videos again afterwards.

### Issue: CORS errors in browser

**Symptoms:**
```
Access to fetch has been blocked by CORS policy
```

**Solution:**
1. Check that `CORS_ALLOWED_ORIGINS` in `.env` matches your frontend URL exactly
2. Disable any browser CORS extensions
3. Test in Incognito mode
4. Restart Docker after any `.env` changes:
```powershell
docker-compose down
docker-compose up
```

### Issue: Container does not start

Check the logs:
```powershell
docker-compose logs web
```

Common causes:
- `.env` file missing or not UTF-8 encoded
- Database credentials incorrect
- Port 8000 already in use on your machine

### Issue: .env encoding error

**Symptoms:**
```
failed to read .env: unexpected character "â"
```

**Solution (Windows PowerShell):**
```powershell
Get-Content .env | Set-Content -Encoding UTF8 .env_temp
Remove-Item .env
Rename-Item .env_temp .env
```

### Issue: Cannot run manage.py commands on Windows

`django-rq` uses Linux's `fork` process context and does not run on Windows natively.

**Solution:** Always run Django management commands inside the Docker container:

```powershell
docker exec -it videoflix_backend python manage.py <command>
```

### Issue: Video shows 404 after upload

The HLS conversion runs in the background and takes a few seconds to minutes depending on video length. Monitor progress:

```powershell
docker-compose logs web --tail=50
```

Look for: `Successfully completed upload_app.tasks.convert_to_hls`

### Issue: Emails not arriving

1. Check your SMTP credentials in `.env`
2. Make sure `EMAIL_USE_TLS=True` and `EMAIL_USE_SSL=False` for port 587
3. Some providers (e.g. Gmail) require an app-specific password instead of your regular password
4. Check your spam folder

---

## Production Deployment

Before deploying to production, make the following changes in your `.env`:

**1. Disable debug mode:**
```env
DEBUG=False
```

**2. Update allowed hosts:**
```env
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

**3. Update CORS and CSRF origins:**
```env
CORS_ALLOWED_ORIGINS=https://yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
```

**4. Update URLs:**
```env
FRONTEND_URL=https://yourdomain.com
BACKEND_URL=https://api.yourdomain.com
```

**5. Use a strong secret key:**
```env
SECRET_KEY="your-very-long-random-secret-key-here"
```

**6. Enable HTTPS settings** in `core/settings.py`:
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

---

## License

This project is licensed under the MIT License.
