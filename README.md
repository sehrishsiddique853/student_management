# Student Management

A Flask REST API for creating, viewing, editing, and deleting student records. Student data is stored in Supabase.

## Requirements

- Python 3.11 or newer
- A Supabase project
- Git

## Setup For A New Developer

### 1. Clone the repository

```bash
git clone https://github.com/sehrishsiddique853/student_management.git
cd student_management
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

When activated, the terminal should show `(venv)` before the prompt.

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure Supabase

1. Create or open the team Supabase project.
2. Open **Project Settings > Data API** and copy the project URL.
3. Open **Project Settings > API Keys** and copy the publishable/anon key. Do not use a service-role key in this application.
4. Create a local `.env` file from the example:

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS or Linux:

```bash
cp .env.example .env
```

5. Edit `.env`:

```env
FLASK_SECRET_KEY=replace-with-a-random-secret
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-publishable-or-anon-key
```

The `.env` file is ignored by Git and must never be committed.

### 5. Create the database table

In Supabase, create a `public.students` table and confirm that it contains:

	- `id`
	- `name`
	- `email`
	- `age`
	- `course`
	- `created_at`

The `email` column is unique. The `age` migration is included because an existing `students` table may have been created before the age field was added.

### 6. Start the application

```bash
python main.py
```

The API is available at <http://127.0.0.1:5000/students>. Stop the development server with `Ctrl+C`.

## Application Features

- `GET /students` lists all students
- `POST /students` creates a student
- `GET /students/<id>` returns one student
- `PUT` or `PATCH /students/<id>` updates a student
- `DELETE /students/<id>` deletes a student
- Prevent duplicate email addresses through the database constraint

## Authentication

- `POST /auth/register` creates an email/password user
- `POST /auth/login` returns Supabase access and refresh tokens
- `GET /auth/me` returns the authenticated user

Protect student endpoints with the login access token:

```text
Authorization: Bearer <access_token>
```


## Project Structure

```text
Student_management/
├── controllers/              # Request handling and validation
├── models/                   # Supabase database operations
├── routes/                   # Flask URL routes
├── .env.example              # Environment variable template
├── database.py               # Supabase client setup
├── requirements.txt          # Python dependencies
├── main.py                   # Flask application entry point
└── README.md
```

## Common Problems

### `SUPABASE_URL is missing from .env`

Make sure the file is named `.env`, is in the project root beside `main.py`, and contains `SUPABASE_URL`.

### `Invalid API key`

Check that `SUPABASE_KEY` is copied from the same Supabase project and does not include quotation marks or extra spaces.

### `Email already exists`

Email addresses must be unique. Check the existing record in Supabase before trying another insert.

## Git Workflow

Before starting work:

```bash
git pull origin main
```

After making changes:

```bash
git add .
git commit -m "Describe the change"
git push origin main
```
