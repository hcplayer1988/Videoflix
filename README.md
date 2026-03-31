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

- Docker Desktop
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/hcplayer1988/Videoflix.git
cd Videoflix
```

### 2. Environment Configuration

Copy the template and fill in your values:

```bash
cp .env.template .env
```

Edit `.env` with your settings:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
CORS_ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
FRONTEND_URL=http://127.0.0.1:5500
BACKEND_URL=http://127.0.0.1:8000

DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=db
DB_PORT=5432

REDIS_HOST=redis
REDIS_LOCATION=redis://redis:6379/1
REDIS_PORT=6379
REDIS_DB=0

EMAIL_HOST=your-smtp-host
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=your-email@domain.com
```

> ⚠️ **Important:** If your `SECRET_KEY` contains a `#` character, wrap it in double quotes: `SECRET_KEY="your#key"`
>
> ⚠️ **Important:** The `.env` file must be **UTF-8 encoded**. If you created it with Notepad on Windows, convert it:
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

On startup the container automatically:
- Waits for PostgreSQL to be ready
- Runs `collectstatic`
- Runs `makemigrations` and `migrate`
- Creates the superuser from `.env` credentials
- Starts the RQ worker
- Starts Gunicorn

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | — |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost` |
| `FRONTEND_URL` | Frontend base URL for email links | `http://localhost:5500` |
| `BACKEND_URL` | Backend base URL | `http://127.0.0.1:8000` |
| `DB_NAME` | PostgreSQL database name | `videoflix_db` |
| `DB_USER` | PostgreSQL user | `videoflix_user` |
| `DB_PASSWORD` | PostgreSQL password | — |
| `DB_HOST` | PostgreSQL host | `db` |
| `REDIS_HOST` | Redis host | `redis` |
| `MEDIA_ROOT` | Media files directory | `<BASE_DIR>/media` |

### RQ Queue Configuration

The project uses a single `default` queue with a 3600s timeout to handle all background tasks including HLS video conversion:

| Queue | Use Case | Timeout |
|-------|----------|---------|
| `default` | HLS conversion, thumbnail generation | 3600s |

The RQ worker starts automatically in the Docker container and listens on the `default` queue.

### Email Configuration

The project uses HTML email templates with dark mode support. Emails are sent directly (not via queue) for reliability.

Supported SMTP providers: All-inkl, Gmail, Outlook, any standard SMTP server.

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/register/` | Register new user | No |
| GET | `/api/activate/<uidb64>/<token>/` | Activate account | No |
| POST | `/api/login/` | Login and set JWT cookies | No |
| POST | `/api/logout/` | Logout and invalidate tokens | Refresh-Token-Cookie |
| POST | `/api/password_reset/` | Send password reset email | No |
| POST | `/api/password_confirm/<uidb64>/<token>/` | Confirm new password | No |
| POST | `/api/token/refresh/` | Refresh access token | Refresh-Token-Cookie |

### Video

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/video/` | List all videos with metadata | JWT |
| GET | `/api/video/<id>/<resolution>/index.m3u8` | HLS master playlist | JWT |
| GET | `/api/video/<id>/<resolution>/<segment>/` | HLS video segment | JWT |

**Resolutions:** `480p`, `720p`, `1080p`

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

After registration an activation email is sent. The account remains inactive until activation.

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

**Response (200):** Sets `access_token` and `refresh_token` as httpOnly cookies.
```json
{
  "detail": "Login successful",
  "user": {
    "id": 1,
    "username": "user@example.com"
  }
}
```

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

**Response (200):**
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

Videos are returned sorted by creation date descending (newest first).

### HLS Playlist

```bash
GET http://127.0.0.1:8000/api/video/1/720p/index.m3u8
```

Returns the HLS master playlist file (`Content-Type: application/vnd.apple.mpegurl`).

### HLS Segment

```bash
GET http://127.0.0.1:8000/api/video/1/720p/000.ts/
```

Returns the binary TS segment (`Content-Type: video/MP2T`).

## Video Upload & Processing

### Upload Flow

1. Upload video via Django Admin (`/admin/`) under **Upload App → File Uploads → Add**
2. `post_save` signal fires on `FileUpload` save
3. A `Video` object is automatically created in `content_app`
4. HLS conversion job is enqueued in the `default` RQ queue
5. ffmpeg converts the video to 480p, 720p and 1080p HLS format
6. Thumbnail is extracted from the video and saved to the `Video` object

> ℹ️ **Note:** When uploading via the Admin Panel, the browser may show a 500 error briefly after saving. This is normal — simply refresh the page and the video will appear correctly. The HLS conversion runs in the background and completes within a few seconds to minutes depending on video length.

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

## Admin Panel

Access the Django admin at: `http://127.0.0.1:8000/admin/`

Login with the superuser credentials from your `.env`:
- **Username:** `DJANGO_SUPERUSER_USERNAME`
- **Password:** `DJANGO_SUPERUSER_PASSWORD`

**Features:**
- User management
- Video management (add, edit, delete)
- File upload management
- RQ job monitoring at `/django-rq/`

## Troubleshooting

### Issue: CORS errors in browser

**Symptoms:**
```
Access to fetch has been blocked by CORS policy
```

**Solution:**
1. Check `CORS_ALLOWED_ORIGINS` in `.env` matches your frontend URL exactly
2. Ensure `CORS_ALLOW_CREDENTIALS = True` is set in `settings.py`
3. Disable any browser CORS extensions
4. Test in Incognito mode

### Issue: Container does not start

```bash
docker-compose logs web
```

Common causes:
- `.env` missing or incorrectly encoded (must be UTF-8)
- Database credentials wrong
- Port 8000 already in use

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

`django-rq` uses Linux's `fork` process context and does not work on Windows.

**Solution:** Run Django management commands inside the Docker container:

```powershell
docker exec -it videoflix_backend python manage.py <command>
```

### Issue: Video shows 404 after upload

The HLS conversion runs in the background and may take a few seconds to minutes. Wait for the conversion to complete before trying to play the video. You can monitor the progress in the Docker logs:

```powershell
docker-compose logs web --tail=50
```

Look for: `Successfully completed upload_app.tasks.convert_to_hls`

## Production Deployment

Before deploying to production:

**1. Set `DEBUG = False`** in `.env`

**2. Update `ALLOWED_HOSTS`:**
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

**5. Enable HTTPS settings** in `settings.py`:
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## License

This project is licensed under the MIT License.
