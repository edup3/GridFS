FROM python:3.13-slim

WORKDIR /app

COPY ../requirements.txt .

COPY . .

RUN pip install -r requirements.txt

ENV PORT=12345

CMD ["flask","--app","datanode","run","-p",PORT]
