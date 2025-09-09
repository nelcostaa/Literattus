# Literattus Python Scripts

This directory contains Python utility scripts for the Literattus project.

## Setup

1. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure environment variables are set in the project root `.env` file.

## Scripts

### `db_setup.py`
Database setup and migration utility.

```bash
python scripts/db_setup.py
```

### `google_books_sync.py`
Synchronize book data from Google Books API.

```bash
python scripts/google_books_sync.py
```

## Environment Variables

Make sure these variables are set in your `.env` file:

- `DB_HOST`, `DB_PORT`, `DB_SERVICE_NAME`, `DB_USERNAME`, `DB_PASSWORD`
- `GOOGLE_BOOKS_API_KEY`

## Oracle Database Setup

Ensure you have Oracle Instant Client installed for the `oracledb` package to work properly.
