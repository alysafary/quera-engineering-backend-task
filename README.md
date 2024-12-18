# quera-engineering-task

# Project Overview

This project is a Django-based web application that includes RESTful APIs. The key features and functionalities are
structured into modular components within the application. It uses the following tools and frameworks:

- **Docker**: For containerization and ease of deployment.
- **Docker Compose**: For managing multi-container applications.
- **Poetry**: For dependency management.
- **Django REST Framework (DRF) Spectacular**: For generating OpenAPI documentation for the APIs.

---

## Project Setup Instructions

### Prerequisites

Ensure that you have the following installed:

- Docker
- Docker Compose

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Configure Environment Variables

Create a `.env` file in the project root and provide the necessary environment variables. For example:

```
SQL_ENGINE=django.db.backends.postgresql # if you don't want to use sqlite3
POSTGRES_DB=your_database
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

### 3. Build and Start the Project

Use Docker Compose to build and start the services:

```bash
docker-compose up --build
```

This command will:

- Build the Django application using the `development` target in the Dockerfile.
- Run database migrations automatically.
- Start the development server at `http://0.0.0.0:8080/`.

### 4. Stop the Project

To stop the project, use:

```bash
docker-compose down
```

## Folder Structure

Below is an overview of the project's folder structure:

- **`app/`**: Contains the core application logic, including models, serializers, views, and tests.
    - **`models/`**: Defines the database models for questions and answers.
    - **`serializers/`**: Handles data serialization and deserialization for API requests and responses.
    - **`views/`**: Contains logic for handling HTTP requests for the APIs.
    - **`tests/`**: Includes unit tests for various components.

- **`project/`**: Contains project-level configurations such as settings and URL routing.
- **`templates/`**: Includes templates like Swagger UI for API documentation.
- **`docker-compose.yml`**: Defines the multi-container setup.
- **`Dockerfile`**: Specifies the instructions to build the Docker image.
- **`pyproject.toml`**: Poetry configuration file for dependencies.
- **`poetry.lock`**: Locks dependency versions for consistency.

---

## API Documentation

This project uses DRF Spectacular to provide API documentation. The documentation is auto-generated based on the defined
serializers and views. To access it, navigate to:

```
http://0.0.0.0:8080/docs/
```

---

## Running Tests

Tests can be executed using `pytest` inside the Docker container:

```bash
docker exec -it <container_name> pytest
```

Alternatively, if Poetry is installed, you can run:

```bash
poetry run pytest
```

or just:

```bash
pytest
```
