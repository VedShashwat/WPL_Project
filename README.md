# MetaSync

MetaSync is a gaming analytics platform built with Django.

## Tech Stack

- Python 3
- Django
- SQLite

## Project Setup

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run migrations:

```powershell
python manage.py makemigrations
python manage.py migrate
```

4. Create an admin user:

```powershell
python manage.py createsuperuser
```

5. Start the development server:

```powershell
python manage.py runserver
```

6. Open Django Admin:

- http://127.0.0.1:8000/admin/

## App Structure

- `metasync_project/`: Django project configuration
- `core/`: Main app (custom user + player profile)
- `templates/`: Project-level templates

## Notes

- SQLite is used as the default database (`db.sqlite3`).
- `db.sqlite3` is excluded from git via `.gitignore`.
