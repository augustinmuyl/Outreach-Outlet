FROM python:3.13-slim

WORKDIR /flask-app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["gunicorn", "-b", "0.0.0.0:5001", "main:app"]
