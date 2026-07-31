# Social Media API

A RESTful API for a social media platform built with **Django REST Framework**.

The project includes authentication, user profiles, following system, posts, hashtags, likes, comments, filtering, pagination, API documentation, and scheduled post publishing with Celery.

## Features

* JWT authentication
* User registration and profile management
* Follow / Unfollow users
* Create, update and delete posts
* Scheduled post publishing (Celery + Celery Beat)
* Likes and comments
* Hashtags support
* Filtering, searching and pagination
* Swagger & ReDoc API documentation
* Dockerized application

## Tech Stack

* Python 3.12
* Django
* Django REST Framework
* PostgreSQL
* Docker & Docker Compose
* Celery
* Redis
* drf-spectacular
* django-filter

## Installation

Clone the repository:

```bash
git clone https://github.com/step-98/social-media-api.git
cd social-media-api
```

Create an `.env` file and run:
```env
POSTGRES_DB=your_db
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=social_db
POSTGRES_PORT=5432

SECRET_KEY=your_secret_key

REDIS_HOST=redis
REDIS_PORT=6379
```
```bash
docker compose up --build
```

Apply migrations and create a superuser:

```bash
docker compose exec social python manage.py migrate
docker compose exec social python manage.py createsuperuser
```

## API Documentation

* Swagger: `http://127.0.0.1:8000/api/doc/swagger/`
* ReDoc: `http://127.0.0.1:8000/api/doc/redoc/`

