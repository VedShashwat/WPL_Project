# MetaSync

MetaSync is a Django-based gaming analytics platform with account auth, player dashboards, Clash of Clans linking, and a live global leaderboard.

## Tech Stack

- Python 3.10+
- Django 4.2
- SQLite (default local database)
- jQuery + Bootstrap 5 (frontend interactivity)

## Teammate Quick Start

1. Clone the repository and move into it.

```powershell
git clone <your-repo-url>
cd Gaming-Tracking
```

2. Create and activate a virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies.

```powershell
pip install -r requirements.txt
```

4. Create your local `.env` from `.env.example`.

```powershell
Copy-Item .env.example .env
```

5. Update `.env` values (especially `SECRET_KEY` and `COC_API_KEY`).

6. Apply migrations.

```powershell
python manage.py migrate
```

7. (Optional) Create a superuser for admin access.

```powershell
python manage.py createsuperuser
```

8. Run the development server.

```powershell
python manage.py runserver
```

9. Open the app:

- Dashboard/Login: http://127.0.0.1:8000/
- Django Admin: http://127.0.0.1:8000/admin/

## Environment Variables

MetaSync reads environment variables from `.env` in the project root.

- `SECRET_KEY`: Django secret key for local/dev runtime.
- `DEBUG`: `True` or `False`.
- `COC_API_KEY`: Clash of Clans API Bearer token.

To get a CoC API key:
1. Visit the official Clash of Clans developer portal.
2. Create an API key.
3. Add your current public IP to the key allowlist.
4. Paste the token into `COC_API_KEY`.

## Core Features

- Combined login/signup flow with custom user model.
- Player profile cards for generic game metrics and CoC stats.
- Async CoC linking via AJAX modal.
- Global leaderboard refreshed every 30 seconds via AJAX polling.
- "View Profile" leaderboard action showing player stats in a modal.

## App Structure

- `metasync_project/`: Django project settings and URL config.
- `core/`: Main app (models, forms, views, APIs).
- `templates/`: Dashboard and auth templates.

## Troubleshooting

- `Clash of Clans API request failed`: verify `COC_API_KEY` and IP allowlist.
- `ModuleNotFoundError`: ensure virtual environment is active and run `pip install -r requirements.txt`.
- Migration issues: run `python manage.py migrate` again and confirm `db.sqlite3` is writable.

## Notes

- `.env` is gitignored and must never be committed.
- `db.sqlite3` is local-only and excluded from git.
