# events_manager


### How to setup locally
#### Requirements

- Python3
- pip
- venv


#### setup instructions

- create   a virtualenv using venv
```cmd
   python -m pip install --upgrade pip
   python3 -m venv venv
   ```
- activate it 
```cmd
   source venv/bin/activate
   ```

- or activate Windows
```cmd
   venv/bin/activate.bat
   ```

- install dependencies from the requirements.txt file
```cmd
   pip install -r requirements.txt
   ```

- connect to postgresql database
```cmd
   create psql database with name event_manager and connect according to django settings
   ```

- migrate the database tables
```cmd
   python manage.py migrate
   ```

- create a new superuser
```cmd
   python manage.py createsuperuser
   ```

- start a development server using 
```cmd
   python manage.py runserver
   ```

- start the celery server using 
```cmd
   celery -A event_manager worker -l info
   ```

- start a postman application and export the api collection
```cmd
   start running the api's
   ```

FYI - 
  ```
   Celery is used for booking an event.
  Also an extra api is provided to check the progess of celery task w.r.t task_id.
  Also date,time check is added while booking an event.
```


Use Case - 
```
  Create multiple users.
  Create multiple events(only superusers are allowed to create).
  Login using any user email_id and password.
  Use the login token for all the other api for authentication.
  Start booking events with uses.
  Get user event info.
  Get event user info(only superusers are allowed to check).
```
  











