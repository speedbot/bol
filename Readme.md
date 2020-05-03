### Clone The Repo

`git clone git@github.com:speedbot/bol.git`

### Set up the virtual environment

`virtualenv -p python3 venv`

### Activate the virtual environment

``pip install -r reqs``

### Run migrations

`python manage.py migrate`

### Run the Dev server 

`python manage.py runserver`


### Create superuser to access Admin

`python manage.py createsuperuser`

### Url list

- Shipment Details API `http://127.0.0.1:8000/api/shipment/`
- Client CRUD API - `http://127.0.0.1:8000/api/client/`
- Initial Sync API - `http://127.0.0.1:8000/api/shipment/initial_sync/`
- Admin interface for cron jobs - `http://127.0.0.1:8000/admin/`   

### Start Celery 

`celery -A bol  worker --loglevel=info`

`celery flower`

`celery -A app beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler`