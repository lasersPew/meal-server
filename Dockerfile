# Use python3.10 as a base
FROM python:3.13-alpine

LABEL Author=lasersPew \
    Maintainer=lasersPew \
    Name=meal-server

ARG SECRET_KEY

ENV DB_URL="sqlite:///database.db" \
    ALEMBIC_DB_URL="sqlite:///database.db" \
    SECRET_KEY=${SECRET_KEY} \
    ALGORITHM="HS256" \
    baseUrl="http://127.0.0.1:8000"

WORKDIR /app

COPY . .

RUN apk add --no-cache --upgrade curl && \
    pip3 install --no-cache-dir argon2-cffi -r requirements.txt 

EXPOSE 8000

# Entrypoint to run the application
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]