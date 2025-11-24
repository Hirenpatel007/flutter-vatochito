@echo off
REM Migration script for new models (Windows)

echo Creating migrations for chat app...
python manage.py makemigrations chat

echo Creating migrations for accounts app...
python manage.py makemigrations accounts

echo Running migrations...
python manage.py migrate

echo Migration complete!
pause
