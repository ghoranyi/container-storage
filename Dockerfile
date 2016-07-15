FROM python:2.7.12-alpine

RUN apk update && apk add py-virtualenv
RUN virtualenv /virtualenv

ADD requirements.txt /app/requirements.txt
RUN /virtualenv/bin/pip install -r /app/requirements.txt

ADD . /app

RUN /virtualenv/bin/python /app/manage.py makemigrations
RUN /virtualenv/bin/python /app/manage.py migrate

EXPOSE 8878

CMD /virtualenv/bin/python /app/manage.py runserver 0.0.0.0:8878
