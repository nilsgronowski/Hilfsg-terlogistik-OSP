# Django Project Setup

## Overview

This project uses Docker Compose for Django + MySQL 8.4. Configuration is done via `.env` files:

- `.env.local` for local development
- `.env.prod` for production

**Project Structure:**

- Django project: `HilfsgüterlogikstikApp/`
- Container working directory: `/app/HilfsgüterlogikstikApp`
- Environment variables are loaded via `env_file` in docker-compose
- `DOCKER_ENV=1` signals container environment

## Prerequisites

- Docker
- Docker Compose

## Quick Start (Local / Dev)

1. **Navigate to the project:**

   ```bash
   cd /path/to/project
   ```

2. **Start containers (Dev):**

   ```bash
   docker-compose up -d --build
   ```

3. **Run migrations:**

   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. **Create superuser:**

   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5. **Open app:**
   - Django: http://localhost:8000
   - Admin: http://localhost:8000/admin/

## Switching Between Dev and Prod

**Default:** Docker Compose loads `.env.local` via `env_file`.

### Starting Prod with Custom Env

To use the production configuration, adjust `docker-compose.yml`:

```yaml
env_file:
  - .env.prod
```

Or start with override:

```bash
docker-compose --env-file .env.prod up -d --build
```

**Note:** In the container, environment variables are set directly by docker-compose. Local development (without Docker) loads `.env.local` via `load_dotenv()` in the settings.

## Important Environment Variables

- `DOCKER_ENV`: `1` in container (signals docker-compose environment)
- `DJANGO_ENV`: `local` or `prod` (for local development)
- `DEBUG`: `true`/`false` or `1`/`0`
- `SECRET_KEY`: Django Secret Key (never leave empty in prod!)
- `ALLOWED_HOSTS`: Comma-separated list (e.g., `localhost,127.0.0.1`)
- `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`

## Useful Commands

- **Start:** `docker-compose up -d`
- **Stop:** `docker-compose down`
- **Logs:** `docker-compose logs -f web`
- **Shell:** `docker-compose exec web python manage.py shell`
- **Create app:** `docker-compose exec web python manage.py startapp appname`
- **Migrations:** `docker-compose exec web python manage.py makemigrations`
- **Apply:** `docker-compose exec web python manage.py migrate`

## Requirements Workflow

**Goal:** requirements.txt is the source-of-truth and is maintained consciously.

### Recommended Process

1. **Add new package**
   - Add it directly to `requirements.txt` (with desired version).
   - Rebuild container:

   ```bash
   docker-compose up -d --build
   ```

   Or install without rebuild:

   ```bash
   docker-compose exec web pip install <package>
   ```

2. **Update package**
   - Adjust version in `requirements.txt`.
   - Rebuild:

   ```bash
   docker-compose up -d --build
   ```

3. **Freeze only on releases**
   - `pip freeze` is **not** used after every install.
   - Update once on release or major changes:

   ```bash
   docker-compose exec web pip freeze > requirements.txt
   ```

### Why This Way?

- More stable and traceable dependencies
- Avoids unwanted version updates

## Database

- **Host:** db
- **Port:** 3306
- **Root Password:** rootpassword
- **Database:** django_db
- **User:** django_user
- **Password:** django_password
