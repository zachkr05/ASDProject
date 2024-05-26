# project-b-11

To run the code do the following:

1) Create a virtual environment using Conda or Python Venv

Conda:

```
conda create --name project-b-11 python=3.11
conda activate project-b-11
pip3 install -r requirements.txt
```

Python Venv (Windows -> so adapt to Linux/Unix)
```
python3 -m venv venv
venv\Scripts\activate
pip3 install -r requirements.txt
```

2) To access the login page run:

```
python manage.py makemigrations
python manage.py makemigrations whistleblower
python manage.py migrate
python manage.py runserver
```

3) To begin, you need to create a site user from:
```
localhost/admin
```
Click users, then click create user group siteAdmin

4) Then all required setup is complete.
