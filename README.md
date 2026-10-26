# 🎓 CapstoneIQ - College Capstone Management System

CapstoneIQ is a modular Django-based web application built to manage student profiles, telemetry, project repositories, and collaboration groups.

---

## 🚀 Getting Started

Follow these steps to run the project locally on your machine.

### 1. Clone the Repository
```bash
git clone [https://github.com/prathmeshhalande1/CapstoneIQ](https://github.com/prathmeshhalande1/CapstoneIQ)

cd capstoneIq
```


### 2. Create and Activate Virtual Environment

#### On Windows (PowerShell)
```bash
python -m venv venv
venv\Scripts\Activate
```
#### On Mac/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3.Install Dependencies
```bash
pip install -r requirements.txt
```

### 4.Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5.Create a Superuser (Admin Access) 
```bash
python manage.py createsuperuser
```

### 6.Run the Development Server
```bash
python manage.py runserver
```