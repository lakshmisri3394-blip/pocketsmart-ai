# PocketSmart AI — Smart Budget & Recommendation Assistant

A FastAPI + Gemini-powered budget recommendation web application based on the supplied project specification.

## Features
- User registration/login/logout
- JWT authentication
- Home Interior Budget Planner
- Party Budget Planner
- Jewelry Budget Planner with optional outfit image
- Gemini-powered recommendations
- Recommendation history
- Responsive HTML/CSS/JavaScript UI
- SQLite database
- Safe fallback recommendations when Gemini is unavailable

## Project structure
```text
PocketSmart_AI/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── auth.py
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── templates/
│   └── static/
├── uploads/
├── requirements.txt
├── .env.example
└── README.md
```

## Run locally

1. Install Python 3.10+.
2. Open a terminal inside this folder.
3. Create a virtual environment:
   - Windows: `python -m venv venv`
   - macOS/Linux: `python3 -m venv venv`
4. Activate it.
5. Install packages:
   `pip install -r requirements.txt`
6. Copy `.env.example` to `.env`.
7. Put your Gemini API key into `.env`.
8. Start:
   `uvicorn app.main:app --reload`
9. Open:
   `http://127.0.0.1:8000`

## Important
The product/service links in generated recommendations are example/search links. Real-time inventory, pricing, and vendor APIs are not included because the supplied project document describes those integrations but does not provide API credentials or concrete API implementations.

The application therefore uses Gemini for contextual recommendations and provides platform search links as a practical working fallback.
