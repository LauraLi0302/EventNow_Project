# EventNow - Integrated Event Management SaaS Platform

EventNow is a full-stack web application designed for seamless event organization and attendee management. This project focuses on accessibility (WCAG 2.1 AA), secure data persistence, and a modern user experience.

---

## 🚀 Core Features
* **Role-Based Access Control (RBAC):** Distinct workflows for Attendees, Organisers, and Administrators.
* **Rich Text Content:** Integrated Quill editor for professional event descriptions.
* **Accessible Design:** Built with semantic HTML and ARIA standards for inclusive navigation.
* **Data Integrity:** Subscription management with an archival (soft-delete) strategy.

## 🛠 Tech Stack
* **Backend:** Django 4.x (Python)
* **Frontend:** Bootstrap 5, JavaScript (ES6+), Quill.js
* **Database:** SQLite (Development) / PostgreSQL (Production)
* **Environment:** UQCloud Zone (Target Deployment)

---

## 📦 Installation & Setup

### 1. Prerequisites
* Python 3.10+
* Virtualenv

### 2. Local Setup
```bash
# Clone the repository
git clone [https://github.com/your-username/EventNow.git](https://github.com/your-username/EventNow.git)
cd EventNow

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Database migrations
python manage.py makemigrations
python manage.py migrate
3. Running the Server
Bash
python manage.py runserver 8002
The application will be available at http://127.0.0.1:8002.
