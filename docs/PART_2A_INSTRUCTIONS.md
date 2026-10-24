# Part 2A — Django Foundation

This package adds the initial Django project configuration and health endpoints. It does not yet add complaint models or application workflows.

## Apply the files

1. Stop the Django server if it is running.
2. Extract this ZIP.
3. Copy `manage.py` and the `config` folder into your existing `Cloud-Based-Complaint-Management-System` project folder.
4. If Windows asks whether to merge folders, choose **merge**. Replace only the matching `config` files with these Part 2A versions.
5. Keep your existing `.env`, `.gitignore`, and `requirements.txt`.

## Check the virtual environment

Open VS Code terminal at the project root:

```cmd
.venv\Scripts\activate
python -m pip install -r requirements.txt
python manage.py check
```

If `mysqlclient` fails to install on Windows, save the full error and send it before changing database packages.

## Configure MySQL

Make sure MySQL Server is running. Create the database and user from a MySQL client:

```sql
CREATE DATABASE complaint_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'complaint_app'@'localhost' IDENTIFIED BY 'YOUR_STRONG_PASSWORD';
GRANT ALL PRIVILEGES ON complaint_management.* TO 'complaint_app'@'localhost';
FLUSH PRIVILEGES;
```

Put the same credentials into the existing `.env`:

```dotenv
MYSQL_DATABASE=complaint_management
MYSQL_USER=complaint_app
MYSQL_PASSWORD=YOUR_STRONG_PASSWORD
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
```

Do not use the literal placeholder password. Do not share your real password in chat or commit `.env` to Git.

## Run initial checks

```cmd
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open these addresses in your browser:
- `http://127.0.0.1:8000/` — project status
- `http://127.0.0.1:8000/health/` — health endpoint
- `http://127.0.0.1:8000/admin/` — Django admin

`migrate` requires a running MySQL server and correct credentials. Do not move to complaint models until this foundation works.

## Git checkpoint

After checks pass:

```cmd
git status
git add manage.py config docs/PART_2A_INSTRUCTIONS.md
git commit -m "Add Django project foundation"
```

If Git has not been initialized, run `git init` first.
