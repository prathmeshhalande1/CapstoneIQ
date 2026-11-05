# ⚠️ Work in Progress (WIP)
This project is currently under active development and is not yet fully functional. Please do not copy, fork, or use this codebase, as it is incomplete and subject to breaking changes.

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
### 6.Configure Environment Variables (`.env`)

Create a file named `.env` in the root directory of your project (same level as `manage.py`) and add your configuration details:

```env
DEBUG=True
SECRET_KEY=your_django_secret_key_here

# Email Configuration (Gmail SMTP)
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_gmail_app_password

# GitHub Integration API Key
GITHUB_ACCESS_TOKEN=your_github_personal_access_token
```
### 6.🔑 How to get your credentials:
1. **Gmail App Password:**
   - Go to your [Google Account Security Settings](https://myaccount.google.com/security) (Ensure 2-Step Verification is enabled).
   - Navigate to **App passwords** (or visit [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)).
   - Generate a new app password and paste it as `EMAIL_HOST_PASSWORD`.
2. **GitHub Personal Access Token:**
   - Go to GitHub **Settings** > **Developer settings** > **Personal access tokens** > **Tokens (classic)** (or click [here](https://github.com/settings/tokens)).
   - Generate a new token with `repo` scope permissions and paste it as `GITHUB_ACCESS_TOKEN`.

> 📺 **Need a visual guide?** Watch this helpful tutorial on [How to Generate GitHub Tokens and Gmail App Passwords](https://www.youtube.com/results?search_query=how+to+get+github+personal+access+token+and+gmail+app+password).**or** [GitHub Tokens and Gmail App Passwords direact link of vidow](https://www.youtube.com/watch?v=Vylc7UdQDi0).

### 7.Run the Development Server
```bash
python manage.py runserver
```