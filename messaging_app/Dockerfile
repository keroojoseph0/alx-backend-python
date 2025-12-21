FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE -p 8000

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]