# ISP Portal

A small **FastAPI** application for managing internet connection requests, customer
complaints, and admin-side resolutions — with both a **web UI** (customer + admin)
and a **JSON API**.

Built as a single-file app with an in-memory store so you can spin it up in seconds
and swap in a real database later without touching the routes.

---

## Features

- **Customer portal** — apply for a new internet connection, track application
  status, file complaints, and view resolution notes.
- **Admin dashboard** — review all applications, change their status
  (`pending → approved → installed → rejected`), and resolve complaints with a note.
- **JSON API** — every action available from the UI is also exposed as a REST
  endpoint, with interactive Swagger docs at `/docs`.
- **Status filters** — filter applications and complaints by status from both the
  UI and the API.
- **Shared state** — the customer UI, admin UI, and API all read/write the same
  thread-safe in-memory store.
- **No database required** — pure Python, instant startup, easy to test.

---

## Project Structure

```
isp_portal/
├── main.py                    # FastAPI app: HTML routes + JSON API
├── models.py                  # Pydantic models and enums
├── storage.py                 # Thread-safe in-memory store
├── templates/
│   ├── base.html              # Shared layout + CSS
│   ├── customer.html          # Customer portal (apply, track, complain)
│   └── admin.html             # Admin dashboard (approve, resolve)
├── requirements.txt
└── README.md
```

---

## Requirements

- Python **3.10+** (uses `X | None`-style typing in some helpers and modern `match`-friendly enums)
- pip

Dependencies (pinned in `requirements.txt`):

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
jinja2==3.1.4
pydantic==2.9.2
python-multipart==0.0.9
```

---

## Installation

```bash
# 1. Clone or copy the project folder
cd isp_portal

# 2. (Recommended) create a virtual environment
python -m venv .venv
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Running the App

```bash
uvicorn main:app --reload
```

Then open:

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/ | Customer portal (apply, track, complain) |
| http://127.0.0.1:8000/admin | Admin dashboard (approve, resolve) |
| http://127.0.0.1:8000/docs | Interactive Swagger API docs |
| http://127.0.0.1:8000/redoc | ReDoc API reference |

---

## Usage Walkthrough

### 1. Customer applies for a connection

Open **`/`**, fill in the "Apply for a New Connection" form, and submit.
You'll be redirected back with your **Application ID** displayed.

Status starts at `pending`.

### 2. Admin approves the application

Go to **`/admin`**, find the row under **Connection Applications**, change the
status dropdown to `approved` (or `installed`), and click **Save**.

### 3. Customer tracks status

Back on **`/`**, enter your **Application ID** in the "Track Your Application"
form. You'll see the current status pill.

### 4. Customer files a complaint

On the same page (once an application is loaded), fill in the "File a Complaint"
form — subject, category (`no_internet`, `slow_speed`, `billing`,
`router_issue`, `other`), and description.

### 5. Admin resolves the complaint

On **`/admin`**, find the complaint, enter a **resolution note**, pick a status
(`resolved`, `in_progress`, or `closed`), and click **Save**. The note and
timestamp are attached to the complaint.

### 6. Customer sees the resolution

Reload the customer portal with the same application ID — the resolution note
appears under "Your Complaints".
