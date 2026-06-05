# EduEvents Flask + MySQL Version

Simple Flask structure for the Event Manager project. Data is stored in MySQL.

## MySQL Settings

Default connection:

```text
Host: localhost
Port: 3306
User: root
Password: empty
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
cd C:\Users\Demon\Downloads\Event-manager-main\Event-manager-main\eduevents_flask
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
```

Open:

- Public portal: http://127.0.0.1:5000/
- Admin dashboard: http://127.0.0.1:5000/admin

## Structure

```text
eduevents_flask/
├─ app.py
├─ config.py
├─ database.py
├─ run.py
├─ requirements.txt
├─ controllers/
│  ├─ authController.py
│  ├─ eventController.py
│  ├─ participantController.py
│  └─ storage.py
├─ routes/
│  ├─ authRoutes.py
│  ├─ eventRoutes.py
│  ├─ pageRoutes.py
│  └─ participantRoutes.py
├─ templates/
│  ├─ admin.html
│  └─ portal.html
└─ static/
   └─ uploads/
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
