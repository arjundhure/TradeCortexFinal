# TradeCortex AI — Setup Guide

## Project Structure (Fixed)
```
TradeCortex/
├── app.py                  ← Main Flask app
├── auth_routes.py          ← Login/signup routes
├── db.py                   ← DB connection helper
├── run.py                  ← Easy launcher script
├── requirements.txt
├── .env.example            ← Copy to .env and fill in your DB password
├── templates/
│   ├── index.html          ← Main dashboard UI
│   └── auth.html           ← Login/signup page
└── services/
    ├── __init__.py
    ├── stock_service.py
    ├── news_service.py
    ├── sentiment.py
    ├── ml_predictor.py
    ├── volatility.py
    ├── recommendation.py
    ├── explanation.py
    └── db_service.py
```

## Step-by-Step Setup

### 1. Install Python dependencies
```bash
pip install -r requirements.txt
python -m textblob.download_corpora
```

### 2. Set up MySQL
Open MySQL and run:
```sql
CREATE DATABASE IF NOT EXISTS stock_project;
```
(The app auto-creates the tables on first run.)

### 3. Configure your DB password
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Then edit `.env` and set your MySQL password:
```
DB_PASSWORD=your_actual_password
```

### 4. Run the app
```bash
python run.py
```
Or directly:
```bash
python app.py
```

Open browser at: **http://localhost:5000**

## What Was Fixed
1. **Broken folder structure** — Files were all in the root. Flask's `render_template` requires an `index.html` and `auth.html` inside a `templates/` folder.
2. **Missing services/ package** — `app.py` imports from `services.*` (e.g. `from services.stock_service import ...`). All service files are now in the `services/` subfolder with `__init__.py`.
3. **Corrupt `.pyc` file** — `auth_routes.cpython-314.pyc` was a broken compiled bytecode file (Python 3.14 format, unreadable). It's not needed; Python will regenerate it automatically.
4. **CRLF line endings** — `auth_routes.py` had Windows-style line endings that can cause issues. Fixed.
5. **Missing python-dotenv** — Added to requirements so `.env` file works.
