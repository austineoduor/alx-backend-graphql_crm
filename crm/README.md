# CRM Setup Guide

### Step 1: Install Redis
Install Redis on your local machine:

- **Linux**: `sudo apt-get install redis-server`
- **macOS**: `brew install redis`
- **Windows**: Use **WSL** or Docker to run Redis.

Start the Redis server:

```bash
    redis-server

In a separate terminal, run the Celery worker:
    celery -A crm worker -l info

In another terminal, run Celery Beat:
    celery -A crm beat -l info

Run the migrations:
    python manage.py migrate