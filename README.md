# FastAPI Authentication Service

A robust, production-ready backend API for user identity and access management. Built with FastAPI, it implements JWT authentication, secure session management, role-based access control (RBAC), and an email-based password recovery system.

---

## 🚀 Features

- **User Registration:** Email validation and strong password enforcement (Bcrypt hashing).
- **Secure Authentication:** Dual-token system (Access Token + Refresh Token).
- **HttpOnly Cookies:** Refresh tokens are stored securely to prevent XSS attacks.
- **Role-Based Access:** Distinct endpoints for Users and Admins.
- **Password Recovery:** Email-based reset flow using Gmail/Brevo SMTP.
- **Automated Testing:** Complete Pytest suite for reliability.
- **CORS Support:** Configured for seamless frontend integration.

---

## 🛠 Tech Stack

- **Framework:** FastAPI & Uvicorn
- **Database:** SQLite (Dev) / PostgreSQL (Prod) via SQLAlchemy
- **Validation:** Pydantic V2
- **Security:** Python-JOSE (JWT), Passlib (Bcrypt)
- **Email:** FastAPI-Mail
- **Testing:** Pytest

---

## 📋 Prerequisites

- Python 3.9+
- Git
- A Gmail Account or Brevo SMTP Key (for email features)

---

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/KilaBean/auth-service-rest-api.git
   cd auth-service
   ```

2. **Create a virtual environment** (Windows)
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

---

## 🔐 Configuration

Create a `.env` file in the project root directory and add the following variables:

```env
# Database
DATABASE_URL=sqlite:///./test.db

# Security
SECRET_KEY=your_super_secret_random_string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email Configuration (Example: Gmail)
MAIL_USERNAME=philiptandoh878@gmail.com
MAIL_PASSWORD=your_16_char_app_password
MAIL_FROM=philiptandoh878@gmail.com
MAIL_FROM_NAME=ByteForge
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_STARTTLS=True
MAIL_SSL_TLS=False
USE_CREDENTIALS=True
```

> **Note:** If using Gmail, generate an [App Password](https://support.google.com/accounts/answer/185833) instead of using your login password.

---

## ▶️ Running the Application

1. **Start the server:**
   ```powershell
   uvicorn app.main:app --reload
   ```

2. **Access the API:**
   - Swagger UI: `http://127.0.0.1:8000/docs`
   - API JSON: `http://127.0.0.1:8000/openapi.json`

---

## 👤 Admin User Creation

Since registration defaults to "user", you must create the first admin manually.

Run the included script:
```powershell
python create_admin.py
```
This creates an admin user (`admin@myapp.com` / `StrongAdminPass123`) instantly.

---

## 🧪 Testing

Run the automated test suite:
```powershell
pytest
```

This will verify user registration, login, protected routes, and validation logic.

---

## 📂 Project Structure

```text
auth-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # App entry point & CORS
│   ├── config.py            # Pydantic Settings
│   ├── database.py          # DB Connection
│   ├── models.py            # SQLAlchemy Models
│   ├── schemas.py           # Pydantic Schemas
│   ├── security.py          # JWT & Password Hashing
│   ├── dependencies.py       # DB Dependency
│   ├── dependencies_auth.py  # Auth Logic
│   ├── routes/
│   │   ├── auth.py         # Register, Login, Reset
│   │   └── users.py        # User & Admin Routes
│   └── services/
│       └── email_service.py # Email Logic
├── conftest.py             # Pytest Configuration
├── create_admin.py          # Admin Script
├── requirements.txt
└── .env                    # Your Secrets (Not in Git)
```

---

## 🌐 API Endpoints

### Authentication
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/auth/register` | Create a new user account |
| `POST` | `/auth/login` | Login and receive tokens |
| `POST` | `/auth/refresh` | Get a new Access Token (uses Cookie) |
| `POST` | `/auth/logout` | Revoke session and clear cookie |
| `POST` | `/auth/forgot-password` | Request password reset link |
| `POST` | `/auth/reset-password` | Update password using token |

### Users
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/users/me` | Get current user profile |
| `POST` | `/users/promote/{id}` | Promote user to Admin (Admin Only) |
| `GET` | `/users/admin-only` | Admin dashboard (Admin Only) |

---
