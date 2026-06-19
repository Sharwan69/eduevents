# EduEvents Flask + MySQL

EduEvents is a Flask event management app for school events. Data is stored in MySQL, and the project is arranged in the requested Flask file structure.

## MySQL Settings

Default connection:

```text
Host: localhost
Port: 3306
User: " "
Password: " "
Database: eduevents
```

If your MySQL password is different, set it before running:

```powershell
$env:MYSQL_HOST="localhost"
$env:MYSQL_PORT="3306"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="your_password"
$env:MYSQL_DATABASE="eduevents"
```

The app creates the `eduevents` database and tables automatically.

## Run

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirement.txt
.\.venv\Scripts\python.exe run.py
```

Open:

- Home: http://127.0.0.1:5000/
- Login: http://127.0.0.1:5000/login
- Dashboard: http://127.0.0.1:5000/dashboard
- Register: http://127.0.0.1:5000/register
- About: http://127.0.0.1:5000/about
- Database: http://127.0.0.1:5000/database

## Structure

```text
eduevents_flask/
|-- app/
|   |-- __init__.py
|   |-- database.py
|   |-- run.py
|   |-- middleware/
|   |   `-- authcheck.py
|   |-- routes/
|   |   |-- __init__.py
|   |   |-- authRoutes.py
|   |   |-- eventRoutes.py
|   |   |-- pageRoutes.py
|   |   `-- participantRoutes.py
|   |-- static/
|   |   |-- css/
|   |   |   `-- register.css
|   |   `-- uploads/
|   |-- test/
|   |   `-- test_app.py
|   `-- templates/
|       |-- about.html
|       |-- base.html
|       |-- dashboard.html
|       |-- database.html
|       |-- home.html
|       |-- login.html
|       `-- register.html
|-- controllers/
|   |-- __init__.py
|   |-- authController.py
|   |-- eventController.py
|   |-- participantController.py
|   `-- storage.py
|-- app.py
|-- config.py
|-- database.py
|-- requirement.txt
|-- requirements.txt
`-- run.py
```

## API

- `POST /api/login`
- `GET /api/events`
- `GET /api/events/<id>`
- `POST /api/events`
- `PUT /api/events/<id>`
- `DELETE /api/events/<id>`
- `GET /api/participants`
- `GET /api/participants/<id>`
- `POST /api/participants`
- `PUT /api/participants/<id>`
- `DELETE /api/participants/<id>`
- `GET /api/stats`
- `POST /api/seed`
- `POST /api/sync`
