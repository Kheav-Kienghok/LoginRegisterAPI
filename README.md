# LoginRegisterAPI

LoginRegisterAPI is a simple RESTful API-based application designed for user authentication. The project focuses on two main pages: the **Register Page** and the **Login Page**. Users can register an account, which is stored in the database, and subsequently log in using their credentials.

---

## Features

1. **User Registration**:
   - Users can register with their name, email, and password.
   - The API validates the registration details.
   - Registered data is securely added to the database.

2. **User Login**:
   - Users can log in using their registered email and password.
   - Validation ensures the credentials match the database records.
   - Session management is implemented for user authentication.

---

## Pages Overview

### 1. Register Page (Image 1)
- **Form Fields**:
  - Name
  - Email
  - Password
  - Confirm Password
- **Validations**:
  - Password and Confirm Password must match.
  - Email must be unique.

### 2. Login Page (Image 2)
- **Form Fields**:
  - Email
  - Password
- **Validations**:
  - Checks if the email exists in the database.
  - Verifies if the password matches the stored hash.

---

## Technology Stack

- **Backend Framework**: FastAPI
- **Database**: SQLite (configurable for PostgreSQL in production)
- **Frontend Templates**: Jinja2
- **Session Management**: Starlette SessionMiddleware
- **Environment Management**: Python-dotenv

---

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip

### Steps to Run Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/kheav-kienghok/LoginRegisterAPI.git
   cd LoginRegisterAPI

2. Create and activate a virtual environment:
    ```bash
    python -m venv env
    source env/bin/activate   # On Windows: env\Scripts\activate

3. Install dependencies:
    ```bash
    pip install -r requirements.txt

4. Set up environment variables: Create a **.env** file in the root directory with the following content: