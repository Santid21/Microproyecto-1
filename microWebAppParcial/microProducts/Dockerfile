FROM python:3.9

WORKDIR /app

COPY . .

RUN pip install requests requests flask flask_sqlalchemy flask-mysql flask-cors requests pymysql

ENV PYTHONPATH=/app

EXPOSE 5001

CMD ["python", "run.py"]
