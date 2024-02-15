# Firefly Task Manager

An indie web project for simple task management in development teams.

Tech stack: [python3](https://www.python.org/downloads/release/python-3100/), [Django4](https://docs.djangoproject.com/en/4.2/), [django-taggit](https://django-taggit.readthedocs.io/en/stable/), [django-select2](https://django-select2.readthedocs.io/en/8.1.2/), [django signals](https://docs.djangoproject.com/en/4.2/topics/signals/), [Bootstrap5](https://getbootstrap.com/docs/5.3/getting-started/introduction/), [crispy-bootstrap5](https://pypi.org/project/crispy-bootstrap5/)

## Project features:

 - Teams management with their own members and projects.
 - Separated tasks management for different projects.
 - Notification system [based on the django signals] with filtering for current Team/Project.
 - User-friendly multiselect inputs with autocompleting.

## Installing and settings

You must have installed Python 3.10.0 or above<br>
__(Instructions for Windows)__

1. Installing project:
```commandline
git clone https://github.com/Quiet-Klirik/firefly-task-manager.git
cd firefly-task-manager
py -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
```

2. Setting up DB
```commandline
py manage.py migrate
py manage.py loaddata fixture_demo.json
```

3. Start project
```commandline
py manage.py runserver
```

### Demo user credentials:<br>
- Username: `user.demo`<br>
- Password: `demo_password`
