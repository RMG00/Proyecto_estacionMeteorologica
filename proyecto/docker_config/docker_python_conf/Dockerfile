
FROM python:3.9.2

WORKDIR /app

COPY . /app

RUN pip install psycopg2==2.9.6 RPi.bme280

CMD ["python", "main.py"]
