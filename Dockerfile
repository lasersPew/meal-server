# Use python3.10 as a base
FROM python:3.10-alpine

LABEL Author=lasersPew \
    Maintainer=lasersPew \
    Name=meal-server

ARG SECRET_KEY

ENV DB_URL=sqlite:///database.db \
    ALEMBIC_DB_URL=sqlite:///database.db \
    SECRET_KEY=${SECRET_KEY} \
    ALGORITHM=HS256 \
    baseUrl=http://127.0.0.1:8000

EXPOSE 8000

RUN \
apk update && \
apk add --no-cache --upgrade alpine-sdk curl && \
mkdir -p /app && \
pip3 install argon2-cffi && \
apk del --purge alpine-sdk

COPY . /app

RUN pip3 install -r /app/requirements.txt

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"]