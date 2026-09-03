# Student Management

A simple Flask student management application using Supabase for storage.

## Project Structure

```text
Student_management/
├── controllers/
│   └── student_controller.py
├── models/
│   └── student_model.py
├── routes/
│   └── student_routes.py
├── templates/
│   ├── base.html
│   └── students/
│       ├── index.html
│       └── form.html
├── static/
│   └── css/
│       └── style.css
├── .env.example
├── .gitignore
├── database.py
├── requirements.txt
├── run.py
├── supabase.sql
└── README.md
```

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and add your Supabase credentials.
4. Run the SQL in `supabase.sql` inside your Supabase SQL editor.
5. Start the app:

```bash
python run.py
```

Open `http://127.0.0.1:5000` in your browser.
