FROM python:3.11

ENV PYTHONUNBUFFERED=1

WORKDIR /

COPY requirements.txt requirements.txt
COPY . .

RUN pip install -r requirements.txt
RUN pip install waitress

EXPOSE 8080

CMD [ "waitress-serve", "--call" , "app:create_app"]
