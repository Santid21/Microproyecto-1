FROM python:3.9

WORKDIR /app

COPY . .

RUN pip install flask flask-cors requests

EXPOSE 8000

CMD ["python", "run.py"]
