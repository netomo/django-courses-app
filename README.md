# Django Courses App

This is the backend implementation that allows users to browse, enroll in, and manage online courses. It includes features such as user authentication, course browsing, enrollment, and course schedules.

The web application is built with Django and Django REST Framework. It provides a REST API for managing courses, course instances, and enrollments.

## Features

- User authentication with registration, login, and simple profile management
- Browsing for courses and course instances
  - Course details with video preview, studies plan, and course instances
  - Course instances with schedules, start and end dates, and teacher information
- Enrollment in course instances

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/netomo/django-courses-app.git
    cd my-django-courses-app
    ```
  
2. Create and activate a virtual environment:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the dependencies:
  
      ```bash
      pip install -r requirements.txt
      ```

4. Apply migrations:

      ```bash
      python manage.py migrate
      ```

5. Create a superuser:

      ```bash
      python manage.py createsuperuser
      ```

6. Run the development server:

      ```bash
      python manage.py runserver
      ```

## Configuration

Change your environment variables for sensitive settings such as DJANGO_SECRET_KEY and DJANGO_DEBUG in settings.ini.

## Usage

1. Visit the web application at [http://localhost:8000/].
2. Browse and search for courses using the course catalog.
3. Register for an account or log in to enroll in courses and manage your enrollments.

## API Endpoints

This backend provides REST API endpoints for managing courses, course instances, and enrollments. For a friendly experience understanding and using the API, visit the API documentation at:

- [http://localhost:8000/api/schema/swagger-ui/]
- [http://localhost:8000/api/schema/redoc/]
