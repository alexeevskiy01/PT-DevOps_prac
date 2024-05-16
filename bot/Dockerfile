FROM python:3.9-alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev linux-headers python3-dev libpq-dev
#RUN pip install psycopg2-binary==2.9.9 python-dotenv==1.0.1 python-telegram-bot==13.7 paramiko

COPY . .
#COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "/app/telegram_bot_2.py"]

