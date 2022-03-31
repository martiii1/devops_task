FROM python:3.11.0a6-alpine3.15
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install psycopg2
RUN apk update && apk add libpq-dev
COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt
COPY . /usr/src/app
CMD python3 /usr/src/app/scraper.py $env_user $env_pass $env_host $env_port $env_name $env_table_name