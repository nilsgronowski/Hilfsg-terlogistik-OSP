# Django Project Setup

## Überblick

Dieses Projekt nutzt Docker Compose für Django + MySQL 8.4. Die Konfiguration erfolgt über `.env`‑Dateien:

- `.env.local` für lokale Entwicklung
- `.env.prod` für Produktion

**Projektstruktur:**

- Django‑Projekt: `HilfsgüterlogikstikApp/`
- Container working directory: `/app/HilfsgüterlogikstikApp`
- Env‑Variablen werden via `env_file` in docker-compose geladen
- `DOCKER_ENV=1` signalisiert Container-Umgebung

## Voraussetzungen

- Docker
- Docker Compose

## Schnellstart (Local / Dev)

1. **In das Projekt wechseln:**

   ```bash
   cd /path/to/project
   ```

2. **Container starten (Dev):**

   ```bash
   docker-compose up -d --build
   ```

3. **Migrationen ausführen:**

   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. **Superuser anlegen:**

   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5. **App öffnen:**
   - Django: http://localhost:8000
   - Admin: http://localhost:8000/admin/

## Wechsel zwischen Dev und Prod

**Standard:** Docker Compose lädt `.env.local` via `env_file`.

### Prod mit eigener Env starten

Um die Prod‑Konfiguration zu nutzen, passe `docker-compose.yml` an:

```yaml
env_file:
  - .env.prod
```

Oder starte mit Override:

```bash
docker-compose --env-file .env.prod up -d --build
```

**Hinweis:** Im Container werden Env-Variablen direkt von docker-compose gesetzt. Lokale Entwicklung (ohne Docker) lädt `.env.local` via `load_dotenv()` in den Settings.

## Wichtige Umgebungsvariablen

- `DOCKER_ENV`: `1` im Container (signalisiert docker-compose Umgebung)
- `DJANGO_ENV`: `local` oder `prod` (für lokale Entwicklung)
- `DEBUG`: `true`/`false` oder `1`/`0`
- `SECRET_KEY`: Django Secret Key (niemals leer lassen in Prod!)
- `ALLOWED_HOSTS`: Kommagetrennte Liste (z.B. `localhost,127.0.0.1`)
- `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`

## Nützliche Kommandos

- **Start:** `docker-compose up -d`
- **Stop:** `docker-compose down`
- **Logs:** `docker-compose logs -f web`
- **Shell:** `docker-compose exec web python manage.py shell`
- **App erstellen:** `docker-compose exec web python manage.py startapp appname`
- **Migrationen:** `docker-compose exec web python manage.py makemigrations`
- **Apply:** `docker-compose exec web python manage.py migrate`

## Requirements Workflow

**Ziel:** requirements.txt ist die source‑of‑truth und wird bewusst gepflegt.

### Empfohlener Ablauf

1. **Neues Paket hinzufügen**
   - Trage es direkt in `requirements.txt` ein (mit gewünschter Version).
   - Rebuild Container:

   ```bash
   docker-compose up -d --build
   ```

   Oder installiere ohne Rebuild:

   ```bash
   docker-compose exec web pip install <package>
   ```

2. **Paket aktualisieren**
   - Version in `requirements.txt` anpassen.
   - Rebuild:

   ```bash
   docker-compose up -d --build
   ```

3. **Freeze nur bei Releases**
   - `pip freeze` wird **nicht** nach jedem Install genutzt.
   - Bei Release oder größeren Änderungen einmal aktualisieren:

   ```bash
   docker-compose exec web pip freeze > requirements.txt
   ```

### Warum so?

- Stabilere und nachvollziehbare Abhängigkeiten
- Vermeidet ungewollte Version‑Updates

## Datenbank

- **Host:** db
- **Port:** 3306
- **Root Password:** rootpassword
- **Database:** django_db
- **User:** django_user
- **Password:** django_password
