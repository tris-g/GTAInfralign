# Gebler Tooth Architects Infralign
![Dynamic JSON Badge](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fgta-infralign-pr-5.onrender.com%2Fstatic%2Ftesting%2Fcoverage.json&query=totals.percent_covered_display&suffix=%25&logo=python&label=coverage)

---
## Description
This is a private web app produced for employees to submit Autodesk Construction Cloud reports for analysis and access dashboard utilities.
## Requirements
- [Python 3.12](https://www.python.org/downloads/)
- [PostgreSQL 16](https://www.postgresql.org/download/)
## Steps
Before walking through the below steps, ensure that a PostgreSQL database is running and the details are provided within an `.env` file located at the project root with the following schema.
```
SECRET_KEY="a_key"
DB_NAME="a_database"
DB_USER="a_user"
DB_PASSWORD="a_password"
DB_HOST="a_host"
DB_PORT="a_port"
```
Firstly, install the required packages from PyPI using a package manager.
```
pip install -r requirements.txt
```
Secondly, collect up the statically served files.
```
python manage.py collectstatic --no-input
```
Thirdly, apply any outstanding database migrations.
```
python manage.py migrate
```
Lastly, run the server.
```
python manage.py runserver
```