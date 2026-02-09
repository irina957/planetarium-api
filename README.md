# 🌌 Planetarium API Service
> A Django-based REST API for managing planetarium operations, including shows, cosmic sessions, and ticket bookings.

This project provides a comprehensive management system for a planetarium. It allows users to browse astronomy shows, book tickets for specific sessions, and manage the planetarium's schedule and resources (domes, shows, etc.) through a professional API.

## 🚀 Features
* **User Authentication:** Secure login & registration using JWT (JSON Web Tokens).
* **Astronomy Shows:** Manage shows with descriptions and themes.
* **Planetarium Domes:** Capacity management for different viewing halls.
* **Show Sessions:** Schedule shows at specific times and domes.
* **Booking System:** User-friendly ticket reservations with seat selection.
* **Image Support:** Ability to upload and view images for astronomy shows.
* **Documentation:** Interactive API docs via Swagger/Redoc.
* **Filtering & Search:** Efficient data browsing for all endpoints.

## 🧪 Technologies Used
* **Python 3.11**
* **Django 5.2.10** & **Django REST Framework**
* **PostgreSQL** (Database)
* **Docker** & **Docker Compose** (Containerization)
* **JWT** (Authentication)
* **Swagger (drf-spectacular)** (API Documentation)

## 🐳 Getting Started with Docker (Recommended)

To run this project locally, you only need to have **Docker** and **Docker Compose** installed.

## 1️⃣  **Clone the repository:**
   ```bash
   git clone https://github.com/irina957/planetarium-api.git
   cd planetarium-api
```

## 2️⃣ Create .env file

Create a `.env` file in the project root and fill it with your environment variables.

## 3️⃣ Build and run containers
```bash
docker-compose up --build
```

## 4️⃣ Load initial data (fixtures)
```bash
docker-compose exec planetarium python manage.py loaddata db_data.json
```

## 5️⃣ Create superuser
```bash
docker-compose exec planetarium python manage.py createsuperuser
```

## 6️⃣ Access the application

- **API Root:** http://127.0.0.1:8000/api/planetarium/
- **Admin panel:** http://127.0.0.1:8000/admin/
- **Get JWT Token:** http://127.0.0.1:8000/api/user/token/

> **Note:** Use the obtained token in the `Authorization` header as `Bearer <your_token>` for protected endpoints.
---

## 🛠 Manual Installation (Without Docker)

If you prefer to run the project without Docker:

### 1️⃣ Clone repository & setup virtual environment
```bash
git clone https://github.com/irina957/planetarium-api.git
cd planetarium-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2️⃣ Database setup

Make sure PostgreSQL is running and update your `.env` file with correct database credentials.

### 3️⃣ Apply migrations and run server
```bash
python manage.py migrate
python manage.py loaddata db_data.json
python manage.py runserver
```

---

## 📖 API Documentation

Once the server is running, API documentation is available at:

- **Swagger UI:** http://127.0.0.1:8000/api/doc/swagger/
- **Redoc:** http://127.0.0.1:8000/api/doc/redoc/

### Database structure
![DB Structure](docs/structure.png)