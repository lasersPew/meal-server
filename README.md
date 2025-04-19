![Plan-a-meal cover](assets/cover.png)

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Introduction](#intro)
- [Usage](#usage)
  - [Running it natively](#running-it-natively)
  - [Running it in a Virtual Environment](#running-it-in-a-virtual-environment)
- [Packages Used](#packages-used)
- [Contributors](#contributors)

## Intro

Plan-a-meal is a meal planning application that allows users to create, manage, and share meal plans. The application provides a user-friendly interface for selecting recipes, generating shopping lists, and tracking nutritional information.

This document describes API as it is right now, but it is not final. The API is still under development and may change in the future.

Please refer to the documentation for the latest updates.

The API is designed to be RESTful and follows standard conventions for HTTP methods and status codes. Each endpoint is documented with its purpose, request parameters, and response formats.

The API supports authentication and authorization mechanisms to ensure secure access to user data.

## Usage

### Running it natively

```sh
# Install requirements
pip install -r requirements.txt

# Start the server
fastapi run --reload main.py
# or fastapi run --reload main.py to run locally
```

### Running it in a Virtual Environment

```sh
# Create a virtual environment
python -m venv venv/

# Use the virtual environment you just created
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Start the server
fastapi run --reload main.py
# or fastapi run --reload main.py to run locally
```

### Running it using Docker

```sh
docker run -d \
  --name meal-server \
  --restart always \
  -p 8000:8000 \
  -e SECRET_KEY=supersecretkey \
  -v meal_db:/config/database.db:rw \
  ghcr.io/laserspew/meal-server:v1.3
```

### or Docker Compose

```sh
wget https://raw.githubusercontent.com/lasersPew/meal-server/refs/heads/master/docker-compose.yml
docker compose up -d docker-compose.yml
```

## Packages used

- `alembic` - Database migrations
- `fastapi[standard]` - API itself
- `python-jose` - Authentication and Authorization with JWT and Bearer tokens
- `python-dotenv` - Environment variables
- `uuid` - UUID Generation
- `passlib[argon2]` - argon2id encryptor and decryptor
- `sqlmodel` - SQL-related things

### Contributors

- lasersPew
